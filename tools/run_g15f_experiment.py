"""G15F-1 — Flux dream consolidation experiment harness.

Protocol, bars and controls are pre-registered in
docs/amendments/g15f_dream_consolidation.md (committed before any data).
This script implements §3 exactly; it computes metrics but does NOT
decide the verdict — the verdict is judged against the frozen bars in
the amendment and recorded in LOGBOOK.md.

Arms (each from an identical deep-copied post-training state):
  D — dream replay on (manual apply_dream, injection booked)
  N — energy-matched unspecific injection, dream off
  R — nothing
NC1 — no-engram control: identical training with active_pattern_id=0
      throughout, then ARM-D. Must produce 0 replay seeds and 0 blends.

Usage:
  python tools/run_g15f_experiment.py --smoke     # one technical smoke (D8)
  python tools/run_g15f_experiment.py             # THE full run (seeds 42,43,44)

Headless (D7). Output: JSON per seed to archive/run-logs/g15f/.
"""
from __future__ import annotations
import argparse
import copy
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.structures import Nodes
from world.flux.bridges import Bridges
from world.flux.audit import EnergyAuditor
from world.flux.binding import BindingConfig
from world.flux.decay import DecayConfig
from world.flux.thermal import ThermalConfig
from world.flux.plasticity import PlasticityConfig
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick
from world.flux.dream import DreamConfig, apply_dream

# ---- fixed protocol parameters (amendment §3; changes require a new ID) ----
CUBE = (80, 40, 10)
N_QUANTA = 10_000
DT = 1.0 / 60.0
SEEDS = (42, 43, 44)
TRAIN_S = 30.0
REST_S = 60.0
WINDOW_S = 2.0
PAT_A = dict(pid=1, freq=800.0, x_window=(0.0, 20.0))
PAT_B = dict(pid=2, freq=3200.0, x_window=(60.0, 80.0))
TRAIN_N_PER_TICK = 10
TRAIN_ENERGY_PER = 10.0
DREAM_SEEDS_PER_TICK = 5
DREAM_SEED_ENERGY = 10.0          # -> 3000 E/s replay injection
NOISE_N_PER_TICK = 30
NOISE_ENERGY_PER = 100.0 / 60.0   # 30 * (100/60) * 60 = 3000 E/s, matched
AUDIT_TOL = 1e-9

OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "g15f"


def make_world(seed: int):
    rng = np.random.default_rng(seed)
    quanta = Quanta(60_000)
    grid = Grid(CUBE, 1.0)
    nodes = Nodes(8192)
    bridges = Bridges(8192 * 10)
    gs = np.array(CUBE, dtype=np.float64) * grid.voxel_size
    n = N_QUANTA
    # Fill the first n slots of the pre-allocated SoA arrays (do NOT
    # rebind the arrays — capacity is 60k for injection headroom).
    quanta.pos[:n] = rng.uniform(0, gs, size=(n, 3))
    quanta.vel[:n] = rng.uniform(-5, 5, size=(n, 3))
    quanta.freq[:n] = rng.uniform(100, 10000, size=n)
    quanta.polarity[:n] = rng.choice([-1, 1], size=n).astype(np.int8)
    quanta.alive[: n // 2] = True
    return quanta, grid, nodes, bridges


def n_by_pattern(nodes: Nodes) -> dict[int, int]:
    alive = nodes.alive
    return {p: int(((nodes.pattern_id == p) & alive).sum()) for p in (1, 2)}


def run_phase_T(quanta, grid, nodes, bridges, audit, seed: int,
                labeled: bool, train_s: float) -> None:
    """Alternating 2 s windows: even -> pattern A, odd -> pattern B.
    labeled=False (NC1): identical injection, active_pattern_id stays 0."""
    binding_cfg = BindingConfig()
    decay_cfg = DecayConfig()
    thermal_cfg = ThermalConfig()
    plasticity_cfg = PlasticityConfig()
    inj_rng = np.random.default_rng(seed + 1_000_000)
    n_ticks = int(train_s / DT)
    state = {"pat": PAT_A}

    def injector(q, g):
        pat = state["pat"]
        n_inj = inject_hot_floor(q, g, n=TRAIN_N_PER_TICK,
                                 energy_per=TRAIN_ENERGY_PER,
                                 freq_mean=pat["freq"], rng=inj_rng,
                                 x_window=pat["x_window"])
        e = n_inj * TRAIN_ENERGY_PER
        audit.record_injection(e)
        return e

    for k in range(n_ticks):
        window = int((k * DT) // WINDOW_S)
        pat = PAT_A if window % 2 == 0 else PAT_B
        state["pat"] = pat
        nodes.active_pattern_id = pat["pid"] if labeled else 0

        result = tick(quanta, grid, DT, injector=injector, nodes=nodes,
                      binding_cfg=binding_cfg, decay_cfg=decay_cfg,
                      bridges=bridges, plasticity_cfg=plasticity_cfg,
                      thermal_cfg=thermal_cfg,
                      rng=np.random.default_rng(seed + k), tick_index=k)
        e_exported, binding_heat, decay_heat = result
        audit.record_export(e_exported)
        audit.record_binding_heat(binding_heat)
        audit.record_decay_heat(decay_heat)
        audit.step()
        if k % 60 == 59:
            audit.check()
    nodes.active_pattern_id = 0
    audit.check()


def run_phase_R(quanta, grid, nodes, bridges, audit, seed: int,
                arm: str, rest_s: float, tick_offset: int) -> dict:
    """Rest phase. arm in {'D', 'N', 'R'}."""
    binding_cfg = BindingConfig()
    decay_cfg = DecayConfig()
    thermal_cfg = ThermalConfig()
    plasticity_cfg = PlasticityConfig()
    inj_rng = np.random.default_rng(seed + 2_000_000)
    n_ticks = int(rest_s / DT)
    dream_cfg = DreamConfig(
        dream_mode_enabled=True,
        dream_replay_seeds_per_tick=DREAM_SEEDS_PER_TICK,
        dream_replay_seed_energy=DREAM_SEED_ENERGY,
    ) if arm == "D" else None

    stats = {"replay_seeds_fired": 0, "blend_events": 0,
             "dream_energy_injected": 0.0}

    def injector_noise_uniform(q, g):
        # Energy-matched unspecific injection: uniform freq 100-10000,
        # full floor, 3000 E/s total (amendment §3, ARM-N).
        e_total = 0.0
        for _ in range(NOISE_N_PER_TICK):
            n_inj = inject_hot_floor(q, g, n=1, energy_per=NOISE_ENERGY_PER,
                                     freq_mean=float(inj_rng.uniform(100, 10000)),
                                     rng=inj_rng)
            e_total += n_inj * NOISE_ENERGY_PER
        audit.record_injection(e_total)
        return e_total

    injector = injector_noise_uniform if arm == "N" else None

    for k in range(n_ticks):
        tk = tick_offset + k
        if dream_cfg is not None:
            out = apply_dream(quanta, nodes, grid, dt=DT, cfg=dream_cfg,
                              tick_index=tk,
                              rng=np.random.default_rng(seed + 3_000_000 + k))
            audit.record_injection(out["energy_injected"])
            stats["replay_seeds_fired"] += out["replay_seeds_fired"]
            stats["blend_events"] += out["blend_events"]
            stats["dream_energy_injected"] += out["energy_injected"]

        result = tick(quanta, grid, DT, injector=injector, nodes=nodes,
                      binding_cfg=binding_cfg, decay_cfg=decay_cfg,
                      bridges=bridges, plasticity_cfg=plasticity_cfg,
                      thermal_cfg=thermal_cfg,
                      rng=np.random.default_rng(seed + tk), tick_index=tk)
        e_exported, binding_heat, decay_heat = result
        audit.record_export(e_exported)
        audit.record_binding_heat(binding_heat)
        audit.record_decay_heat(decay_heat)
        audit.step()
        if k % 60 == 59:
            audit.check()
    audit.check()
    return stats


def run_seed(seed: int, train_s: float, rest_s: float, labeled: bool = True) -> dict:
    """Train once, branch the state into the three arms."""
    quanta, grid, nodes, bridges = make_world(seed)
    audit = EnergyAuditor(quanta=quanta, tol=AUDIT_TOL, nodes=nodes)
    audit.record_initial()

    t0 = time.time()
    run_phase_T(quanta, grid, nodes, bridges, audit, seed,
                labeled=labeled, train_s=train_s)
    n_T = n_by_pattern(nodes)
    tick_offset = int(train_s / DT)

    result = {
        "seed": seed, "labeled": labeled,
        "train_s": train_s, "rest_s": rest_s,
        "N_T": n_T, "arms": {},
        "audit_ok_train": True,   # audit.check() above raises otherwise
    }

    for arm in ("D", "N", "R"):
        q2 = copy.deepcopy(quanta)
        g2 = copy.deepcopy(grid)
        n2 = copy.deepcopy(nodes)
        b2 = copy.deepcopy(bridges)
        a2 = EnergyAuditor(quanta=q2, tol=AUDIT_TOL, nodes=n2)
        a2.record_initial()
        stats = run_phase_R(q2, g2, n2, b2, a2, seed, arm, rest_s, tick_offset)
        n_end = n_by_pattern(n2)
        S = {p: (n_end[p] / n_T[p] if n_T[p] > 0 else None) for p in (1, 2)}
        result["arms"][arm] = {
            "N_end": n_end, "S": S, "audit_ok": True, **stats,
        }
    result["wall_s"] = round(time.time() - t0, 1)
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="One technical smoke (D8): seed 42, 10 s / 10 s. "
                         "Numbers carry no evidential weight.")
    args = ap.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.smoke:
        res = run_seed(42, train_s=10.0, rest_s=10.0)
        out = OUT_DIR / "smoke.json"
        out.write_text(json.dumps(res, indent=2))
        print(json.dumps(res, indent=2))
        print(f"# smoke written to {out} — technical check only (D8)")
        return 0

    # THE full run: 3 seeds x 3 arms + NC1 per seed.
    for seed in SEEDS:
        res = run_seed(seed, train_s=TRAIN_S, rest_s=REST_S, labeled=True)
        nc = run_seed(seed, train_s=TRAIN_S, rest_s=REST_S, labeled=False)
        res["NC1"] = {
            "N_T": nc["N_T"],
            "replay_seeds_fired": nc["arms"]["D"]["replay_seeds_fired"],
            "blend_events": nc["arms"]["D"]["blend_events"],
        }
        out = OUT_DIR / f"seed_{seed}.json"
        out.write_text(json.dumps(res, indent=2))
        print(f"# seed {seed}: N_T={res['N_T']} "
              f"S_D={res['arms']['D']['S']} S_N={res['arms']['N']['S']} "
              f"S_R={res['arms']['R']['S']} blends={res['arms']['D']['blend_events']} "
              f"NC1={res['NC1']['replay_seeds_fired']}/{res['NC1']['blend_events']} "
              f"({res['wall_s']}s wall)")
    print(f"# full run written to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

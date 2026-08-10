"""G15F-2 — engram persistence condition map.

Pre-registered in docs/amendments/g15f2_engram_persistence.md (committed
before any data). Fixed matrix, no adaptive search: 6 conditions x 3 seeds,
each 30 s labeled training + 60 s rest with NOTHING (ARM-R only).
Computes metrics; the verdict is judged against the frozen bars.

Usage:
  python tools/run_g15f2_experiment.py          # the full matrix
Output: archive/run-logs/g15f2/<cond>_seed<k>.json + summary line per run.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from world.flux.structures import Nodes
from world.flux.audit import EnergyAuditor
from world.flux.binding import BindingConfig
from world.flux.decay import DecayConfig
from world.flux.thermal import ThermalConfig
from world.flux.plasticity import PlasticityConfig
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick

from tools.run_g15f_experiment import (
    make_world, n_by_pattern, PAT_A, PAT_B,
    TRAIN_N_PER_TICK, TRAIN_ENERGY_PER, DT, SEEDS, AUDIT_TOL,
)

TRAIN_S = 30.0
REST_S = 60.0

# Fixed condition matrix (amendment §2). Changes require a new ID.
CONDITIONS = {
    "C0": dict(window_s=2.0, t_decay_crit=0.02, gamma=100.0, single_pattern=False),
    "C1": dict(window_s=5.0, t_decay_crit=0.02, gamma=100.0, single_pattern=False),
    "C2": dict(window_s=2.0, t_decay_crit=0.05, gamma=100.0, single_pattern=False),
    "C3": dict(window_s=2.0, t_decay_crit=0.02, gamma=20.0, single_pattern=False),
    "C4": dict(window_s=2.0, t_decay_crit=0.02, gamma=100.0, single_pattern=True),
    "C5": dict(window_s=5.0, t_decay_crit=0.05, gamma=100.0, single_pattern=False),
}

OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "g15f2"


def run_condition(cond_name: str, cond: dict, seed: int) -> dict:
    quanta, grid, nodes, bridges = make_world(seed)
    audit = EnergyAuditor(quanta=quanta, tol=AUDIT_TOL, nodes=nodes)
    audit.record_initial()

    binding_cfg = BindingConfig()
    decay_cfg = DecayConfig(gamma=cond["gamma"], T_decay_crit=cond["t_decay_crit"])
    thermal_cfg = ThermalConfig()
    plasticity_cfg = PlasticityConfig()
    inj_rng = np.random.default_rng(seed + 1_000_000)
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

    def step(k, inj):
        result = tick(quanta, grid, DT, injector=inj, nodes=nodes,
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

    t0 = time.time()
    n_train_ticks = int(TRAIN_S / DT)
    for k in range(n_train_ticks):
        if cond["single_pattern"]:
            pat = PAT_A
        else:
            window = int((k * DT) // cond["window_s"])
            pat = PAT_A if window % 2 == 0 else PAT_B
        state["pat"] = pat
        nodes.active_pattern_id = pat["pid"]
        step(k, injector)
    nodes.active_pattern_id = 0
    audit.check()
    n_T = n_by_pattern(nodes)

    n_rest_ticks = int(REST_S / DT)
    for k in range(n_rest_ticks):
        step(n_train_ticks + k, None)
    audit.check()
    n_end = n_by_pattern(nodes)

    S = {p: (n_end[p] / n_T[p] if n_T[p] > 0 else None) for p in (1, 2)}
    return {
        "condition": cond_name, "params": cond, "seed": seed,
        "N_T": n_T, "N_end": n_end, "S": S,
        "audit_ok": True,  # audit.check() raises otherwise
        "wall_s": round(time.time() - t0, 1),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for cond_name, cond in CONDITIONS.items():
        for seed in SEEDS:
            res = run_condition(cond_name, cond, seed)
            out = OUT_DIR / f"{cond_name}_seed{seed}.json"
            out.write_text(json.dumps(res, indent=2))
            print(f"# {cond_name} seed {seed}: N_T={res['N_T']} "
                  f"N_end={res['N_end']} S={res['S']} ({res['wall_s']}s)")
    print(f"# matrix complete -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

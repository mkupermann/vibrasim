"""G164 — retention of the rest-length register under thermal agitation.

Pre-registered in docs/amendments/g164_register_retention.md.
Metrics only; verdict against the frozen bars.

Usage: python tools/run_g164_register_retention.py
Output: archive/run-logs/g164/results.json + summary.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick

SEEDS = [42, 7, 13]
K_BITS = 6
X0 = 15.0
BAND_Y = 30.0
SHORT, LONG = 6.5, 10.5
UNIFORM = 8.5
T_CONSOL = 8
T_RETRIEVE = 800
N_PATTERNS = 8
TENSION_K = 8.0
DAMPING = 0.95
IDLE_THERMAL = 2.0          # chain_cascade calibration value
IDLE_INTERVALS = (2_000, 10_000, 50_000)
CENSUS_EVERY = 1_000
EMPTY = np.empty(0, dtype=np.int32)
OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "g164"


def base_cfg(seed: int, per_bond: bool, thermal: float) -> WorldConfig:
    return WorldConfig(
        rng_seed=seed, box_size=(120.0, 60.0, 60.0),
        repulsion_cell_size=120.0,
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
        lambda_gen=0.0, lambda_dec=0.0, atom_valence=2,
        atom_repulsion_k=0.0, repulsion_k=0.0,
        node_thermal_speed=thermal,
        anchor_damping=0.0, neuron_dynamics_enabled=False,
        stdp_enabled=False, btsp_enabled=False, r_2=12.0,
        graceful_capacity=True,
        per_bond_rest_enabled=per_bond,
        bridge_tension_k=TENSION_K, bridge_tension_damping=DAMPING,
    )


def encoded_positions(pattern) -> list[float]:
    xs = [X0]
    for bit in pattern:
        xs.append(xs[-1] + (LONG if bit else SHORT))
    return xs


def census(w: World) -> list[tuple[int, int, float]]:
    out = []
    for b in range(w.b_count):
        if w.b_alive[b]:
            out.append((int(w.b_atom_i[b]), int(w.b_atom_j[b]),
                        round(float(w.b_rest_len[b]), 2)))
    return sorted(out)


def run_one(pattern, seed: int, arm: str, idle_ticks: int) -> dict:
    """arm in {'P','T0','OLDREST','NEG'}. Returns decode acc + diagnostics.

    Thermal applies ONLY during idle (cfg swap); write and retrieve run at
    thermal 0 exactly as G163.
    """
    per_bond = arm != "OLDREST"
    idle_thermal = 0.0 if arm == "T0" else IDLE_THERMAL
    cfg_quiet = base_cfg(seed, per_bond, 0.0)
    w = World(cfg_quiet)

    xs_enc = encoded_positions(pattern)
    slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4,
                             EMPTY, 0) for x in xs_enc]

    # WRITE (thermal 0), census gate as G163
    for _ in range(T_CONSOL):
        for s, x in zip(slots, xs_enc):
            w.k_pos[s] = (x, BAND_Y, 30.0)
            w.k_vel[s] = 0.0
        tick(w, cfg_quiet.dt)
    c0 = census(w)
    pairs0 = {(min(a, b), max(a, b)) for a, b, _ in c0}
    write_valid = (len(c0) == K_BITS
                   and pairs0 == {(i, i + 1) for i in range(K_BITS)})

    if arm == "NEG":
        w.b_alive[: w.b_count] = False

    # IDLE — free dynamics, pins released, thermal per arm
    w.config = replace(w.config, node_thermal_speed=idle_thermal)
    census_events = []
    new_pairs_total = 0
    lost_pairs_total = 0
    for t in range(idle_ticks):
        tick(w, w.config.dt)
        if (t + 1) % CENSUS_EVERY == 0 and arm not in ("NEG",):
            c_now = census(w)
            pairs_now = {(min(a, b), max(a, b)) for a, b, _ in c_now}
            if pairs_now != pairs0:
                census_events.append((t + 1, c_now))
                new_pairs_total += len(pairs_now - pairs0)
                lost_pairs_total += len(pairs0 - pairs_now)
                pairs0 = pairs_now
    drift_max = float(max(
        abs(float(w.k_pos[s][0]) - x) for s, x in zip(slots, xs_enc)))
    # back to quiet for scramble+retrieve
    w.config = replace(w.config, node_thermal_speed=0.0)

    # SCRAMBLE
    for i, s in enumerate(slots):
        w.k_pos[s] = (X0 + i * UNIFORM, BAND_Y, 30.0)
        w.k_vel[s] = 0.0

    # RETRIEVE (thermal 0, carrier-0 pin, formation freeze)
    pairs_frozen = {(min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
                     max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
                    for b in range(w.b_count) if w.b_alive[b]}
    for _ in range(T_RETRIEVE):
        w.k_pos[slots[0]] = (X0, BAND_Y, 30.0)
        w.k_vel[slots[0]] = 0.0
        tick(w, w.config.dt)
        for b in range(w.b_count):
            if w.b_alive[b]:
                key = (min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
                       max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
                if key not in pairs_frozen:
                    w.b_alive[b] = False

    decoded = []
    for i in range(K_BITS):
        d = float(w.k_pos[slots[i + 1]][0] - w.k_pos[slots[i]][0])
        decoded.append(1 if d > UNIFORM else 0)
    acc = sum(int(a == b) for a, b in zip(decoded, pattern)) / K_BITS
    return {"acc": acc, "write_valid": write_valid,
            "census_events": len(census_events),
            "new_bonds": new_pairs_total, "lost_bonds": lost_pairs_total,
            "drift_max": round(drift_max, 2)}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    arms = ([("P", n) for n in IDLE_INTERVALS]
            + [("T0", 50_000), ("OLDREST", 50_000), ("NEG", 50_000)])
    agg = {f"{a}@{n}": [] for a, n in arms}
    events = {f"{a}@{n}": 0 for a, n in arms}
    new_bonds = {f"{a}@{n}": 0 for a, n in arms}
    lost_bonds = {f"{a}@{n}": 0 for a, n in arms}
    drift = {f"{a}@{n}": 0.0 for a, n in arms}
    write_valid_all = True

    for seed in SEEDS:
        rng = np.random.default_rng(1640 + seed)
        acc = {k: 0.0 for k in agg}
        for _ in range(N_PATTERNS):
            while True:
                pattern = list(rng.integers(0, 2, K_BITS))
                if 0 < sum(pattern) < K_BITS:
                    break
            for a, n in arms:
                r = run_one(pattern, seed, a, n)
                key = f"{a}@{n}"
                acc[key] += r["acc"]
                events[key] += r["census_events"]
                new_bonds[key] += r["new_bonds"]
                lost_bonds[key] += r["lost_bonds"]
                drift[key] = max(drift[key], r["drift_max"])
                if a == "P":
                    write_valid_all &= r["write_valid"]
        for k in agg:
            agg[k].append(acc[k] / N_PATTERNS)
        print(f"# seed {seed}: " + " ".join(
            f"{k}={agg[k][-1]:.3f}" for k in agg))

    out = {
        "per_seed": agg,
        "mean": {k: float(np.mean(v)) for k, v in agg.items()},
        "census_change_events": events,
        "new_bonds": new_bonds, "lost_bonds": lost_bonds,
        "drift_max": drift,
        "write_valid_all_P": bool(write_valid_all),
    }
    (OUT_DIR / "results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out["mean"], indent=2))
    print(f"# census_change_events={events}")
    print(f"# new_bonds={new_bonds} lost_bonds={lost_bonds}")
    print(f"# drift_max={drift}")
    print(f"# write_valid_all_P={write_valid_all}")
    print(f"# written -> {OUT_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

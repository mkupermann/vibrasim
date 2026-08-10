"""PRIM14-D1 — restore-dynamics regime matrix (tension_k × damping).

Pre-registered in docs/amendments/bp_prim14_d1_dynamics_matrix.md.
Same single-bond diagnostic as D0 post-erratum; 3×3 fixed matrix; arms P/C
per condition; stability recorded. Metrics only — verdict against frozen bars.

Usage: python tools/run_bp_prim14_d1.py
Output: archive/run-logs/prim14/d1.json + summary lines.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import tick

BAND_Y = 30.0
EMPTY = np.empty(0, dtype=np.int32)
SEEDS = (42, 7, 13)
RELAX_TICKS = 2000
STORED = (13.0, 17.0, 29.0)
DISPLACED_MID = 21.0
DISPLACEMENT = 4.0
MATRIX = {          # fixed 3x3 (amendment §3); changes = new ID
    "C0":  (0.5, 0.95),   # anchor = D0
    "C-a": (0.5, 0.90),
    "C-b": (0.5, 0.98),
    "C-c": (2.0, 0.90),
    "C-d": (2.0, 0.95),
    "C-e": (2.0, 0.98),
    "C-f": (8.0, 0.90),
    "C-g": (8.0, 0.95),
    "C-h": (8.0, 0.98),
}
OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "prim14"


def make_cfg(seed: int, per_bond: bool, k: float, damping: float) -> WorldConfig:
    return WorldConfig(rng_seed=seed, box_size=(60.0, 60.0, 60.0),
                       n_initial_vibrations=0, n_vibrations_max=64,
                       n_nodes_max=64, lambda_gen=0.0, lambda_dec=0.0,
                       atom_valence=2, atom_repulsion_k=0.0, repulsion_k=0.0,
                       node_thermal_speed=0.0, anchor_damping=0.0,
                       neuron_dynamics_enabled=False, stdp_enabled=False,
                       btsp_enabled=False, r_2=12.0, graceful_capacity=True,
                       per_bond_rest_enabled=per_bond,
                       bridge_tension_k=k, bridge_tension_damping=damping)


def run_arm(seed: int, per_bond: bool, k: float, damping: float) -> dict:
    cfg = make_cfg(seed, per_bond, k, damping)
    w = World(cfg)
    slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0)
             for x in STORED]
    for _ in range(8):
        for s, x in zip(slots, STORED):
            w.k_pos[s] = (x, BAND_Y, 30.0)
            w.k_vel[s] = 0.0
        tick(w, cfg.dt)

    mid = slots[1]
    w.k_pos[mid] = (DISPLACED_MID, BAND_Y, 30.0)
    w.k_vel[mid] = 0.0

    max_dev = 0.0
    x_1500 = None
    for t in range(RELAX_TICKS):
        w.k_pos[slots[0]] = (STORED[0], BAND_Y, 30.0); w.k_vel[slots[0]] = 0.0
        w.k_pos[slots[2]] = (STORED[2], BAND_Y, 30.0); w.k_vel[slots[2]] = 0.0
        tick(w, cfg.dt)
        dev = abs(float(w.k_pos[mid][0]) - STORED[1])
        max_dev = max(max_dev, dev)
        if t == 1499:
            x_1500 = float(w.k_pos[mid][0])
    end_x = float(w.k_pos[mid][0])
    R = (DISPLACEMENT - abs(end_x - STORED[1])) / DISPLACEMENT
    # Stability per amendment §3: max|x_mid - stored| > 1.5 * 6 units, or
    # endpoint not settled (|x(2000) - x(1500)| >= 0.1).
    unstable = (max_dev > 1.5 * 6.0) or (abs(end_x - x_1500) >= 0.1)
    return {"end_x": round(end_x, 3), "R": round(R, 3),
            "max_dev": round(max_dev, 3), "settled": abs(end_x - x_1500) < 0.1,
            "unstable": bool(unstable)}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for cond, (k, damping) in MATRIX.items():
        for seed in SEEDS:
            p = run_arm(seed, True, k, damping)
            c = run_arm(seed, False, k, damping)
            row = {"condition": cond, "k": k, "damping": damping, "seed": seed,
                   "P": p, "C": c}
            results.append(row)
        print(f"# {cond} (k={k}, d={damping}): "
              f"P R={p['R']} max_dev={p['max_dev']} unstable={p['unstable']} | "
              f"C R={c['R']}")
    (OUT_DIR / "d1.json").write_text(json.dumps(results, indent=2))
    print(f"# written -> {OUT_DIR / 'd1.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

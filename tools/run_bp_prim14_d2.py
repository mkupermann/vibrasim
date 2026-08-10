"""PRIM14-D2 — pure attractor test (write channel closed via valence saturation).

Pre-registered in docs/amendments/bp_prim14_d2_pure_attractor.md.
Metrics only; verdict against the frozen bars.

Usage: python tools/run_bp_prim14_d2.py
Output: archive/run-logs/prim14/d2.json + summary lines.
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
TENSION_K = 8.0
DAMPING = 0.95
OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "prim14"


def make_cfg(seed: int, per_bond: bool) -> WorldConfig:
    return WorldConfig(rng_seed=seed, box_size=(60.0, 60.0, 60.0),
                       n_initial_vibrations=0, n_vibrations_max=64,
                       n_nodes_max=64, lambda_gen=0.0, lambda_dec=0.0,
                       atom_valence=1,  # D2: saturate the write channel
                       atom_repulsion_k=0.0, repulsion_k=0.0,
                       node_thermal_speed=0.0, anchor_damping=0.0,
                       neuron_dynamics_enabled=False, stdp_enabled=False,
                       btsp_enabled=False, r_2=12.0, graceful_capacity=True,
                       per_bond_rest_enabled=per_bond,
                       bridge_tension_k=TENSION_K,
                       bridge_tension_damping=DAMPING)


def bond_census(w: World) -> list[tuple[int, int, float]]:
    out = []
    for b in range(w.b_count):
        if w.b_alive[b]:
            out.append((int(w.b_atom_i[b]), int(w.b_atom_j[b]),
                        round(float(w.b_rest_len[b]), 3)))
    return out


def run_arm(seed: int, arm: str) -> dict:
    per_bond = arm in ("P", "NC")
    cfg = make_cfg(seed, per_bond)
    w = World(cfg)
    slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0)
             for x in STORED]
    for _ in range(8):
        for s, x in zip(slots, STORED):
            w.k_pos[s] = (x, BAND_Y, 30.0)
            w.k_vel[s] = 0.0
        tick(w, cfg.dt)

    census_pre = bond_census(w)
    valid_pre = (len(census_pre) == 1 and
                 {census_pre[0][0], census_pre[0][1]} == {0, 1})

    mid = slots[1]
    w.k_pos[mid] = (DISPLACED_MID, BAND_Y, 30.0)
    w.k_vel[mid] = 0.0
    if arm == "NC":
        w.b_alive[: w.b_count] = False

    x_1500 = None
    for t in range(RELAX_TICKS):
        w.k_pos[slots[0]] = (STORED[0], BAND_Y, 30.0); w.k_vel[slots[0]] = 0.0
        w.k_pos[slots[2]] = (STORED[2], BAND_Y, 30.0); w.k_vel[slots[2]] = 0.0
        tick(w, cfg.dt)
        if t == 1499:
            x_1500 = float(w.k_pos[mid][0])

    census_post = bond_census(w)
    write_closed = (arm == "NC") or (census_post == census_pre)
    end_x = float(w.k_pos[mid][0])
    return {"arm": arm, "seed": seed, "end_x": round(end_x, 3),
            "settled": abs(end_x - x_1500) < 0.1,
            "census_pre": census_pre, "census_post": census_post,
            "valid_pre": valid_pre, "write_closed": bool(write_closed)}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for seed in SEEDS:
        for arm in ("P", "C", "NC"):
            r = run_arm(seed, arm)
            results.append(r)
            print(f"# seed {seed} ARM-{arm}: end_x={r['end_x']} "
                  f"settled={r['settled']} valid_pre={r['valid_pre']} "
                  f"write_closed={r['write_closed']} census_post={r['census_post']}")
    (OUT_DIR / "d2.json").write_text(json.dumps(results, indent=2))
    print(f"# written -> {OUT_DIR / 'd2.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

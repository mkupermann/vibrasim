"""PRIM14-D0 — per-bond rest length diagnostic.

Pre-registered in docs/amendments/bp_prim14_per_bond_rest_length.md
(incl. the 4a erratum: asymmetric stored chain). Computes metrics only;
the verdict is judged against the frozen bars.

Arms per seed {42, 7, 13}:
  ARM-P : per_bond_rest_enabled=True,  chain stored at {13,17,29}
  ARM-C : flag off (global r_eq=6),    same chain
  NC1   : per-bond ON, bonds formed at {13,21,29}, middle set to 17 (must
          restore toward formation geometry 21 — content neutrality)
  NC2   : ARM-P setup, bridges deleted after displacement (drift ±1 max)

Usage: python tools/run_bp_prim14_d0.py
Output: archive/run-logs/prim14/d0.json + summary lines.
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

SPACING_R2 = 12.0          # r_2 -> global r_eq = 6.0, as in the G154 probe
BAND_Y = 30.0
EMPTY = np.empty(0, dtype=np.int32)
SEEDS = (42, 7, 13)
RELAX_TICKS = 2000
STORED = (13.0, 17.0, 29.0)     # asymmetric: l1=4, l2=12 (erratum 4a)
NC1_FORM = (13.0, 21.0, 29.0)   # symmetric formation for content-neutrality
DISPLACED_MID = 21.0            # = ARM-C's global equilibrium (midpoint)
OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "prim14"


def make_cfg(seed: int, per_bond: bool) -> WorldConfig:
    return WorldConfig(rng_seed=seed, box_size=(60.0, 60.0, 60.0),
                       n_initial_vibrations=0, n_vibrations_max=64,
                       n_nodes_max=64, lambda_gen=0.0, lambda_dec=0.0,
                       atom_valence=2, atom_repulsion_k=0.0, repulsion_k=0.0,
                       node_thermal_speed=0.0, anchor_damping=0.0,
                       neuron_dynamics_enabled=False, stdp_enabled=False,
                       btsp_enabled=False, r_2=SPACING_R2,
                       graceful_capacity=True,
                       per_bond_rest_enabled=per_bond)


def build_chain(w: World, xs) -> list[int]:
    slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0)
             for x in xs]
    # Consolidation: hold all three in place while bonds form at THIS geometry.
    for _ in range(8):
        for slot, x in zip(slots, xs):
            w.k_pos[slot] = (x, BAND_Y, 30.0)
            w.k_vel[slot] = 0.0
        tick(w, w.config.dt)
    return slots


def relax_and_measure(w: World, slots, ends_xs, mid_target: float,
                      displaced_from: float) -> dict:
    """Pin the ends, release the middle, run RELAX_TICKS."""
    mid = slots[1]
    traj = []
    for t in range(RELAX_TICKS):
        w.k_pos[slots[0]] = (ends_xs[0], BAND_Y, 30.0); w.k_vel[slots[0]] = 0.0
        w.k_pos[slots[2]] = (ends_xs[1], BAND_Y, 30.0); w.k_vel[slots[2]] = 0.0
        tick(w, w.config.dt)
        if t in (0, 99, 499, 999, RELAX_TICKS - 1):
            traj.append((t + 1, round(float(w.k_pos[mid][0]), 3)))
    end_x = float(w.k_pos[mid][0])
    denom = abs(displaced_from - mid_target)
    R = (denom - abs(end_x - mid_target)) / denom if denom > 0 else None
    return {"end_x": round(end_x, 3), "R": round(R, 3), "traj": traj}


def run_arm(seed: int, arm: str) -> dict:
    per_bond = arm in ("P", "NC1", "NC2")
    cfg = make_cfg(seed, per_bond)
    w = World(cfg)

    if arm == "NC1":
        slots = build_chain(w, NC1_FORM)      # formed symmetric (mid at 21)
        stored_mid = NC1_FORM[1]              # formation geometry = 21
        start_mid = 17.0                      # displaced INTO the "correct" pattern
    else:
        slots = build_chain(w, STORED)        # formed asymmetric (mid at 17)
        stored_mid = STORED[1]
        start_mid = DISPLACED_MID             # 21

    n_bonds = int(w.b_alive[: w.b_count].sum())

    # Displace the middle, zero its velocity.
    w.k_pos[slots[1]] = (start_mid, BAND_Y, 30.0)
    w.k_vel[slots[1]] = 0.0

    if arm == "NC2":
        w.b_alive[: w.b_count] = False        # delete all bridges post-displacement

    ends = (NC1_FORM[0], NC1_FORM[2]) if arm == "NC1" else (STORED[0], STORED[2])
    m = relax_and_measure(w, slots, ends, stored_mid, start_mid)
    m.update(arm=arm, seed=seed, bonds_formed=n_bonds,
             stored_mid=stored_mid, start_mid=start_mid)
    return m


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for seed in SEEDS:
        for arm in ("P", "C", "NC1", "NC2"):
            r = run_arm(seed, arm)
            results.append(r)
            print(f"# seed {seed} ARM-{arm}: bonds={r['bonds_formed']} "
                  f"start={r['start_mid']} stored={r['stored_mid']} "
                  f"end={r['end_x']} R={r['R']} traj={r['traj']}")
    (OUT_DIR / "d0.json").write_text(json.dumps(results, indent=2))
    print(f"# written -> {OUT_DIR / 'd0.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

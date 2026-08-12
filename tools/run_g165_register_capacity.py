"""G165 — register capacity: K ∈ {6, 12, 24} bits.

Pre-registered in docs/amendments/g165_register_capacity.md.
Metrics only; verdict against the frozen bars. Includes the mandatory strain
metrics (min non-neighbour distance, gyration radius) and the break-point
classifier (W-FAIL / X-BOND / D-FAIL).

Usage: python tools/run_g165_register_capacity.py
Output: archive/run-logs/g165/results.json + summary.
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

SEEDS = [42, 7, 13]
K_LIST = (6, 12, 24)
X0 = 15.0
BAND_Y = 30.0
SHORT, LONG = 6.5, 10.5
UNIFORM = 8.5
T_CONSOL = 8
T_RETRIEVE = 800
N_PATTERNS = 8
TENSION_K = 8.0
DAMPING = 0.95
EMPTY = np.empty(0, dtype=np.int32)
OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "g165"


def box_x_for(k_bits: int) -> float:
    import math
    return math.ceil((X0 + k_bits * LONG + 30.0) / 10.0) * 10.0


def base_cfg(seed: int, per_bond: bool, n_max: int, k_bits: int) -> WorldConfig:
    bx = box_x_for(k_bits)
    return WorldConfig(
        rng_seed=seed, box_size=(bx, 60.0, 60.0),
        repulsion_cell_size=bx,
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=n_max,
        lambda_gen=0.0, lambda_dec=0.0, atom_valence=2,
        atom_repulsion_k=0.0, repulsion_k=0.0, node_thermal_speed=0.0,
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


def census_pairs(w: World) -> set:
    return {(min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
             max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
            for b in range(w.b_count) if w.b_alive[b]}


def run_one(pattern, seed: int, arm: str) -> dict:
    k_bits = len(pattern)
    per_bond = arm != "OLDREST"
    cfg = base_cfg(seed, per_bond, n_max=64, k_bits=k_bits)
    w = World(cfg)
    box = np.array([box_x_for(k_bits), 60.0, 60.0])
    boundary_confound = False

    xs_enc = encoded_positions(pattern)
    slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4,
                             EMPTY, 0) for x in xs_enc]

    for _ in range(T_CONSOL):
        for s, x in zip(slots, xs_enc):
            w.k_pos[s] = (x, BAND_Y, 30.0)
            w.k_vel[s] = 0.0
        tick(w, cfg.dt)

    pairs0 = census_pairs(w)
    expected = {(i, i + 1) for i in range(k_bits)}
    write_valid = pairs0 == expected
    n_bonds_written = len(pairs0)

    if arm == "NEG":
        w.b_alive[: w.b_count] = False

    for i, s in enumerate(slots):
        w.k_pos[s] = (X0 + i * UNIFORM, BAND_Y, 30.0)
        w.k_vel[s] = 0.0

    # RETRIEVE with formation freeze + strain metrics
    min_nn_dist = float("inf")
    kills = 0
    pos_arr = np.zeros((len(slots), 3))
    for t in range(T_RETRIEVE):
        w.k_pos[slots[0]] = (X0, BAND_Y, 30.0)
        w.k_vel[slots[0]] = 0.0
        tick(w, w.config.dt)
        if arm != "NEG":
            now = census_pairs(w)
            for key in now - pairs0:
                for b in range(w.b_count):
                    if w.b_alive[b]:
                        kk = (min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
                              max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
                        if kk == key:
                            w.b_alive[b] = False
                            kills += 1
        if t % 20 == 19:
            for i, s in enumerate(slots):
                pos_arr[i] = w.k_pos[s]
            if ((pos_arr < 5.0).any()
                    or ((box[None, :] - pos_arr) < 5.0).any()):
                boundary_confound = True
            d = pos_arr[:, None, :] - pos_arr[None, :, :]
            dist = np.sqrt((d ** 2).sum(-1))
            idx = np.abs(np.subtract.outer(np.arange(len(slots)),
                                           np.arange(len(slots)))) >= 2
            min_nn_dist = min(min_nn_dist, float(dist[idx].min()))

    for i, s in enumerate(slots):
        pos_arr[i] = w.k_pos[s]
    gyration = float(np.sqrt(((pos_arr - pos_arr.mean(0)) ** 2)
                             .sum(1).mean()))

    decoded = []
    for i in range(k_bits):
        d = float(w.k_pos[slots[i + 1]][0] - w.k_pos[slots[i]][0])
        decoded.append(1 if d > UNIFORM else 0)
    acc = sum(int(a == b) for a, b in zip(decoded, pattern)) / k_bits

    # Break-point class (only meaningful when acc < 0.90)
    if acc >= 0.90:
        break_class = "OK"
    elif not write_valid:
        break_class = "W-FAIL"
    elif kills > 0:
        break_class = "X-BOND"
    else:
        break_class = "D-FAIL"

    if boundary_confound and acc < 0.90:
        break_class = "BOUNDARY-CONFOUND"
    return {"acc": acc, "write_valid": write_valid,
            "n_bonds_written": n_bonds_written, "freeze_kills": kills,
            "min_nn_dist": round(min_nn_dist, 2),
            "gyration": round(gyration, 2), "break_class": break_class,
            "boundary_confound": boundary_confound}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for K in K_LIST:
        arms = ["P", "OLDREST"] + (["NEG"] if K == 24 else [])
        for arm in arms:
            key = f"{arm}@K{K}"
            accs, classes, min_dists, gyrs = [], [], [], []
            n_boundary = 0
            n_runs = 0
            for seed in SEEDS:
                rng = np.random.default_rng(1650 + seed + K)
                acc_sum = 0.0
                n_valid = 0
                for _ in range(N_PATTERNS):
                    while True:
                        pattern = list(rng.integers(0, 2, K))
                        if 0 < sum(pattern) < K:
                            break
                    r = run_one(pattern, seed, arm)
                    n_runs += 1
                    if r["boundary_confound"]:
                        n_boundary += 1
                        classes.append("BOUNDARY-CONFOUND")
                        continue  # neither pass nor break (anti-bias gate)
                    acc_sum += r["acc"]
                    n_valid += 1
                    classes.append(r["break_class"])
                    min_dists.append(r["min_nn_dist"])
                    gyrs.append(r["gyration"])
                accs.append(acc_sum / max(1, n_valid))
            results[key] = {
                "per_seed": [round(a, 4) for a in accs],
                "mean": round(float(np.mean(accs)), 4),
                "break_classes": {c: classes.count(c)
                                  for c in set(classes)},
                "boundary_rate": round(n_boundary / max(1, n_runs), 3),
                "min_nn_dist": (round(float(np.min(min_dists)), 2)
                                if min_dists else None),
                "gyration_max": (round(float(np.max(gyrs)), 2)
                                 if gyrs else None),
            }
            print(f"# {key}: mean={results[key]['mean']} "
                  f"per_seed={results[key]['per_seed']} "
                  f"classes={results[key]['break_classes']} "
                  f"min_nn={results[key]['min_nn_dist']} "
                  f"gyr_max={results[key]['gyration_max']}")
    (OUT_DIR / "results.json").write_text(json.dumps(results, indent=2))
    print(f"# written -> {OUT_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

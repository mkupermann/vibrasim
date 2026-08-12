"""G167 — retention at scale, certification re-run with measurable NEG.

Pre-registered in docs/amendments/g167_retention_at_scale_valid_neg.md (all round-table
conditions: per-tick min-NN + time-fraction-below-window, K6 contrast arm,
within-run T0, rebonding threshold, boundary gate, perturbation floor).

Usage: python tools/run_g167_retention_at_scale.py
Output: archive/run-logs/g166/results.json + summary.
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
X0 = 15.0
BAND_Y = 30.0
SHORT, LONG = 6.5, 10.5
UNIFORM = 8.5
T_CONSOL = 8
T_RETRIEVE = 800
N_PATTERNS = 8
TENSION_K = 8.0
DAMPING = 0.95
IDLE_THERMAL = 2.0
KICK_EVERY = 50
IDLE_INTERVALS = (2_000, 10_000, 50_000)
CENSUS_EVERY = 1_000
WINDOW = 12.0
OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "g167"
EMPTY = np.empty(0, dtype=np.int32)


def box_x_for(k_bits: int) -> float:
    import math
    return math.ceil((X0 + k_bits * LONG + 30.0) / 10.0) * 10.0


def base_cfg(seed: int, per_bond: bool, k_bits: int) -> WorldConfig:
    bx = box_x_for(k_bits)
    return WorldConfig(
        rng_seed=seed, box_size=(bx, 60.0, 60.0), repulsion_cell_size=bx,
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
        lambda_gen=0.0, lambda_dec=0.0, atom_valence=2,
        atom_repulsion_k=0.0, repulsion_k=0.0, node_thermal_speed=0.0,
        anchor_damping=0.0, neuron_dynamics_enabled=False,
        stdp_enabled=False, btsp_enabled=False, r_2=12.0,
        graceful_capacity=True, per_bond_rest_enabled=per_bond,
        bridge_tension_k=TENSION_K, bridge_tension_damping=DAMPING,
    )


def encoded_positions(pattern):
    xs = [X0]
    for bit in pattern:
        xs.append(xs[-1] + (LONG if bit else SHORT))
    return xs


def census_pairs(w: World) -> set:
    return {(min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
             max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
            for b in range(w.b_count) if w.b_alive[b]}


def run_one(pattern, seed: int, arm: str, idle_ticks: int) -> dict:
    """arm in {'P','T0','OLDREST','NEG'}; K comes from len(pattern)."""
    k_bits = len(pattern)
    per_bond = arm != "OLDREST"
    kicks_on = arm not in ("T0", "NEG")   # G167: NEG is static (no kicks)
    cfg = base_cfg(seed, per_bond, k_bits)
    w = World(cfg)
    box = np.array([box_x_for(k_bits), 60.0, 60.0])
    kick_rng = np.random.default_rng(
        (seed * 1_000_003 + idle_ticks * 101 + k_bits * 13
         + hash(arm) % 997) & 0x7FFFFFFF)

    xs_enc = encoded_positions(pattern)
    slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4,
                             EMPTY, 0) for x in xs_enc]
    slot_idx = np.array(slots)
    nn_mask = np.abs(np.subtract.outer(np.arange(len(slots)),
                                       np.arange(len(slots)))) >= 2

    for _ in range(T_CONSOL):
        for s, x in zip(slots, xs_enc):
            w.k_pos[s] = (x, BAND_Y, 30.0)
            w.k_vel[s] = 0.0
        tick(w, cfg.dt)

    pairs0 = census_pairs(w)
    write_valid = pairs0 == {(i, i + 1) for i in range(k_bits)}

    # G167: NEG keeps its bonds through a (kick-free) idle and loses them
    # at scramble time — its role is the readout-needs-bonds check.

    # IDLE with kicks; per-tick strain tracking (researcher A's condition)
    written = np.array([[x, BAND_Y, 30.0] for x in xs_enc])
    rms_accum, rms_n = 0.0, 0
    new_bonds = lost_bonds = 0
    min_nn = float("inf")
    ticks_below = 0
    boundary = False
    pairs_now = set(pairs0)
    KICK_SPEED = IDLE_THERMAL / np.sqrt(4.0)
    for t in range(idle_ticks):
        if kicks_on and t % KICK_EVERY == 0:
            for s_ in slots:
                z = kick_rng.uniform(-1.0, 1.0)
                phi = kick_rng.uniform(0.0, 2 * np.pi)
                sq = np.sqrt(1 - z * z)
                w.k_vel[s_] = KICK_SPEED * np.array(
                    [sq * np.cos(phi), sq * np.sin(phi), z])
        tick(w, cfg.dt)
        pos = w.k_pos[slot_idx]
        d = pos[:, None, :] - pos[None, :, :]
        dist = np.sqrt((d ** 2).sum(-1))
        m = float(dist[nn_mask].min())
        if m < min_nn:
            min_nn = m
        if m < WINDOW:
            ticks_below += 1
        if (pos < 5.0).any() or ((box[None, :] - pos) < 5.0).any():
            boundary = True
        if (t + 1) % 10 == 0:
            disp = pos - written
            rms_accum += float((disp ** 2).sum(axis=1).mean())
            rms_n += 1
        if (t + 1) % CENSUS_EVERY == 0 and arm != "NEG":
            now = census_pairs(w)
            if now != pairs_now:
                new_bonds += len(now - pairs_now)
                lost_bonds += len(pairs_now - now)
                pairs_now = now

    rms = float(np.sqrt(rms_accum / max(1, rms_n)))

    # SCRAMBLE + RETRIEVE (quiet, formation freeze)
    if arm == "NEG":
        w.b_alive[: w.b_count] = False   # G167: delete bonds AT scramble
    for i, s in enumerate(slots):
        w.k_pos[s] = (X0 + i * UNIFORM, BAND_Y, 30.0)
        w.k_vel[s] = 0.0
    pairs_frozen = census_pairs(w)
    for _ in range(T_RETRIEVE):
        w.k_pos[slots[0]] = (X0, BAND_Y, 30.0)
        w.k_vel[slots[0]] = 0.0
        tick(w, cfg.dt)
        for b in range(w.b_count):
            if w.b_alive[b]:
                kk = (min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
                      max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
                if kk not in pairs_frozen:
                    w.b_alive[b] = False

    decoded = []
    for i in range(k_bits):
        d_ = float(w.k_pos[slots[i + 1]][0] - w.k_pos[slots[i]][0])
        decoded.append(1 if d_ > UNIFORM else 0)
    acc = sum(int(a == b) for a, b in zip(decoded, pattern)) / k_bits

    return {"acc": acc, "write_valid": write_valid, "rms": round(rms, 3),
            "new_bonds": new_bonds, "lost_bonds": lost_bonds,
            "min_nn": round(min_nn, 3),
            "frac_below": round(ticks_below / max(1, idle_ticks), 4),
            "boundary": boundary}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    arms = ([("P", 24, n) for n in IDLE_INTERVALS]
            + [("P", 6, n) for n in IDLE_INTERVALS]      # C's contrast arm
            + [("T0", 24, 50_000), ("OLDREST", 24, 50_000),
               ("NEG", 24, 50_000)])
    out = {}
    for arm, K, n in arms:
        key = f"{arm}@K{K}@{n}"
        accs, aggr = [], {"new_bonds": 0, "lost_bonds": 0, "boundary": 0,
                          "min_nn": float("inf"), "frac_below": 0.0,
                          "rms": 0.0, "runs": 0}
        wv_all = True
        for seed in SEEDS:
            rng = np.random.default_rng(1660 + seed + K)
            acc_sum, n_valid = 0.0, 0
            for _ in range(N_PATTERNS):
                while True:
                    pattern = list(rng.integers(0, 2, K))
                    if 0 < sum(pattern) < K:
                        break
                r = run_one(pattern, seed, arm, n)
                aggr["runs"] += 1
                wv_all &= r["write_valid"]
                if r["boundary"]:
                    aggr["boundary"] += 1
                    continue
                acc_sum += r["acc"]
                n_valid += 1
                aggr["new_bonds"] += r["new_bonds"]
                aggr["lost_bonds"] += r["lost_bonds"]
                aggr["min_nn"] = min(aggr["min_nn"], r["min_nn"])
                aggr["frac_below"] = max(aggr["frac_below"], r["frac_below"])
                aggr["rms"] += r["rms"]
            accs.append(acc_sum / max(1, n_valid))
        out[key] = {
            "per_seed": [round(a, 4) for a in accs],
            "mean": round(float(np.mean(accs)), 4),
            "new_bonds": aggr["new_bonds"], "lost_bonds": aggr["lost_bonds"],
            "min_nn": (round(aggr["min_nn"], 3)
                       if aggr["min_nn"] < float("inf") else None),
            "frac_below_max": aggr["frac_below"],
            "boundary_rate": round(aggr["boundary"] / aggr["runs"], 3),
            "rms_mean": round(aggr["rms"] / max(1, aggr["runs"]
                                                - aggr["boundary"]), 3),
            "write_valid_all": bool(wv_all),
        }
        print(f"# {key}: mean={out[key]['mean']} per_seed={out[key]['per_seed']} "
              f"new_bonds={out[key]['new_bonds']} min_nn={out[key]['min_nn']} "
              f"frac_below={out[key]['frac_below_max']} "
              f"boundary={out[key]['boundary_rate']} rms={out[key]['rms_mean']}")
    (OUT_DIR / "results.json").write_text(json.dumps(out, indent=2))
    print(f"# written -> {OUT_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

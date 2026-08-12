"""G170 — LI-channel mechanism attribution: allocation-order arms.

Pre-registered in docs/amendments/g170_li_channel_mechanism.md.
Metrics only; verdict against the frozen bars.

Usage: python tools/run_g170_li_channel_mechanism.py   (resumable per arm)
Output: archive/run-logs/g168/results.json + summary.
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
K_BITS = 6
X0 = 15.0
Z0 = 30.0
SHORT, LONG = 6.5, 10.5
UNIFORM = 8.5
T_CONSOL = 8
T_RETRIEVE = 800
N_PAIRS = 8
TENSION_K = 8.0
DAMPING = 0.95
IDLE_TICKS = 10_000
IDLE_THERMAL = 2.0
KICK_EVERY = 50
CENSUS_EVERY = 1_000
WINDOW = 12.0
OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "g170"
EMPTY = np.empty(0, dtype=np.int32)


def base_cfg(seed: int, per_bond: bool) -> WorldConfig:
    return WorldConfig(
        rng_seed=seed, box_size=(120.0, 60.0, 60.0),
        repulsion_cell_size=120.0,
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


def cross_bonds(pairs: set, set1: set, set2: set) -> int:
    return sum(1 for a, b in pairs
               if (a in set1 and b in set2) or (a in set2 and b in set1))


def run_one(pat1, pat2, seed: int, arm: str, dy: float, r1_first: bool,
            alloc_mode: str = "base") -> dict:
    per_bond = arm != "OLDREST"
    cfg = base_cfg(seed, per_bond)
    w = World(cfg)
    box = np.array([120.0, 60.0, 60.0])
    kick_rng = np.random.default_rng(
        (seed * 1_000_003 + int(dy * 10) * 101
         + (1 if r1_first else 0)) & 0x7FFFFFFF)

    y1, y2 = 30.0 - dy / 2, 30.0 + dy / 2
    xs1, xs2 = encoded_positions(pat1), encoded_positions(pat2)
    # G170: allocation ORDER is the treatment (slot indices decide the
    # form_bridges pair-scan order — H-INDEX's proposed mechanism).
    if alloc_mode == "base":
        slots1 = [w.allocate_node(np.array([x, y1, Z0]), 1.0, True, 4,
                                  EMPTY, 0) for x in xs1]
        slots2 = [w.allocate_node(np.array([x, y2, Z0]), 1.0, True, 4,
                                  EMPTY, 0) for x in xs2]
    elif alloc_mode == "swap":
        slots2 = [w.allocate_node(np.array([x, y2, Z0]), 1.0, True, 4,
                                  EMPTY, 0) for x in xs2]
        slots1 = [w.allocate_node(np.array([x, y1, Z0]), 1.0, True, 4,
                                  EMPTY, 0) for x in xs1]
    else:  # sim: interleaved
        slots1, slots2 = [], []
        for x1_, x2_ in zip(xs1, xs2):
            slots1.append(w.allocate_node(np.array([x1_, y1, Z0]), 1.0,
                                          True, 4, EMPTY, 0))
            slots2.append(w.allocate_node(np.array([x2_, y2, Z0]), 1.0,
                                          True, 4, EMPTY, 0))
    set1, set2 = set(slots1), set(slots2)
    all_slots = slots1 + slots2
    slot_idx = np.array(all_slots)

    # Sequential consolidation, order permuted (researcher C)
    order = ([(slots1, xs1, y1), (slots2, xs2, y2)] if r1_first
             else [(slots2, xs2, y2), (slots1, xs1, y1)])
    for chain_slots, chain_xs, cy in order:
        for _ in range(T_CONSOL):
            # pin BOTH chains at their written geometry during each
            # consolidation phase (the not-yet-consolidated chain is pinned
            # too — its bonds simply have not formed yet)
            for s, x in zip(slots1, xs1):
                w.k_pos[s] = (x, y1, Z0); w.k_vel[s] = 0.0
            for s, x in zip(slots2, xs2):
                w.k_pos[s] = (x, y2, Z0); w.k_vel[s] = 0.0
            tick(w, cfg.dt)

    pairs_w = census_pairs(w)
    intra1 = {(min(slots1[i], slots1[i+1]), max(slots1[i], slots1[i+1]))
              for i in range(K_BITS)}
    intra2 = {(min(slots2[i], slots2[i+1]), max(slots2[i], slots2[i+1]))
              for i in range(K_BITS)}
    write_x = cross_bonds(pairs_w, set1, set2)
    write_valid = intra1 <= pairs_w and intra2 <= pairs_w

    # G169: cross-bond location classes (only end pairs can bond)
    ends = {slots1[0]: "0", slots1[-1]: "L", slots2[0]: "0", slots2[-1]: "L"}
    def x_classes(pairs):
        out = []
        for a, b in pairs:
            if (a in set1 and b in set2) or (a in set2 and b in set1):
                out.append(ends.get(a, "I") + ends.get(b, "I"))
        return out
    xclasses_write = x_classes(pairs_w)

    # IDLE with kicks; cross-distance tracked per tick
    written = np.array([[x, y1, Z0] for x in xs1]
                       + [[x, y2, Z0] for x in xs2])
    min_cross = float("inf")
    idle_x_new = 0
    rebonds = 0
    boundary = False
    pairs_now = set(pairs_w)
    KICK_SPEED = IDLE_THERMAL / np.sqrt(4.0)
    pos1_idx = np.arange(len(slots1))
    pos2_idx = np.arange(len(slots1), len(all_slots))
    for t in range(IDLE_TICKS):
        if arm != "NEG" and t % KICK_EVERY == 0:
            for s_ in all_slots:
                z = kick_rng.uniform(-1.0, 1.0)
                phi = kick_rng.uniform(0.0, 2 * np.pi)
                sq = np.sqrt(1 - z * z)
                w.k_vel[s_] = KICK_SPEED * np.array(
                    [sq * np.cos(phi), sq * np.sin(phi), z])
        tick(w, cfg.dt)
        pos = w.k_pos[slot_idx]
        d = pos[pos1_idx][:, None, :] - pos[pos2_idx][None, :, :]
        m = float(np.sqrt((d ** 2).sum(-1)).min())
        if m < min_cross:
            min_cross = m
        if (pos < 5.0).any() or ((box[None, :] - pos) < 5.0).any():
            boundary = True
        if (t + 1) % CENSUS_EVERY == 0:
            now = census_pairs(w)
            if now != pairs_now:
                new = now - pairs_now
                idle_x_new += cross_bonds(new, set1, set2)
                rebonds += len(new) - cross_bonds(new, set1, set2)
                pairs_now = now

    # SCRAMBLE both; NEG loses bonds here (certified static design)
    if arm == "NEG":
        w.b_alive[: w.b_count] = False
    for i, s in enumerate(slots1):
        w.k_pos[s] = (X0 + i * UNIFORM, y1, Z0); w.k_vel[s] = 0.0
    for i, s in enumerate(slots2):
        w.k_pos[s] = (X0 + i * UNIFORM, y2, Z0); w.k_vel[s] = 0.0

    pairs_frozen = census_pairs(w)
    for _ in range(T_RETRIEVE):
        w.k_pos[slots1[0]] = (X0, y1, Z0); w.k_vel[slots1[0]] = 0.0
        w.k_pos[slots2[0]] = (X0, y2, Z0); w.k_vel[slots2[0]] = 0.0
        tick(w, cfg.dt)
        for b in range(w.b_count):
            if w.b_alive[b]:
                kk = (min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
                      max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
                if kk not in pairs_frozen:
                    w.b_alive[b] = False

    def decode_bits(chain_slots):
        bits, margins = [], []
        for i in range(K_BITS):
            d_ = float(w.k_pos[chain_slots[i+1]][0]
                       - w.k_pos[chain_slots[i]][0])
            bits.append(1 if d_ > UNIFORM else 0)
            margins.append(abs(d_ - UNIFORM))
        return bits, margins

    bits1, marg1 = decode_bits(slots1)
    bits2, marg2 = decode_bits(slots2)
    err1 = sum(int(a != b) for a, b in zip(bits1, pat1))
    err2 = sum(int(a != b) for a, b in zip(bits2, pat2))

    # G169 point prediction: (L,L) cross-bond present => exactly one error,
    # on R2; no (L,L) => zero errors. Hit = exact match of count AND register.
    has_LL = "LL" in xclasses_write
    if has_LL:
        pred_hit = (err1 == 0 and err2 == 1)
    else:
        pred_hit = (err1 == 0 and err2 == 0)

    return {"acc1": 1 - err1 / K_BITS, "acc2": 1 - err2 / K_BITS,
            "write_valid": write_valid, "write_x": write_x,
            "xclasses": xclasses_write, "pred_hit": bool(pred_hit),
            "min_margin": round(min(marg1 + marg2), 3),
            "idle_x_new": idle_x_new, "rebonds": rebonds,
            "min_cross": round(min_cross, 3), "boundary": boundary,
            "r1_first": r1_first}


ARMS = [("BASE", "base"), ("SWAP", "swap"), ("SIM", "sim")]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    res_path = OUT_DIR / "results.json"
    out = json.loads(res_path.read_text()) if res_path.exists() else {}
    for name, alloc_mode in ARMS:
        if name in out:
            print(f"# {name}: already complete, skipped (resume)")
            continue
        dy, arm = 10.0, "P"
        acc_first, acc_second = [], []
        accs = []
        r1_seed, r2_seed = [], []
        loss_r1 = loss_r2 = 0
        agg = {"write_x": 0, "idle_x_new": 0, "rebonds": 0, "boundary": 0,
               "min_cross": float("inf"), "runs": 0,
               "pred_hits": 0, "pred_n": 0, "min_margin": float("inf"),
               "xclass_hist": {}}
        wv_all = True
        for seed in SEEDS:
            rng = np.random.default_rng(1690 + seed)
            a_sum, n_valid = 0.0, 0
            for p_i in range(N_PAIRS):
                def draw():
                    while True:
                        p = list(rng.integers(0, 2, K_BITS))
                        if 0 < sum(p) < K_BITS:
                            return p
                pat1, pat2 = draw(), draw()
                r1_first = (p_i % 2 == 0)   # researcher C's permutation
                r = run_one(pat1, pat2, seed, arm, dy, r1_first, alloc_mode)
                agg["runs"] += 1
                wv_all &= r["write_valid"]
                if r["boundary"]:
                    agg["boundary"] += 1
                    continue
                a_sum += (r["acc1"] + r["acc2"]) / 2
                n_valid += 1
                if r["acc1"] < 1.0: loss_r1 += 1
                if r["acc2"] < 1.0: loss_r2 += 1
                first, second = ((r["acc1"], r["acc2"]) if r["r1_first"]
                                 else (r["acc2"], r["acc1"]))
                acc_first.append(first)
                acc_second.append(second)
                agg["write_x"] += r["write_x"]
                agg["idle_x_new"] += r["idle_x_new"]
                agg["rebonds"] += r["rebonds"]
                agg["min_cross"] = min(agg["min_cross"], r["min_cross"])
                agg["pred_hits"] += int(r["pred_hit"])
                agg["pred_n"] += 1
                agg["min_margin"] = min(agg["min_margin"], r["min_margin"])
                for c in r["xclasses"]:
                    agg["xclass_hist"][c] = agg["xclass_hist"].get(c, 0) + 1
            accs.append(a_sum / max(1, n_valid))
        out[name] = {
            "loss_runs_r1": loss_r1, "loss_runs_r2": loss_r2,
            "per_seed": [round(a, 4) for a in accs],
            "mean": round(float(np.mean(accs)), 4),
            "write_x": agg["write_x"], "idle_x_new": agg["idle_x_new"],
            "rebonds": agg["rebonds"],
            "min_cross": (round(agg["min_cross"], 3)
                          if agg["min_cross"] < float("inf") else None),
            "order_effect": round(float(np.mean(acc_first)
                                        - np.mean(acc_second)), 4)
                            if acc_first else None,
            "boundary_rate": round(agg["boundary"] / agg["runs"], 3),
            "write_valid_all": bool(wv_all),
            "pred_hit_rate": (round(agg["pred_hits"] / agg["pred_n"], 4)
                              if agg["pred_n"] else None),
            "min_margin": (round(agg["min_margin"], 3)
                           if agg["min_margin"] < float("inf") else None),
            "xclass_hist": agg["xclass_hist"],
        }
        print(f"# {name}: LOSSES r1={out[name]['loss_runs_r1']} "
              f"r2={out[name]['loss_runs_r2']} mean={out[name]['mean']} "
              f"per_seed={out[name]['per_seed']} "
              f"write_x={out[name]['write_x']} idle_x={out[name]['idle_x_new']} "
              f"min_cross={out[name]['min_cross']} "
              f"order_eff={out[name]['order_effect']} "
              f"boundary={out[name]['boundary_rate']} wv={out[name]['write_valid_all']} "
              f"pred_hit={out[name]['pred_hit_rate']} "
              f"min_margin={out[name]['min_margin']} xhist={out[name]['xclass_hist']}")
        res_path.write_text(json.dumps(out, indent=2))
    print(f"# written -> {res_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

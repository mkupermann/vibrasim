"""G161 — content-addressable matter recall under PRIM14 (capability question).

Pre-registered in docs/amendments/g161_matter_recall_prim14.md.
Protocol = tools/g154_matter_recall.py with the declared §2 changes:
per-bond rest lengths, D2 dynamics cell (k=8, damping 0.95), recall-phase
bridge-formation freeze (harness-enforced, census-verified), ARM-OLDREST
attribution control, Hopfield reported as context only.

Usage: python tools/run_g161_matter_recall.py
Output: archive/run-logs/g161/results.json + summary.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick

# ---- protocol (frozen; identical to G154 except declared §2 changes) -------
SEEDS = [42, 7, 13]
K = 6
SPACING = 6.0
R2 = 2.0 * SPACING
CELL_R = 1.5
BAND_Y = 30.0
X0 = 15.0
CELLS = [X0 + k * SPACING for k in range(K)]
DISPLACE = 14.0
T_CONSOL = 8
T_RELAX = 400
N_PATTERNS = 8
TENSION_K = 8.0      # D2 dynamics cell (declared change vs G154)
DAMPING = 0.95
EMPTY = np.empty(0, dtype=np.int32)
OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "g161"


def base_cfg(seed: int, per_bond: bool) -> WorldConfig:
    return WorldConfig(
        rng_seed=seed, box_size=(60.0, 60.0, 60.0),
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
        lambda_gen=0.0, lambda_dec=0.0, atom_valence=2,
        atom_repulsion_k=0.0, repulsion_k=0.0, node_thermal_speed=0.0,
        anchor_damping=0.0, neuron_dynamics_enabled=False,
        stdp_enabled=False, btsp_enabled=False, r_2=R2,
        graceful_capacity=True,
        per_bond_rest_enabled=per_bond,
        bridge_tension_k=TENSION_K, bridge_tension_damping=DAMPING,
    )


def place_carrier(w: World, x: float) -> int:
    return w.allocate_node(np.array([x, BAND_Y, 30.0], dtype=np.float64),
                           freq=1.0, pol=True, level=4,
                           constituents=EMPTY, comp_kind=0)


def occupied(w: World, cx: float) -> bool:
    K_ = w.k_count
    al = w.k_alive[:K_]
    x = w.k_pos[:K_, 0]
    y = w.k_pos[:K_, 1]
    return bool((al & (np.abs(x - cx) < CELL_R)
                 & (np.abs(y - BAND_Y) < CELL_R)).any())


def census_set(w: World) -> set:
    out = set()
    for b in range(w.b_count):
        if w.b_alive[b]:
            out.add((int(w.b_atom_i[b]), int(w.b_atom_j[b])))
    return out


def substrate_recall(pattern, cue_mask, seed, per_bond: bool, bonds=True):
    """Returns (recalled_bits, secs, census_clean, freeze_kills)."""
    cfg = base_cfg(seed, per_bond)
    if not bonds:
        cfg = replace(cfg, atom_valence=0)   # negative control: no bonds
    w = World(cfg)

    slot = {}
    for k in range(K):
        if pattern[k]:
            slot[k] = place_carrier(w, CELLS[k])

    for _ in range(T_CONSOL):
        for k, i in slot.items():
            w.k_pos[i] = (CELLS[k], BAND_Y, 30.0)
            w.k_vel[i] = 0.0
        tick(w, cfg.dt)

    census0 = census_set(w)

    ones = [k for k in range(K) if pattern[k]]
    cue_ones = [k for k in ones if cue_mask[k]]
    recall_ones = [k for k in ones if not cue_mask[k]]

    for k in recall_ones:
        i = slot[k]
        w.k_pos[i] = (CELLS[k] + DISPLACE, BAND_Y, 30.0)
        w.k_vel[i] = 0.0

    freeze_kills = 0
    t0 = time.perf_counter()
    for _ in range(T_RELAX):
        for k in cue_ones:
            i = slot[k]
            w.k_pos[i] = (CELLS[k], BAND_Y, 30.0)
            w.k_vel[i] = 0.0
        tick(w, cfg.dt)
        # Recall-phase bridge-formation freeze (amendment §2 note): kill any
        # bridge not present at consolidation end. A transient may exert at
        # most one tick of force before removal — shared by all arms,
        # counted and reported.
        if bonds:
            for b in range(w.b_count):
                if w.b_alive[b]:
                    key = (int(w.b_atom_i[b]), int(w.b_atom_j[b]))
                    if key not in census0:
                        w.b_alive[b] = False
                        freeze_kills += 1
    secs = time.perf_counter() - t0

    census_clean = census_set(w) <= census0
    recalled = [1 if occupied(w, CELLS[k]) else 0 for k in range(K)]
    return recalled, secs, census_clean, freeze_kills


def hopfield_recall(stored_patterns, query, cue_mask):
    t0 = time.perf_counter()
    P = np.array([[1 if b else -1 for b in p] for p in stored_patterns], dtype=float)
    W = P.T @ P
    np.fill_diagonal(W, 0.0)
    W /= max(1, len(stored_patterns))
    s = np.array([1 if b else -1 for b in query], dtype=float)
    clamp = np.array(cue_mask, dtype=bool)
    s_clamped = s.copy()
    for _ in range(30):
        for k in range(len(s)):
            if clamp[k]:
                s[k] = s_clamped[k]
                continue
            s[k] = 1.0 if W[k] @ s >= 0 else -1.0
    secs = time.perf_counter() - t0
    return [1 if v > 0 else 0 for v in s], secs


def bit_acc(pred, target, recall_idx):
    if not recall_idx:
        return 1.0
    return sum(int(pred[k] == target[k]) for k in recall_idx) / len(recall_idx)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    per_seed = {"P": [], "OLDREST": [], "NEG": [], "HOP": []}
    secs = {"P": [], "HOP": []}
    census_ok_all = True
    total_kills = 0

    for seed in SEEDS:
        rng = np.random.default_rng(1540 + seed)
        acc = {"P": 0.0, "OLDREST": 0.0, "NEG": 0.0, "HOP": 0.0}
        t_sub = t_hop = 0.0
        for _ in range(N_PATTERNS):
            while True:
                pattern = list(rng.integers(0, 2, K))
                if sum(pattern) >= 2:
                    break
            ones = [k for k in range(K) if pattern[k]]
            n_cue = max(1, len(ones) // 2)
            cue_ones = set(rng.choice(ones, size=n_cue, replace=False).tolist())
            cue_mask = [(k in cue_ones) or (pattern[k] == 0) for k in range(K)]
            recall_idx = [k for k in ones if k not in cue_ones]

            rec, st, clean, kills = substrate_recall(pattern, cue_mask, seed,
                                                     per_bond=True)
            census_ok_all &= clean
            total_kills += kills
            old, _, clean_o, kills_o = substrate_recall(pattern, cue_mask, seed,
                                                        per_bond=False)
            census_ok_all &= clean_o
            total_kills += kills_o
            neg, _, _, _ = substrate_recall(pattern, cue_mask, seed,
                                            per_bond=True, bonds=False)
            hop, ht = hopfield_recall([pattern], pattern, cue_mask)

            acc["P"] += bit_acc(rec, pattern, recall_idx)
            acc["OLDREST"] += bit_acc(old, pattern, recall_idx)
            acc["NEG"] += bit_acc(neg, pattern, recall_idx)
            acc["HOP"] += bit_acc(hop, pattern, recall_idx)
            t_sub += st
            t_hop += ht

        for k in per_seed:
            per_seed[k].append(acc[k] / N_PATTERNS)
        secs["P"].append(t_sub / N_PATTERNS)
        secs["HOP"].append(t_hop / N_PATTERNS)
        print(f"# seed {seed}: P={acc['P']/N_PATTERNS:.3f} "
              f"OLDREST={acc['OLDREST']/N_PATTERNS:.3f} "
              f"NEG={acc['NEG']/N_PATTERNS:.3f} HOP={acc['HOP']/N_PATTERNS:.3f}")

    out = {
        "per_seed": per_seed,
        "mean": {k: float(np.mean(v)) for k, v in per_seed.items()},
        "wallclock_ms": {k: float(np.mean(v) * 1e3) for k, v in secs.items()},
        "census_clean_all": bool(census_ok_all),
        "freeze_kills_total": int(total_kills),
    }
    (OUT_DIR / "results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out["mean"], indent=2))
    print(f"# census_clean_all={census_ok_all} freeze_kills_total={total_kills}")
    print(f"# wallclock/recall: substrate {out['wallclock_ms']['P']:.2f} ms, "
          f"hopfield {out['wallclock_ms']['HOP']:.3f} ms (context only, not a gate)")
    print(f"# written -> {OUT_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

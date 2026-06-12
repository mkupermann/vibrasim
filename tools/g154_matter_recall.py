"""G154 pilot — content-addressable recall on the matter register.

Pre-registered in docs/amendments/G154_matter_recall.md (bars FROZEN 2026-06-12).
NO LLM / transformer / pretrained. Substrate primitives only: injected level-4
carriers, native bridge formation (form_bridges) and bridge tension
(apply_bridge_tension, a spring to r_eq = r_2*0.5) as the associative attractor.

Question: can the matter register do content-addressable recall — store a k-bit
pattern, present a partial cue (half the bits), and have the substrate's OWN
dynamics restore the missing bits — without re-writing them by hand? Compared
against a classical Hopfield net at MATCHED WALL-CLOCK, with a negative control
(no bonds) that MUST fail.

Operationalization (most charitable matter-native test): the bonds formed among
co-stored carriers ARE the stored associations. Recall = hold the cue carriers
pinned at their cells, displace the recall carriers, and let bridge tension pull
them back. A recall bit is correct if a carrier ends within CELLR of its stored
cell (and recall-0 cells stay empty).

Run:  python3 tools/g154_matter_recall.py
"""
from __future__ import annotations

import time
from dataclasses import replace

import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick

# ---- geometry / protocol (frozen) -----------------------------------------
SEEDS = [42, 7, 13]
K = 6                      # cells (bits)
SPACING = 6.0              # cell pitch along x  (== r_eq so a chain is stable)
R2 = 2.0 * SPACING         # binding radius -> r_eq = R2*0.5 = SPACING
CELL_R = 1.5               # occupancy / recall tolerance (G119c CELLR)
BAND_Y = 30.0
X0 = 15.0
CELLS = [X0 + k * SPACING for k in range(K)]   # 15,21,27,33,39,45
DISPLACE = 14.0            # how far a recall carrier is pushed off its cell
T_CONSOL = 8               # ticks to let bonds form (carriers pinned)
T_RELAX = 400              # ticks of free relaxation under tension
N_PATTERNS = 8             # random patterns per seed
EMPTY = np.empty(0, dtype=np.int32)


def base_cfg(seed: int) -> WorldConfig:
    return WorldConfig(
        rng_seed=seed,
        box_size=(60.0, 60.0, 60.0),
        n_initial_vibrations=0,        # inject carriers only; no ambient field
        n_vibrations_max=64,
        n_nodes_max=64,
        lambda_gen=0.0,                # quiet substrate (no regeneration)
        lambda_dec=0.0,                # carriers do not decay
        atom_valence=2,                # linear chains (nearest-neighbour bonds)
        atom_repulsion_k=0.0,          # no non-bonded repulsion
        repulsion_k=0.0,
        node_thermal_speed=0.0,        # no Brownian drift
        anchor_damping=0.0,
        neuron_dynamics_enabled=False,
        stdp_enabled=False,
        btsp_enabled=False,
        r_2=R2,
        graceful_capacity=True,
    )


def place_carrier(w: World, x: float) -> int:
    return w.allocate_node(
        np.array([x, BAND_Y, 30.0], dtype=np.float64),
        freq=1.0, pol=True, level=4, constituents=EMPTY, comp_kind=0,
    )


def occupied(w: World, cx: float) -> bool:
    K_ = w.k_count
    al = w.k_alive[:K_]
    x = w.k_pos[:K_, 0]
    y = w.k_pos[:K_, 1]
    return bool((al & (np.abs(x - cx) < CELL_R) & (np.abs(y - BAND_Y) < CELL_R)).any())


def substrate_recall(pattern, cue_mask, seed, bonds=True):
    """Store `pattern` (k bits) as carriers, pin cue carriers, displace recall
    carriers, relax under bridge tension, read back. Returns (recalled_bits, secs).

    bonds=False is the NEGATIVE CONTROL (atom_valence=0 -> no bonds -> no tension).
    """
    cfg = base_cfg(seed) if bonds else replace(base_cfg(seed), atom_valence=0)
    w = World(cfg)

    # inject a carrier at every "1" cell, remember its slot
    slot = {}
    for k in range(K):
        if pattern[k]:
            slot[k] = place_carrier(w, CELLS[k])

    # consolidation: let native bonds form while carriers sit at their cells
    for _ in range(T_CONSOL):
        for k, i in slot.items():
            w.k_pos[i] = (CELLS[k], BAND_Y, 30.0)
            w.k_vel[i] = 0.0
        tick(w, cfg.dt)

    # split the "1" bits into CUE (revealed) and RECALL (to be restored)
    ones = [k for k in range(K) if pattern[k]]
    cue_ones = [k for k in ones if cue_mask[k]]
    recall_ones = [k for k in ones if not cue_mask[k]]

    # displace the recall carriers off their cells (the missing half)
    for k in recall_ones:
        i = slot[k]
        w.k_pos[i] = (CELLS[k] + DISPLACE, BAND_Y, 30.0)
        w.k_vel[i] = 0.0

    t0 = time.perf_counter()
    for _ in range(T_RELAX):
        for k in cue_ones:            # pin the cue carriers (the given half)
            i = slot[k]
            w.k_pos[i] = (CELLS[k], BAND_Y, 30.0)
            w.k_vel[i] = 0.0
        tick(w, cfg.dt)
    secs = time.perf_counter() - t0

    recalled = [1 if occupied(w, CELLS[k]) else 0 for k in range(K)]
    return recalled, secs


# ---- classical baseline: Hopfield (binary, ±1, Hebbian) --------------------
def hopfield_recall(stored_patterns, query, cue_mask):
    t0 = time.perf_counter()
    P = np.array([[1 if b else -1 for b in p] for p in stored_patterns], dtype=float)
    W = P.T @ P
    np.fill_diagonal(W, 0.0)
    W /= max(1, len(stored_patterns))
    s = np.array([1 if b else -1 for b in query], dtype=float)
    clamp = np.array(cue_mask, dtype=bool)
    s_clamped = np.array([1 if b else -1 for b in query], dtype=float)
    for _ in range(30):                      # async sweeps to convergence
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
    rng_master = np.random.default_rng(154)
    sub_accs, neg_accs, hop_accs = [], [], []
    sub_secs, hop_secs = [], []

    for seed in SEEDS:
        rng = np.random.default_rng(1540 + seed)
        s_acc = n_acc = h_acc = 0.0
        s_t = h_t = 0.0
        for _ in range(N_PATTERNS):
            # random pattern with >=2 ones (so there is something to cue+recall)
            while True:
                pattern = list(rng.integers(0, 2, K))
                if sum(pattern) >= 2:
                    break
            ones = [k for k in range(K) if pattern[k]]
            # cue = half the ones (rounded up); recall = the rest of the ones
            n_cue = max(1, len(ones) // 2)
            cue_ones = set(rng.choice(ones, size=n_cue, replace=False).tolist())
            cue_mask = [(k in cue_ones) or (pattern[k] == 0) for k in range(K)]
            recall_idx = [k for k in ones if k not in cue_ones]

            rec, st = substrate_recall(pattern, cue_mask, seed, bonds=True)
            neg, _ = substrate_recall(pattern, cue_mask, seed, bonds=False)
            hop, ht = hopfield_recall([pattern], pattern, cue_mask)

            s_acc += bit_acc(rec, pattern, recall_idx)
            n_acc += bit_acc(neg, pattern, recall_idx)
            h_acc += bit_acc(hop, pattern, recall_idx)
            s_t += st
            h_t += ht

        sub_accs.append(s_acc / N_PATTERNS)
        neg_accs.append(n_acc / N_PATTERNS)
        hop_accs.append(h_acc / N_PATTERNS)
        sub_secs.append(s_t / N_PATTERNS)
        hop_secs.append(h_t / N_PATTERNS)

    def ms(s):
        return f"{np.mean(s) * 1e3:.3f} ms"

    sub = np.array(sub_accs); neg = np.array(neg_accs); hop = np.array(hop_accs)
    print("=" * 64)
    print("G154 pilot — content-addressable recall on the matter register")
    print(f"K={K} cells, spacing={SPACING} (r_eq={R2*0.5}), displace={DISPLACE}, "
          f"relax={T_RELAX} ticks, {N_PATTERNS} patterns x {len(SEEDS)} seeds")
    print("-" * 64)
    print(f"SUBSTRATE  recall bit-acc : {sub.mean():.3f} +/- {sub.std():.3f}   "
          f"(per-seed {np.round(sub,3).tolist()})")
    print(f"NEG-CTRL   (no bonds)     : {neg.mean():.3f} +/- {neg.std():.3f}   "
          f"(per-seed {np.round(neg,3).tolist()})")
    print(f"HOPFIELD   recall bit-acc : {hop.mean():.3f} +/- {hop.std():.3f}   "
          f"(per-seed {np.round(hop,3).tolist()})")
    print(f"wall-clock/recall  substrate {ms(sub_secs)}   hopfield {ms(hop_secs)}   "
          f"(ratio {np.mean(sub_secs)/max(1e-9,np.mean(hop_secs)):.0f}x)")
    print("-" * 64)

    # frozen bars (amendment G154)
    PASS = sub.mean() >= 0.90 and sub.mean() >= hop.mean() and neg.mean() <= 0.5 + 1e-9
    PARTIAL = 0.75 <= sub.mean() < 0.90
    hop_wins_matched = hop.mean() >= sub.mean() and np.mean(hop_secs) < np.mean(sub_secs)
    neg_artifact = neg.mean() > 0.5 + 1e-9

    if neg_artifact and sub.mean() >= 0.90:
        verdict = "FAIL — negative control also recalls (readout artifact)"
    elif PASS and not hop_wins_matched:
        verdict = "PASS"
    elif hop_wins_matched:
        verdict = ("NULL — Hopfield matches/beats the substrate at a tiny fraction "
                   "of the wall-clock; physics decorative for this task")
    elif PARTIAL:
        verdict = "PARTIAL"
    else:
        verdict = "NULL — substrate recall below 0.75"
    print(f"VERDICT (vs frozen bars): {verdict}")
    print(f"  neg-control fails (<=0.5)? {neg.mean() <= 0.5 + 1e-9}   "
          f"substrate>=0.90? {sub.mean() >= 0.90}   "
          f"hopfield wins at matched compute? {hop_wins_matched}")
    print("=" * 64)


if __name__ == "__main__":
    main()

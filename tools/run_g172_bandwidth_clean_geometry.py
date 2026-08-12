"""G172 — association bandwidth on writability-clean geometry (two-stage).

Pre-registered in docs/amendments/g172_bandwidth_clean_geometry.md.
Metrics only; verdict against the frozen bars. Resumable per arm.

Usage: python tools/run_g172_bandwidth_clean_geometry.py
Output: archive/run-logs/g171/results.json + summary.
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
BITS = 6
X0 = 15.0
Z0 = 80.0   # lane center; box z=160 holds 6 lanes x 20 with margin
SHORT, LONG = 6.5, 10.5
UNIFORM = 8.5
T_CONSOL = 8
T_RETRIEVE = 800
N_PAIRS = 8
TENSION_K = 8.0
DAMPING = 0.95
Y_A, Y_B = 25.0, 33.0        # G172: dy=8 (writability-clean with centering)
CHAIN_DY = 14.0              # chains WITHIN a group: y-offset > 12 (no intra-group cross)
OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "g172"
EMPTY = np.empty(0, dtype=np.int32)


def base_cfg(seed: int) -> WorldConfig:
    return WorldConfig(
        rng_seed=seed, box_size=(120.0, 80.0, 160.0),
        repulsion_cell_size=160.0,
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
        lambda_gen=0.0, lambda_dec=0.0, atom_valence=2,
        atom_repulsion_k=0.0, repulsion_k=0.0, node_thermal_speed=0.0,
        anchor_damping=0.0, neuron_dynamics_enabled=False,
        stdp_enabled=False, btsp_enabled=False, r_2=12.0,
        graceful_capacity=True, per_bond_rest_enabled=True,
        bridge_tension_k=TENSION_K, bridge_tension_damping=DAMPING,
    )


def chain_positions(pattern_bits, x0=X0):
    # G172: CENTERED — the chain's center sits at a fixed station; end
    # deviation from center is bounded by bits_per*2 for every pattern.
    s = [LONG if b else SHORT for b in pattern_bits]
    L = sum(s)
    center = x0 + len(pattern_bits) * UNIFORM / 2   # fixed station
    xs = [center - L / 2]
    for sp in s:
        xs.append(xs[-1] + sp)
    return xs


def census_pairs(w):
    return {(min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
             max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
            for b in range(w.b_count) if w.b_alive[b]}


def consolidate(w, pin_map, ticks=T_CONSOL):
    for _ in range(ticks):
        for s, p in pin_map.items():
            w.k_pos[s] = p
            w.k_vel[s] = 0.0
        tick(w, w.config.dt)


def run_one(patA, patB, seed: int, m: int, mode: str) -> dict:
    """mode in {'assoc', 'neg', 'scramx'}. m chains per group, 6/m bits each.

    Trap mitigation: allocate+consolidate each chain strictly before the
    next exists; cross-bonds written last as their own phase.
    """
    bits_per = BITS // m
    cfg = base_cfg(seed)
    w = World(cfg)

    # Layout: each chain PAIR (A_c, B_c) shares a z-lane; pairs are
    # separated along z by ZSEP=20 (> window 12, no inter-pair bonds).
    # Within a pair, A at y=25 and B at y=35 (Δy=10 — ends in window for
    # the cross-write phase). Identical geometry for every pair.
    ZSEP = 20.0

    slotsA, slotsB = [], []
    # STRICT SEQUENTIAL: chain-by-chain allocate + consolidate (trap doc)
    pin_map = {}
    for c in range(m):
        xsA = chain_positions(patA[c*bits_per:(c+1)*bits_per])
        z = Z0 + (c - (m - 1) / 2) * ZSEP
        sA = [w.allocate_node(np.array([x, Y_A, z]), 1.0, True, 4, EMPTY, 0)
              for x in xsA]
        for s, x in zip(sA, xsA):
            pin_map[s] = (x, Y_A, z)
        consolidate(w, pin_map)
        slotsA.append((sA, xsA, z))
    Y_FAR = 55.0   # B consolidates OUT of the cross window (55-25=30 > 12)
    for c in range(m):
        xsB = chain_positions(patB[c*bits_per:(c+1)*bits_per])
        z = Z0 + (c - (m - 1) / 2) * ZSEP
        sB = [w.allocate_node(np.array([x, Y_FAR, z]), 1.0, True, 4, EMPTY, 0)
              for x in xsB]
        for s, x in zip(sB, xsB):
            pin_map[s] = (x, Y_FAR, z)
        consolidate(w, pin_map)
        slotsB.append((sB, xsB, z))

    # Census: intended intra graph only, so far
    expected_intra = set()
    for sA, xsA, _ in slotsA:
        expected_intra |= {(min(sA[i], sA[i+1]), max(sA[i], sA[i+1]))
                           for i in range(len(sA) - 1)}
    for sB, xsB, _ in slotsB:
        expected_intra |= {(min(sB[i], sB[i+1]), max(sB[i], sB[i+1]))
                           for i in range(len(sB) - 1)}
    c_after_intra = census_pairs(w)
    write_valid = (c_after_intra == expected_intra)

    # CROSS-WRITE phase (its own consolidation phase, per amendment):
    # move B (pinned; rest lengths freeze at FORMATION, moving changes
    # nothing) from Y_FAR into the window at Y_B. For scramx, B is pinned
    # at DECOY x-geometry during this phase, so the cross rest lengths
    # encode the decoy relation instead of the true one.
    decoyB = None
    cross_geom = {c: slotsB[c][1] for c in range(m)}   # true x-geometry
    if mode == "scramx":
        # SPAN-MATCHED decoy (permanent specificity gate): per chain, same
        # bit weight (identical span), different arrangement; chains whose
        # weight forces a unique arrangement keep it (span leak is then
        # zero by identity — recorded via decoy==true flag).
        rng_d = np.random.default_rng(seed * 7 + 991)
        decoyB = []
        for c in range(m):
            true_bits = patB[c*bits_per:(c+1)*bits_per]
            import itertools
            cands = [list(p) for p in set(itertools.permutations(true_bits))
                     if list(p) != true_bits]
            decoyB += (cands[rng_d.integers(0, len(cands))]
                       if cands else true_bits)
        cross_geom = {c: chain_positions(decoyB[c*bits_per:(c+1)*bits_per])
                      for c in range(m)}
    for c in range(m):
        sB, xsB, z = slotsB[c]
        for s, x in zip(sB, cross_geom[c]):
            pin_map[s] = (x, Y_B, z)

    # cross bonds: both end pairs per chain pair (k = 2m)
    cross_expected = set()
    for c in range(m):
        sA, xsA, zA = slotsA[c]
        sB, xsB, zB = slotsB[c]
        for endA, endB in ((sA[0], sB[0]), (sA[-1], sB[-1])):
            cross_expected.add((min(endA, endB), max(endA, endB)))
    consolidate(w, pin_map, ticks=T_CONSOL)  # ends at Δy=10 → bonds form
    c_after_cross = census_pairs(w)
    cross_formed = c_after_cross - c_after_intra
    cross_valid = cross_formed == cross_expected

    if mode == "scramx" and decoyB is not None:
        # restore B pins to true positions (rest lengths stay decoy-frozen)
        for c in range(m):
            sB, xsB, z = slotsB[c]
            for s, x in zip(sB, xsB):
                pin_map[s] = (x, Y_B, z)
        consolidate(w, pin_map)

    # ASSOCIATION TEST: scramble B to uniform; delete B intra bonds
    # (and for NEG also the cross bonds); pin A; relax; decode B.
    b_intra = set()
    for sB, xsB, z in slotsB:
        b_intra |= {(min(sB[i], sB[i+1]), max(sB[i], sB[i+1]))
                    for i in range(len(sB) - 1)}
    for b in range(w.b_count):
        if w.b_alive[b]:
            kk = (min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
                  max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
            if kk in b_intra:
                w.b_alive[b] = False
            elif mode == "neg" and kk in cross_expected:
                w.b_alive[b] = False

    for sB, xsB, z in slotsB:
        n = len(sB) - 1
        center = X0 + n * UNIFORM / 2
        for i, s in enumerate(sB):
            w.k_pos[s] = (center - n * UNIFORM / 2 + i * UNIFORM, Y_B, z)
            w.k_vel[s] = 0.0

    pairs_frozen = census_pairs(w)
    for _ in range(T_RETRIEVE):
        for sA, xsA, z in slotsA:
            for s, x in zip(sA, xsA):
                w.k_pos[s] = (x, Y_A, z)
                w.k_vel[s] = 0.0
        tick(w, w.config.dt)
        for b in range(w.b_count):
            if w.b_alive[b]:
                kk = (min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
                      max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
                if kk not in pairs_frozen:
                    w.b_alive[b] = False

    correct = 0
    for c in range(m):
        sB, xsB, z = slotsB[c]
        bits = patB[c*bits_per:(c+1)*bits_per]
        for i in range(len(sB) - 1):
            d = float(w.k_pos[sB[i+1]][0] - w.k_pos[sB[i]][0])
            correct += int((1 if d > UNIFORM else 0) == bits[i])
    acc = correct / BITS
    return {"acc": acc, "write_valid": write_valid,
            "cross_valid": cross_valid,
            "cross_formed": len(cross_formed)}


ARMS = [("K4", 2, "assoc"), ("K6", 3, "assoc"), ("K12", 6, "assoc"),
        ("NEG", 6, "neg"), ("SCRAMX", 6, "scramx")]


def stage1_writability() -> bool:
    """Corner-pattern writability validation (engineering gate)."""
    ok = True
    for m in (2, 3, 6):
        bp = BITS // m
        corners = [[0]*BITS, [1]*BITS,
                   ([0]*bp + [1]*bp) * (m // 2) + [0]*bp * (m % 2),
                   ([1]*bp + [0]*bp) * (m // 2) + [1]*bp * (m % 2)]
        for seed in SEEDS:
            for pA in corners:
                for pB in corners:
                    r = run_one(pA[:BITS], pB[:BITS], seed, m, "assoc")
                    if not (r["write_valid"] and r["cross_valid"]):
                        print(f"# STAGE1 MISS m={m} seed={seed} "
                              f"pA={pA[:BITS]} pB={pB[:BITS]} {r}")
                        ok = False
    print(f"# STAGE1 {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stage_path = OUT_DIR / "stage1.json"
    if not stage_path.exists():
        ok = stage1_writability()
        stage_path.write_text(json.dumps({"stage1_pass": ok}))
        if not ok:
            print("# engineering stop: Stage 1 failed, Stage 2 not run")
            return 1
    elif not json.loads(stage_path.read_text())["stage1_pass"]:
        print("# Stage 1 previously failed; not running Stage 2")
        return 1
    res_path = OUT_DIR / "results.json"
    out = json.loads(res_path.read_text()) if res_path.exists() else {}
    for name, m, mode in ARMS:
        if name in out:
            print(f"# {name}: already complete, skipped (resume)")
            continue
        accs = []
        wv_all, cv_all = True, True
        cross_tot = 0
        for seed in SEEDS:
            rng = np.random.default_rng(1720 + seed)
            a_sum = 0.0
            for _ in range(N_PAIRS):
                def draw():
                    while True:
                        p = list(rng.integers(0, 2, BITS))
                        if 0 < sum(p) < BITS:
                            return p
                patA, patB = draw(), draw()
                r = run_one(patA, patB, seed, m, mode)
                a_sum += r["acc"]
                wv_all &= r["write_valid"]
                cv_all &= r["cross_valid"]
                cross_tot += r["cross_formed"]
            accs.append(a_sum / N_PAIRS)
        out[name] = {
            "per_seed": [round(a, 4) for a in accs],
            "mean": round(float(np.mean(accs)), 4),
            "write_valid_all": bool(wv_all),
            "cross_valid_all": bool(cv_all),
            "cross_formed_total": cross_tot,
        }
        print(f"# {name}: mean={out[name]['mean']} "
              f"per_seed={out[name]['per_seed']} wv={wv_all} cv={cv_all} "
              f"cross_total={cross_tot}")
        res_path.write_text(json.dumps(out, indent=2))
    print(f"# written -> {res_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

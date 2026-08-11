"""G162 — rest-length register: geometry-coded bits under PRIM14.

Pre-registered in docs/amendments/g162_rest_length_register.md.
Metrics only; verdict against the frozen bars.

Usage: python tools/run_g162_rest_length_register.py
Output: archive/run-logs/g162/results.json + summary.
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
BAND_Y = 30.0
SHORT, LONG = 4.0, 8.0     # bit 0 / bit 1 spacing
UNIFORM = 6.0              # scramble spacing = global equilibrium
T_CONSOL = 8
T_RETRIEVE = 800
N_PATTERNS = 8
TENSION_K = 8.0
DAMPING = 0.95
EMPTY = np.empty(0, dtype=np.int32)
OUT_DIR = Path(__file__).resolve().parent.parent / "archive" / "run-logs" / "g162"


def base_cfg(seed: int, per_bond: bool) -> WorldConfig:
    return WorldConfig(
        rng_seed=seed, box_size=(120.0, 60.0, 60.0),
        repulsion_cell_size=120.0,
        n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
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


def census(w: World) -> list[tuple[int, int, float]]:
    out = []
    for b in range(w.b_count):
        if w.b_alive[b]:
            out.append((int(w.b_atom_i[b]), int(w.b_atom_j[b]),
                        round(float(w.b_rest_len[b]), 2)))
    return sorted(out)


def run_register(pattern, seed: int, arm: str) -> dict:
    """arm in {'P', 'OLDREST', 'NEG'}. Returns decode accuracy + validity."""
    per_bond = arm != "OLDREST"
    cfg = base_cfg(seed, per_bond)
    w = World(cfg)

    xs_enc = encoded_positions(pattern)
    slots = [w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4,
                             EMPTY, 0) for x in xs_enc]

    # Phase 1 — driven write at encoded geometry
    for _ in range(T_CONSOL):
        for s, x in zip(slots, xs_enc):
            w.k_pos[s] = (x, BAND_Y, 30.0)
            w.k_vel[s] = 0.0
        tick(w, cfg.dt)

    c0 = census(w)
    pairs = {(min(a, b), max(a, b)) for a, b, _ in c0}
    expected_pairs = {(i, i + 1) for i in range(K_BITS)}
    valid = (len(c0) == K_BITS and pairs == expected_pairs)
    if arm == "P" and valid:
        # rests must mirror the encoded spacings
        rest_by_pair = {(min(a, b), max(a, b)): r for a, b, r in c0}
        for i, bit in enumerate(pattern):
            want = LONG if bit else SHORT
            if abs(rest_by_pair[(i, i + 1)] - want) > 0.5:
                valid = False

    # Phase 2 — scramble to uniform spacing (maximum ignorance)
    for i, s in enumerate(slots):
        w.k_pos[s] = (X0 + i * UNIFORM, BAND_Y, 30.0)
        w.k_vel[s] = 0.0

    if arm == "NEG":
        w.b_alive[: w.b_count] = False

    # Phase 3 — retrieve: pin carrier 0 only; formation freeze active
    kills = 0
    for _ in range(T_RETRIEVE):
        w.k_pos[slots[0]] = (X0, BAND_Y, 30.0)
        w.k_vel[slots[0]] = 0.0
        tick(w, cfg.dt)
        if arm != "NEG":
            for b in range(w.b_count):
                if w.b_alive[b]:
                    key = (min(int(w.b_atom_i[b]), int(w.b_atom_j[b])),
                           max(int(w.b_atom_i[b]), int(w.b_atom_j[b])))
                    if key not in pairs:
                        w.b_alive[b] = False
                        kills += 1

    # Phase 4 — read spacings
    decoded = []
    for i in range(K_BITS):
        d = float(w.k_pos[slots[i + 1]][0] - w.k_pos[slots[i]][0])
        decoded.append(1 if d > UNIFORM else 0)
    acc = sum(int(a == b) for a, b in zip(decoded, pattern)) / K_BITS
    return {"acc": acc, "valid": valid, "kills": kills}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    per_seed = {"P": [], "OLDREST": [], "NEG": []}
    all_valid = True
    total_kills = 0

    for seed in SEEDS:
        rng = np.random.default_rng(1620 + seed)
        acc = {"P": 0.0, "OLDREST": 0.0, "NEG": 0.0}
        for _ in range(N_PATTERNS):
            while True:
                pattern = list(rng.integers(0, 2, K_BITS))
                if 0 < sum(pattern) < K_BITS:
                    break
            for arm in ("P", "OLDREST", "NEG"):
                r = run_register(pattern, seed, arm)
                acc[arm] += r["acc"]
                total_kills += r["kills"]
                if arm == "P":
                    all_valid &= r["valid"]
        for arm in per_seed:
            per_seed[arm].append(acc[arm] / N_PATTERNS)
        print(f"# seed {seed}: P={per_seed['P'][-1]:.3f} "
              f"OLDREST={per_seed['OLDREST'][-1]:.3f} "
              f"NEG={per_seed['NEG'][-1]:.3f}")

    out = {
        "per_seed": per_seed,
        "mean": {k: float(np.mean(v)) for k, v in per_seed.items()},
        "census_valid_all_P": bool(all_valid),
        "freeze_kills_total": int(total_kills),
    }
    (OUT_DIR / "results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out["mean"], indent=2))
    print(f"# census_valid_all_P={all_valid} freeze_kills={total_kills}")
    print(f"# written -> {OUT_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

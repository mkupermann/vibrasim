"""BP-B3 — multi-bit molecule composition content (headless lab).

Pre-registered: docs/amendments/bp_b3_multibit_molecule.md
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.classify_molecules import _ground_atom_decades, species_fingerprint
from world.config import WorldConfig
from world.physics import tick
from world.state import World

BAR_B1, BAR_B2, BAR_B3, BAR_B4, BAR_B5 = 0.90, 0.40, 0.40, 0.45, 0.80
SEEDS = (71, 73)
N_FULL = 24
T_FULL = 500
# label -> decades for two atoms
SPECIES = {
    0: (3, 3),  # A33
    1: (3, 4),  # A34
    2: (4, 4),  # A44
}
FP_TO_LABEL = {"A33": 0, "A34": 1, "A44": 2}


def make_cfg(seed: int) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 80.0, 80.0),
        n_vibrations_max=64,
        n_nodes_max=256,
        rng_seed=seed,
        lambda_gen=0.0,
        lambda_dec=0.0,
        lambda_dec_mol=0.0,
        node_thermal_speed=0.0,
        mol_fusion_enabled=False,
        repulsion_k=0.0,
        speed_min=0.0,
        speed_max=0.0,
    )


def _freq(decade: int, offset: float = 0.0) -> float:
    return float(10**decade * 3.0 + offset)


def plant_species(world: World, label: int, pos: np.ndarray) -> int:
    d0, d1 = SPECIES[label]
    f0, f1 = _freq(d0, 0.0), _freq(d1, 150.0 if d0 == d1 else 0.0)
    box = np.asarray(world.config.box_size, dtype=np.float64)
    a0 = world.allocate_node(
        pos=(pos + np.array([box[0] * 0.3, 0, 0])) % box,
        freq=f0, pol=True, level=4,
        constituents=np.array([], dtype=np.int32), comp_kind=1,
    )
    a1 = world.allocate_node(
        pos=(pos + np.array([0, box[1] * 0.3, 0])) % box,
        freq=f1, pol=True, level=4,
        constituents=np.array([], dtype=np.int32), comp_kind=1,
    )
    mol = world.allocate_node(
        pos=pos.copy(), freq=f0 + f1, pol=True, level=5,
        constituents=np.array([a0, a1], dtype=np.int32), comp_kind=1,
    )
    world.k_strength[mol] = 10.0
    return mol


def plant_empty(world: World, pos: np.ndarray) -> int:
    mol = world.allocate_node(
        pos=pos.copy(), freq=6000.0, pol=True, level=5,
        constituents=np.array([], dtype=np.int32), comp_kind=1,
    )
    world.k_strength[mol] = 10.0
    return mol


def mol_fp(world: World, idx: int) -> str:
    if idx < 0 or not world.k_alive[idx] or int(world.k_level[idx]) < 5:
        return "A?"
    return species_fingerprint(_ground_atom_decades(world, idx))


def scramble(world: World, mol: int, label: int) -> None:
    start, end = int(world.k_comp_offset[mol]), int(world.k_comp_end[mol])
    kids = [int(world.k_comp_indices[j]) for j in range(start, end)]
    if len(kids) < 2:
        return
    # Force a different species
    other = (label + 1) % 3
    d0, d1 = SPECIES[other]
    world.k_freq[kids[0]] = _freq(d0)
    world.k_freq[kids[1]] = _freq(d1, 200.0)


def hold(world: World, n: int) -> None:
    dt = float(world.config.dt)
    for _ in range(n):
        tick(world, dt)
        world.t += dt


def decode_fp(fp: str) -> int | None:
    return FP_TO_LABEL.get(fp)


def decode_pos(pos: np.ndarray, box: np.ndarray) -> int:
    # ternary by x thirds — chance if positions random
    x = float(pos[0]) / float(box[0])
    if x < 1.0 / 3.0:
        return 0
    if x < 2.0 / 3.0:
        return 1
    return 2


def schedule(n: int, rng: np.random.Generator) -> list[int]:
    per = n // 3
    labels = [0] * per + [1] * per + [2] * (n - 2 * per)
    rng.shuffle(labels)
    return labels


def run_protocol(n_trials: int, t_hold: int, seeds: tuple[int, ...], smoke: bool) -> dict:
    rows_t, rows_c1, rows_c2, rows_c3 = [], [], [], []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        labels = schedule(n_trials, rng)
        box = np.array([80.0, 80.0, 80.0])
        for i, lab in enumerate(labels):
            # T
            w = World(make_cfg(seed))
            pos = rng.uniform(0, 1, 3) * box
            mol = plant_species(w, lab, pos)
            hold(w, t_hold)
            alive = bool(w.k_alive[mol])
            fp = mol_fp(w, mol) if alive else "A?"
            pred = decode_fp(fp)
            rows_t.append({
                "label": lab, "fp": fp, "pred": pred,
                "correct": pred == lab,
                "ok": alive and fp not in ("A?", ""),
            })
            # C1 empty
            w1 = World(make_cfg(seed))
            m1 = plant_empty(w1, rng.uniform(0, 1, 3) * box)
            hold(w1, t_hold)
            fp1 = mol_fp(w1, m1) if w1.k_alive[m1] else "A?"
            p1 = decode_fp(fp1)
            rows_c1.append({"label": lab, "correct": p1 == lab})
            # C2 scramble
            w2 = World(make_cfg(seed))
            pos2 = rng.uniform(0, 1, 3) * box
            m2 = plant_species(w2, lab, pos2)
            scramble(w2, m2, lab)
            hold(w2, t_hold)
            fp2 = mol_fp(w2, m2) if w2.k_alive[m2] else "A?"
            p2 = decode_fp(fp2)
            rows_c2.append({"label": lab, "correct": p2 == lab})
            # C3 position
            w3 = World(make_cfg(seed))
            pos3 = rng.uniform(0, 1, 3) * box
            m3 = plant_species(w3, lab, pos3)
            hold(w3, t_hold)
            pos_r = w3.k_pos[m3] if w3.k_alive[m3] else pos3
            p3 = decode_pos(np.asarray(pos_r), box)
            rows_c3.append({"label": lab, "correct": p3 == lab})

    def acc(rows, key="correct"):
        return float(sum(1 for r in rows if r[key]) / len(rows)) if rows else 0.0

    a_t, a_c1, a_c2, a_c3 = acc(rows_t), acc(rows_c1), acc(rows_c2), acc(rows_c3)
    surv = acc(rows_t, "ok")
    b1 = a_t >= BAR_B1
    b2 = a_c1 <= BAR_B2
    b3 = a_c2 <= BAR_B3
    b4 = a_c3 <= BAR_B4
    b5 = surv >= BAR_B5
    verdict = "PASS" if (b1 and b2 and b3 and b4 and b5) else "NULL"
    return {
        "id": "BP-B3",
        "smoke": smoke,
        "seeds": list(seeds),
        "bars": {
            "B1_T": {"value": a_t, "threshold": BAR_B1, "pass": b1},
            "B2_C1": {"value": a_c1, "threshold": BAR_B2, "pass": b2},
            "B3_C2": {"value": a_c2, "threshold": BAR_B3, "pass": b3},
            "B4_C3": {"value": a_c3, "threshold": BAR_B4, "pass": b4},
            "B5_surv": {"value": surv, "threshold": BAR_B5, "pass": b5},
        },
        "verdict": verdict,
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    if args.smoke:
        n, t, seeds, smoke = 6, 50, (71,), True
    else:
        n, t, seeds, smoke = N_FULL, T_FULL, SEEDS, False
    print(f"BP-B3 start smoke={smoke} N={n} T={t} seeds={seeds} live=False")
    result = run_protocol(n, t, seeds, smoke)
    out = Path.home() / ".eqmod" / "bet" / "BP-B3"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-B3: {result['verdict']}\nwrote {path}\nDONE")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

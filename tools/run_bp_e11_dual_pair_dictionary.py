"""BP-E11 two exclusive pairs co-resident with multislot. Headless."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from world.config import WorldConfig
from world.physics import apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (421, 431), 10
N_WRITE, T_IDLE, MID = 12, 300, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
PAIRS = (
    (400.0, 7000.0),
    (1500.0, 2500.0),
    (5000.0, 800.0),
)


def make_cfg(seed: int, multislot: bool) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 50.0, 50.0),
        n_vibrations_max=2048,
        n_nodes_max=2048,
        rng_seed=seed,
        r_1=5.0,
        r_2=45.0,
        freq_tolerance=0.03,
        pair_decay_time=60.0,
        triad_decay_time=600.0,
        lambda_gen=0.0,
        lambda_dec=0.0,
        speed_min=0.0,
        speed_max=0.0,
        midplane_wall_enabled=True,
        midplane_wall_x=MID,
        ilw_enabled=True,
        ilw_radius=8.0,
        ilw_delta_strength=0.5,
        atom_valence=4,
        ilw_multislot_enabled=multislot,
        ilw_multislot_rel_freq=0.35,
    )


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)


def write_pair(w: World, rng, c: int) -> None:
    fL, fR = PAIRS[c]
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=fL)
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=fR)


def bridge_classes(w: World) -> set[int]:
    found = set()
    B = w.b_count if w.b_count > 0 else len(w.b_alive)
    for b in range(B):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        xi, xj = float(w.k_pos[i, 0]), float(w.k_pos[j, 0])
        if (xi < MID) == (xj < MID):
            continue
        if xi < MID:
            fL, fR = float(w.k_freq[i]), float(w.k_freq[j])
        else:
            fL, fR = float(w.k_freq[j]), float(w.k_freq[i])
        best, bd = 0, 1e18
        for c, (a, b_) in enumerate(PAIRS):
            d = (fL - a) ** 2 + (fR - b_) ** 2
            if d < bd:
                bd, best = d, c
        found.add(best)
    return found


def n_cross(w: World) -> int:
    n = 0
    B = w.b_count if w.b_count > 0 else len(w.b_alive)
    for b in range(B):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        if (float(w.k_pos[i, 0]) < MID) != (float(w.k_pos[j, 0]) < MID):
            n += 1
    return n


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((421,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E11 start smoke={args.smoke}")
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 27023 + ti * 97)
            w = World(make_cfg(seed, True))
            write_pair(w, rng, 0)
            write_pair(w, rng, 1)
            idle(w, T_IDLE)
            cls = bridge_classes(w)
            b1s.append(0 in cls and 1 in cls)
            b3s.append(n_cross(w) >= 1)
            w0 = World(make_cfg(seed, False))
            write_pair(w0, rng, 0)
            write_pair(w0, rng, 1)
            idle(w0, T_IDLE)
            cls0 = bridge_classes(w0)
            b2s.append(0 in cls0 and 1 in cls0)
    a1, a2, a3 = float(np.mean(b1s)), float(np.mean(b2s)), float(np.mean(b3s))
    p1, p2, p3 = a1 >= 0.80, a2 <= 0.25, a3 >= 0.90
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "BP-E11",
        "bars": {
            "B1_both_pairs": {"value": a1, "threshold": 0.80, "pass": p1},
            "B2_legacy_both": {"value": a2, "threshold": 0.25, "pass": p2},
            "B3_cross": {"value": a3, "threshold": 0.90, "pass": p3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E11"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E11: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

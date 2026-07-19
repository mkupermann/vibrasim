"""PRIM5-D0 exclusive pair link on dual write. Headless."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (521, 531), 10
N_WRITE, T_IDLE, MID = 10, 40, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
PAIRS = ((400.0, 7000.0), (1500.0, 2500.0))


def make_cfg(seed: int, pair_link: bool) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 50.0, 50.0),
        n_vibrations_max=2048,
        n_nodes_max=2048,
        rng_seed=seed,
        r_1=5.0,
        r_2=28.0,  # short: form_bridges won't span mid if valence were on
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
        atom_valence=0,  # only pair_link creates bridges
        ilw_multislot_enabled=True,
        ilw_multislot_rel_freq=0.35,
        ilw_pair_link_enabled=pair_link,
        ilw_pair_link_delta=1.0,
    )


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)


def n_cross(w: World) -> int:
    n = 0
    for b in range(w.b_count):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        if (float(w.k_pos[i, 0]) < MID) != (float(w.k_pos[j, 0]) < MID):
            n += 1
    return n


def bridge_classes(w: World) -> set[int]:
    found = set()
    for b in range(w.b_count):
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
        for c, (a, br) in enumerate(PAIRS):
            d = (fL - a) ** 2 + (fR - br) ** 2
            if d < bd:
                bd, best = d, c
        found.add(best)
    return found


def write_two_pairs(w: World, rng) -> None:
    for c in (0, 1):
        fL, fR = PAIRS[c]
        for _ in range(N_WRITE):
            apply_ilw_pair_write(w, PORT_L, PORT_R, fL, fR, rng)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((521,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"PRIM5-D0 start smoke={args.smoke}")
    l1, l2, l3 = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 32043 + ti * 113)
            w = World(make_cfg(seed, True))
            write_two_pairs(w, rng)
            idle(w, T_IDLE)
            nc = n_cross(w)
            l1.append(nc == 2)
            cls = bridge_classes(w)
            l3.append(0 in cls and 1 in cls)
            w0 = World(make_cfg(seed, False))
            write_two_pairs(w0, rng)
            idle(w0, T_IDLE)
            l2.append(n_cross(w0) == 0)
    a1, a2, a3 = float(np.mean(l1)), float(np.mean(l2)), float(np.mean(l3))
    p1, p2, p3 = a1 >= 0.85, a2 >= 0.90, a3 >= 0.80
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "PRIM5-D0",
        "bars": {
            "L1_two_bridges": {"value": a1, "threshold": 0.85, "pass": p1},
            "L2_off_zero": {"value": a2, "threshold": 0.90, "pass": p2},
            "L3_both_classes": {"value": a3, "threshold": 0.80, "pass": p3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "PRIM5-D0"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nPRIM5-D0: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""BP-E10 multiset K=3 bands on one port with multislot. Headless."""
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

SEEDS, TRIALS = (401, 411), 10
N_WRITE, T_IDLE, MID = 10, 40, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
BANDS = (400.0, 1500.0, 5000.0)
CENT = np.array(BANDS)


def make_cfg(seed: int, multislot: bool) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 50.0, 50.0),
        n_vibrations_max=2048,
        n_nodes_max=2048,
        rng_seed=seed,
        r_1=5.0,
        r_2=28.0,
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
        ilw_multislot_enabled=multislot,
        ilw_multislot_rel_freq=0.35,
    )


def left_bin_set(w: World):
    occupied = set()
    n = 0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) >= MID:
            continue
        n += 1
        f = float(w.k_freq[i])
        occupied.add(int(np.argmin(np.abs(CENT - f))))
    return occupied, n


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)


def write_all(w: World, rng) -> None:
    for band in BANDS:
        for _ in range(N_WRITE):
            apply_ilw_port_event(w, PORT_L, rng, seed_freq=band)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((401,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E10 start smoke={args.smoke}")
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 26019 + ti * 89)
            w = World(make_cfg(seed, True))
            write_all(w, rng)
            idle(w, T_IDLE)
            occ, n = left_bin_set(w)
            b1s.append(len(occ) >= 3)
            b3s.append(n >= 3)
            w0 = World(make_cfg(seed, False))
            write_all(w0, rng)
            idle(w0, T_IDLE)
            occ0, _ = left_bin_set(w0)
            b2s.append(len(occ0) >= 3)
    a1, a2, a3 = float(np.mean(b1s)), float(np.mean(b2s)), float(np.mean(b3s))
    p1, p2, p3 = a1 >= 0.85, a2 <= 0.15, a3 >= 0.85
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "BP-E10",
        "bars": {
            "B1_multi_3bins": {"value": a1, "threshold": 0.85, "pass": p1},
            "B2_legacy_3bins": {"value": a2, "threshold": 0.15, "pass": p2},
            "B3_n_atoms": {"value": a3, "threshold": 0.85, "pass": p3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E10"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E10: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

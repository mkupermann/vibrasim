"""PRIM4-D0: multi-slot ILW holds two distinct bands. Headless."""
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

SEEDS, TRIALS = (381, 391), 10
N_WRITE, T_IDLE, MID = 12, 50, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
F_LO, F_HI, F_MID = 400.0, 5000.0, 1581.0


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


def left_bands(w: World) -> tuple[bool, bool, int]:
    """Return (has_low, has_high, n_L4_left)."""
    has_lo = has_hi = False
    n = 0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) >= MID:
            continue
        n += 1
        f = float(w.k_freq[i])
        if f < F_MID:
            has_lo = True
        else:
            has_hi = True
    return has_lo, has_hi, n


def free_delta(w0_counts, w1_counts) -> int:
    return abs(w1_counts[0] - w0_counts[0]) + abs(w1_counts[1] - w0_counts[1])


def free_counts(w: World):
    nL = nR = 0
    for i in range(len(w.s_alive)):
        if not w.s_alive[i]:
            continue
        if float(w.s_pos[i, 0]) < MID:
            nL += 1
        else:
            nR += 1
    return nL, nR


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)


def write_two_bands(w: World, rng) -> None:
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=F_LO)
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=F_HI)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((381,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"PRIM4-D0 start smoke={args.smoke} seeds={seeds} trials={trials}")

    m1, m2, m3 = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 25017 + ti * 83)

            w_on = World(make_cfg(seed, True))
            f0 = free_counts(w_on)
            write_two_bands(w_on, rng)
            idle(w_on, T_IDLE)
            lo, hi, n = left_bands(w_on)
            m1.append(lo and hi and n >= 2)
            f1 = free_counts(w_on)
            m3.append(free_delta(f0, f1) == 0)

            w_off = World(make_cfg(seed, False))
            write_two_bands(w_off, rng)
            idle(w_off, T_IDLE)
            _, _, n_off = left_bands(w_off)
            # legacy: should collapse to one slot (n_L4 <= 1) OR not both bands
            lo2, hi2, n2 = left_bands(w_off)
            multi_legacy = n2 >= 2 and lo2 and hi2
            m2.append(multi_legacy)  # we want this rare → mean <= 0.20

    a1 = float(np.mean(m1))
    a2 = float(np.mean(m2))  # fraction legacy multi — want LOW
    a3 = float(np.mean(m3))
    b1, b2, b3 = a1 >= 0.85, a2 <= 0.20, a3 >= 0.90
    verdict = "PASS" if all([b1, b2, b3]) else "NULL"
    result = {
        "id": "PRIM4-D0",
        "bars": {
            "M1_multislot_two_bands": {"value": a1, "threshold": 0.85, "pass": b1},
            "M2_legacy_multi_rate": {"value": a2, "threshold": 0.20, "pass": b2},
            "M3_no_free": {"value": a3, "threshold": 0.90, "pass": b3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "PRIM4-D0"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nPRIM4-D0: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

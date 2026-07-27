"""PRIM1-D1 — DLW Variant A: dual engineered compartments; accept if χ ≤ 0.15.

Pre-registered: docs/amendments/bp_prim1_directional_write.md §4 D1
Only run after D0 class=leaky (satisfied: mean χ≈0.43).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from world.config import WorldConfig
from world.physics import tick
from world.state import World

N_SIDE, T_TRAIN = 400, 1200
SEEDS, TRIALS = (171, 173), 2
MID = 40.0
LOW, HIGH = (100.0, 2000.0), (500.0, 10000.0)
# Two spheres covering left / right halves (box 80×50×50)
COMPARTMENTS = (
    (20.0, 25.0, 25.0, 19.0),  # left
    (60.0, 25.0, 25.0, 19.0),  # right
)


def make_cfg(seed: int, walls: bool) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 50.0, 50.0),
        n_vibrations_max=8192,
        n_nodes_max=4096,
        rng_seed=seed,
        r_1=5.0,
        r_2=28.0,
        freq_tolerance=0.030,
        pair_decay_time=60.0,
        triad_decay_time=600.0,
        lambda_gen=0.0,
        lambda_dec=0.0,
        speed_min=5.0,
        speed_max=25.0,
        compartment_k=1.0 if walls else 0.0,
        compartments=COMPARTMENTS if walls else (),
        compartment_mode="clamp",
    )


def inject(world, rng, birth, n, x0, x1, f0, f1, tag):
    dead = np.where(~world.s_alive)[0]
    if len(dead) >= n:
        slots = dead[:n]
    else:
        start = int(world.n_alive)
        slots = np.arange(start, min(start + n, world.config.n_vibrations_max))
    for k, i in enumerate(slots):
        i = int(i)
        world.s_pos[i] = [rng.uniform(x0, x1), rng.uniform(8, 42), rng.uniform(8, 42)]
        world.s_freq[i] = float(np.exp(rng.uniform(np.log(f0), np.log(f1))))
        world.s_pol[i] = bool(k % 2 == 0)
        z, phi = rng.uniform(-1, 1), rng.uniform(0, 2 * np.pi)
        sq = float(np.sqrt(max(1 - z * z, 0)))
        sp = float(rng.uniform(5, 25))
        world.s_vel[i] = sp * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        world.s_alive[i] = True
        birth[i] = tag
    world.n_alive = int(world.s_alive.sum())


def chi_and_pop(world, birth, ticks):
    dt = float(world.config.dt)
    wrong_s = free_s = 0
    for _ in range(ticks):
        for i in np.where(world.s_alive)[0]:
            tag = int(birth[i])
            if tag == 0:
                continue
            free_s += 1
            x = float(world.s_pos[i, 0])
            if tag == 1 and x >= MID:
                wrong_s += 1
            if tag == 2 and x < MID:
                wrong_s += 1
        tick(world, dt)
        world.t += dt
    chi = float(wrong_s / free_s) if free_s else 0.0
    # level≥4 both sides
    nL = nR = 0
    for i in range(world.k_count):
        if not world.k_alive[i] or int(world.k_level[i]) < 4:
            continue
        if float(world.k_pos[i, 0]) < MID:
            nL += 1
        else:
            nR += 1
    return chi, (nL >= 1 and nR >= 1)


def trial(seed, ti, walls, ticks):
    w = World(make_cfg(seed, walls))
    birth = np.zeros(w.config.n_vibrations_max, dtype=np.int8)
    rng = np.random.default_rng(seed * 1009 + ti * 17 + (10 if walls else 0))
    inject(w, rng, birth, N_SIDE, 8, 32, LOW[0], LOW[1], 1)
    inject(w, rng, birth, N_SIDE, 48, 72, HIGH[0], HIGH[1], 2)
    chi, pop = chi_and_pop(w, birth, ticks)
    return {"walls": walls, "chi": chi, "pop": pop, "seed": seed, "trial": ti}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    if args.smoke:
        seeds, trials, ticks = (171,), 1, 200
        smoke = True
    else:
        seeds, trials, ticks = SEEDS, TRIALS, T_TRAIN
        smoke = False
    print(f"PRIM1-D1 start smoke={smoke} seeds={seeds} T={ticks}")

    on_rows, off_rows = [], []
    for s in seeds:
        for ti in range(trials):
            on_rows.append(trial(s, ti, True, ticks))
            off_rows.append(trial(s, ti, False, ticks))

    chi_on = float(np.mean([r["chi"] for r in on_rows]))
    chi_off = float(np.mean([r["chi"] for r in off_rows]))
    pop_on = float(sum(1 for r in on_rows if r["pop"]) / len(on_rows))
    b_p1 = chi_on <= 0.15
    b_p2 = pop_on >= 0.80
    # informative: walls should reduce χ vs off
    reduced = chi_on < chi_off
    verdict = "PASS" if (b_p1 and b_p2) else "NULL"
    result = {
        "id": "PRIM1-D1",
        "smoke": smoke,
        "bars": {
            "P1_chi_on": {"value": chi_on, "threshold": 0.15, "pass": b_p1},
            "P2_pop": {"value": pop_on, "threshold": 0.80, "pass": b_p2},
        },
        "chi_off": chi_off,
        "chi_reduced_vs_off": reduced,
        "on_trials": on_rows,
        "off_trials": off_rows,
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "PRIM1-D1"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"  chi_on={chi_on:.4f} chi_off={chi_off:.4f} reduced={reduced} pop_on={pop_on:.4f}")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nPRIM1-D1: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

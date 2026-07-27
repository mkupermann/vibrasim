"""PRIM1-D0 — containment audit (cross-talk χ). Headless.

Pre-registered: docs/amendments/bp_prim1_directional_write.md §4 D0
No talent bars. Classification only: tight χ≤0.15 / leaky χ≥0.40 / else mid.
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
# birth side tags: extend via parallel array on free vibs
# 0 = unknown/ambient, 1 = injected L, 2 = injected R


def make_cfg(seed: int) -> WorldConfig:
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
    )


def inject(world, rng, birth: np.ndarray, n: int, x0: float, x1: float, f0: float, f1: float, tag: int) -> None:
    dead = np.where(~world.s_alive)[0]
    if len(dead) >= n:
        slots = dead[:n]
    else:
        start = int(world.n_alive)
        slots = np.arange(start, min(start + n, world.config.n_vibrations_max))
    for k, i in enumerate(slots):
        i = int(i)
        world.s_pos[i] = [rng.uniform(x0, x1), rng.uniform(5, 45), rng.uniform(5, 45)]
        world.s_freq[i] = float(np.exp(rng.uniform(np.log(f0), np.log(f1))))
        world.s_pol[i] = bool(k % 2 == 0)
        z, phi = rng.uniform(-1, 1), rng.uniform(0, 2 * np.pi)
        sq = float(np.sqrt(max(1 - z * z, 0)))
        sp = float(rng.uniform(5, 25))
        world.s_vel[i] = sp * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        world.s_alive[i] = True
        birth[i] = tag
    world.n_alive = int(world.s_alive.sum())


def run_trial(seed: int, trial: int, ticks: int) -> dict:
    w = World(make_cfg(seed))
    birth = np.zeros(w.config.n_vibrations_max, dtype=np.int8)
    rng = np.random.default_rng(seed * 1009 + trial * 17)
    inject(w, rng, birth, N_SIDE, 5, 35, LOW[0], LOW[1], tag=1)
    inject(w, rng, birth, N_SIDE, 45, 75, HIGH[0], HIGH[1], tag=2)
    dt = float(w.config.dt)
    # sample midplane crossings of tagged free vibs each tick
    cross_L_to_R = 0
    cross_R_to_L = 0
    free_tag_samples = 0
    wrong_side_samples = 0
    for _ in range(ticks):
        # before tick: count tagged free on wrong side
        alive = w.s_alive
        for i in np.where(alive)[0]:
            tag = int(birth[i])
            if tag == 0:
                continue
            free_tag_samples += 1
            x = float(w.s_pos[i, 0])
            if tag == 1 and x >= MID:
                wrong_side_samples += 1
            if tag == 2 and x < MID:
                wrong_side_samples += 1
        # detect crossing events this tick (position before/after)
        pos_before = w.s_pos.copy()
        tick(w, dt)
        w.t += dt
        for i in np.where(w.s_alive)[0]:
            tag = int(birth[i])
            if tag == 0:
                continue
            x0, x1 = float(pos_before[i, 0]), float(w.s_pos[i, 0])
            if tag == 1 and x0 < MID <= x1:
                cross_L_to_R += 1
            if tag == 2 and x0 >= MID > x1:
                cross_R_to_L += 1

    # χ definitions (locked in spirit of PRIM1 doc)
    # χ_pos = fraction of tagged free currently on wrong side (end-of-run snapshot)
    tagged = []
    wrong = 0
    for i in np.where(w.s_alive)[0]:
        tag = int(birth[i])
        if tag == 0:
            continue
        tagged.append(i)
        x = float(w.s_pos[i, 0])
        if tag == 1 and x >= MID:
            wrong += 1
        if tag == 2 and x < MID:
            wrong += 1
    n_tagged = len(tagged)
    chi_snapshot = float(wrong / n_tagged) if n_tagged else 0.0
    # χ_time = wrong-side samples / tagged free samples over train
    chi_time = float(wrong_side_samples / free_tag_samples) if free_tag_samples else 0.0
    # crossings per tick normalized by mean free tagged
    chi_cross = float((cross_L_to_R + cross_R_to_L) / max(ticks, 1))

    # primary χ for classification = chi_time (occupation contamination)
    chi = chi_time
    if chi <= 0.15:
        klass = "tight"
    elif chi >= 0.40:
        klass = "leaky"
    else:
        klass = "mid"

    return {
        "seed": seed,
        "trial": trial,
        "chi": chi,
        "chi_snapshot": chi_snapshot,
        "chi_cross_per_tick": chi_cross,
        "n_tagged_end": n_tagged,
        "cross_L_to_R": cross_L_to_R,
        "cross_R_to_L": cross_R_to_L,
        "class": klass,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    if args.smoke:
        seeds, trials, ticks = (171,), 1, 200
        smoke = True
    else:
        seeds, trials, ticks = SEEDS, TRIALS, T_TRAIN
        smoke = False
    print(f"PRIM1-D0 start smoke={smoke} seeds={seeds} trials={trials} T={ticks}")

    rows = []
    for s in seeds:
        for ti in range(trials):
            rows.append(run_trial(s, ti, ticks))

    chis = [r["chi"] for r in rows]
    mean_chi = float(np.mean(chis))
    # majority class
    classes = [r["class"] for r in rows]
    if classes.count("tight") >= classes.count("leaky") and classes.count("tight") >= classes.count("mid"):
        overall = "tight"
    elif classes.count("leaky") >= classes.count("mid"):
        overall = "leaky"
    else:
        overall = "mid"
    # lock interpretation from pre-reg using mean χ
    if mean_chi <= 0.15:
        overall = "tight"
    elif mean_chi >= 0.40:
        overall = "leaky"
    else:
        overall = "mid"

    result = {
        "id": "PRIM1-D0",
        "smoke": smoke,
        "mean_chi": mean_chi,
        "class": overall,
        "interpretation": {
            "tight": "containment already tight; C failure is not walls — need internal non-broadcast write",
            "leaky": "dual inject is leaky; PRIM1-D1 Variant A compartments justified",
            "mid": "intermediate; report χ, do not claim talent; optional D1",
        }[overall],
        "trials": rows,
        "verdict": "DIAGNOSTIC",  # not PASS/NULL talent
    }
    out = Path.home() / ".eqmod" / "bet" / "PRIM1-D0"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"  mean_chi={mean_chi:.4f}  class={overall}")
    print(f"  interpretation: {result['interpretation']}")
    for r in rows:
        print(f"  seed={r['seed']} trial={r['trial']} chi={r['chi']:.4f} class={r['class']} tagged_end={r['n_tagged_end']}")
    print(f"--- VERDICT ---\nPRIM1-D0: DIAGNOSTIC ({overall})\nwrote {path}\nDONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

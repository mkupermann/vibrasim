"""BP-C2 — probe-response talent after dual-drive training.

Pre-registered: docs/amendments/bp_c2_probe_talent.md
Lab is headless by default; pass --live only if you want PyVista.
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

from world.bet_live import run_ticks_live
from world.config import WorldConfig
from world.state import World

BAR_B1, BAR_B2, BAR_B3, BAR_B4 = 0.75, 0.75, 0.60, 0.80
N_SIDE, N_PROBE = 400, 200
T_TRAIN, T_PROBE = 1200, 400
SEEDS = (53, 59, 61)
TRIALS = 3
MID_X = 40.0
BAND_LOW = (100.0, 2000.0)
BAND_HIGH = (500.0, 10000.0)
BAND_SAME = (100.0, 10000.0)


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


def _inject(world, rng, start, n, x_lo, x_hi, y_lo, y_hi, z_lo, z_hi, f_lo, f_hi):
    for k in range(n):
        i = start + k
        if i >= world.config.n_vibrations_max:
            break
        world.s_pos[i] = [
            rng.uniform(x_lo, x_hi),
            rng.uniform(y_lo, y_hi),
            rng.uniform(z_lo, z_hi),
        ]
        world.s_freq[i] = float(np.exp(rng.uniform(np.log(f_lo), np.log(f_hi))))
        world.s_pol[i] = bool(k % 2 == 0)
        z = rng.uniform(-1, 1)
        phi = rng.uniform(0, 2 * np.pi)
        sq = float(np.sqrt(max(1 - z * z, 0)))
        sp = float(rng.uniform(world.config.speed_min, world.config.speed_max))
        world.s_vel[i] = sp * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        world.s_alive[i] = True


def plant_train(world, plant_seed, same_band):
    rng = np.random.default_rng(plant_seed)
    bl = BAND_SAME if same_band else BAND_LOW
    br = BAND_SAME if same_band else BAND_HIGH
    _inject(world, rng, 0, N_SIDE, 5, 35, 5, 45, 5, 45, bl[0], bl[1])
    _inject(world, rng, N_SIDE, N_SIDE, 45, 75, 5, 45, 5, 45, br[0], br[1])
    world.n_alive = min(2 * N_SIDE, world.config.n_vibrations_max)


def inject_probe(world, plant_seed, band):
    """Add N_PROBE free vibrations across full box in *band*; reuse dead slots if needed."""
    rng = np.random.default_rng(plant_seed + 999)
    f_lo, f_hi = band
    bx, by, bz = world.config.box_size
    # free slots
    dead = np.where(~world.s_alive)[0]
    if len(dead) < N_PROBE:
        # overwrite oldest free indices 0.. if needed
        slots = list(range(min(N_PROBE, world.config.n_vibrations_max)))
    else:
        slots = dead[:N_PROBE].tolist()
    for k, i in enumerate(slots):
        world.s_pos[i] = [rng.uniform(0, bx), rng.uniform(0, by), rng.uniform(0, bz)]
        world.s_freq[i] = float(np.exp(rng.uniform(np.log(f_lo), np.log(f_hi))))
        world.s_pol[i] = bool(k % 2 == 0)
        z = rng.uniform(-1, 1)
        phi = rng.uniform(0, 2 * np.pi)
        sq = float(np.sqrt(max(1 - z * z, 0)))
        sp = float(rng.uniform(world.config.speed_min, world.config.speed_max))
        world.s_vel[i] = sp * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        world.s_alive[i] = True
    world.n_alive = int(world.s_alive.sum())


def count_nodes_by_side(world, min_level=1):
    nL = nR = 0
    for i in range(world.k_count):
        if not world.k_alive[i] or int(world.k_level[i]) < min_level:
            continue
        if float(world.k_pos[i, 0]) < MID_X:
            nL += 1
        else:
            nR += 1
    return nL, nR


def both_l4(world) -> bool:
    nL = nR = 0
    for i in range(world.k_count):
        if not world.k_alive[i] or int(world.k_level[i]) < 4:
            continue
        if float(world.k_pos[i, 0]) < MID_X:
            nL += 1
        else:
            nR += 1
    return nL >= 1 and nR >= 1


def run_one(seed, trial_i, same_band, probe_band, n_train, n_probe_ticks, live, title):
    cfg = make_cfg(seed)
    world = World(cfg)
    plant_seed = int(seed * 1_000_003 + trial_i * 71 + (5 if same_band else 0))
    plant_train(world, plant_seed, same_band)
    run_ticks_live(world, n_train, float(cfg.dt), live=live, title=title + " TRAIN", ticks_per_frame=12)
    pop_ok = both_l4(world)
    nL0, nR0 = count_nodes_by_side(world, 1)
    inject_probe(world, plant_seed + 17, probe_band)
    run_ticks_live(world, n_probe_ticks, float(cfg.dt), live=False, title=title + " PROBE")
    nL1, nR1 = count_nodes_by_side(world, 1)
    dL, dR = nL1 - nL0, nR1 - nR0
    if probe_band == BAND_LOW:
        success = dL > dR
    else:
        success = dR > dL
    return {
        "seed": seed,
        "trial_i": trial_i,
        "same_band": same_band,
        "probe": "LOW" if probe_band == BAND_LOW else "HIGH",
        "nL0": nL0, "nR0": nR0, "nL1": nL1, "nR1": nR1,
        "dL": dL, "dR": dR,
        "success": success,
        "pop_ok": pop_ok,
    }


def run_protocol(seeds, trials, smoke, live, live_all):
    t_low, t_high, c1_low, c1_high = [], [], [], []
    live_used = False
    n_train = 400 if smoke else T_TRAIN
    n_probe = 200 if smoke else T_PROBE
    if smoke:
        seeds, trials = (53,), 1

    for seed in seeds:
        for ti in range(trials):
            use = bool(live and (live_all or not live_used))
            if use:
                live_used = True
            t_low.append(run_one(seed, ti, False, BAND_LOW, n_train, n_probe, use, "BP-C2 dual+LOW"))
            t_high.append(run_one(seed, ti, False, BAND_HIGH, n_train, n_probe, False, "BP-C2 dual+HIGH"))
            c1_low.append(run_one(seed, ti, True, BAND_LOW, n_train, n_probe, False, "BP-C2 same+LOW"))
            c1_high.append(run_one(seed, ti, True, BAND_HIGH, n_train, n_probe, False, "BP-C2 same+HIGH"))

    def rate(rows):
        return float(sum(1 for r in rows if r["success"]) / len(rows)) if rows else 0.0

    def pop_rate(rows):
        return float(sum(1 for r in rows if r["pop_ok"]) / len(rows)) if rows else 0.0

    r_tl, r_th = rate(t_low), rate(t_high)
    r_c1 = 0.5 * (rate(c1_low) + rate(c1_high))
    # B4 over dual-train trials (t_low rows share train worlds... actually separate worlds)
    pop = pop_rate(t_low + t_high)

    b1, b2, b3, b4 = r_tl >= BAR_B1, r_th >= BAR_B2, r_c1 <= BAR_B3, pop >= BAR_B4
    verdict = "PASS" if (b1 and b2 and b3 and b4) else "NULL"
    return {
        "id": "BP-C2",
        "smoke": smoke,
        "seeds": list(seeds),
        "bars": {
            "B1_T_low": {"value": r_tl, "threshold": BAR_B1, "pass": b1},
            "B2_T_high": {"value": r_th, "threshold": BAR_B2, "pass": b2},
            "B3_C1_mean": {"value": r_c1, "threshold": BAR_B3, "pass": b3},
            "B4_train_pop": {"value": pop, "threshold": BAR_B4, "pass": b4},
        },
        "sample": t_low[:2] + t_high[:2],
        "verdict": verdict,
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--live", action="store_true", default=False)
    p.add_argument("--live-all", action="store_true")
    args = p.parse_args(argv)
    live = bool(args.live or args.live_all)
    print(f"BP-C2 start smoke={args.smoke} live={live}")
    result = run_protocol(SEEDS, TRIALS, args.smoke, live, args.live_all)
    out = Path.home() / ".eqmod" / "bet" / "BP-C2"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-C2: {result['verdict']}\nwrote {path}\nDONE")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

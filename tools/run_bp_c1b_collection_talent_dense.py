"""BP-C1b — denser dual-drive collection specialisation (follows C1 NULL).

Pre-registered: docs/amendments/bp_c1b_collection_talent_dense.md
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

BAR_B1, BAR_B2, BAR_B3, BAR_B4 = 0.90, 0.60, 0.60, 0.80
N_SIDE = 400
T_FULL = 1500
SEEDS_FULL = (19, 31, 47)
TRIALS_PER_SEED = 3
MID_X = 40.0
BAND_LOW = (100.0, 2000.0)
BAND_HIGH = (500.0, 10000.0)
BAND_SAME = (100.0, 10000.0)


def make_cfg(seed: int) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 50.0, 50.0),
        n_vibrations_max=4096,
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


def _inject(world, rng, start, n, x_lo, x_hi, f_lo, f_hi):
    for k in range(n):
        i = start + k
        pos = np.array([
            rng.uniform(x_lo, x_hi),
            rng.uniform(5.0, 45.0),
            rng.uniform(5.0, 45.0),
        ])
        freq = float(np.exp(rng.uniform(np.log(f_lo), np.log(f_hi))))
        z = rng.uniform(-1, 1)
        phi = rng.uniform(0, 2 * np.pi)
        sq = float(np.sqrt(max(1 - z * z, 0)))
        speed = float(rng.uniform(world.config.speed_min, world.config.speed_max))
        world.s_pos[i] = pos
        world.s_freq[i] = freq
        world.s_pol[i] = bool(k % 2 == 0)
        world.s_vel[i] = speed * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        world.s_alive[i] = True


def plant(world, plant_seed, same_band):
    rng = np.random.default_rng(plant_seed)
    if same_band:
        bl, br = BAND_SAME, BAND_SAME
    else:
        bl, br = BAND_LOW, BAND_HIGH
    _inject(world, rng, 0, N_SIDE, 5, 35, bl[0], bl[1])
    _inject(world, rng, N_SIDE, N_SIDE, 45, 75, br[0], br[1])
    world.n_alive = 2 * N_SIDE


def region_stats(world):
    left, right = [], []
    for i in range(world.k_count):
        if not world.k_alive[i] or int(world.k_level[i]) < 4:
            continue
        d = int(math.floor(math.log10(max(float(world.k_freq[i]), 1.0))))
        (left if float(world.k_pos[i, 0]) < MID_X else right).append(d)
    ml = float(np.mean(left)) if left else None
    mr = float(np.mean(right)) if right else None
    return {
        "n_left": len(left),
        "n_right": len(right),
        "mean_left": ml,
        "mean_right": mr,
        "both_populated": len(left) >= 1 and len(right) >= 1,
        "success_natural": ml is not None and mr is not None and ml < mr,
        "success_flipped": ml is not None and mr is not None and ml > mr,
    }


def trial(seed, trial_i, same_band, n_ticks, live, title):
    cfg = make_cfg(seed)
    world = World(cfg)
    plant(world, int(seed * 1_000_003 + trial_i * 59 + (3 if same_band else 0)), same_band)
    run_ticks_live(world, n_ticks, float(cfg.dt), live=live, title=title, ticks_per_frame=10)
    return {"seed": seed, "trial_i": trial_i, "same_band": same_band, **region_stats(world)}


def run_protocol(seeds, trials, n_ticks, smoke, live, live_all):
    t_rows, c1_rows = [], []
    live_used = False
    for seed in seeds:
        for ti in range(trials):
            use = bool(live and (live_all or not live_used))
            if use:
                live_used = True
            t_rows.append(trial(seed, ti, False, n_ticks, use, "BP-C1b dual L-low/R-high"))
            c1_rows.append(trial(seed, ti, True, n_ticks, live_all, "BP-C1b same band"))

    def rate(rows, key):
        return float(sum(1 for r in rows if r.get(key)) / len(rows)) if rows else 0.0

    acc_t, acc_c1 = rate(t_rows, "success_natural"), rate(c1_rows, "success_natural")
    acc_flip, pop = rate(t_rows, "success_flipped"), rate(t_rows, "both_populated")
    b1, b2, b3, b4 = acc_t >= BAR_B1, acc_c1 <= BAR_B2, acc_flip <= BAR_B3, pop >= BAR_B4
    verdict = "PASS" if (b1 and b2 and b3 and b4) else "NULL"
    return {
        "id": "BP-C1b",
        "smoke": smoke,
        "seeds": list(seeds),
        "bars": {
            "B1_T": {"value": acc_t, "threshold": BAR_B1, "pass": b1},
            "B2_C1": {"value": acc_c1, "threshold": BAR_B2, "pass": b2},
            "B3_flip": {"value": acc_flip, "threshold": BAR_B3, "pass": b3},
            "B4_pop": {"value": pop, "threshold": BAR_B4, "pass": b4},
        },
        "sample_T": t_rows[:4],
        "verdict": verdict,
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--live", action="store_true", default=False)
    p.add_argument("--live-all", action="store_true")
    args = p.parse_args(argv)
    if args.smoke:
        seeds, trials, n_ticks, smoke = (19,), 1, 600, True
    else:
        seeds, trials, n_ticks, smoke = SEEDS_FULL, TRIALS_PER_SEED, T_FULL, False
    live = bool(args.live or args.live_all)
    print(f"BP-C1b start smoke={smoke} seeds={seeds} trials={trials} T={n_ticks} live={live}")
    result = run_protocol(seeds, trials, n_ticks, smoke, live, args.live_all)
    out = Path.home() / ".eqmod" / "bet" / "BP-C1b"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-C1b: {result['verdict']}\nwrote {path}\nDONE")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

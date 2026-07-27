"""BP-C1 — Dual-drive collections specialise (Rung C structural talent).

Pre-registered: docs/amendments/bp_c1_collection_talent.md
Lab is headless by default; pass --live only if you want PyVista.

Usage:
    python tools/run_bp_c1_collection_talent.py --smoke
    python tools/run_bp_c1_collection_talent.py
    python tools/run_bp_c1_collection_talent.py --headless
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

BAR_B1 = 0.90
BAR_B2 = 0.60
BAR_B3 = 0.60
BAR_B4 = 0.80
N_SIDE = 300
T_FULL = 800
SEEDS_FULL = (17, 29, 43)
TRIALS_PER_SEED = 4
MID_X = 40.0
BAND_LOW = (100.0, 2000.0)
BAND_HIGH = (500.0, 10000.0)
BAND_SAME = (100.0, 10000.0)


def make_cfg(seed: int) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 40.0, 40.0),
        n_vibrations_max=4096,
        n_nodes_max=2048,
        rng_seed=seed,
        r_1=5.0,
        r_2=20.0,
        freq_tolerance=0.030,
        pair_decay_time=60.0,
        triad_decay_time=600.0,
        lambda_gen=0.0,
        lambda_dec=0.0,
        speed_min=5.0,
        speed_max=20.0,
    )


def _inject_region(
    world: World,
    rng: np.random.Generator,
    *,
    start: int,
    n: int,
    x_lo: float,
    x_hi: float,
    f_lo: float,
    f_hi: float,
    yz_lo: float = 5.0,
    yz_hi: float = 35.0,
) -> None:
    for k in range(n):
        i = start + k
        pos = np.array([
            rng.uniform(x_lo, x_hi),
            rng.uniform(yz_lo, yz_hi),
            rng.uniform(yz_lo, yz_hi),
        ], dtype=np.float64)
        freq = float(np.exp(rng.uniform(np.log(f_lo), np.log(f_hi))))
        pol = bool(k % 2 == 0)
        z = rng.uniform(-1.0, 1.0)
        phi = rng.uniform(0.0, 2.0 * np.pi)
        sq = float(np.sqrt(max(1.0 - z * z, 0.0)))
        speed = float(rng.uniform(world.config.speed_min, world.config.speed_max))
        vel = speed * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        world.s_pos[i] = pos
        world.s_freq[i] = freq
        world.s_pol[i] = pol
        world.s_vel[i] = vel
        world.s_alive[i] = True


def plant_dual(
    world: World,
    plant_seed: int,
    *,
    same_band: bool,
) -> None:
    rng = np.random.default_rng(plant_seed)
    if same_band:
        lo_l, hi_l = BAND_SAME
        lo_r, hi_r = BAND_SAME
    else:
        lo_l, hi_l = BAND_LOW
        lo_r, hi_r = BAND_HIGH
    _inject_region(world, rng, start=0, n=N_SIDE, x_lo=5.0, x_hi=35.0, f_lo=lo_l, f_hi=hi_l)
    _inject_region(world, rng, start=N_SIDE, n=N_SIDE, x_lo=45.0, x_hi=75.0, f_lo=lo_r, f_hi=hi_r)
    world.n_alive = 2 * N_SIDE


def region_stats(world: World) -> dict:
    left_d: list[int] = []
    right_d: list[int] = []
    for i in range(world.k_count):
        if not world.k_alive[i]:
            continue
        if int(world.k_level[i]) < 4:
            continue
        d = int(math.floor(math.log10(max(float(world.k_freq[i]), 1.0))))
        if float(world.k_pos[i, 0]) < MID_X:
            left_d.append(d)
        else:
            right_d.append(d)
    mean_l = float(np.mean(left_d)) if left_d else None
    mean_r = float(np.mean(right_d)) if right_d else None
    return {
        "n_left": len(left_d),
        "n_right": len(right_d),
        "mean_left": mean_l,
        "mean_right": mean_r,
        "both_populated": len(left_d) >= 1 and len(right_d) >= 1,
        "success_natural": (
            mean_l is not None and mean_r is not None and mean_l < mean_r
        ),
        "success_flipped": (
            mean_l is not None and mean_r is not None and mean_l > mean_r
        ),
    }


def run_trial(
    *,
    seed: int,
    trial_i: int,
    same_band: bool,
    n_ticks: int,
    live: bool,
    title: str,
) -> dict:
    plant_seed = int(seed * 1_000_003 + trial_i * 53 + (7 if same_band else 0))
    cfg = make_cfg(seed)
    world = World(cfg)
    plant_dual(world, plant_seed, same_band=same_band)
    dt = float(cfg.dt)
    run_ticks_live(world, n_ticks, dt, live=live, title=title, ticks_per_frame=8)
    st = region_stats(world)
    return {
        "seed": seed,
        "trial_i": trial_i,
        "same_band": same_band,
        **st,
    }


def run_protocol(
    *, seeds: tuple[int, ...], trials: int, n_ticks: int, smoke: bool,
    live: bool, live_all: bool,
) -> dict:
    t_rows: list[dict] = []
    c1_rows: list[dict] = []
    live_used = False

    for seed in seeds:
        for ti in range(trials):
            use_live = False
            if live and (live_all or not live_used):
                use_live = True
                live_used = True
            t_rows.append(run_trial(
                seed=seed, trial_i=ti, same_band=False, n_ticks=n_ticks,
                live=use_live, title="BP-C1 dual drive L-low / R-high",
            ))
            c1_rows.append(run_trial(
                seed=seed, trial_i=ti, same_band=True, n_ticks=n_ticks,
                live=live_all, title="BP-C1 C1 both same band",
            ))

    def rate(rows: list[dict], key: str) -> float:
        if not rows:
            return 0.0
        return float(sum(1 for r in rows if r.get(key)) / len(rows))

    acc_t = rate(t_rows, "success_natural")
    acc_c1 = rate(c1_rows, "success_natural")
    acc_c2 = rate(t_rows, "success_flipped")  # flipped inequality on T physics
    pop = rate(t_rows, "both_populated")

    b1 = acc_t >= BAR_B1
    b2 = acc_c1 <= BAR_B2
    b3 = acc_c2 <= BAR_B3
    b4 = pop >= BAR_B4
    verdict = "PASS" if (b1 and b2 and b3 and b4) else "NULL"

    return {
        "id": "BP-C1",
        "smoke": smoke,
        "seeds": list(seeds),
        "trials_per_seed": trials,
        "n_ticks": n_ticks,
        "bars": {
            "B1_T_specialisation": {"value": acc_t, "threshold": BAR_B1, "pass": b1},
            "B2_C1_same_band": {"value": acc_c1, "threshold": BAR_B2, "pass": b2},
            "B3_C2_flipped": {"value": acc_c2, "threshold": BAR_B3, "pass": b3},
            "B4_both_populated": {"value": pop, "threshold": BAR_B4, "pass": b4},
        },
        "sample_T": t_rows[:4],
        "verdict": verdict,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="run_bp_c1_collection_talent")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--live", action="store_true", default=False)
    p.add_argument("--live-all", action="store_true")
    args = p.parse_args(argv)

    if args.smoke:
        seeds, trials, n_ticks, smoke = (17,), 2, 300, True
    else:
        seeds, trials, n_ticks, smoke = SEEDS_FULL, TRIALS_PER_SEED, T_FULL, False

    live = bool(args.live or args.live_all)
    print(f"BP-C1 start smoke={smoke} seeds={seeds} trials={trials} T={n_ticks} live={live}")
    result = run_protocol(
        seeds=seeds, trials=trials, n_ticks=n_ticks, smoke=smoke,
        live=live, live_all=bool(args.live_all),
    )

    out_dir = Path.home() / ".eqmod" / "bet" / "BP-C1"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / ("result_smoke.json" if smoke else "result.json")
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("--- bars ---")
    for k, v in result["bars"].items():
        print(f"  {k}: value={v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print("--- VERDICT ---")
    print(f"BP-C1: {result['verdict']}")
    print(f"wrote {out_path}")
    print("DONE")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

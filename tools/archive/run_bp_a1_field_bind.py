"""BP-A1 — Local density field enables binding (belief path Rung A).

Pre-registered: docs/amendments/bp_a1_field_bind.md
Official seeds {13, 37, 41} held out from design probes.

Usage:
    python tools/run_bp_a1_field_bind.py
    python tools/run_bp_a1_field_bind.py --smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from world.bet_live import run_ticks_live
from world.config import WorldConfig
from world.state import World

# --- Locked protocol ---
BAR_B1 = 0.35
BAR_B2 = 0.55
BAR_B3 = 0.55
N_MAIN = 40
N_LO = 10
T_FULL = 200
SEEDS_FULL = (13, 37, 41)
TRIALS_PER_SEED = 4
CLUSTER_SIGMA = 2.0
BASE_F = 500.0
PARTNER_RATIO = 1.08
SPEED = 15.0


def make_cfg(seed: int) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(60.0, 60.0, 60.0),
        n_vibrations_max=2048,
        n_nodes_max=512,
        rng_seed=seed,
        r_1=5.0,
        r_2=28.0,
        freq_tolerance=0.030,
        pair_decay_time=60.0,
        triad_decay_time=600.0,
        lambda_gen=0.0,
        lambda_dec=0.0,
        lambda_dec_mol=0.0,
    )


def plant(
    world: World,
    n: int,
    *,
    mode: str,
    scramble_freq: bool,
    plant_seed: int,
) -> None:
    rng = np.random.default_rng(plant_seed)
    box = np.asarray(world.config.box_size, dtype=np.float64)
    centre = box / 2.0
    for i in range(n):
        if mode == "cluster":
            pos = (centre + rng.normal(0.0, CLUSTER_SIGMA, size=3)) % box
        elif mode == "sparse":
            pos = rng.uniform(0.0, 1.0, size=3) * box
        else:
            raise ValueError(mode)
        if scramble_freq:
            freq = float(np.exp(rng.uniform(np.log(100.0), np.log(10000.0))))
        else:
            freq = BASE_F if (i % 2 == 0) else BASE_F * PARTNER_RATIO
        pol = bool(i % 2 == 0)
        z = rng.uniform(-1.0, 1.0)
        phi = rng.uniform(0.0, 2.0 * np.pi)
        sq = float(np.sqrt(max(1.0 - z * z, 0.0)))
        vel = SPEED * np.array([sq * np.cos(phi), sq * np.sin(phi), z], dtype=np.float64)
        world.s_pos[i] = pos
        world.s_freq[i] = freq
        world.s_pol[i] = pol
        world.s_vel[i] = vel
        world.s_alive[i] = True
    world.n_alive = n


def count_electrons(world: World) -> int:
    return int(((world.k_level[: world.k_count] == 1) & world.k_alive[: world.k_count]).sum())


def run_arm(
    *,
    seed: int,
    trial_i: int,
    n: int,
    mode: str,
    scramble_freq: bool,
    n_ticks: int,
    live: bool = False,
) -> dict:
    plant_seed = int(seed * 1_000_003 + trial_i * 91 + n * 7 + (1 if scramble_freq else 0) + (2 if mode == "sparse" else 0))
    cfg = make_cfg(seed)
    world = World(cfg)
    plant(world, n, mode=mode, scramble_freq=scramble_freq, plant_seed=plant_seed)
    dt = float(cfg.dt)
    tag = f"{mode}{'+scramble' if scramble_freq else ''} N={n}"
    run_ticks_live(
        world, n_ticks, dt,
        live=live,
        title=f"BP-A1 {tag}",
        ticks_per_frame=5,
    )
    e = count_electrons(world)
    return {
        "seed": seed,
        "trial_i": trial_i,
        "n": n,
        "mode": mode,
        "scramble_freq": scramble_freq,
        "electrons": e,
        "electrons_per_n": e / max(n, 1),
        "free_left": int(world.s_alive.sum()),
    }


def run_protocol(
    *, seeds: tuple[int, ...], trials: int, n_ticks: int, smoke: bool, live: bool = False, live_all: bool = False,
) -> dict:
    t_rows: list[dict] = []
    c1_rows: list[dict] = []
    c2_rows: list[dict] = []
    b4_cluster: list[dict] = []
    b4_sparse: list[dict] = []

    live_used = False
    for seed in seeds:
        for ti in range(trials):
            def _live_now() -> bool:
                nonlocal live_used
                if not live:
                    return False
                if live_all:
                    return True
                if live_used:
                    return False
                live_used = True
                return True

            t_rows.append(run_arm(seed=seed, trial_i=ti, n=N_MAIN, mode="cluster", scramble_freq=False, n_ticks=n_ticks, live=_live_now()))
            c1_rows.append(run_arm(seed=seed, trial_i=ti, n=N_MAIN, mode="sparse", scramble_freq=False, n_ticks=n_ticks, live=_live_now() if live_all else False))
            c2_rows.append(run_arm(seed=seed, trial_i=ti, n=N_MAIN, mode="cluster", scramble_freq=True, n_ticks=n_ticks, live=_live_now() if live_all else False))
            b4_cluster.append(run_arm(seed=seed, trial_i=ti, n=N_LO, mode="cluster", scramble_freq=False, n_ticks=n_ticks, live=False))
            b4_sparse.append(run_arm(seed=seed, trial_i=ti, n=N_LO, mode="sparse", scramble_freq=False, n_ticks=n_ticks, live=False))

    def mean_e(rows: list[dict]) -> float:
        return float(np.mean([r["electrons"] for r in rows])) if rows else 0.0

    mean_t = mean_e(t_rows)
    mean_c1 = mean_e(c1_rows)
    mean_c2 = mean_e(c2_rows)
    mean_b4c = mean_e(b4_cluster)
    mean_b4s = mean_e(b4_sparse)

    ratio_c1 = mean_c1 / mean_t if mean_t > 0 else 999.0
    ratio_c2 = mean_c2 / mean_t if mean_t > 0 else 999.0
    frac_t = mean_t / N_MAIN

    b1 = frac_t >= BAR_B1
    b2 = ratio_c1 <= BAR_B2
    b3 = ratio_c2 <= BAR_B3
    b4 = (mean_b4s <= 1.0) and (mean_b4c >= 3.0)

    verdict = "PASS" if (b1 and b2 and b3 and b4) else "NULL"

    return {
        "id": "BP-A1",
        "smoke": smoke,
        "seeds": list(seeds),
        "trials_per_seed": trials,
        "n_main": N_MAIN,
        "n_lo": N_LO,
        "n_ticks": n_ticks,
        "means": {
            "T_cluster_eligible": mean_t,
            "C1_sparse_eligible": mean_c1,
            "C2_cluster_scramble": mean_c2,
            "B4_cluster_N10": mean_b4c,
            "B4_sparse_N10": mean_b4s,
        },
        "bars": {
            "B1_T_frac": {"value": frac_t, "threshold": BAR_B1, "pass": b1},
            "B2_C1_ratio": {"value": ratio_c1, "threshold": BAR_B2, "pass": b2},
            "B3_C2_ratio": {"value": ratio_c2, "threshold": BAR_B3, "pass": b3},
            "B4_threshold_N10": {
                "value": {"cluster": mean_b4c, "sparse": mean_b4s},
                "threshold": {"cluster_ge": 3.0, "sparse_le": 1.0},
                "pass": b4,
            },
        },
        "verdict": verdict,
        "sample_T": t_rows[:3],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="run_bp_a1_field_bind")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--live", action="store_true", default=False,
                   help="optional PyVista 3D (off by default — lab is headless)")
    p.add_argument("--live-all", action="store_true",
                   help="live-view every main arm trial (slow)")
    args = p.parse_args(argv)

    if args.smoke:
        seeds, trials, n_ticks, smoke = (13,), 2, 100, True
    else:
        seeds, trials, n_ticks, smoke = SEEDS_FULL, TRIALS_PER_SEED, T_FULL, False

    live = bool(args.live or args.live_all)
    print(f"BP-A1 start smoke={smoke} seeds={seeds} trials={trials} T={n_ticks} live={live}")
    result = run_protocol(
        seeds=seeds, trials=trials, n_ticks=n_ticks, smoke=smoke,
        live=live, live_all=bool(args.live_all),
    )

    out_dir = Path.home() / ".eqmod" / "bet" / "BP-A1"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / ("result_smoke.json" if smoke else "result.json")
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("--- means ---")
    for k, v in result["means"].items():
        print(f"  {k}: {v:.3f}")
    print("--- bars ---")
    for k, v in result["bars"].items():
        print(f"  {k}: value={v['value']} thr={v['threshold']} pass={v['pass']}")
    print("--- VERDICT ---")
    print(f"BP-A1: {result['verdict']}")
    print(f"wrote {out_path}")
    print("DONE")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

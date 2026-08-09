"""BP-C4 — temporal dual-drive talent (NEW mechanism vs C1–C3). Headless.

Pre-registered: docs/amendments/bp_c4_temporal_drive_talent.md
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

# Locked protocol
P_L, P_R = 30, 90
N_BURST, N_PROBE = 40, 80
T_TRAIN, T_PROBE = 900, 300
SEEDS, TRIALS = (151, 157, 163), 3
MID = 40.0
BAND = (200.0, 4000.0)
BAR_B1 = BAR_B2 = 0.75
BAR_B3, BAR_B4 = 0.55, 0.70


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
        speed_max=20.0,
    )


def _inject(world: World, rng: np.random.Generator, n: int, x0: float, x1: float) -> None:
    box = np.asarray(world.config.box_size, dtype=np.float64)
    # find free slots
    dead = np.where(~world.s_alive)[0]
    if len(dead) < n:
        # use sequential from n_alive
        start = int(world.n_alive)
        slots = list(range(start, min(start + n, world.config.n_vibrations_max)))
    else:
        slots = dead[:n].tolist()
    f0, f1 = BAND
    for k, i in enumerate(slots):
        world.s_pos[i] = [
            rng.uniform(x0, x1),
            rng.uniform(5.0, 45.0),
            rng.uniform(5.0, 45.0),
        ]
        world.s_freq[i] = float(np.exp(rng.uniform(np.log(f0), np.log(f1))))
        world.s_pol[i] = bool(k % 2 == 0)
        z = rng.uniform(-1.0, 1.0)
        phi = rng.uniform(0.0, 2.0 * np.pi)
        sq = float(np.sqrt(max(1.0 - z * z, 0.0)))
        sp = float(rng.uniform(world.config.speed_min, world.config.speed_max))
        world.s_vel[i] = sp * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        world.s_alive[i] = True
    world.n_alive = int(world.s_alive.sum())


def count_level(world: World, min_level: int, left: bool | None) -> int:
    n = 0
    for i in range(world.k_count):
        if not world.k_alive[i] or int(world.k_level[i]) < min_level:
            continue
        x = float(world.k_pos[i, 0])
        if left is True and x >= MID:
            continue
        if left is False and x < MID:
            continue
        n += 1
    return n


def both_l4(world: World) -> bool:
    return count_level(world, 4, True) >= 1 and count_level(world, 4, False) >= 1


def train(world: World, rng: np.random.Generator, p_left: int, p_right: int, n_ticks: int) -> None:
    dt = float(world.config.dt)
    for t in range(n_ticks):
        if t > 0 and t % p_left == 0:
            _inject(world, rng, N_BURST, 5.0, 35.0)
        if t > 0 and t % p_right == 0:
            _inject(world, rng, N_BURST, 45.0, 75.0)
        tick(world, dt)
        world.t += dt


def probe(world: World, rng: np.random.Generator, period: int, n_ticks: int) -> tuple[int, int]:
    nL0 = count_level(world, 1, True)
    nR0 = count_level(world, 1, False)
    dt = float(world.config.dt)
    for t in range(n_ticks):
        if t % period == 0:
            # global probe — full box
            _inject(world, rng, N_PROBE, 5.0, 75.0)
        tick(world, dt)
        world.t += dt
    nL1 = count_level(world, 1, True)
    nR1 = count_level(world, 1, False)
    return nL1 - nL0, nR1 - nR0


def run_arm(seed: int, trial: int, same_period: bool, probe_period: int,
            t_train: int, t_probe: int) -> dict:
    plant_seed = seed * 10007 + trial * 31 + (1 if same_period else 0) + probe_period
    rng = np.random.default_rng(plant_seed)
    world = World(make_cfg(seed))
    p_l, p_r = (P_L, P_L) if same_period else (P_L, P_R)
    train(world, rng, p_l, p_r, t_train)
    pop = both_l4(world)
    dL, dR = probe(world, rng, probe_period, t_probe)
    if probe_period == P_L:
        success = dL > dR
    else:
        success = dR > dL
    return {
        "same_period": same_period,
        "probe_period": probe_period,
        "dL": dL,
        "dR": dR,
        "success": success,
        "pop": pop,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    if args.smoke:
        seeds, trials, t_tr, t_pr = (151,), 1, 200, 80
        smoke = True
    else:
        seeds, trials, t_tr, t_pr = SEEDS, TRIALS, T_TRAIN, T_PROBE
        smoke = False
    print(f"BP-C4 start smoke={smoke} seeds={seeds} trials={trials} T_train={t_tr} live=False")

    dual_pl, dual_pr, ctrl_pl, ctrl_pr = [], [], [], []
    for seed in seeds:
        for ti in range(trials):
            dual_pl.append(run_arm(seed, ti, False, P_L, t_tr, t_pr))
            dual_pr.append(run_arm(seed, ti, False, P_R, t_tr, t_pr))
            ctrl_pl.append(run_arm(seed, ti, True, P_L, t_tr, t_pr))
            ctrl_pr.append(run_arm(seed, ti, True, P_R, t_tr, t_pr))

    def rate(rows):
        return float(sum(1 for r in rows if r["success"]) / len(rows)) if rows else 0.0

    def pop_rate(rows):
        return float(sum(1 for r in rows if r["pop"]) / len(rows)) if rows else 0.0

    r1, r2 = rate(dual_pl), rate(dual_pr)
    r3 = 0.5 * (rate(ctrl_pl) + rate(ctrl_pr))
    r4 = pop_rate(dual_pl + dual_pr)
    b1, b2, b3, b4 = r1 >= BAR_B1, r2 >= BAR_B2, r3 <= BAR_B3, r4 >= BAR_B4
    verdict = "PASS" if all([b1, b2, b3, b4]) else "NULL"
    result = {
        "id": "BP-C4",
        "smoke": smoke,
        "seeds": list(seeds),
        "mechanism": "temporal_period_dual_drive_same_freq_band",
        "bars": {
            "B1_probe_PL": {"value": r1, "threshold": BAR_B1, "pass": b1},
            "B2_probe_PR": {"value": r2, "threshold": BAR_B2, "pass": b2},
            "B3_control": {"value": r3, "threshold": BAR_B3, "pass": b3},
            "B4_pop": {"value": r4, "threshold": BAR_B4, "pass": b4},
        },
        "sample": dual_pl[:2] + dual_pr[:2],
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-C4"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-C4: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

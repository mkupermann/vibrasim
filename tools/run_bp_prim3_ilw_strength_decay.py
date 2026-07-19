"""PRIM3-D0: ILW strength decay mechanism fires. Headless."""
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

SEEDS, TRIALS = (311, 313), 8
N_WRITE, T_IDLE, MID = 20, 400, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
TAU = 2.0


def make_cfg(seed: int, tau: float) -> WorldConfig:
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
        ilw_strength_decay_tau=tau,
    )


def side_strength(w: World) -> float:
    s = 0.0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) < MID:
            s += float(w.k_strength[i])
    return s


def free_count(w: World) -> tuple[int, int]:
    nL = nR = 0
    for i in range(w.n_alive if hasattr(w, "n_alive") else 0):
        pass
    # vibrations
    n = int(np.sum(w.s_alive[: w.s_count] if hasattr(w, "s_count") else w.s_alive))
    # split by x
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


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((311,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"PRIM3-D0 start smoke={args.smoke} seeds={seeds} trials={trials}")

    p1_ok, p2_ok, p3_ok = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 21001 + ti * 67)

            # decay ON
            w = World(make_cfg(seed, TAU))
            free0 = free_count(w)
            for _ in range(N_WRITE):
                apply_ilw_port_event(w, PORT_L, rng, seed_freq=500.0)
            s_post = side_strength(w)
            idle(w, T_IDLE)
            s_idle = side_strength(w)
            free1 = free_count(w)
            p1_ok.append(s_idle < 0.5 * s_post if s_post > 0 else False)
            p3_ok.append(
                (free1[0] - free0[0] == 0) and (free1[1] - free0[1] == 0)
            )

            # decay OFF
            w0 = World(make_cfg(seed, 0.0))
            for _ in range(N_WRITE):
                apply_ilw_port_event(w0, PORT_L, rng, seed_freq=500.0)
            s0 = side_strength(w0)
            idle(w0, T_IDLE)
            s1 = side_strength(w0)
            p2_ok.append(s1 >= 0.90 * s0 if s0 > 0 else False)

    a1, a2, a3 = float(np.mean(p1_ok)), float(np.mean(p2_ok)), float(np.mean(p3_ok))
    b1, b2, b3 = a1 >= 0.90, a2 >= 0.90, a3 >= 0.90
    verdict = "PASS" if all([b1, b2, b3]) else "NULL"
    result = {
        "id": "PRIM3-D0",
        "bars": {
            "P1_decay_on": {"value": a1, "threshold": 0.90, "pass": b1},
            "P2_decay_off": {"value": a2, "threshold": 0.90, "pass": b2},
            "P3_no_free": {"value": a3, "threshold": 0.90, "pass": b3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "PRIM3-D0"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nPRIM3-D0: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

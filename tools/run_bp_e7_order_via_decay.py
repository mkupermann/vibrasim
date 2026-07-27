"""BP-E7 last-write order via PRIM3 strength decay. Headless."""
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

SEEDS, TRIALS = (321, 331), 10
N_WRITE, T_GAP, T_SHORT, MID = 15, 400, 50, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
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


def strengths(w: World):
    sL = sR = 0.0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        s = float(w.k_strength[i])
        if float(w.k_pos[i, 0]) < MID:
            sL += s
        else:
            sR += s
    return sL, sR


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)


def write_side(w: World, rng, side: int) -> None:
    port = PORT_L if side == 0 else PORT_R
    freq = 500.0 if side == 0 else 5000.0
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, port, rng, seed_freq=freq)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((321,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E7 start smoke={args.smoke} seeds={seeds} trials={trials}")

    treat_ok, node_ok, imb = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 22003 + ti * 71)
            last = int(rng.integers(0, 2))
            first = 1 - last

            # treatment: gap + decay
            w = World(make_cfg(seed, TAU))
            write_side(w, rng, first)
            idle(w, T_GAP)
            write_side(w, rng, last)
            idle(w, T_SHORT)
            sL, sR = strengths(w)
            pred = 0 if sL > sR else 1
            treat_ok.append(pred == last)

            # no-decay control
            w0 = World(make_cfg(seed, 0.0))
            write_side(w0, rng, first)
            idle(w0, T_GAP)
            write_side(w0, rng, last)
            idle(w0, T_SHORT)
            a, b = strengths(w0)
            pred0 = 0 if a > b else 1
            node_ok.append(pred0 == last)

            # equal write + decay
            w1 = World(make_cfg(seed, TAU))
            for _ in range(N_WRITE):
                apply_ilw_port_event(w1, PORT_L, rng, seed_freq=500.0)
                apply_ilw_port_event(w1, PORT_R, rng, seed_freq=5000.0)
            idle(w1, T_GAP)
            c, d = strengths(w1)
            imb.append(abs(c - d) / (c + d + 1e-9))

    a1, a2, a3 = float(np.mean(treat_ok)), float(np.mean(node_ok)), float(np.mean(imb))
    b1, b2, b3 = a1 >= 0.85, a2 <= 0.60, a3 <= 0.25
    verdict = "PASS" if all([b1, b2, b3]) else "NULL"
    result = {
        "id": "BP-E7",
        "bars": {
            "B1_treat_last": {"value": a1, "threshold": 0.85, "pass": b1},
            "B2_no_decay_ctrl": {"value": a2, "threshold": 0.60, "pass": b2},
            "B3_eq_imb": {"value": a3, "threshold": 0.25, "pass": b3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E7"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E7: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

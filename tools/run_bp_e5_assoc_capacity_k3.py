"""BP-E5 associative capacity K=3 exclusive pairs. Headless."""
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

SEEDS, TRIALS = (271, 281), 12
N_WRITE, T_IDLE, MID = 20, 150, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])

# Exclusive pairs (class -> (fL, fR))
PAIRS = (
    (400.0, 7000.0),
    (1500.0, 2500.0),
    (5000.0, 800.0),
)
L_CENTROIDS = np.array([p[0] for p in PAIRS], dtype=np.float64)
R_CENTROIDS = np.array([p[1] for p in PAIRS], dtype=np.float64)
K_CLASS = 3


def cfg(seed: int) -> WorldConfig:
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
    )


def side_mean_freq_and_pop(w: World):
    sL = sR = 0.0
    nL = nR = 0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        f = float(w.k_freq[i])
        if float(w.k_pos[i, 0]) < MID:
            sL += f
            nL += 1
        else:
            sR += f
            nR += 1
    mL = sL / nL if nL else 0.0
    mR = sR / nR if nR else 0.0
    return mL, mR, nL, nR


def nearest_L(mean_f: float) -> int:
    return int(np.argmin(np.abs(L_CENTROIDS - mean_f)))


def nearest_R(mean_f: float) -> int:
    return int(np.argmin(np.abs(R_CENTROIDS - mean_f)))


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)
        w.t += dt


def write_pair(w: World, rng, fL: float, fR: float) -> None:
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=fL)
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=fR)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((271,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E5 start smoke={args.smoke} seeds={seeds} trials={trials}")
    print(f"  pairs={PAIRS}")

    b1s, b2s, b3s, b4s = [], [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 17011 + ti * 53)
            c = int(rng.integers(0, K_CLASS))
            fL, fR = PAIRS[c]

            w = World(cfg(seed))
            write_pair(w, rng, fL, fR)
            idle(w, T_IDLE)
            mL, mR, nL, nR = side_mean_freq_and_pop(w)
            pred_L = nearest_L(mL) if nL >= 1 else int(rng.integers(0, K_CLASS))
            pred_R = nearest_R(mR) if nR >= 1 else int(rng.integers(0, K_CLASS))
            b1s.append(pred_L == c)
            b2s.append(pred_R == c)
            b4s.append(nL >= 1 and nR >= 1)

            # control: L and R classes independent
            cL = int(rng.integers(0, K_CLASS))
            cR = int(rng.integers(0, K_CLASS))
            fL2 = PAIRS[cL][0]
            fR2 = PAIRS[cR][1]
            w2 = World(cfg(seed))
            write_pair(w2, rng, fL2, fR2)
            idle(w2, T_IDLE)
            mL2, mR2, nL2, nR2 = side_mean_freq_and_pop(w2)
            pL2 = nearest_L(mL2) if nL2 >= 1 else int(rng.integers(0, K_CLASS))
            pR2 = nearest_R(mR2) if nR2 >= 1 else int(rng.integers(0, K_CLASS))
            b3s.append(pL2 == pR2)

    a1 = float(np.mean(b1s))
    a2 = float(np.mean(b2s))
    a3 = float(np.mean(b3s))
    a4 = float(np.mean(b4s))
    p1, p2, p3, p4 = a1 >= 0.85, a2 >= 0.85, a3 <= 0.45, a4 >= 0.90
    verdict = "PASS" if all([p1, p2, p3, p4]) else "NULL"
    result = {
        "id": "BP-E5",
        "bars": {
            "B1_L_class": {"value": a1, "threshold": 0.85, "pass": p1},
            "B2_R_class": {"value": a2, "threshold": 0.85, "pass": p2},
            "B3_ctrl_match": {"value": a3, "threshold": 0.45, "pass": p3},
            "B4_pop": {"value": a4, "threshold": 0.90, "pass": p4},
        },
        "verdict": verdict,
        "n_trials": len(b1s),
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E5"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E5: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

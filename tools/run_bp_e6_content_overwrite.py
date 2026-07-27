"""BP-E6 sequential content overwrite: last joint pair wins. Headless."""
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

SEEDS, TRIALS = (291, 301), 12
N_WRITE, T_IDLE, MID = 20, 150, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
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


def side_means(w: World):
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
    return (sL / nL if nL else 0.0), (sR / nR if nR else 0.0), nL, nR


def nearest_L(m: float) -> int:
    return int(np.argmin(np.abs(L_CENTROIDS - m)))


def nearest_R(m: float) -> int:
    return int(np.argmin(np.abs(R_CENTROIDS - m)))


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)
        w.t += dt


def write_class(w: World, rng, c: int) -> None:
    fL, fR = PAIRS[c]
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=fL)
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=fR)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((291,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E6 start smoke={args.smoke} seeds={seeds} trials={trials}")

    b1s, b2s, b3s, b4s = [], [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 19013 + ti * 59)
            first = int(rng.integers(0, K_CLASS))
            last = int(rng.integers(0, K_CLASS - 1))
            if last >= first:
                last += 1  # distinct from first

            w = World(cfg(seed))
            write_class(w, rng, first)
            write_class(w, rng, last)
            idle(w, T_IDLE)
            mL, mR, nL, nR = side_means(w)
            dL = nearest_L(mL) if nL else -1
            dR = nearest_R(mR) if nR else -1
            b1s.append(dL == last)
            b2s.append(dR == last)
            b3s.append(dL == first)

            # control: same class twice
            a = int(rng.integers(0, K_CLASS))
            w2 = World(cfg(seed))
            write_class(w2, rng, a)
            write_class(w2, rng, a)
            idle(w2, T_IDLE)
            mL2, _, nL2, _ = side_means(w2)
            dL2 = nearest_L(mL2) if nL2 else -1
            b4s.append(dL2 == a)

    a1, a2, a3, a4 = map(float, (np.mean(b1s), np.mean(b2s), np.mean(b3s), np.mean(b4s)))
    p1, p2, p3, p4 = a1 >= 0.85, a2 >= 0.85, a3 <= 0.20, a4 >= 0.90
    verdict = "PASS" if all([p1, p2, p3, p4]) else "NULL"
    result = {
        "id": "BP-E6",
        "bars": {
            "B1_L_last": {"value": a1, "threshold": 0.85, "pass": p1},
            "B2_R_last": {"value": a2, "threshold": 0.85, "pass": p2},
            "B3_L_residual_first": {"value": a3, "threshold": 0.20, "pass": p3},
            "B4_ctrl_stable": {"value": a4, "threshold": 0.90, "pass": p4},
        },
        "verdict": verdict,
        "n_trials": len(b1s),
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E6"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E6: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

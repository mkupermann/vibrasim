"""BP-E4 cross-port association: L band predicts R partner. Headless."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from world.config import WorldConfig
from world.physics import apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (251, 263), 12
N_WRITE, T_IDLE, MID = 20, 150, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
F_LO, F_HI = 500.0, 5000.0
F_MID = math.sqrt(F_LO * F_HI)  # ~1581


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
    """Return (mean_freq_L, mean_freq_R, nL, nR) for level>=4 nodes."""
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


def band(mean_f: float) -> int:
    """0 = low, 1 = high. Empty side (0.0) → treat as low (will hurt accuracy if used)."""
    return 0 if mean_f < F_MID else 1


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
    seeds, trials = ((251,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E4 start smoke={args.smoke} seeds={seeds} trials={trials}")
    print(f"  F_MID={F_MID:.2f} N_write={N_WRITE} T_idle={T_IDLE}")

    treat_ok, ctrl_ok, pop_ok = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 13007 + ti * 41)

            # --- treatment: correlated opposite bands ---
            c = int(rng.integers(0, 2))  # association class
            if c == 0:
                fL, fR = F_LO, F_HI
            else:
                fL, fR = F_HI, F_LO
            true_R = 0 if fR < F_MID else 1

            w = World(cfg(seed))
            write_pair(w, rng, fL, fR)
            idle(w, T_IDLE)
            mL, mR, nL, nR = side_mean_freq_and_pop(w)
            band_L = band(mL)
            # paired association: predict R as opposite of L
            pred_R = 1 - band_L
            treat_ok.append(pred_R == true_R)
            pop_ok.append(nL >= 1 and nR >= 1)

            # --- control: uncorrelated L/R ---
            fL2 = F_LO if int(rng.integers(0, 2)) == 0 else F_HI
            fR2 = F_LO if int(rng.integers(0, 2)) == 0 else F_HI
            true_R2 = 0 if fR2 < F_MID else 1
            w2 = World(cfg(seed))
            write_pair(w2, rng, fL2, fR2)
            idle(w2, T_IDLE)
            mL2, _, nL2, _ = side_mean_freq_and_pop(w2)
            if nL2 < 1:
                pred2 = int(rng.integers(0, 2))
            else:
                pred2 = 1 - band(mL2)
            ctrl_ok.append(pred2 == true_R2)

    a1 = float(np.mean(treat_ok))
    a2 = float(np.mean(ctrl_ok))
    a3 = float(np.mean(pop_ok))
    b1, b2, b3 = a1 >= 0.90, a2 <= 0.60, a3 >= 0.90
    verdict = "PASS" if all([b1, b2, b3]) else "NULL"
    result = {
        "id": "BP-E4",
        "bars": {
            "B1_treat": {"value": a1, "threshold": 0.90, "pass": b1},
            "B2_ctrl": {"value": a2, "threshold": 0.60, "pass": b2},
            "B3_pop": {"value": a3, "threshold": 0.90, "pass": b3},
        },
        "verdict": verdict,
        "n_trials": len(treat_ok),
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E4"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E4: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

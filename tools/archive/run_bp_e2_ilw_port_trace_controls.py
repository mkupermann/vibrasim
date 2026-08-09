"""BP-E2 ILW port trace with none / equal controls. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick, apply_ilw_port_event
from world.state import World

SEEDS, TRIALS = (211, 223), 12
N_WRITE, T_IDLE, MID = 25, 200, 40.0
PORT_L, PORT_R = np.array([20., 25., 25.]), np.array([60., 25., 25.])


def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80., 50., 50.),
        n_vibrations_max=2048, n_nodes_max=2048, rng_seed=seed,
        r_1=5., r_2=28., freq_tolerance=0.03,
        pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8.0, ilw_delta_strength=0.5,
    )


def side_strength(w):
    sL = sR = 0.0
    nL = nR = 0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        s = float(w.k_strength[i])
        if float(w.k_pos[i, 0]) < MID:
            sL += s; nL += 1
        else:
            sR += s; nR += 1
    return sL, sR, nL, nR


def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((211,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E2 start smoke={args.smoke} seeds={seeds} trials={trials}")
    treat_ok, none_ok, eq_imb, treat_w = [], [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 10007 + ti * 31)
            label = int(rng.integers(0, 2))
            # treatment
            w = World(cfg(seed))
            port = PORT_L if label == 0 else PORT_R
            freq = 500.0 if label == 0 else 5000.0
            for _ in range(N_WRITE):
                apply_ilw_port_event(w, port, rng, seed_freq=freq)
            idle(w, T_IDLE)
            sL, sR, nL, nR = side_strength(w)
            pred = 0 if sL > sR else 1
            treat_ok.append(pred == label)
            treat_w.append((nL >= 1) if label == 0 else (nR >= 1))
            # C_none
            w0 = World(cfg(seed))
            idle(w0, T_IDLE)
            sL0, sR0, _, _ = side_strength(w0)
            # if both zero, random guess via rng
            if sL0 == 0 and sR0 == 0:
                pred0 = int(rng.integers(0, 2))
            else:
                pred0 = 0 if sL0 > sR0 else 1
            none_ok.append(pred0 == label)
            # C_eq
            w1 = World(cfg(seed))
            for _ in range(N_WRITE // 2):
                apply_ilw_port_event(w1, PORT_L, rng, seed_freq=500.0)
                apply_ilw_port_event(w1, PORT_R, rng, seed_freq=5000.0)
            idle(w1, T_IDLE)
            sL1, sR1, _, _ = side_strength(w1)
            den = sL1 + sR1 + 1e-9
            eq_imb.append(abs(sL1 - sR1) / den)
    aT = float(np.mean(treat_ok))
    aN = float(np.mean(none_ok))
    aE = float(np.mean(eq_imb))
    aW = float(np.mean(treat_w))
    b1, b2, b3, b4 = aT >= 0.90, aN <= 0.55, aE <= 0.25, aW >= 0.85
    verdict = "PASS" if all([b1, b2, b3, b4]) else "NULL"
    result = {"id": "BP-E2", "bars": {
        "B1_treat": {"value": aT, "threshold": 0.90, "pass": b1},
        "B2_none": {"value": aN, "threshold": 0.55, "pass": b2},
        "B3_eq_imbalance": {"value": aE, "threshold": 0.25, "pass": b3},
        "B4_written": {"value": aW, "threshold": 0.85, "pass": b4},
    }, "verdict": verdict}
    out = Path.home()/".eqmod"/"bet"/"BP-E2"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E2: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

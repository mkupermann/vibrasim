"""BP-E1 — which side was ILW-written (port trace). Headless."""
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
N_WRITE, T_IDLE = 25, 200
MID = 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])


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
            sL += s
            nL += 1
        else:
            sR += s
            nR += 1
    return sL, sR, nL, nR


def run_trial(seed, ti, control: bool):
    w = World(cfg(seed))
    rng = np.random.default_rng(seed * 10007 + ti * 31 + (1 if control else 0))
    label = int(rng.integers(0, 2))  # 0=L, 1=R
    if control:
        for _ in range(N_WRITE // 2):
            apply_ilw_port_event(w, PORT_L, rng, seed_freq=500.0)
            apply_ilw_port_event(w, PORT_R, rng, seed_freq=5000.0)
        # pad if odd
        if N_WRITE % 2:
            apply_ilw_port_event(w, PORT_L, rng, seed_freq=500.0)
    else:
        port = PORT_L if label == 0 else PORT_R
        freq = 500.0 if label == 0 else 5000.0
        for _ in range(N_WRITE):
            apply_ilw_port_event(w, port, rng, seed_freq=freq)
    dt = float(w.config.dt)
    for _ in range(T_IDLE):
        tick(w, dt)
        w.t += dt
    sL, sR, nL, nR = side_strength(w)
    pred = 0 if sL > sR else 1
    written_ok = (nL >= 1 if label == 0 else nR >= 1) if not control else (nL + nR >= 1)
    return {
        "control": control,
        "label": label,
        "pred": pred,
        "correct": pred == label,
        "sL": sL, "sR": sR, "nL": nL, "nR": nR,
        "written_ok": written_ok,
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((211,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E1 start smoke={args.smoke} seeds={seeds} trials={trials}")
    treat, ctrl = [], []
    for s in seeds:
        for ti in range(trials):
            treat.append(run_trial(s, ti, False))
            ctrl.append(run_trial(s, ti, True))
    aT = float(sum(1 for r in treat if r["correct"]) / len(treat))
    aC = float(sum(1 for r in ctrl if r["correct"]) / len(ctrl))
    aW = float(sum(1 for r in treat if r["written_ok"]) / len(treat))
    b1, b2, b3 = aT >= 0.90, aC <= 0.60, aW >= 0.85
    verdict = "PASS" if (b1 and b2 and b3) else "NULL"
    result = {
        "id": "BP-E1",
        "bars": {
            "B1_treat": {"value": aT, "threshold": 0.90, "pass": b1},
            "B2_ctrl": {"value": aC, "threshold": 0.60, "pass": b2},
            "B3_written_side": {"value": aW, "threshold": 0.85, "pass": b3},
        },
        "sample_t": treat[:3],
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E1"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E1: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

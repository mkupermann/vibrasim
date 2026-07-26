"""BP-E163 multi-assoc c0→c1 last-write residual multislot OFF. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (4381, 4391), 8
N_TRAIN, N_WRITE, T_IDLE = 12, 12, 60
MID = 40.0
PORT_L = np.array([20., 25., 25.])
PORT_R = np.array([60., 25., 25.])
F_LO, F_HI = 500.0, 5000.0
F_MID = math.sqrt(F_LO * F_HI)

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0,
        ilw_multislot_enabled=False,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt

def write_L(w, rng, f, n=N_WRITE):
    for _ in range(n):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=float(f))
    idle(w, 3)

def write_dual(w, rng, fL, fR, n=N_WRITE):
    for _ in range(n):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=float(fL))
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=float(fR))
    idle(w, 3)

def side_means(w):
    sL = sR = 0.0; nL = nR = 0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        f = float(w.k_freq[i])
        if float(w.k_pos[i, 0]) < MID:
            sL += f; nL += 1
        else:
            sR += f; nR += 1
    return (sL / nL if nL else 0.0), (sR / nR if nR else 0.0), nL, nR

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((4381,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E163 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            # treatment: c0 then c1 then L-only at c1 L
            rng = np.random.default_rng(seed * 2203 + ti * 191)
            w = World(cfg(seed))
            for _ in range(N_TRAIN):
                write_dual(w, rng, F_LO, F_HI)
                idle(w, 6)
            for _ in range(N_TRAIN):
                write_dual(w, rng, F_HI, F_LO)
                idle(w, 6)
            write_L(w, rng, F_HI)
            idle(w, T_IDLE)
            mL, mR, nL, nR = side_means(w)
            b1s.append(nR >= 1 and mR < F_MID)
            b2s.append(nL >= 1 and mL >= F_MID)
            # control: c0 only then L-only at F_HI — R should not be low
            rng2 = np.random.default_rng(seed * 2203 + ti * 191 + 77)
            w2 = World(cfg(seed + 11))
            for _ in range(N_TRAIN):
                write_dual(w2, rng2, F_LO, F_HI)
                idle(w2, 6)
            write_L(w2, rng2, F_HI)
            idle(w2, T_IDLE)
            mL2, mR2, nL2, nR2 = side_means(w2)
            b3s.append(not (nR2 >= 1 and mR2 < F_MID))
    a1, a2, a3 = map(float, (np.mean(b1s), np.mean(b2s), np.mean(b3s)))
    p1, p2, p3 = a1 >= 0.80, a2 >= 0.90, a3 >= 0.80
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E163", "bars": {
        "B1_treat_R_low_c1": {"value": a1, "threshold": 0.80, "pass": p1},
        "B2_treat_L_high": {"value": a2, "threshold": 0.90, "pass": p2},
        "B3_ctrl_R_not_low": {"value": a3, "threshold": 0.80, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E163"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E163: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

"""BP-E168 write-order temporal gap residual L-first vs R-first. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (4481, 4491), 8
N_TRAIN, N_WRITE, T_IDLE, T_GAP = 15, 12, 60, 40
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

def write_port(w, rng, pos, f, n=N_WRITE):
    for _ in range(n):
        apply_ilw_port_event(w, pos, rng, seed_freq=float(f))
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

def run_arm(seed, ti, l_first):
    rng = np.random.default_rng(seed * 2701 + ti * 149 + int(l_first) * 17)
    w = World(cfg(seed + (0 if l_first else 5)))
    for _ in range(N_TRAIN):
        if l_first:
            write_port(w, rng, PORT_L, F_LO)
            idle(w, T_GAP)
            write_port(w, rng, PORT_R, F_HI)
        else:
            write_port(w, rng, PORT_R, F_HI)
            idle(w, T_GAP)
            write_port(w, rng, PORT_L, F_LO)
        idle(w, 8)
    write_port(w, rng, PORT_L, F_LO)
    idle(w, T_IDLE)
    mL, mR, nL, nR = side_means(w)
    return nR >= 1 and mR >= F_MID

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((4481,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E168 start smoke={args.smoke}", flush=True)
    a_hits, b_hits = [], []
    for seed in seeds:
        for ti in range(trials):
            a_hits.append(run_arm(seed, ti, True))
            b_hits.append(run_arm(seed, ti, False))
    a1 = float(np.mean(a_hits))
    a2 = float(np.mean(b_hits))
    a3 = abs(a1 - a2)
    p1, p2, p3 = a1 >= 0.80, a2 >= 0.80, a3 <= 0.25
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E168", "bars": {
        "B1_L_first_residual": {"value": a1, "threshold": 0.80, "pass": p1},
        "B2_R_first_residual": {"value": a2, "threshold": 0.80, "pass": p2},
        "B3_abs_delta": {"value": a3, "threshold": 0.25, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E168"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E168: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

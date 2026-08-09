"""BP-E175 fire selective residual pure dual ILW no pair-link. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (4641, 4651), 8
N_TRAIN, N_WRITE, T_PROP = 12, 12, 80
MID = 40.0
PORT_L = np.array([20., 25., 25.])
PORT_R = np.array([60., 25., 25.])
F_LO, F_HI = 500.0, 5000.0
F_MID = math.sqrt(F_LO * F_HI)
LOG_TOL = 0.35

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0,
        ilw_multislot_enabled=True,
        ilw_pair_link_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        bridge_charge_prop_rate=2., bridge_prop_min_strength=0.,
        charge_latch_enabled=True, charge_latch_tau=0.,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt

def write_dual(w, rng, fL, fR, n=N_WRITE):
    for _ in range(n):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=float(fL))
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=float(fR))
    idle(w, 4)

def train_both(w, rng):
    for _ in range(N_TRAIN):
        write_dual(w, rng, F_LO, F_HI)
        idle(w, 4)
    for _ in range(N_TRAIN):
        write_dual(w, rng, F_HI, F_LO)
        idle(w, 4)

def clear_state(w):
    w.k_charge[:] = 0
    if hasattr(w, "k_latch"):
        w.k_latch[:] = 0

def fire_L_band(w, f_target, n=T_PROP):
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    log_t = math.log(max(f_target, 1.0))
    for t in range(n):
        if t % 6 == 0:
            for i in range(w.k_count):
                if not w.k_alive[i] or int(w.k_level[i]) < 4:
                    continue
                if float(w.k_pos[i, 0]) >= MID:
                    continue
                lf = math.log(max(float(w.k_freq[i]), 1.0))
                if abs(lf - log_t) <= LOG_TOL:
                    w.k_charge[i] = thr + 5.
        tick(w, dt); w.t += dt

def peak_R_bands(w):
    hi = lo = 0.0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) < MID:
            continue
        lat = float(w.k_latch[i]) if hasattr(w, "k_latch") else float(w.k_charge[i])
        if float(w.k_freq[i]) >= F_MID:
            hi = max(hi, lat)
        else:
            lo = max(lo, lat)
    return hi, lo

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((4641,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E175 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 3501 + ti * 119)
            w = World(cfg(seed))
            train_both(w, rng)
            clear_state(w)
            fire_L_band(w, F_LO)
            hi_a, lo_a = peak_R_bands(w)
            ok_a = hi_a >= 1.0 and hi_a > lo_a
            b1s.append(ok_a)
            rng2 = np.random.default_rng(seed * 3501 + ti * 119 + 13)
            w2 = World(cfg(seed + 9))
            train_both(w2, rng2)
            clear_state(w2)
            fire_L_band(w2, F_HI)
            hi_b, lo_b = peak_R_bands(w2)
            ok_b = lo_b >= 1.0 and lo_b > hi_b
            b2s.append(ok_b)
            b3s.append(ok_a and ok_b)
    a1, a2, a3 = map(float, (np.mean(b1s), np.mean(b2s), np.mean(b3s)))
    p1, p2, p3 = a1 >= 0.80, a2 >= 0.80, a3 >= 0.70
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E175", "bars": {
        "B1_fire_Llo_Rhi": {"value": a1, "threshold": 0.80, "pass": p1},
        "B2_fire_Lhi_Rlo": {"value": a2, "threshold": 0.80, "pass": p2},
        "B3_both": {"value": a3, "threshold": 0.70, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E175"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E175: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

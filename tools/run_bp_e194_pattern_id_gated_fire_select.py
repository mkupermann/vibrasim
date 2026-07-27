"""BP-E194 pattern-id gated fire-select G12. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
from dataclasses import replace
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (5361, 5371), 8
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
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1.0, ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        bridge_charge_prop_rate=2., bridge_prop_min_strength=0.,
        charge_latch_enabled=True, charge_latch_tau=0.,
        firing_eligibility_gate=True,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt

def train_both(w, rng):
    for _ in range(N_TRAIN):
        for __ in range(N_WRITE):
            apply_ilw_pair_write(w, PORT_L, PORT_R, F_LO, F_HI, rng)
        idle(w, 4)
    for _ in range(N_TRAIN):
        for __ in range(N_WRITE):
            apply_ilw_pair_write(w, PORT_L, PORT_R, F_HI, F_LO, rng)
        idle(w, 4)

def tag_patterns(w):
    """Tag c0 (L-lo,R-hi)=1 and c1 (L-hi,R-lo)=2 by side and freq band."""
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        f = float(w.k_freq[i])
        x = float(w.k_pos[i, 0])
        if x < MID:
            w.k_pattern_id[i] = 1 if f < F_MID else 2
        else:
            w.k_pattern_id[i] = 1 if f >= F_MID else 2

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

def select_lo(w):
    hi, lo = peak_R_bands(w)
    return hi >= 1.0 and hi > lo

def select_hi(w):
    hi, lo = peak_R_bands(w)
    return lo >= 1.0 and lo > hi

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((5361,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E194 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 6901 + ti * 17)
            w = World(cfg(seed))
            train_both(w, rng)
            tag_patterns(w)
            # B1: pid 1 correct
            w.active_pattern_id = 1
            clear_state(w)
            fire_L_band(w, F_LO)
            b1s.append(select_lo(w))
            # B2: pid 2 correct
            w.active_pattern_id = 2
            clear_state(w)
            fire_L_band(w, F_HI)
            b2s.append(select_hi(w))
            # B3: wrong pattern — pid1 but fire L-hi should fail R-lo select
            w.active_pattern_id = 1
            clear_state(w)
            fire_L_band(w, F_HI)
            b3s.append(not select_hi(w))
    a1, a2, a3 = map(float, (np.mean(b1s), np.mean(b2s), np.mean(b3s)))
    p1, p2, p3 = a1 >= 0.80, a2 >= 0.80, a3 >= 0.70
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E194", "bars": {
        "B1_pid1_correct": {"value": a1, "threshold": 0.80, "pass": p1},
        "B2_pid2_correct": {"value": a2, "threshold": 0.80, "pass": p2},
        "B3_wrong_pattern_fail": {"value": a3, "threshold": 0.70, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E194"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E194: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

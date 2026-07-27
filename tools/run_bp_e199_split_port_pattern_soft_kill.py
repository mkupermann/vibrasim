"""BP-E199 split-port G12 soft-kill R1; pid1 survives. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (5521, 5531), 8
N_TRAIN, N_WRITE, T_PROP = 12, 12, 80
MID = 40.0
NEAR = 7.0
L0 = np.array([20., 15., 25.]); R0 = np.array([60., 15., 25.])
L1 = np.array([20., 35., 25.]); R1 = np.array([60., 35., 25.])
F_LO, F_HI = 500.0, 5000.0

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=6., ilw_delta_strength=0.5, atom_valence=0,
        ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1.0, ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        bridge_charge_prop_rate=2., bridge_prop_min_strength=0.,
        charge_latch_enabled=True, charge_latch_tau=0.,
        firing_eligibility_gate=True,
        fire_weaken_bridge_radius=10.0, fire_weaken_bridge_frac=1.0,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt

def train_both(w, rng):
    w.active_pattern_id = 1
    for _ in range(N_TRAIN):
        for __ in range(N_WRITE):
            apply_ilw_pair_write(w, L0, R0, F_LO, F_HI, rng)
        idle(w, 3)
    w.active_pattern_id = 2
    for _ in range(N_TRAIN):
        for __ in range(N_WRITE):
            apply_ilw_pair_write(w, L1, R1, F_HI, F_LO, rng)
        idle(w, 3)
    w.active_pattern_id = 0

def clear_state(w):
    w.k_charge[:] = 0
    if hasattr(w, "k_latch"):
        w.k_latch[:] = 0

def fire_near(w, pos, n=T_PROP):
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    for t in range(n):
        if t % 6 == 0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - pos)) <= NEAR:
                    w.k_charge[i] = thr + 5.
        tick(w, dt); w.t += dt

def peak_near(w, pos):
    m = 0.0
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - pos)) <= NEAR:
            lat = float(w.k_latch[i]) if hasattr(w, "k_latch") else float(w.k_charge[i])
            m = max(m, lat)
    return m

def select_c0(w):
    p0, p1 = peak_near(w, R0), peak_near(w, R1)
    return p0 >= 1.0 and p0 > p1

def select_c1(w):
    p0, p1 = peak_near(w, R0), peak_near(w, R1)
    return p1 >= 1.0 and p1 > p0

def soft_cut_at(w, pos):
    if hasattr(w, "k_weaken_bridge_emitter"):
        w.k_weaken_bridge_emitter[:] = 0
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - pos)) <= 6.0:
            w.k_weaken_bridge_emitter[i] = 1
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    for t in range(36):
        if t % 5 == 0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - pos)) <= 7:
                    w.k_charge[i] = thr + 5.
        tick(w, dt); w.t += dt
    if hasattr(w, "k_weaken_bridge_emitter"):
        w.k_weaken_bridge_emitter[:] = 0

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((5521,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E199 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 7701 + ti * 47)
            w = World(cfg(seed))
            train_both(w, rng)
            w.active_pattern_id = 2
            clear_state(w)
            fire_near(w, L1)
            b1s.append(select_c1(w))
            soft_cut_at(w, R1)
            idle(w, 10)
            clear_state(w)
            fire_near(w, L1)
            b2s.append(not select_c1(w))
            w.active_pattern_id = 1
            clear_state(w)
            fire_near(w, L0)
            b3s.append(select_c0(w))
    a1, a2, a3 = map(float, (np.mean(b1s), np.mean(b2s), np.mean(b3s)))
    p1, p2, p3 = a1 >= 0.90, a2 >= 0.70, a3 >= 0.80
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E199", "bars": {
        "B1_pre_pid2": {"value": a1, "threshold": 0.90, "pass": p1},
        "B2_post_soft_pid2_fail": {"value": a2, "threshold": 0.70, "pass": p2},
        "B3_pid1_survives": {"value": a3, "threshold": 0.80, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E199"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E199: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

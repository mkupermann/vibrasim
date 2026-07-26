"""BP-E183 triple-arm middle kill + restore multi-trial. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (4901, 4911), 8
N_TRAIN, N_WRITE, N_RES, T_PROP = 10, 10, 8, 80
MID = 40.0
NEAR = 7.0
ARMS = [
    (np.array([20., 10., 25.]), np.array([60., 10., 25.]), 300.0, 3000.0),
    (np.array([20., 25., 25.]), np.array([60., 25., 25.]), 1000.0, 10000.0),
    (np.array([20., 40., 25.]), np.array([60., 40., 25.]), 500.0, 5000.0),
]

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=5., ilw_delta_strength=0.5, atom_valence=0,
        ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1.0, ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        bridge_charge_prop_rate=2., bridge_prop_min_strength=0.,
        charge_latch_enabled=True, charge_latch_tau=0.,
        fire_kill_bridge_radius=10.0,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt

def train_all(w, rng):
    for L, R, fL, fR in ARMS:
        for _ in range(N_TRAIN):
            for __ in range(N_WRITE):
                apply_ilw_pair_write(w, L, R, fL, fR, rng)
            idle(w, 3)

def restore_c1(w, rng):
    L, R, fL, fR = ARMS[1]
    for _ in range(4):
        for __ in range(N_RES):
            apply_ilw_pair_write(w, L, R, fL, fR, rng)
        idle(w, 3)

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

def select_arm(w, idx):
    peaks = [peak_near(w, ARMS[j][1]) for j in range(3)]
    return peaks[idx] >= 1.0 and peaks[idx] == max(peaks) and peaks[idx] > sorted(peaks)[-2]

def hard_cut_at(w, pos):
    if hasattr(w, "k_kill_bridge_emitter"):
        w.k_kill_bridge_emitter[:] = 0
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - pos)) <= 6.0:
            w.k_kill_bridge_emitter[i] = 1
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    for t in range(36):
        if t % 5 == 0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - pos)) <= 7:
                    w.k_charge[i] = thr + 5.
        tick(w, dt); w.t += dt
    if hasattr(w, "k_kill_bridge_emitter"):
        w.k_kill_bridge_emitter[:] = 0

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((4901,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E183 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 4801 + ti * 61)
            w = World(cfg(seed))
            train_all(w, rng)
            hard_cut_at(w, ARMS[1][1])
            idle(w, 10)
            clear_state(w)
            fire_near(w, ARMS[0][0])
            b1s.append(select_arm(w, 0))
            restore_c1(w, rng)
            clear_state(w)
            fire_near(w, ARMS[1][0])
            b2s.append(select_arm(w, 1))
            clear_state(w)
            fire_near(w, ARMS[2][0])
            b3s.append(select_arm(w, 2))
    a1, a2, a3 = map(float, (np.mean(b1s), np.mean(b2s), np.mean(b3s)))
    p1, p2, p3 = a1 >= 0.80, a2 >= 0.80, a3 >= 0.80
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E183", "bars": {
        "B1_post_kill_c0": {"value": a1, "threshold": 0.80, "pass": p1},
        "B2_restore_c1": {"value": a2, "threshold": 0.80, "pass": p2},
        "B3_c2_after_restore": {"value": a3, "threshold": 0.80, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E183"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E183: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

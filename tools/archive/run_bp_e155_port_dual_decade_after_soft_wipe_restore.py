"""BP-E155 port dual decade specialisation soft wipe then ILW restore. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (4141, 4151), 8
N_WRITE, T_IDLE, N_RES = 20, 100, 12
MID = 40.0
PORT_L = np.array([20., 25., 25.])
PORT_R = np.array([60., 25., 25.])
F_LOW, F_HIGH = 400.0, 5000.0

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        fire_weaken_bridge_radius=10.0, fire_weaken_bridge_frac=1.0,
    )

def idle(w, n):
    dt=float(w.config.dt)
    for _ in range(n):
        tick(w,dt)

def write_dual(w, rng, n=N_WRITE):
    for _ in range(n):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=F_LOW)
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=F_HIGH)
    idle(w, 4)

def set_weaken_at(w, pos):
    if hasattr(w, "k_weaken_bridge_emitter"):
        w.k_weaken_bridge_emitter[:] = 0
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - pos)) <= 6.0:
            w.k_weaken_bridge_emitter[i] = 1

def disarm(w):
    if hasattr(w, "k_weaken_bridge_emitter"):
        w.k_weaken_bridge_emitter[:] = 0

def soft_cut_port(w, pos):
    set_weaken_at(w, pos)
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    for t in range(36):
        if t % 5 == 0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - pos)) <= 7:
                    w.k_charge[i] = thr + 5.
        tick(w, dt)
    disarm(w)

def ordered(w):
    L, R = [], []
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        d = int(math.floor(math.log10(max(float(w.k_freq[i]), 1.))))
        (L if float(w.k_pos[i, 0]) < MID else R).append(d)
    pop = len(L) >= 1 and len(R) >= 1
    return pop and float(np.mean(L)) < float(np.mean(R))

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((4141,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E155 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 1911 + ti * 137)
            w = World(cfg(seed))
            write_dual(w, rng)
            idle(w, T_IDLE)
            b1s.append(ordered(w))
            soft_cut_port(w, PORT_L)
            soft_cut_port(w, PORT_R)
            idle(w, 40)
            b2s.append(not ordered(w))  # post-wipe: ordered fails
            write_dual(w, rng, n=N_RES)
            idle(w, T_IDLE)
            b3s.append(ordered(w))
    a1, a2, a3 = map(float, (np.mean(b1s), np.mean(b2s), np.mean(b3s)))
    p1, p2, p3 = a1 >= 0.90, a2 >= 0.70, a3 >= 0.90
    # B2 threshold: post-wipe disruption rate ≥0.70 (ordered fails often enough)
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E155", "bars": {
        "B1_initial_ordered": {"value": a1, "threshold": 0.90, "pass": p1},
        "B2_post_wipe_disrupted": {"value": a2, "threshold": 0.70, "pass": p2},
        "B3_restore_ordered": {"value": a3, "threshold": 0.90, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E155"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E155: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

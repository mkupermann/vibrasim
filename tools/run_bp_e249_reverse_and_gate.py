"""BP-E249 reverse coincidence-AND gated R→G→L. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (7441, 7451), 6
N_WRITE, T_PROP = 10, 80
NEAR = 7.0
R = np.array([65., 25., 25.])
G = np.array([40., 25., 25.])
L = np.array([15., 25., 25.])

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=5., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1.0, ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        bridge_charge_prop_rate=2.5, bridge_prop_min_strength=0.5,
        charge_latch_enabled=True, charge_latch_tau=0.,
        coincidence_and_enabled=True,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt

def link(w, rng, a, b, fa, fb, n=N_WRITE):
    for _ in range(n):
        apply_ilw_pair_write(w, a, b, fa, fb, rng)
    idle(w, 5)

def train(w, rng):
    link(w, rng, R, G, 400., 1000.)
    link(w, rng, G, L, 1000., 2500.)
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, G, rng, seed_freq=9000.)
    idle(w, 4)
    if hasattr(w, "k_coincidence_gate"):
        for i in range(w.k_count):
            if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - G)) <= 6:
                w.k_coincidence_gate[i] = 1

def clear_state(w):
    w.k_charge[:] = 0
    if hasattr(w, "k_latch"):
        w.k_latch[:] = 0

def fire_targets(w, targets, n=T_PROP):
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    for t in range(n):
        if t % 5 == 0:
            for target in targets:
                for i in range(w.k_count):
                    if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - target)) <= NEAR:
                        w.k_charge[i] = thr + 5.
        tick(w, dt); w.t += dt

def peak_L(w):
    m = 0.0
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(np.linalg.norm(w.k_pos[i] - L)) <= NEAR:
            lat = float(w.k_latch[i]) if hasattr(w, "k_latch") else float(w.k_charge[i])
            m = max(m, lat)
    return m

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((7441,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E249 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 20401 + ti * 241)
            w = World(cfg(seed))
            train(w, rng)
            clear_state(w)
            fire_targets(w, [R])
            b1s.append(peak_L(w) < 1.0)
            clear_state(w)
            fire_targets(w, [R, G])
            b2s.append(peak_L(w) >= 1.0)
            clear_state(w)
            fire_targets(w, [G])
            b3s.append(peak_L(w) < 1.0)
    b1 = float(np.mean(b1s)); b2 = float(np.mean(b2s)); b3 = float(np.mean(b3s))
    p1, p2, p3 = b1 >= 0.70, b2 >= 0.80, b3 >= 0.70
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E249", "bars": {
        "B1_r_only_fail": {"value": b1, "threshold": 0.70, "pass": p1},
        "B2_r_and_g_ok": {"value": b2, "threshold": 0.80, "pass": p2},
        "B3_g_only_fail": {"value": b3, "threshold": 0.70, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E249"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E249: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

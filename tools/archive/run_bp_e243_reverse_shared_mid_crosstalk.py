"""BP-E243 reverse shared-mid crosstalk vs separate mids. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (7321, 7331), 6
N_WRITE, T_PROP = 12, 100
NEAR = 8.0
L1 = np.array([12., 20., 25.]); L2 = np.array([12., 35., 25.])
R1 = np.array([68., 20., 25.]); R2 = np.array([68., 35., 25.])
M = np.array([40., 25., 25.])
M1 = np.array([40., 20., 25.]); M2 = np.array([40., 35., 25.])

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=6., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1.0, ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        bridge_charge_prop_rate=2.5, bridge_prop_min_strength=0.,
        charge_latch_enabled=True, charge_latch_tau=0.,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt

def link(w, rng, a, b, fa, fb, n=N_WRITE):
    for _ in range(n):
        apply_ilw_pair_write(w, a, b, fa, fb, rng)
    idle(w, 6)

def train_separate(w, rng):
    link(w, rng, L1, M1, 400., 1500.); link(w, rng, M1, R1, 1500., 5000.)
    link(w, rng, L2, M2, 800., 1500.); link(w, rng, M2, R2, 1500., 7000.)

def train_shared(w, rng):
    link(w, rng, L1, M, 400., 1500.); link(w, rng, M, R1, 1500., 5000.)
    link(w, rng, L2, M, 800., 1500.); link(w, rng, M, R2, 1500., 7000.)

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

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((7321,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E243 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 19201 + ti * 211)
            # separate: selective reverse
            w = World(cfg(seed))
            train_separate(w, rng)
            clear_state(w)
            fire_near(w, R1)
            b1s.append(peak_near(w, L1) >= 1.0 and peak_near(w, L2) < 1.0)
            # shared: L1 hits + L2 leak
            w2 = World(cfg(seed + 5))
            rng2 = np.random.default_rng(seed * 19201 + ti * 211 + 7)
            train_shared(w2, rng2)
            clear_state(w2)
            fire_near(w2, R1)
            b2s.append(peak_near(w2, L1) >= 1.0)
            b3s.append(peak_near(w2, L2) >= 1.0)
    b1 = float(np.mean(b1s)); b2 = float(np.mean(b2s)); b3 = float(np.mean(b3s))
    p1, p2, p3 = b1 >= 0.80, b2 >= 0.80, b3 >= 0.70
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E243", "bars": {
        "B1_separate_selective": {"value": b1, "threshold": 0.80, "pass": p1},
        "B2_shared_l1": {"value": b2, "threshold": 0.80, "pass": p2},
        "B3_shared_l2_leak": {"value": b3, "threshold": 0.70, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E243"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E243: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

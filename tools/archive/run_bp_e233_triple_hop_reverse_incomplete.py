"""BP-E233 triple-hop reverse incomplete (omit A-R hops). Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (7001, 7011), 6
N_TRAIN, N_WRITE, T_PROP = 10, 10, 120
NEAR = 7.0
L0 = np.array([12., 15., 25.]); M0 = np.array([28., 15., 25.]); A0 = np.array([44., 15., 25.]); R0 = np.array([60., 15., 25.])
L1 = np.array([12., 35., 25.]); M1 = np.array([28., 35., 25.]); A1 = np.array([44., 35., 25.]); R1 = np.array([60., 35., 25.])
F0 = (300.0, 800.0, 2000.0, 6000.0)
F1 = (6000.0, 2500.0, 900.0, 350.0)

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=5., ilw_delta_strength=0.5, atom_valence=0,
        ilw_multislot_enabled=True,
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
    idle(w, 3)

def train_incomplete(w, rng):
    # L-M and M-A only; no A-R
    for _ in range(N_TRAIN):
        link(w, rng, L0, M0, F0[0], F0[1])
        link(w, rng, M0, A0, F0[1], F0[2])
        link(w, rng, L1, M1, F1[0], F1[1])
        link(w, rng, M1, A1, F1[1], F1[2])
        idle(w, 4)

def train_full(w, rng):
    for _ in range(N_TRAIN):
        link(w, rng, L0, M0, F0[0], F0[1])
        link(w, rng, M0, A0, F0[1], F0[2])
        link(w, rng, A0, R0, F0[2], F0[3])
        link(w, rng, L1, M1, F1[0], F1[1])
        link(w, rng, M1, A1, F1[1], F1[2])
        link(w, rng, A1, R1, F1[2], F1[3])
        idle(w, 4)

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

def reverse_p0(w):
    p0, p1 = peak_near(w, L0), peak_near(w, L1)
    return p0 >= 1.0 and p0 > p1

def reverse_p1(w):
    p0, p1 = peak_near(w, L0), peak_near(w, L1)
    return p1 >= 1.0 and p1 > p0

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((7001,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E233 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 16001 + ti * 157)
            w = World(cfg(seed))
            train_incomplete(w, rng)
            clear_state(w)
            fire_near(w, R0)
            b1s.append(not reverse_p0(w))
            clear_state(w)
            fire_near(w, R1)
            b2s.append(not reverse_p1(w))
            w2 = World(cfg(seed + 19))
            rng2 = np.random.default_rng(seed * 16001 + ti * 157 + 9)
            train_full(w2, rng2)
            clear_state(w2)
            fire_near(w2, R0)
            b3s.append(reverse_p0(w2))
    b1 = float(np.mean(b1s)); b2 = float(np.mean(b2s)); b3 = float(np.mean(b3s))
    p1, p2, p3 = b1 >= 0.70, b2 >= 0.70, b3 >= 0.80
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E233", "bars": {
        "B1_incomplete_r0_fail": {"value": b1, "threshold": 0.70, "pass": p1},
        "B2_incomplete_r1_fail": {"value": b2, "threshold": 0.70, "pass": p2},
        "B3_full_r0_ok": {"value": b3, "threshold": 0.80, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E233"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E233: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

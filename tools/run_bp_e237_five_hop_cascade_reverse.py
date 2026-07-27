"""BP-E237 five-hop cascade reverse dual fire-select. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (7161, 7171), 6
N_TRAIN, N_WRITE, T_PROP = 10, 10, 160
NEAR = 7.0
# six ports each (5 hops); x spacing ~11.5 to fit box 80
P0 = [np.array([8. + i * 11.5, 15., 25.]) for i in range(6)]
P1 = [np.array([8. + i * 11.5, 35., 25.]) for i in range(6)]
F0 = (250.0, 500.0, 1000.0, 2000.0, 4000.0, 9000.0)
F1 = (9000.0, 4000.0, 2000.0, 1000.0, 500.0, 250.0)

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
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

def train_both(w, rng):
    for _ in range(N_TRAIN):
        for i in range(5):
            link(w, rng, P0[i], P0[i + 1], F0[i], F0[i + 1])
            link(w, rng, P1[i], P1[i + 1], F1[i], F1[i + 1])
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
    p0, p1 = peak_near(w, P0[0]), peak_near(w, P1[0])
    return p0 >= 1.0 and p0 > p1

def reverse_p1(w):
    p0, p1 = peak_near(w, P0[0]), peak_near(w, P1[0])
    return p1 >= 1.0 and p1 > p0

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((7161,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E237 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 17601 + ti * 179)
            w = World(cfg(seed))
            train_both(w, rng)
            clear_state(w)
            fire_near(w, P0[5])
            ok0 = reverse_p0(w)
            b1s.append(ok0)
            clear_state(w)
            fire_near(w, P1[5])
            ok1 = reverse_p1(w)
            b2s.append(ok1)
            b3s.append(ok0 and ok1)
    b1 = float(np.mean(b1s)); b2 = float(np.mean(b2s)); b3 = float(np.mean(b3s))
    p1, p2, p3 = b1 >= 0.80, b2 >= 0.80, b3 >= 0.70
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E237", "bars": {
        "B1_rev_p0": {"value": b1, "threshold": 0.80, "pass": p1},
        "B2_rev_p1": {"value": b2, "threshold": 0.80, "pass": p2},
        "B3_both": {"value": b3, "threshold": 0.70, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E237"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E237: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

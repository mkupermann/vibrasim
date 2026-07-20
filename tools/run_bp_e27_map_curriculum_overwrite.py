"""BP-E27 curriculum map overwrite last-map-wins. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (871, 881), 10
N_WRITE, T_PROP, T_END, MID = 8, 40, 30, 40.0
MAP_A = ((400.0, 7000.0), (1500.0, 2500.0))
MAP_B = ((400.0, 2500.0), (1500.0, 7000.0))
Y_SLOTS = (13.0, 37.0)

def make_cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_multislot_rel_freq=0.35, ilw_pair_link_enabled=True, ilw_pair_link_delta=1.0,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=0., charge_latch_enabled=True, charge_latch_tau=0.,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n): tick(w, dt)

def ports(y):
    return np.array([20., y, 25.]), np.array([60., y, 25.])

def train_map(w, rng, pairs):
    for c, (fL, fR) in enumerate(pairs):
        for y in Y_SLOTS:
            pl, pr = ports(y)
            for _ in range(N_WRITE):
                apply_ilw_pair_write(w, pl, pr, fL, fR, rng)
            idle(w, 6)

def bridged_L(w):
    out = set()
    for b in range(w.b_count):
        if not w.b_alive[b]: continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]: continue
        xi, xj = float(w.k_pos[i,0]), float(w.k_pos[j,0])
        if (xi < MID) == (xj < MID): continue
        if xi < MID: out.add(i)
        if xj < MID: out.add(j)
    return list(out)

def true_partner(fL, pairs):
    # nearest L centroid
    best, bd = pairs[0][1], 1e18
    for a, b in pairs:
        d = abs(fL - a)
        if d < bd: bd, best = d, b
    return best

def other_R(true_r, pairs):
    rs = [p[1] for p in pairs]
    return rs[0] if abs(true_r - rs[1]) < abs(true_r - rs[0]) else rs[1]

def latch_partner(w, Li):
    thr = float(w.config.theta_fire); dt = float(w.config.dt)
    w.k_charge[:w.k_count] = 0.; w.k_latch[:w.k_count] = 0.
    for t in range(T_PROP):
        if t % 10 == 0 and w.k_alive[Li]:
            w.k_charge[Li] = thr + 5.
        tick(w, dt)
    idle(w, T_END)
    best_i, best_v = -1, -1.
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4 or float(w.k_pos[i,0]) < MID: continue
        v = float(w.k_latch[i])
        if v > best_v: best_v, best_i = v, i
    return float(w.k_freq[best_i]) if best_i >= 0 and best_v > 0 else 0.

def match_rate(w, pairs):
    Ls = bridged_L(w)
    if not Ls: return 0., False
    ok = 0; n = 0
    for Li in Ls:
        fL = float(w.k_freq[Li])
        pred = latch_partner(w, Li)
        if pred <= 0: continue
        n += 1
        true = true_partner(fL, pairs)
        oth = [p[1] for p in pairs if abs(p[1]-true) > 1]
        oth = oth[0] if oth else true
        ok += int(abs(pred - true) < abs(pred - oth))
    return (ok / n if n else 0.), True

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((871,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E27 start smoke={args.smoke}")
    b1s, b2s, b3s, b4s = [], [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 45097 + ti * 191)
            # A then B
            w = World(make_cfg(seed))
            train_map(w, rng, MAP_A)
            train_map(w, rng, MAP_B)
            rB, has = match_rate(w, MAP_B)
            rA, _ = match_rate(w, MAP_A)
            b1s.append(rB); b2s.append(rA); b4s.append(has and len(bridged_L(w)) >= 1)
            # A only
            w2 = World(make_cfg(seed))
            train_map(w2, rng, MAP_A)
            rAonly, _ = match_rate(w2, MAP_A)
            b3s.append(rAonly)
    a1, a2, a3, a4 = map(float, (np.mean(b1s), np.mean(b2s), np.mean(b3s), np.mean(b4s)))
    p1, p2, p3, p4 = a1 >= 0.85, a2 <= 0.25, a3 >= 0.85, a4 >= 0.90
    verdict = "PASS" if all([p1, p2, p3, p4]) else "NULL"
    result = {"id": "BP-E27", "bars": {
        "B1_match_B": {"value": a1, "threshold": 0.85, "pass": p1},
        "B2_residual_A": {"value": a2, "threshold": 0.25, "pass": p2},
        "B3_A_only": {"value": a3, "threshold": 0.85, "pass": p3},
        "B4_bridged": {"value": a4, "threshold": 0.90, "pass": p4},
    }, "verdict": verdict}
    out = Path.home()/".eqmod"/"bet"/"BP-E27"; out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E27: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

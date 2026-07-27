"""BP-E252 multi-trial map curriculum A→B with strength decay, replace OFF. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (7561, 7571), 8
N_WRITE, T_PROP, T_END, MID = 8, 40, 30, 40.0
MAP_A = ((400.0, 7000.0), (1500.0, 2500.0))
MAP_B = ((400.0, 2500.0), (1500.0, 7000.0))
Y_SLOTS = (13.0, 37.0)
TAU = 30.0

def make_cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0,
        ilw_multislot_enabled=True, ilw_multislot_rel_freq=0.35,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1.0, ilw_pair_replace_enabled=False,
        ilw_strength_decay_tau=float(TAU),
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        bridge_charge_prop_rate=2., bridge_prop_min_strength=0.,
        charge_latch_enabled=True, charge_latch_tau=0.,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt

def ports(y):
    return np.array([20., y, 25.]), np.array([60., y, 25.])

def train_map(w, rng, pairs):
    for fL, fR in pairs:
        for y in Y_SLOTS:
            pl, pr = ports(y)
            for _ in range(N_WRITE):
                apply_ilw_pair_write(w, pl, pr, fL, fR, rng)
            idle(w, 6)

def bridged_L(w):
    out = set()
    for b in range(w.b_count):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        xi, xj = float(w.k_pos[i, 0]), float(w.k_pos[j, 0])
        if (xi < MID) == (xj < MID):
            continue
        if xi < MID:
            out.add(i)
        if xj < MID:
            out.add(j)
    return list(out)

def true_partner(fL, pairs):
    best, bd = pairs[0][1], 1e18
    for a, b in pairs:
        d = abs(fL - a)
        if d < bd:
            bd, best = d, b
    return best

def latch_partner(w, Li):
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    w.k_charge[:w.k_count] = 0.
    w.k_latch[:w.k_count] = 0.
    for t in range(T_PROP):
        if t % 10 == 0 and w.k_alive[Li]:
            w.k_charge[Li] = thr + 5.
        tick(w, dt)
    idle(w, T_END)
    best_i, best_v = -1, -1.
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4 or float(w.k_pos[i, 0]) < MID:
            continue
        v = float(w.k_latch[i])
        if v > best_v:
            best_v, best_i = v, i
    return float(w.k_freq[best_i]) if best_i >= 0 and best_v > 0 else 0.

def match_rate(w, pairs):
    Ls = bridged_L(w)
    if not Ls:
        return 0., False
    ok = n = 0
    for Li in Ls:
        fL = float(w.k_freq[Li])
        pred = latch_partner(w, Li)
        if pred <= 0:
            continue
        n += 1
        true = true_partner(fL, pairs)
        oth = [p[1] for p in pairs if abs(p[1] - true) > 1][0]
        ok += int(abs(pred - true) < abs(pred - oth))
    return (ok / n if n else 0.), True

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((7561,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E252 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 21601 + ti * 263)
            w = World(make_cfg(seed))
            train_map(w, rng, MAP_A)
            idle(w, 40)  # allow strength decay on A
            train_map(w, rng, MAP_B)
            rB, _ = match_rate(w, MAP_B)
            rA, _ = match_rate(w, MAP_A)
            b1s.append(rB)
            b2s.append(rA)
            w2 = World(make_cfg(seed + 3))
            rng2 = np.random.default_rng(seed * 21601 + ti * 263 + 5)
            train_map(w2, rng2, MAP_A)
            rAo, _ = match_rate(w2, MAP_A)
            b3s.append(rAo)
    b1 = float(np.mean(b1s)); b2 = float(np.mean(b2s)); b3 = float(np.mean(b3s))
    p1, p2, p3 = b1 >= 0.85, b2 <= 0.25, b3 >= 0.85
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E252", "bars": {
        "B1_match_B": {"value": b1, "threshold": 0.85, "pass": p1},
        "B2_residual_A": {"value": b2, "threshold": 0.25, "pass": p2},
        "B3_A_only": {"value": b3, "threshold": 0.85, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E252"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E252: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

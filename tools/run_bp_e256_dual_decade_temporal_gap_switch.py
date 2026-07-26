"""BP-E256 dual decade multi-trial co-residence after temporal gap. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (7721, 7731), 6
N_TRAIN, N_WRITE, T_PROP, T_GAP = 10, 10, 60, 200
MID = 40.0
PORT_L = np.array([20., 25., 25.])
PORT_R = np.array([60., 25., 25.])
PA = (400.0, 7000.0)
PB = (1500.0, 2500.0)

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0,
        ilw_multislot_enabled=True, ilw_multislot_rel_freq=0.35,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1.0, ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        bridge_charge_prop_rate=2.0, bridge_prop_min_strength=0.,
        charge_latch_enabled=True, charge_latch_tau=0.,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt

def train_pair(w, rng, fL, fR):
    for _ in range(N_TRAIN):
        for __ in range(N_WRITE):
            apply_ilw_pair_write(w, PORT_L, PORT_R, fL, fR, rng)
        idle(w, 6)

def clear_state(w):
    w.k_charge[:] = 0
    if hasattr(w, "k_latch"):
        w.k_latch[:] = 0

def bridged_L_near(w, fL_target):
    """Pick L atom closest in freq to fL_target among cross-mid bridged L."""
    best_i, best_d = -1, 1e18
    for b in range(w.b_count):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        for a in (i, j):
            if float(w.k_pos[a, 0]) >= MID:
                continue
            d = abs(float(w.k_freq[a]) - fL_target)
            if d < best_d:
                best_d, best_i = d, a
    return best_i

def peak_partner_R(w, Li):
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    clear_state(w)
    for t in range(T_PROP):
        if t % 8 == 0 and Li >= 0 and w.k_alive[Li]:
            w.k_charge[Li] = thr + 5.
        tick(w, dt)
    best_i, best_v = -1, -1.
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4 or float(w.k_pos[i, 0]) < MID:
            continue
        v = float(w.k_latch[i]) if hasattr(w, "k_latch") else float(w.k_charge[i])
        if v > best_v:
            best_v, best_i = v, i
    if best_i < 0 or best_v < 1.0:
        return 0.0
    return float(w.k_freq[best_i])

def selective_A(pred):
    # closer to 7000 than 2500
    return pred > 0 and abs(pred - 7000.0) < abs(pred - 2500.0)

def selective_B(pred):
    return pred > 0 and abs(pred - 2500.0) < abs(pred - 7000.0)

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials, t_gap = ((7721,), 2, 40) if args.smoke else (SEEDS, TRIALS, T_GAP)
    print(f"BP-E256 start smoke={args.smoke}", flush=True)
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 23201 + ti * 293)
            w = World(cfg(seed))
            train_pair(w, rng, PA[0], PA[1])
            idle(w, t_gap)
            train_pair(w, rng, PB[0], PB[1])
            LiA = bridged_L_near(w, PA[0])
            predA = peak_partner_R(w, LiA)
            okA = selective_A(predA)
            LiB = bridged_L_near(w, PB[0])
            predB = peak_partner_R(w, LiB)
            okB = selective_B(predB)
            b1s.append(okA)
            b2s.append(okB)
            b3s.append(okA and okB)
    b1 = float(np.mean(b1s)); b2 = float(np.mean(b2s)); b3 = float(np.mean(b3s))
    p1, p2, p3 = b1 >= 0.80, b2 >= 0.80, b3 >= 0.70
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E256", "bars": {
        "B1_A_selective": {"value": b1, "threshold": 0.80, "pass": p1},
        "B2_B_selective": {"value": b2, "threshold": 0.80, "pass": p2},
        "B3_both": {"value": b3, "threshold": 0.70, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E256"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E256: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

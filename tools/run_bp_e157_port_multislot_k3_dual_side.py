"""BP-E157 port multislot K=3 dual-side band occupancy. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (4181, 4191), 8
N_WRITE, T_IDLE = 8, 80
MID = 40.0
PORT_L = np.array([20., 25., 25.])
PORT_R = np.array([60., 25., 25.])
L_BANDS = (400.0, 1500.0, 5000.0)
R_BANDS = (600.0, 2000.0, 7000.0)

def cfg(seed, multislot):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0,
        ilw_multislot_enabled=bool(multislot),
    )

def idle(w, n):
    dt=float(w.config.dt)
    for _ in range(n):
        tick(w,dt)

def write_all(w, rng):
    for f in L_BANDS:
        for _ in range(N_WRITE):
            apply_ilw_port_event(w, PORT_L, rng, seed_freq=float(f))
        idle(w, 3)
    for f in R_BANDS:
        for _ in range(N_WRITE):
            apply_ilw_port_event(w, PORT_R, rng, seed_freq=float(f))
        idle(w, 3)

def bin_occupied(freqs, centroids, tol_frac=0.35):
    """True if each centroid has at least one freq within relative window."""
    occupied = [False] * len(centroids)
    for f in freqs:
        i = int(np.argmin([abs(math.log(max(f,1e-9)/c)) for c in centroids]))
        c = centroids[i]
        if abs(f - c) / c <= tol_frac or abs(math.log(max(f,1)/c)) < 0.5:
            occupied[i] = True
    return all(occupied)

def sides_freqs(w):
    L, R = [], []
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        f = float(w.k_freq[i])
        (L if float(w.k_pos[i, 0]) < MID else R).append(f)
    return L, R

def all_six(w):
    L, R = sides_freqs(w)
    pop = len(L) >= 1 and len(R) >= 1
    if not pop:
        return False, False
    ok = bin_occupied(L, L_BANDS) and bin_occupied(R, R_BANDS)
    return pop, ok

def run_one(seed, ti, multislot):
    w = World(cfg(seed, multislot))
    rng = np.random.default_rng(seed * 1931 + ti * 149 + int(multislot) * 11)
    write_all(w, rng)
    idle(w, T_IDLE)
    return all_six(w)

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((4181,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E157 start smoke={args.smoke}", flush=True)
    on, off = [], []
    for s in seeds:
        for ti in range(trials):
            on.append(run_one(s, ti, True))
            off.append(run_one(s, ti, False))
    b1 = float(np.mean([1 if r[1] else 0 for r in on]))
    b2 = float(np.mean([1 if r[1] else 0 for r in off]))
    b3 = float(np.mean([1 if r[0] else 0 for r in on]))
    p1, p2, p3 = b1 >= 0.80, b2 <= 0.20, b3 >= 0.90
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {"id": "BP-E157", "bars": {
        "B1_treat_all_six": {"value": b1, "threshold": 0.80, "pass": p1},
        "B2_ctrl_all_six": {"value": b2, "threshold": 0.20, "pass": p2},
        "B3_treat_pop": {"value": b3, "threshold": 0.90, "pass": p3},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E157"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E157: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

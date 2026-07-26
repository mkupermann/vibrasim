"""BP-E154 port dual-side ordered decade specialisation via ILW only. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (4121, 4131), 8
N_WRITE, T_IDLE = 20, 150
MID = 40.0
PORT_L = np.array([20., 25., 25.])
PORT_R = np.array([60., 25., 25.])
# treatment bands; control uses SAME full for both
F_LOW, F_HIGH = 400.0, 5000.0
F_MID = float(np.sqrt(F_LOW * F_HIGH))

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
    )

def idle(w, n):
    dt=float(w.config.dt)
    for _ in range(n):
        tick(w,dt)

def write_side(w, rng, port, f):
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, port, rng, seed_freq=float(f))
    idle(w, 4)

def sides_decade(w):
    L, R = [], []
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        d = int(math.floor(math.log10(max(float(w.k_freq[i]), 1.))))
        (L if float(w.k_pos[i, 0]) < MID else R).append(d)
    pop = len(L) >= 1 and len(R) >= 1
    ordered = pop and float(np.mean(L)) < float(np.mean(R))
    return pop, ordered

def run_one(seed, ti, treatment):
    w = World(cfg(seed))
    rng = np.random.default_rng(seed * 1901 + ti * 131 + int(treatment) * 17)
    if treatment:
        write_side(w, rng, PORT_L, F_LOW)
        write_side(w, rng, PORT_R, F_HIGH)
    else:
        # same-band control: both sides mid-band
        write_side(w, rng, PORT_L, F_MID)
        write_side(w, rng, PORT_R, F_MID)
    idle(w, T_IDLE)
    return sides_decade(w)

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((4121,), 2) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E154 start smoke={args.smoke}", flush=True)
    on, off = [], []
    for s in seeds:
        for ti in range(trials):
            on.append(run_one(s, ti, True))
            off.append(run_one(s, ti, False))
    b1 = float(np.mean([1 if r[1] else 0 for r in on]))
    b2 = float(np.mean([1 if r[1] else 0 for r in off]))
    b3 = float(np.mean([1 if r[0] else 0 for r in on]))
    b4 = b1 - b2
    p1, p2, p3, p4 = b1 >= 0.90, b2 <= 0.40, b3 >= 0.90, b4 >= 0.40
    verdict = "PASS" if all([p1, p2, p3, p4]) else "NULL"
    result = {"id": "BP-E154", "bars": {
        "B1_treat_ordered": {"value": b1, "threshold": 0.90, "pass": p1},
        "B2_ctrl_ordered": {"value": b2, "threshold": 0.40, "pass": p2},
        "B3_treat_pop": {"value": b3, "threshold": 0.90, "pass": p3},
        "B4_delta": {"value": b4, "threshold": 0.40, "pass": p4},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E154"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E154: {verdict}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

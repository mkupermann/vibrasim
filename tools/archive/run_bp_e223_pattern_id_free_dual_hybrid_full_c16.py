"""BP-E223 G12+C16 free dual hybrid full C16 budget. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick
from world.state import World

N_SIDE, T_FULL = 400, 1200
SEEDS, TRIALS = (6551, 6561, 6571), 3
MID = 40.0
LOW, HIGH = (100.0, 2000.0), (500.0, 10000.0)
TAU = 30.0

def cfg(seed, gate):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=8192, n_nodes_max=4096,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03,
        pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=5., speed_max=25.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_strength_decay_tau=TAU,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        firing_eligibility_gate=bool(gate),
    )

def inject(w, rng, n, x0, x1, f0, f1):
    dead = np.where(~w.s_alive)[0]
    slots = dead[:n] if len(dead) >= n else np.arange(int(w.n_alive), min(int(w.n_alive) + n, w.config.n_vibrations_max))
    for k, i in enumerate(slots):
        i = int(i)
        w.s_pos[i] = [rng.uniform(x0, x1), rng.uniform(8, 42), rng.uniform(8, 42)]
        w.s_freq[i] = float(np.exp(rng.uniform(np.log(f0), np.log(f1))))
        w.s_pol[i] = k % 2 == 0
        z, phi = rng.uniform(-1, 1), rng.uniform(0, 2 * np.pi)
        sq = float(np.sqrt(max(1 - z * z, 0)))
        sp = float(rng.uniform(5, 25))
        w.s_vel[i] = sp * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        w.s_alive[i] = True
    w.n_alive = int(w.s_alive.sum())

def evolve(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt); w.t += dt

def sides(w):
    L, R = [], []
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        d = int(math.floor(math.log10(max(float(w.k_freq[i]), 1.))))
        (L if float(w.k_pos[i, 0]) < MID else R).append(d)
    pop = len(L) >= 1 and len(R) >= 1
    ok = pop and float(np.mean(L)) < float(np.mean(R))
    return pop, ok

def run_one(seed, ti, gate, t_total):
    w = World(cfg(seed, gate))
    rng = np.random.default_rng(seed * 12701 + ti * 181 + int(gate) * 283)
    inject(w, rng, N_SIDE, 8, 32, LOW[0], LOW[1])
    inject(w, rng, N_SIDE, 48, 72, HIGH[0], HIGH[1])
    evolve(w, t_total)
    return sides(w)

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials, t_tot = ((6551,), 1, 300) if args.smoke else (SEEDS, TRIALS, T_FULL)
    print(f"BP-E223 start smoke={args.smoke} seeds={len(seeds)} trials={trials} T={t_tot}", flush=True)
    on, off = [], []
    for s in seeds:
        for ti in range(trials):
            print(f"  run seed={s} ti={ti} gate=ON", flush=True)
            on.append(run_one(s, ti, True, t_tot))
            print(f"  run seed={s} ti={ti} gate=OFF", flush=True)
            off.append(run_one(s, ti, False, t_tot))
    b1 = float(np.mean([1 if r[1] else 0 for r in on]))
    b2 = float(np.mean([1 if r[1] else 0 for r in off]))
    b3 = float(np.mean([1 if r[0] else 0 for r in on]))
    b4 = abs(b1 - b2)
    p1, p2, p3, p4 = b1 >= 0.90, b2 >= 0.90, b3 >= 0.80, b4 <= 0.20
    verdict = "PASS" if all([p1, p2, p3, p4]) else "NULL"
    result = {"id": "BP-E223", "bars": {
        "B1_treat_gate_spec": {"value": b1, "threshold": 0.90, "pass": p1},
        "B2_ctrl_nogate_spec": {"value": b2, "threshold": 0.90, "pass": p2},
        "B3_treat_pop": {"value": b3, "threshold": 0.80, "pass": p3},
        "B4_abs_delta": {"value": b4, "threshold": 0.20, "pass": p4},
    }, "n_runs": len(on), "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-E223"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}", flush=True)
    print(f"--- VERDICT ---\nBP-E223: {verdict} n_runs={len(on)}\nwrote {path}\nDONE", flush=True)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

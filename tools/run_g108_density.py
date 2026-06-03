"""G108 — dose-response: does injection DENSITY decide propagate-vs-freeze? Direct test of G107.
Launch n moving vibrations into clear space, sweep n, measure far-region energy and atoms formed at the
source. Low n should propagate (far energy high, few atoms); high n should bind at source (far energy ~0,
atoms formed). Bars pre-registered in docs/amendments/g108_density_transport.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
TRIALS = 40
X0 = 4.0
VX = 6.0
PROP = 6
FARX = 18.0
NS = [2, 6, 14, 28]


def clear_atoms(w):
    if w.k_count:
        w.k_alive[:w.k_count] = False


def inject_moving(w, cfg, box, x0, n, vx, sigma=0.8):
    rng = w.rng
    free = np.where(~w.s_alive[:cfg.n_vibrations_max])[0]
    k = min(n, len(free))
    if k == 0:
        return
    sl = free[:k]
    w.s_pos[sl] = np.column_stack([
        rng.normal(x0, sigma, k) % box[0],
        rng.normal(box[1] / 2, sigma, k) % box[1],
        rng.normal(box[2] / 2, sigma, k) % box[2]])
    w.s_vel[sl] = np.tile([vx, 0.0, 0.0], (k, 1))
    w.s_freq[sl] = w._sample_frequencies(k)
    w.s_pol[sl] = rng.random(k) < 0.5
    w.s_alive[sl] = True
    w.n_alive = max(w.n_alive, int(sl.max()) + 1)


def far_energy(w, box, xmin):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    return float((alive & (w.s_pos[:n, 0] > xmin)).sum())


def alive_atoms(w):
    return int(w.k_alive[:w.k_count].sum()) if w.k_count else 0


def run_n(seed, n):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    far_tot, atoms_tot = 0.0, 0
    for _ in range(TRIALS):
        cull_free_vibrations(w, keep_frac=0.0)
        clear_atoms(w)
        a0 = alive_atoms(w)
        inject_moving(w, c, box, X0, n, VX)
        for _ in range(PROP):
            tick(w, c.dt)
        far_tot += far_energy(w, box, FARX)
        atoms_tot += max(0, alive_atoms(w) - a0)
    return dict(far=far_tot / TRIALS, atoms=atoms_tot / TRIALS)


if __name__ == "__main__":
    print("=== G108: density dose-response (propagate vs freeze) ===", flush=True)
    seeds = [42, 7]
    R = {s: {} for s in seeds}
    for s in seeds:
        for n in NS:
            R[s][n] = run_n(s, n)
            print(f"  seed {s} n={n:>2}: far_energy={R[s][n]['far']:.2f} | atoms_formed={R[s][n]['atoms']:.2f}", flush=True)
    G108a = all(R[s][2]['far'] > R[s][28]['far'] for s in seeds)
    G108b = all(R[s][28]['atoms'] > R[s][2]['atoms'] for s in seeds)
    passed = G108a and G108b
    print("\n--- VERDICT ---", flush=True)
    print(f"G108a far(n=2) > far(n=28) both seeds : {G108a}", flush=True)
    print(f"G108b atoms(n=28) > atoms(n=2) both    : {G108b}", flush=True)
    print(("G108: PASS - 'to send is to freeze' confirmed by dose-response: dense packets bind to matter at the source, sparse ones propagate"
           if passed else "G108: NULL - dose-response does not support the binding mechanism"), flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G108"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): {str(n): R[s][n] for n in NS} for s in seeds},
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

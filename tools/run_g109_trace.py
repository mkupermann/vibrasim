"""G109 — trace a single injected packet tick-by-tick to identify what removes the carrier.
Inject n moving vibrations (vel +x) in clear space; track the EXACT injected slots each tick: how many
stay alive, their mean/max x, and atom count. Distinguishes: (H1) velocity not applied (mean x stays ~4);
(H2) moves then dies before the far end; (H3) dies instantly at source.
Diagnostic; expectations pre-registered in docs/amendments/g109_trace.md.
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
X0 = 4.0
VX = 6.0
STEPS = 8


def inject_moving(w, cfg, box, x0, n, vx, sigma=0.8):
    rng = w.rng
    free = np.where(~w.s_alive[:cfg.n_vibrations_max])[0]
    k = min(n, len(free))
    if k == 0:
        return np.array([], int)
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
    return sl


def trace(seed, n):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    if w.k_count:
        w.k_alive[:w.k_count] = False
    k0 = int(w.k_alive[:w.k_count].sum()) if w.k_count else 0
    sl = inject_moving(w, c, box, X0, n, VX)
    rows = []
    for step in range(STEPS):
        tick(w, c.dt)
        alive = w.s_alive[sl]
        na = int(alive.sum())
        if na > 0:
            xs = w.s_pos[sl][alive, 0]
            mx, xmax = float(xs.mean()), float(xs.max())
        else:
            mx, xmax = -1.0, -1.0
        katoms = int(w.k_alive[:w.k_count].sum()) if w.k_count else 0
        rows.append((step + 1, na, round(mx, 1), round(xmax, 1), katoms - k0))
    return rows


if __name__ == "__main__":
    print("=== G109: trace a moving packet (what removes the carrier?) ===", flush=True)
    print("  columns: tick | alive | mean_x | max_x | atoms_formed   (inject x=4, vx=6, dt=0.5)", flush=True)
    for seed in [42, 7]:
        for n in [2, 14]:
            rows = trace(seed, n)
            print(f"  seed {seed} n={n}:", flush=True)
            for r in rows:
                print(f"     t={r[0]} alive={r[1]:>2} mean_x={r[2]:>5} max_x={r[3]:>5} atoms={r[4]}", flush=True)
    print("\n  Interpretation: mean_x rising then alive->0 = moves-then-dies; mean_x~4 = velocity not applied;", flush=True)
    print("  alive->0 at t=1 = removed at source. (See docs/amendments/g109_trace.md.)", flush=True)
    print("DONE", flush=True)

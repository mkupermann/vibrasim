"""G110 — do BOUND NODES (atoms) travel ballistically where free vibrations don't?
G109 found free vibrations are quasi-stationary (velocity not conserved). Nodes move via a different path
(move_nodes). Give a settled atom a +x velocity and trace its position: if it conserves momentum and
travels, matter is a transport avenue; if it's damped like vibrations, transport is fundamentally closed.
Diagnostic; expectations pre-registered in docs/amendments/g110_node_motion.md.
"""
import sys, time
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
VX = 6.0
STEPS = 8


def trace(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    K_ = w.k_count
    if K_ == 0:
        return None
    # pick an alive level>=4 atom near the low-x side
    al = w.k_alive[:K_]
    lvl = w.k_level[:K_]
    cand = np.where(al & (lvl >= 4))[0]
    if len(cand) == 0:
        cand = np.where(al)[0]
    if len(cand) == 0:
        return None
    idx = int(cand[np.argmin(w.k_pos[cand, 0])])
    x0 = float(w.k_pos[idx, 0])
    w.k_vel[idx] = np.array([VX, 0.0, 0.0])
    rows = []
    for step in range(STEPS):
        tick(w, c.dt)
        alive = bool(w.k_alive[idx])
        x = float(w.k_pos[idx, 0]) if alive else -1.0
        vx = float(w.k_vel[idx, 0]) if alive else 0.0
        rows.append((step + 1, alive, round(x, 2), round(vx, 2)))
    return x0, rows


if __name__ == "__main__":
    print("=== G110: do bound nodes (atoms) travel ballistically? (vx=6, dt=0.5 -> 3.0/tick if conserved) ===", flush=True)
    for seed in [42, 7]:
        r = trace(seed)
        if r is None:
            print(f"  seed {seed}: no atom available", flush=True)
            continue
        x0, rows = r
        print(f"  seed {seed}: atom start x={x0:.2f}", flush=True)
        for t, alive, x, vx in rows:
            print(f"     t={t} alive={alive} x={x:>6} vx={vx:>5}", flush=True)
        if rows[-1][2] >= 0:
            disp = rows[-1][2] - x0
            print(f"     -> net displacement over {STEPS} ticks = {disp:.2f} (ballistic would be ~{VX*0.5*STEPS:.0f})", flush=True)
    print("\n  Interpretation: x rising ~3/tick & vx~6 = ballistic (matter transports);", flush=True)
    print("  x ~flat & vx->0 = damped like vibrations (transport fundamentally closed). See g110_node_motion.md.", flush=True)
    print("DONE", flush=True)

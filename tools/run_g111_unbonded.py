"""G111 — is a lattice atom held by its BONDS or intrinsically immobile? (precision refinement of G110)
move_nodes is ballistic (pos += k_vel*dt). Yet G110's bonded atom barely moved. Test: cut the chosen
atom's bridges, then give it velocity and trace. If it now travels ballistically, lattice atoms are
BOND-RESTRAINED (spring-held), not overdamped; if it still sticks, motion is damped intrinsically.
Diagnostic; expectations pre-registered in docs/amendments/g111_unbonded.md.
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
VX = 6.0
STEPS = 8


def cut_bridges_of(w, idx):
    cut = 0
    for b in range(w.b_count):
        if w.b_alive[b] and (int(w.b_atom_i[b]) == idx or int(w.b_atom_j[b]) == idx):
            w.b_alive[b] = False
            cut += 1
    return cut


def trace(seed, cut):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    K_ = w.k_count
    al = w.k_alive[:K_]
    lvl = w.k_level[:K_]
    cand = np.where(al & (lvl >= 4))[0]
    if len(cand) == 0:
        cand = np.where(al)[0]
    if len(cand) == 0:
        return None
    idx = int(cand[np.argmin(w.k_pos[cand, 0])])
    ncut = cut_bridges_of(w, idx) if cut else 0
    x0 = float(w.k_pos[idx, 0])
    w.k_vel[idx] = np.array([VX, 0.0, 0.0])
    xs = []
    for _ in range(STEPS):
        w.k_vel[idx, 0] = VX           # re-assert drive each tick (isolate the position response)
        tick(w, c.dt)
        xs.append(round(float(w.k_pos[idx, 0]), 2) if w.k_alive[idx] else -1.0)
    return x0, ncut, xs


if __name__ == "__main__":
    print("=== G111: bonded vs bridge-cut atom motion (vx=6 re-asserted; ballistic ~3.0/tick) ===", flush=True)
    for seed in [42, 7]:
        for cut in [False, True]:
            r = trace(seed, cut)
            if r is None:
                print(f"  seed {seed} cut={cut}: no atom", flush=True)
                continue
            x0, ncut, xs = r
            disp = (xs[-1] - x0) if xs[-1] >= 0 else float('nan')
            tag = f"BRIDGE-CUT(n={ncut})" if cut else "BONDED"
            print(f"  seed {seed} {tag}: x0={x0:.2f} -> x8={xs[-1]} (net {disp:.2f}); traj={xs}", flush=True)
    print("\n  Interpretation: cut atom travels (net >> bonded) = lattice atoms are BOND-RESTRAINED, not", flush=True)
    print("  intrinsically immobile. Cut atom also stuck = motion damped regardless of bonds. See g111_unbonded.md.", flush=True)
    print("DONE", flush=True)

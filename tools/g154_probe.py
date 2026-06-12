"""G154 mechanism-fired probe (docs/patterns/01): before believing the NULL,
confirm (a) bonds form, (b) bridge tension actually moves a displaced carrier,
and (c) where it settles — the best possible case: one interior carrier pinned
between two correct neighbours.
"""
from __future__ import annotations
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import tick

SPACING = 6.0; R2 = 2 * SPACING; BAND_Y = 30.0
EMPTY = np.empty(0, dtype=np.int32)


def cfg(valence=2):
    return WorldConfig(rng_seed=42, box_size=(60.0, 60.0, 60.0),
                       n_initial_vibrations=0, n_vibrations_max=64, n_nodes_max=64,
                       lambda_gen=0.0, lambda_dec=0.0, atom_valence=valence,
                       atom_repulsion_k=0.0, repulsion_k=0.0, node_thermal_speed=0.0,
                       anchor_damping=0.0, neuron_dynamics_enabled=False,
                       stdp_enabled=False, btsp_enabled=False, r_2=R2,
                       graceful_capacity=True)


def place(w, x):
    return w.allocate_node(np.array([x, BAND_Y, 30.0]), 1.0, True, 4, EMPTY, 0)


def probe(displace, relax, valence=2):
    c = cfg(valence); w = World(c)
    cells = [15.0, 21.0, 27.0]          # 3-chain, spacing 6 == r_eq
    s = [place(w, x) for x in cells]
    for _ in range(8):                  # consolidation
        for i, x in zip(s, cells):
            w.k_pos[i] = (x, BAND_Y, 30.0); w.k_vel[i] = 0.0
        tick(w, c.dt)
    b_after_consol = int(w.b_count)
    # displace the MIDDLE carrier; pin the two ends
    mid = s[1]
    w.k_pos[mid] = (cells[1] + displace, BAND_Y, 30.0); w.k_vel[mid] = 0.0
    start_x = float(w.k_pos[mid][0])
    traj = []
    for t in range(relax):
        for i, x in (("end0", cells[0]), ("end2", cells[2])):
            pass
        w.k_pos[s[0]] = (cells[0], BAND_Y, 30.0); w.k_vel[s[0]] = 0.0
        w.k_pos[s[2]] = (cells[2], BAND_Y, 30.0); w.k_vel[s[2]] = 0.0
        tick(w, c.dt)
        if t in (0, 9, 49, 199, relax - 1):
            traj.append((t + 1, round(float(w.k_pos[mid][0]), 3)))
    end_x = float(w.k_pos[mid][0])
    return dict(bonds=b_after_consol, target=cells[1], start_x=start_x,
                end_x=round(end_x, 3), err=round(abs(end_x - cells[1]), 3), traj=traj)


if __name__ == "__main__":
    print("== bonds formed? mechanism-fired check (interior carrier, pinned ends) ==")
    for disp in (3.0, 8.0, 14.0):
        r = probe(disp, 400)
        print(f"displace={disp:>4}: bonds={r['bonds']}  start_x={r['start_x']:.1f} "
              f"-> end_x={r['end_x']:.3f}  target={r['target']}  err={r['err']:.3f}")
        print(f"             traj(t->x): {r['traj']}")
    print("\n== negative control (valence=0, no bonds) ==")
    r0 = probe(8.0, 400, valence=0)
    print(f"displace=8.0: bonds={r0['bonds']}  start_x={r0['start_x']:.1f} "
          f"-> end_x={r0['end_x']:.3f}  err={r0['err']:.3f}  (should NOT return)")
    print("\n== longer relax (1500 ticks), displace=8 ==")
    rl = probe(8.0, 1500)
    print(f"end_x={rl['end_x']:.3f}  target={rl['target']}  err={rl['err']:.3f}")

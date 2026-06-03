"""G121 — WHERE do the repopulating atoms come from? (diagnostic for G120)
After writing [1,0,1] and releasing, run a scaffold-free POST and trace in-band non-carrier atoms: are
they NEW (k_birth after write start) or PRE-EXISTING atoms that DRIFTED into the band (y moved toward 15)?
This identifies whether the maintenance requirement could be replaced by a passive structural barrier
(if drift-in) or is fundamental churn (if new formation).
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
VX = 6.0
DRIVE_T = 250
POST_T = 800
BAND_Y, BAND_HALF = 15.0, 4.0
CELLS = [7.0, 14.0, 21.0]


def clear_band_except(w, keep_arr):
    K_ = w.k_count
    al = w.k_alive[:K_]; y = w.k_pos[:K_, 1]
    inband = al & (np.abs(y - BAND_Y) < BAND_HALF)
    if len(keep_arr):
        kmask = np.zeros(K_, dtype=bool); kmask[keep_arr[keep_arr < K_]] = True
        inband = inband & ~kmask
    w.k_alive[:K_][inband] = False


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    K_ = w.k_count
    cand = np.where(w.k_alive[:K_] & (w.k_level[:K_] >= 4) & (np.abs(w.k_pos[:K_, 1] - BAND_Y) < BAND_HALF))[0]
    order = list(cand[np.argsort(w.k_pos[cand, 0])])
    assign = {}
    for k, bit in enumerate([1, 0, 1]):
        if bit and order:
            ci = int(order.pop(0)); w.k_pos[ci, 1] = BAND_Y; assign[ci] = CELLS[k]
    keep = np.array(list(assign.keys()), dtype=int)
    for _ in range(DRIVE_T):
        clear_band_except(w, keep)
        for ci, tx in assign.items():
            if w.k_alive[ci]:
                w.k_vel[ci, 0] = VX if w.k_pos[ci, 0] < tx else 0.0
        tick(w, c.dt)
    for ci in assign:
        if w.k_alive[ci]:
            w.k_vel[ci] = 0.0
    # record max birth at POST start (to tell NEW atoms apart)
    birth_cut = float(np.max(w.k_birth[:w.k_count])) if w.k_count else 0.0
    keepset = set(int(i) for i in keep)
    rows = []
    for step in range(POST_T):
        tick(w, c.dt)
        if (step + 1) % 200 == 0:
            Kc = w.k_count
            al = w.k_alive[:Kc]; y = w.k_pos[:Kc, 1]
            inband_idx = [i for i in np.where(al & (np.abs(y - BAND_Y) < BAND_HALF))[0] if int(i) not in keepset]
            new = sum(1 for i in inband_idx if float(w.k_birth[i]) > birth_cut + 1e-6)
            old = len(inband_idx) - new
            rows.append((step + 1, len(inband_idx), new, old))
    return rows


if __name__ == "__main__":
    print("=== G121: repopulation source trace (in-band non-carrier atoms: NEW vs DRIFTED-IN) ===", flush=True)
    for seed in [42]:
        rows = run(seed)
        print(f"  seed {seed}: (tick | inband_noncarrier | NEW | drifted-in-OLD)", flush=True)
        for r in rows:
            print(f"     t={r[0]:>4} total={r[1]:>3} new={r[2]:>3} old={r[3]:>3}", flush=True)
    print("\n  NEW-dominated => churn/formation (fundamental); OLD-dominated => drift-in (a passive y-barrier could block it).", flush=True)
    print("DONE", flush=True)

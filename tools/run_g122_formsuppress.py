"""G122 — decompose the maintenance: does suppressing FORMATION (cull free vibrations in the band) keep
empty cells clean, or does DRIFT-in still fill them? Scaffold-free POST except free-vibration culling in
the band each tick (no atom clearing). G121 said repopulation ~56% drift + 44% formation. If culling
formation leaves cells much cleaner than G120 ([1,1,1]), a lighter maintenance suffices; if cells still
fill, drift dominates and atom-level clearing (or a barrier) is still needed.
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
CELLR = 1.5
K = len(CELLS)


def clear_band_atoms_except(w, keep_arr):
    K_ = w.k_count
    al = w.k_alive[:K_]; y = w.k_pos[:K_, 1]
    inband = al & (np.abs(y - BAND_Y) < BAND_HALF)
    if len(keep_arr):
        kmask = np.zeros(K_, dtype=bool); kmask[keep_arr[keep_arr < K_]] = True
        inband = inband & ~kmask
    w.k_alive[:K_][inband] = False


def cull_band_vibrations(w):
    n = w.config.n_vibrations_max
    al = w.s_alive[:n]
    idx = np.where(al & (np.abs(w.s_pos[:n, 1] - BAND_Y) < BAND_HALF))[0]
    if len(idx):
        w.s_alive[idx] = False


def occ(w, cx):
    K_ = w.k_count
    al = w.k_alive[:K_]; x = w.k_pos[:K_, 0]; y = w.k_pos[:K_, 1]
    return int((al & (np.abs(x - cx) < CELLR) & (np.abs(y - BAND_Y) < CELLR)).sum() >= 1)


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
        clear_band_atoms_except(w, keep)
        for ci, tx in assign.items():
            if w.k_alive[ci]:
                w.k_vel[ci, 0] = VX if w.k_pos[ci, 0] < tx else 0.0
        tick(w, c.dt)
    for ci in assign:
        if w.k_alive[ci]:
            w.k_vel[ci] = 0.0
    # POST: only vibration-culling in band (formation suppression), NO atom clearing
    for _ in range(POST_T):
        cull_band_vibrations(w)
        tick(w, c.dt)
    return [occ(w, CELLS[k]) for k in range(K)]


if __name__ == "__main__":
    print("=== G122: formation-suppression maintenance (cull band vibrations; no atom clearing) ===", flush=True)
    target = [1, 0, 1]
    ok = True
    for s in [42, 7]:
        r = run(s)
        match = (r == target)
        ok = ok and match
        print(f"  seed {s}: readout={r} target={target} exact={match}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"G122 pattern held with formation-suppression only (both seeds): {ok}", flush=True)
    print(("G122: PASS - culling formation (band vibrations) suffices; drift-in alone does NOT fill cells -> lighter maintenance works"
           if ok else "G122: NULL/PARTIAL - cells still fill (drift-in matters) -> formation-suppression alone is not enough"), flush=True)
    print("DONE", flush=True)

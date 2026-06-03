"""G119b — minimal/cheap test of the spacing fix: ONE fixed pattern [1,0,1] per seed, wide cells.
Avoids the expensive multi-pattern statistics (compute-blocked in G119). If wide spacing fixes the
systematic boundary error (G118), the 3 bits recover exactly. Preliminary signal, 1 world/seed.
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
POST_T = 250
BAND_Y, BAND_HALF = 15.0, 4.0
CELLS = [7.0, 14.0, 21.0]
CELLR = 1.5
PATTERN = [1, 0, 1]


def clear_band_except(w, keep_arr):
    K_ = w.k_count
    if K_ == 0:
        return
    al = w.k_alive[:K_]
    y = w.k_pos[:K_, 1]
    inband = al & (np.abs(y - BAND_Y) < BAND_HALF)
    if len(keep_arr):
        kmask = np.zeros(K_, dtype=bool); kmask[keep_arr[keep_arr < K_]] = True
        inband = inband & ~kmask
    w.k_alive[:K_][inband] = False


def occ(w, cx):
    K_ = w.k_count
    al = w.k_alive[:K_]; x = w.k_pos[:K_, 0]; y = w.k_pos[:K_, 1]
    return int((al & (np.abs(x - cx) < CELLR) & (np.abs(y - BAND_Y) < CELLR)).sum() >= 1)


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c); box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    K_ = w.k_count
    cand = np.where(w.k_alive[:K_] & (w.k_level[:K_] >= 4) & (np.abs(w.k_pos[:K_, 1] - BAND_Y) < BAND_HALF))[0]
    order = list(cand[np.argsort(w.k_pos[cand, 0])])
    assign = {}
    for k, bit in enumerate(PATTERN):
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
    for _ in range(POST_T):
        clear_band_except(w, keep); tick(w, c.dt)
    return [occ(w, CELLS[k]) for k in range(len(CELLS))]


if __name__ == "__main__":
    print(f"=== G119b: minimal spacing test, pattern={PATTERN}, cells={CELLS} r={CELLR} ===", flush=True)
    ok = True
    for s in [42, 7]:
        r = run(s)
        match = (r == PATTERN)
        ok = ok and match
        print(f"  seed {s}: readout={r} target={PATTERN} exact={match}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"G119b spacing recovers pattern exactly (both seeds): {ok}", flush=True)
    print(("G119b: PASS(preliminary) - wide spacing recovers the 3-bit pattern exactly -> spacing fixes the systematic error; clean multi-bit is reachable"
           if ok else "G119b: NULL/PARTIAL - spacing alone did not give exact recovery (see readout)"), flush=True)
    print("DONE", flush=True)

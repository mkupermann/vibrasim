"""G120 — how load-bearing is the band scaffold? Write with band-clearing, POST with NONE.
If the pattern [1,0,1] still recovers (carrier persists at A; empty cells stay empty because atoms are
quasi-stationary, G110/G111), matter-position memory is robust beyond the engineered scaffold — the band
only aids the WRITE, not the HOLD. Settle-once harness. No-write control included.
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
POST_T = 1500
BAND_Y, BAND_HALF = 15.0, 4.0
CELLS = [7.0, 14.0, 21.0]
CELLR = 1.5
K = len(CELLS)
PATTERN = [1, 0, 1]


def snapshot(w):
    return {k: (v.copy() if isinstance(v, np.ndarray) else v)
            for k, v in vars(w).items()
            if isinstance(v, (np.ndarray, int, float, bool, np.integer, np.floating))}


def restore(w, snap):
    for k, v in snap.items():
        cur = getattr(w, k, None)
        if isinstance(cur, np.ndarray) and cur.shape == np.shape(v):
            cur[:] = v
        else:
            setattr(w, k, v)


def clear_band_except(w, keep_arr):
    K_ = w.k_count
    if K_ == 0:
        return
    al = w.k_alive[:K_]; y = w.k_pos[:K_, 1]
    inband = al & (np.abs(y - BAND_Y) < BAND_HALF)
    if len(keep_arr):
        kmask = np.zeros(K_, dtype=bool); kmask[keep_arr[keep_arr < K_]] = True
        inband = inband & ~kmask
    w.k_alive[:K_][inband] = False


def occ(w, cx):
    K_ = w.k_count
    al = w.k_alive[:K_]; x = w.k_pos[:K_, 0]; y = w.k_pos[:K_, 1]
    return int((al & (np.abs(x - cx) < CELLR) & (np.abs(y - BAND_Y) < CELLR)).sum() >= 1)


def trial(w, c, snap, write):
    restore(w, snap)
    assign = {}
    if write:
        K_ = w.k_count
        cand = np.where(w.k_alive[:K_] & (w.k_level[:K_] >= 4) & (np.abs(w.k_pos[:K_, 1] - BAND_Y) < BAND_HALF))[0]
        order = list(cand[np.argsort(w.k_pos[cand, 0])])
        for k, bit in enumerate(PATTERN):
            if bit and order:
                ci = int(order.pop(0)); w.k_pos[ci, 1] = BAND_Y; assign[ci] = CELLS[k]
    keep = np.array(list(assign.keys()), dtype=int)
    # WRITE: band-clearing ON
    for _ in range(DRIVE_T):
        clear_band_except(w, keep)
        for ci, tx in assign.items():
            if w.k_alive[ci]:
                w.k_vel[ci, 0] = VX if w.k_pos[ci, 0] < tx else 0.0
        tick(w, c.dt)
    for ci in assign:
        if w.k_alive[ci]:
            w.k_vel[ci] = 0.0
    # POST: band-clearing OFF (no scaffold)
    for _ in range(POST_T):
        tick(w, c.dt)
    return [occ(w, CELLS[k]) for k in range(K)]


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    snap = snapshot(w)
    return trial(w, c, snap, True), trial(w, c, snap, False)


if __name__ == "__main__":
    print(f"=== G120: matter memory WITHOUT POST band-scaffold (pattern={PATTERN}) ===", flush=True)
    okW, okC = True, True
    for s in [42, 7]:
        wr, ctrl = run(s)
        print(f"  seed {s}: WRITE readout={wr} target={PATTERN} | CONTROL readout={ctrl}", flush=True)
        if wr != PATTERN:
            okW = False
        if any(ctrl):
            okC = False
    passed = okW and okC
    print("\n--- VERDICT ---", flush=True)
    print(f"G120a write recovers pattern without POST scaffold (both seeds): {okW}", flush=True)
    print(f"G120b control stays empty (both seeds)                          : {okC}", flush=True)
    print(("G120: PASS - matter memory HOLDS without the POST band-scaffold; the band only aids the WRITE, the hold is intrinsic (quasi-stationary atoms)"
           if passed else "G120: NULL/PARTIAL - pattern degrades without the POST scaffold (band is load-bearing for the hold)"), flush=True)
    print("DONE", flush=True)

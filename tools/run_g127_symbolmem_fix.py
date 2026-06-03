"""G126 — deep-goal capstone: store written HEX-NIBBLE symbols in the matter memory and recall them.
Each 4-bit nibble (hex digit) is written as a presence pattern across K=4 wide-spaced cells, held with
maintenance (short stable-window hold), and read back. Demonstrates the matter memory stores and recalls
written symbols — persistent written memory, no LLM. Settle-once harness.
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
VX = 6.0
DRIVE_T = 280
POST_T = 300
BAND_Y, BAND_HALF = 15.0, 4.0
CELLS = [6.0, 11.0, 16.0, 21.0]   # K=4, pitch 5, all >=9 units from box edge
CELLR = 1.5
K = 4
SYMBOLS = [0xE, 0x4, 0xA, 0x7]    # test nibbles (E,4,A,7)


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


def store_recall(w, c, snap, nibble):
    restore(w, snap)
    bits = [(nibble >> (K - 1 - k)) & 1 for k in range(K)]   # MSB-first
    K_ = w.k_count
    cand = np.where(w.k_alive[:K_] & (w.k_level[:K_] >= 4) & (np.abs(w.k_pos[:K_, 1] - BAND_Y) < BAND_HALF))[0]
    order = list(cand[np.argsort(w.k_pos[cand, 0])])
    assign = {}
    for k, b in enumerate(bits):
        if b and order:
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
        clear_band_except(w, keep)
        tick(w, c.dt)
    rb = [occ(w, CELLS[k]) for k in range(K)]
    val = 0
    for b in rb:
        val = (val << 1) | b
    return val


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    snap = snapshot(w)
    got = [store_recall(w, c, snap, d) for d in SYMBOLS]
    return got


if __name__ == "__main__":
    print(f"=== G127: store+recall hex nibbles (edge-margin fix: cells x=6,11,16,21) ===", flush=True)
    print(f"  stored : {[hex(d) for d in SYMBOLS]}", flush=True)
    allok = True
    for s in [42, 7]:
        got = run(s)
        exact = (got == SYMBOLS)
        allok = allok and exact
        print(f"  seed {s}: recalled={[hex(d) for d in got]} exact={exact}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"G127 all nibbles recalled exactly (both seeds): {allok}", flush=True)
    print(("G127: PASS - CLEAN store+recall of written hex symbols in matter memory (edge-margin fix); deep goal demonstrated, no LLM"
           if allok else "G127: NULL/PARTIAL - edge-margin fix did not give clean recall (see output)"), flush=True)
    print("DONE", flush=True)

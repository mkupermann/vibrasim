"""G128 — store + recall an ASCII CHARACTER (a full byte) in the matter memory (2 cell-rows = 2 nibbles).
Extends G127 (hex nibbles) to real text characters. A byte = high nibble (row at y=10) + low nibble (row
at y=20), each across K=4 wide-spaced cells. Write both rows, hold with per-row maintenance, read back,
reconstruct the char. Settle-once. No LLM. Test chars 'E','Q'.
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
ROWS = [10.0, 20.0]          # two rows: high nibble, low nibble
HALF = 3.0
CELLS = [6.0, 11.0, 16.0, 21.0]
CELLR = 1.5
K = 4
TEXT = "EQMOD"


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


def clear_rows_except(w, keep_arr):
    K_ = w.k_count
    al = w.k_alive[:K_]; y = w.k_pos[:K_, 1]
    inrows = al & ((np.abs(y - ROWS[0]) < HALF) | (np.abs(y - ROWS[1]) < HALF))
    if len(keep_arr):
        kmask = np.zeros(K_, dtype=bool); kmask[keep_arr[keep_arr < K_]] = True
        inrows = inrows & ~kmask
    w.k_alive[:K_][inrows] = False


def occ(w, cx, ry):
    K_ = w.k_count
    al = w.k_alive[:K_]; x = w.k_pos[:K_, 0]; y = w.k_pos[:K_, 1]
    return int((al & (np.abs(x - cx) < CELLR) & (np.abs(y - ry) < CELLR)).sum() >= 1)


def store_char(w, c, snap, byte):
    restore(w, snap)
    hi = [(byte >> (7 - k)) & 1 for k in range(4)]
    lo = [(byte >> (3 - k)) & 1 for k in range(4)]
    assign = {}
    for ry, bits in ((ROWS[0], hi), (ROWS[1], lo)):
        K_ = w.k_count
        cand = np.where(w.k_alive[:K_] & (w.k_level[:K_] >= 4) & (np.abs(w.k_pos[:K_, 1] - ry) < HALF))[0]
        order = list(cand[np.argsort(w.k_pos[cand, 0])])
        for k, b in enumerate(bits):
            if b and order:
                ci = int(order.pop(0)); w.k_pos[ci, 1] = ry; assign[ci] = (CELLS[k], ry)
    keep = np.array(list(assign.keys()), dtype=int)
    for _ in range(DRIVE_T):
        clear_rows_except(w, keep)
        for ci, (tx, ry) in assign.items():
            if w.k_alive[ci]:
                w.k_pos[ci, 1] = ry
                w.k_vel[ci, 0] = VX if w.k_pos[ci, 0] < tx else 0.0
        tick(w, c.dt)
    for ci in assign:
        if w.k_alive[ci]:
            w.k_vel[ci] = 0.0
    for _ in range(POST_T):
        clear_rows_except(w, keep)
        tick(w, c.dt)
    hi_rb = [occ(w, CELLS[k], ROWS[0]) for k in range(K)]
    lo_rb = [occ(w, CELLS[k], ROWS[1]) for k in range(K)]
    val = 0
    for b in hi_rb + lo_rb:
        val = (val << 1) | b
    return val


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    snap = snapshot(w)
    out = ""
    for ch in TEXT:
        v = store_char(w, c, snap, ord(ch))
        out += chr(v) if 32 <= v < 127 else "?"
    return out


if __name__ == "__main__":
    print(f"=== G129: store+recall a WORD in matter memory (char-by-char, 2 rows/byte) ===", flush=True)
    print(f"  stored text: {TEXT!r}", flush=True)
    allok = True
    for s in [42, 7]:
        out = run(s)
        exact = (out == TEXT)
        allok = allok and exact
        print(f"  seed {s}: recalled={out!r} exact={exact}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"G129 word recalled exactly (both seeds): {allok}", flush=True)
    print(("G129: PASS - the substrate writes and recalls a WORD from persistent matter memory (no LLM)"
           if allok else "G129: NULL/PARTIAL - word not recalled exactly (see output)"), flush=True)
    print("DONE", flush=True)

"""G123 — full memory cycle capstone: WRITE -> long HOLD with light (G122) maintenance -> READ, + control.
Validates the integrated matter-position memory primitive as one system: random pattern written, held over
POST_T with only formation-suppression maintenance (cull band vibrations; carriers untouched), read back;
plus a no-write control that must stay empty. Settle-once harness.
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
NPAT = 3


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


def cycle(w, c, snap, pattern):
    restore(w, snap)
    assign = {}
    K_ = w.k_count
    cand = np.where(w.k_alive[:K_] & (w.k_level[:K_] >= 4) & (np.abs(w.k_pos[:K_, 1] - BAND_Y) < BAND_HALF))[0]
    order = list(cand[np.argsort(w.k_pos[cand, 0])])
    for k, bit in enumerate(pattern):
        if bit and order:
            ci = int(order.pop(0)); w.k_pos[ci, 1] = BAND_Y; assign[ci] = CELLS[k]
    keep = np.array(list(assign.keys()), dtype=int)
    for _ in range(DRIVE_T):                 # WRITE
        clear_band_atoms_except(w, keep)
        for ci, tx in assign.items():
            if w.k_alive[ci]:
                w.k_vel[ci, 0] = VX if w.k_pos[ci, 0] < tx else 0.0
        tick(w, c.dt)
    for ci in assign:
        if w.k_alive[ci]:
            w.k_vel[ci] = 0.0
    for _ in range(POST_T):                  # HOLD with light maintenance
        cull_band_vibrations(w)
        tick(w, c.dt)
    return [occ(w, CELLS[k]) for k in range(K)]   # READ


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    snap = snapshot(w)
    rng = np.random.default_rng(12300 + seed)
    tot = cor = 0
    for p in range(NPAT):
        pat = list(rng.integers(0, 2, K))
        rd = cycle(w, c, snap, pat)
        tot += K; cor += int((np.array(rd) == np.array(pat)).sum())
    ctrl = cycle(w, c, snap, [0, 0, 0])
    return cor / tot, ctrl


if __name__ == "__main__":
    print(f"=== G123: full memory cycle (write -> {POST_T}-tick hold w/ light maintenance -> read), {NPAT} patterns ===", flush=True)
    okA = okC = True
    for s in [42, 7]:
        acc, ctrl = run(s)
        print(f"  seed {s}: per-bit accuracy={acc:.3f} | no-write control readout={ctrl}", flush=True)
        if acc < 0.95:
            okA = False
        if any(ctrl):
            okC = False
    passed = okA and okC
    print("\n--- VERDICT ---", flush=True)
    print(f"G123a patterns recovered over long hold (acc>=0.95 both): {okA}", flush=True)
    print(f"G123b no-write control empty (both)                     : {okC}", flush=True)
    print(("G123: PASS - full matter-memory cycle validated: write -> long hold (light maintenance) -> read, selective & persistent"
           if passed else "G123: NULL/PARTIAL - full cycle did not hold (see accuracy/control)"), flush=True)
    print("DONE", flush=True)

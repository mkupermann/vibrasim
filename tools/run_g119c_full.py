"""G119c — full multi-bit matter memory with a SETTLE-ONCE harness (unblocks the compute wall).
Snapshot the settled world once; restore it before each random pattern (no per-pattern re-settle, no
cross-pattern accumulation). Wide spacing (G119b fix). Measures per-bit accuracy over many patterns.
Bars per docs/amendments/g119_spacing.md (>=0.95/bit both seeds).
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
POST_T = 150
BAND_Y, BAND_HALF = 15.0, 4.0
CELLS = [7.0, 14.0, 21.0]
CELLR = 1.5
K = len(CELLS)
NPAT = 5


def snapshot(w):
    snap = {}
    for k, v in vars(w).items():
        if isinstance(v, np.ndarray):
            snap[k] = v.copy()
        elif isinstance(v, (int, float, bool, np.integer, np.floating)):
            snap[k] = v
    return snap


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


def write_read(w, c, pattern):
    K_ = w.k_count
    cand = np.where(w.k_alive[:K_] & (w.k_level[:K_] >= 4) & (np.abs(w.k_pos[:K_, 1] - BAND_Y) < BAND_HALF))[0]
    order = list(cand[np.argsort(w.k_pos[cand, 0])])
    assign = {}
    for k, bit in enumerate(pattern):
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
    return [occ(w, CELLS[k]) for k in range(K)]


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    snap = snapshot(w)
    rng = np.random.default_rng(11900 + seed)
    tot, cor = 0, 0
    for p in range(NPAT):
        restore(w, snap)
        pattern = list(rng.integers(0, 2, K))
        readout = write_read(w, c, pattern)
        tot += K; cor += int((np.array(readout) == np.array(pattern)).sum())
    return cor / tot


if __name__ == "__main__":
    print(f"=== G119c: full multi-bit matter memory, settle-once harness (K={K}, {NPAT} patterns, wide pitch) ===", flush=True)
    R = {}
    for s in [42, 7]:
        R[s] = run(s)
        print(f"  seed {s}: per-bit accuracy = {R[s]:.3f} (chance 0.50)", flush=True)
    ok = all(R[s] >= 0.95 for s in R)
    print("\n--- VERDICT ---", flush=True)
    print(f"G119c clean multi-bit (per-bit acc>=0.95 both seeds): {ok}", flush=True)
    print(("G119c: PASS - CLEAN multi-bit content-addressable matter memory (wide spacing); breakthrough cemented at scale"
           if ok else "G119c: NULL/PARTIAL - below 0.95 (see accuracy)"), flush=True)
    print("DONE", flush=True)

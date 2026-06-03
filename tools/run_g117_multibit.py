"""G117 — content-addressable MULTI-BIT memory via matter position (scales the G116 breakthrough).
In a cleared band with K cells, write a random K-bit pattern: drive a carrier atom to each 1-cell, leave
0-cells empty. POST, read occupancy per cell, recover the pattern. Measure per-bit accuracy across many
random patterns. If high, matter-position is a real multi-bit content store.
Bars pre-registered in docs/amendments/g117_multibit.md.
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
VX = 6.0
DRIVE_T = 320
POST_T = 800
BAND_Y, BAND_HALF = 15.0, 4.0
CELLS = [8.0, 13.0, 18.0, 23.0]     # K=4 cells, pitch 5 (> G97 ~3)
K = len(CELLS)
CELLR = 2.0
NPAT = 6


def clear_band_except(w, keep):
    K_ = w.k_count
    if K_ == 0:
        return
    al = w.k_alive[:K_]
    y = w.k_pos[:K_, 1]
    inband = np.where(al & (np.abs(y - BAND_Y) < BAND_HALF))[0]
    for i in inband:
        if int(i) not in keep:
            w.k_alive[i] = False


def cell_occupied(w, cx):
    K_ = w.k_count
    if K_ == 0:
        return 0
    al = w.k_alive[:K_]
    x = w.k_pos[:K_, 0]
    y = w.k_pos[:K_, 1]
    return int((al & (np.abs(x - cx) < CELLR) & (np.abs(y - BAND_Y) < CELLR)).sum() >= 1)


def write_read(w, c, box, pattern):
    # assign one carrier per 1-bit, from leftmost band atoms
    K_ = w.k_count
    al = w.k_alive[:K_]
    lvl = w.k_level[:K_]
    cand = np.where(al & (lvl >= 4) & (np.abs(w.k_pos[:K_, 1] - BAND_Y) < BAND_HALF))[0]
    if len(cand) == 0:
        cand = np.where(al & (lvl >= 4))[0]
    order = list(cand[np.argsort(w.k_pos[cand, 0])])
    ones = [k for k in range(K) if pattern[k]]
    assign = {}   # carrier_idx -> target_x
    for k in ones:
        if order:
            ci = int(order.pop(0))
            w.k_pos[ci, 1] = BAND_Y
            assign[ci] = CELLS[k]
    keep = set(assign.keys())
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
    return [cell_occupied(w, CELLS[k]) for k in range(K)]


def run(seed):
    rng = np.random.default_rng(11700 + seed)
    bits_total, bits_correct = 0, 0
    for p in range(NPAT):
        c = replace(protocfg(seed), membrane_channel_k=0.0)
        w = World(c)
        box = np.asarray(c.box_size)
        for _ in range(SETTLE):
            tick(w, c.dt)
        object.__setattr__(c, 'lambda_gen', 0.0)
        pattern = rng.integers(0, 2, K)
        readout = write_read(w, c, box, pattern)
        bits_total += K
        bits_correct += int((np.array(readout) == pattern).sum())
    return bits_correct / bits_total


if __name__ == "__main__":
    print(f"=== G117: multi-bit content memory via matter position (K={K} cells, {NPAT} random patterns) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: per-bit accuracy = {R[s]:.2f} (chance 0.50)", flush=True)
    G117 = all(R[s] >= 0.90 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G117 multi-bit memory (per-bit acc>=0.90 both seeds): {G117}", flush=True)
    if G117:
        print("G117: PASS - matter position is a content-addressable MULTI-BIT memory (random patterns written+recovered)", flush=True)
    else:
        print("G117: NULL/PARTIAL - multi-bit recovery below bar (see accuracy)", flush=True)
    out = __import__('pathlib').Path.home() / ".eqmod" / "bet" / "G117"
    out.mkdir(parents=True, exist_ok=True)
    print("DONE", flush=True)

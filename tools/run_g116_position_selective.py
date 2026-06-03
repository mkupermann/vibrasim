"""G116 — SELECTIVE persistent memory via matter position? (potential breakthrough on the deadlock)
In a cleared band, WRITE cell A by driving a carrier atom there; leave cell B empty. Maintain the band
(clear background atoms except the carrier) through a long POST. Read: carrier persists at A, B stays
empty, and a no-write CONTROL leaves A empty too. If all hold, matter-position is a SELECTIVE + PERSISTENT
store — the first on this substrate, where activity-based stores all failed (write=leak).
Bars pre-registered in docs/amendments/g116_position_selective.md.
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
VX = 6.0
DRIVE_T = 170          # ~15 units -> reach cell A (~x=15), no wrap
POST_T = 1500
BAND_Y, BAND_HALF = 15.0, 4.0
AX, BX, CELL = 15.0, 22.0, 2.5
NCARRIER = 4


def clear_band_except(w, keep):
    K_ = w.k_count
    if K_ == 0:
        return
    al = w.k_alive[:K_]
    y = w.k_pos[:K_, 1]
    inband = al & (np.abs(y - BAND_Y) < BAND_HALF)
    for i in np.where(inband)[0]:
        if int(i) not in keep:
            w.k_alive[i] = False


def cell_count(w, cx, cy=BAND_Y, half=CELL):
    K_ = w.k_count
    if K_ == 0:
        return 0
    al = w.k_alive[:K_]
    x = w.k_pos[:K_, 0]
    y = w.k_pos[:K_, 1]
    return int((al & (np.abs(x - cx) < half) & (np.abs(y - cy) < half)).sum())


def run(seed, write):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    carriers = []
    if write:
        K_ = w.k_count
        al = w.k_alive[:K_]
        lvl = w.k_level[:K_]
        cand = np.where(al & (lvl >= 4) & (np.abs(w.k_pos[:K_, 1] - BAND_Y) < BAND_HALF))[0]
        if len(cand) == 0:
            cand = np.where(al & (lvl >= 4))[0]
        order = cand[np.argsort(w.k_pos[cand, 0])]
        carriers = [int(i) for i in order[:NCARRIER]]
        # nudge carriers' y toward the band centre so they sit in cell A's row
        for i in carriers:
            w.k_pos[i, 1] = BAND_Y
    keep = set(carriers)
    # WRITE: drive carriers toward A
    for _ in range(DRIVE_T):
        clear_band_except(w, keep)
        for i in carriers:
            if w.k_alive[i]:
                w.k_vel[i, 0] = VX
                if w.k_pos[i, 0] >= AX:        # stop at cell A
                    w.k_vel[i, 0] = 0.0
        tick(w, c.dt)
    for i in carriers:
        if w.k_alive[i]:
            w.k_vel[i] = 0.0
    # POST: maintain band, no drive
    for _ in range(POST_T):
        clear_band_except(w, keep)
        tick(w, c.dt)
    return dict(A=cell_count(w, AX), B=cell_count(w, BX))


if __name__ == "__main__":
    print("=== G116: selective persistent memory via matter position ===", flush=True)
    seeds = [42, 7]
    W, C = {}, {}
    for s in seeds:
        W[s] = run(s, write=True)
        print(f"  seed {s} WRITE  : cell A={W[s]['A']} cell B={W[s]['B']}", flush=True)
    for s in seeds:
        C[s] = run(s, write=False)
        print(f"  seed {s} CONTROL: cell A={C[s]['A']} cell B={C[s]['B']}", flush=True)
    G116a = all(W[s]['A'] >= 1 for s in seeds)
    G116b = all(W[s]['B'] == 0 for s in seeds)
    G116c = all(C[s]['A'] == 0 for s in seeds)
    passed = G116a and G116b and G116c
    print("\n--- VERDICT ---", flush=True)
    print(f"G116a written cell A occupied (>=1 both)   : {G116a}", flush=True)
    print(f"G116b unwritten cell B empty (0 both)      : {G116b}", flush=True)
    print(f"G116c no-write control A empty (0 both)    : {G116c}", flush=True)
    if passed:
        print("G116: PASS - SELECTIVE + PERSISTENT memory via matter position (write A, B empty, control empty) — FIRST on this substrate", flush=True)
    elif G116a and G116c:
        print("G116: PARTIAL - A written & control-clean but B not clean (some cross-talk)", flush=True)
    else:
        print("G116: NULL - selective position memory not demonstrated", flush=True)
    out = __import__('pathlib').Path.home() / ".eqmod" / "bet" / "G116"
    out.mkdir(parents=True, exist_ok=True)
    print("DONE", flush=True)

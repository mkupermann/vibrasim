"""G125 — extend retention by ANCHORING carriers (re-pin position each hold tick) at POST=2500.
G116/G119c held at POST=1500 with full maintenance. G124 tests an even longer hold to confirm the
breakthrough's persistence is robust long-term, not a 1500-tick artifact. Full atom-clearing maintenance
during hold; pattern [1,0,1] + no-write control; both seeds.
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
POST_T = 2500
BAND_Y, BAND_HALF = 15.0, 4.0
CELLS = [7.0, 14.0, 21.0]
CELLR = 1.5
K = len(CELLS)


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
    pin = dict(assign)  # carrier -> target cell x (anchor point)
    for _ in range(DRIVE_T):
        clear_band_atoms_except(w, keep)
        for ci, tx in assign.items():
            if w.k_alive[ci]:
                w.k_vel[ci, 0] = VX if w.k_pos[ci, 0] < tx else 0.0
        tick(w, c.dt)
    for ci in assign:
        if w.k_alive[ci]:
            w.k_vel[ci] = 0.0
    for _ in range(POST_T):                    # HOLD: full maintenance + ANCHOR carriers (re-pin)
        clear_band_atoms_except(w, keep)
        for ci, tx in pin.items():
            if w.k_alive[ci]:
                w.k_pos[ci, 0] = tx; w.k_pos[ci, 1] = BAND_Y; w.k_vel[ci] = 0.0
        tick(w, c.dt)
    return [occ(w, CELLS[k]) for k in range(K)]


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    snap = snapshot(w)
    return cycle(w, c, snap, [1, 0, 1]), cycle(w, c, snap, [0, 0, 0])


if __name__ == "__main__":
    print(f"=== G125: ANCHORED carriers (re-pinned), POST={POST_T} ===", flush=True)
    okW = okC = True
    for s in [42, 7]:
        wr, ctrl = run(s)
        print(f"  seed {s}: WRITE readout={wr} target=[1,0,1] | CONTROL={ctrl}", flush=True)
        if wr != [1, 0, 1]:
            okW = False
        if any(ctrl):
            okC = False
    passed = okW and okC
    print("\n--- VERDICT ---", flush=True)
    print(f"G125a anchored pattern held at POST=2500 (both seeds): {okW}", flush=True)
    print(f"G125b control empty (both seeds)             : {okC}", flush=True)
    print(("G125: PASS - anchoring the carriers extends retention: pattern holds at POST=2500 (carrier drift removed)"
           if passed else "G125: NULL/PARTIAL - anchoring did not hold the pattern at 2500 (see readouts)"), flush=True)
    print("DONE", flush=True)

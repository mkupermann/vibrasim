"""G115 — clean redo of G114: is matter POSITION persistent? Short no-wrap drive + k_birth identity.
Drive atoms a SHORT distance (no periodic wrap), record (index, k_birth, target_x). Release. POST. Trust
the position only if k_birth is unchanged (same atom in the slot). Measures whether a written position
holds after the drive stops.
Bars pre-registered in docs/amendments/g115_position_clean.md.
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
VX = 6.0
DRIVE_T = 70          # ~7 units at 0.10/tick — NO wrap (box=30)
POST_T = 2000
NDRIVE = 6


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    K_ = w.k_count
    al = w.k_alive[:K_]
    lvl = w.k_level[:K_]
    cand = np.where(al & (lvl >= 4))[0]
    if len(cand) == 0:
        cand = np.where(al)[0]
    order = cand[np.argsort(w.k_pos[cand, 0])]
    drive = [int(i) for i in order[:NDRIVE]]
    birth0 = {i: round(float(w.k_birth[i]), 4) for i in drive}
    x_start = {i: float(w.k_pos[i, 0]) for i in drive}
    for _ in range(DRIVE_T):
        for i in drive:
            if w.k_alive[i]:
                w.k_vel[i, 0] = VX
        tick(w, c.dt)
    target_x = {i: float(w.k_pos[i, 0]) for i in drive}
    moved = {i: target_x[i] - x_start[i] for i in drive}
    for i in drive:
        if w.k_alive[i]:
            w.k_vel[i] = 0.0
    for _ in range(POST_T):
        tick(w, c.dt)
    res = []
    for i in drive:
        same = bool(w.k_alive[i]) and round(float(w.k_birth[i]), 4) == birth0[i]
        xf = float(w.k_pos[i, 0]) if w.k_alive[i] else -999.0
        drift = abs(xf - target_x[i]) if same else None
        res.append(dict(moved=round(moved[i], 1), same_atom=same,
                        target_x=round(target_x[i], 1), xf=round(xf, 1),
                        drift=(round(drift, 2) if drift is not None else None)))
    return res


if __name__ == "__main__":
    print(f"=== G115: matter-position persistence (clean: {DRIVE_T}-tick no-wrap drive, k_birth identity, {POST_T} POST) ===", flush=True)
    seeds = [42, 7]
    ok_move, ok_hold = True, True
    for seed in seeds:
        res = run(seed)
        print(f"  seed {seed}:", flush=True)
        for r in res:
            print(f"     moved={r['moved']:>5} same_atom={r['same_atom']} target_x={r['target_x']:>5} post_x={r['xf']:>6} drift={r['drift']}", flush=True)
        same = [r for r in res if r['same_atom']]
        if not same:
            ok_hold = False
        for r in same:
            if r['drift'] is not None and r['drift'] >= 2.0:
                ok_hold = False
        # sanity: the drive actually moved atoms a few units
        if np.mean([r['moved'] for r in res]) < 2.0:
            ok_move = False
    print("\n--- VERDICT ---", flush=True)
    print(f"sanity: drive moved atoms (>2 units mean)   : {ok_move}", flush=True)
    print(f"G115: written position held (same-atom drift<2 both seeds): {ok_hold}", flush=True)
    if ok_move and ok_hold:
        print("G115: PASS - matter POSITION persists: an atom driven a few units holds that position after release (a persistent non-activity store)", flush=True)
    elif not ok_move:
        print("G115: INCONCLUSIVE - drive did not move atoms (sanity failed)", flush=True)
    else:
        print("G115: NULL/PARTIAL - written position not held (atom drifts or identity lost)", flush=True)
    print("DONE", flush=True)

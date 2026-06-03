"""G114 — is MATTER POSITION a persistent store? (new angle on the memory deadlock via the G112 discovery)
Drive an atom to a target location, then RELEASE the drive and run a long POST. If the atom holds its
position (doesn't drift) and stays alive, atom-position is a persistent store — a representation the
activity-based memory deadlock (bridges/firing spread+leak) never had.
Bars pre-registered in docs/amendments/g114_position_memory.md.
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
VX = 6.0
DRIVE_T = 220
POST_T = 3000
NDRIVE = 4


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
    # WRITE: drive atoms +x
    for _ in range(DRIVE_T):
        for i in drive:
            if w.k_alive[i]:
                w.k_vel[i, 0] = VX
        tick(w, c.dt)
    x_written = {i: float(w.k_pos[i, 0]) for i in drive}
    for i in drive:
        if w.k_alive[i]:
            w.k_vel[i] = 0.0      # RELEASE the drive
    # POST: no drive
    for _ in range(POST_T):
        tick(w, c.dt)
    res = []
    for i in drive:
        alive = bool(w.k_alive[i])
        xf = float(w.k_pos[i, 0]) if alive else -999.0
        drift = abs(xf - x_written[i]) if alive else 999.0
        res.append(dict(x_written=round(x_written[i], 1), alive=alive, xf=round(xf, 1), drift=round(drift, 2)))
    return res


if __name__ == "__main__":
    print(f"=== G114: matter-position persistence (write by drive, release, {POST_T}-tick POST) ===", flush=True)
    all_persist, all_alive = True, True
    for seed in [42, 7]:
        res = run(seed)
        print(f"  seed {seed}:", flush=True)
        for r in res:
            print(f"     written_x={r['x_written']:>5} alive={r['alive']} post_x={r['xf']:>7} drift={r['drift']}", flush=True)
        # persistence: alive atoms drift < 2 over the POST
        alive_rs = [r for r in res if r['alive']]
        if len(alive_rs) < max(1, len(res) // 2):
            all_alive = False
        for r in alive_rs:
            if r['drift'] >= 2.0:
                all_persist = False
    print("\n--- VERDICT ---", flush=True)
    print(f"G114a majority of written atoms survive POST: {all_alive}", flush=True)
    print(f"G114b position held (drift<2 on survivors)  : {all_persist}", flush=True)
    if all_alive and all_persist:
        print("G114: PASS - matter POSITION is a persistent store: an atom driven to a location stays there after release (a new, non-activity memory representation)", flush=True)
    elif all_alive:
        print("G114: PARTIAL - atoms survive but drift from the written position (position not stable)", flush=True)
    else:
        print("G114: NULL - written atoms do not survive the POST (position store decays)", flush=True)
    out = __import__('pathlib').Path.home() / ".eqmod" / "bet" / "G114"
    out.mkdir(parents=True, exist_ok=True)
    print("DONE", flush=True)

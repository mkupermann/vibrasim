"""G112 — can SLOW driven MATTER carry a symbol across the box? (resolves the G111-opened avenue)
Continuously drive the leftmost atoms in +x (re-assert k_vel each tick, since G111 showed velocity
decays). Over up to MAXT ticks, record whether each driven atom reaches the far side (x>20) ALIVE and
whether its y (the symbol) is preserved. If atoms arrive with y intact, driven-matter transport works.
Bars pre-registered in docs/amendments/g112_driven_matter.md.
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
VX = 6.0
MAXT = 260
FARX = 20.0
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
    y0 = {i: float(w.k_pos[i, 1]) for i in drive}
    x0 = {i: float(w.k_pos[i, 0]) for i in drive}
    arrived = {i: None for i in drive}   # tick of arrival or None
    for t in range(MAXT):
        for i in drive:
            if w.k_alive[i]:
                w.k_vel[i, 0] = VX
        tick(w, c.dt)
        for i in drive:
            if arrived[i] is None and w.k_alive[i] and w.k_pos[i, 0] > FARX:
                arrived[i] = t + 1
    res = []
    for i in drive:
        alive = bool(w.k_alive[i])
        x = float(w.k_pos[i, 0]) if alive else -1.0
        ydrift = abs(float(w.k_pos[i, 1]) - y0[i]) if alive else -1.0
        res.append(dict(x0=round(x0[i], 1), alive=alive, xf=round(x, 1),
                        arrived=arrived[i], ydrift=round(ydrift, 2)))
    return res


if __name__ == "__main__":
    print(f"=== G112: driven-matter transport (drive {NDRIVE} atoms +x for {MAXT} ticks, far x>{FARX}) ===", flush=True)
    any_arrived = False
    yok = True
    for seed in [42, 7]:
        res = run(seed)
        print(f"  seed {seed}:", flush=True)
        for r in res:
            print(f"     x0={r['x0']:>5} alive={r['alive']} xf={r['xf']:>6} arrived_tick={r['arrived']} ydrift={r['ydrift']}", flush=True)
        for r in res:
            if r['arrived'] is not None:
                any_arrived = True
                if r['ydrift'] > 3.0:
                    yok = False
    print("\n--- VERDICT ---", flush=True)
    print(f"G112a any driven atom reached far side alive: {any_arrived}", flush=True)
    print(f"G112b y (symbol) preserved on arrivals (<3) : {yok if any_arrived else 'n/a'}", flush=True)
    if any_arrived and yok:
        print("G112: PASS - slow driven MATTER transports across distance with y/symbol preserved (the open avenue is real)", flush=True)
    elif any_arrived:
        print("G112: PARTIAL - matter arrives but y/symbol scrambled en route", flush=True)
    else:
        print("G112: NULL - driven atoms do not reach the far side within the window (bind/decay/stall en route); driven-matter transport not demonstrated", flush=True)
    print("DONE", flush=True)

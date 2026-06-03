"""G113 — multi-symbol MATTER transmission line: capstone of the driven-matter discovery.
Drive M leftmost atoms across the box (re-asserting k_vel each tick). Each atom's SOURCE y-band (K bins)
is its symbol; classify each by its ARRIVAL y-band; measure symbol accuracy. Demonstrates a K-ary
transmission line over distance via driven matter (the over-distance analogue of the co-located codec).
Bars pre-registered in docs/amendments/g113_matter_channel.md.
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
VX = 6.0
MAXT = 280
FARX = 20.0
M = 16
K = 3
YSPAN = (6.0, 24.0)


def yband(y):
    lo, hi = YSPAN
    b = int((y - lo) / (hi - lo) * K)
    return min(max(b, 0), K - 1)


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
    drive = [int(i) for i in order[:M]]
    src_band = {i: yband(float(w.k_pos[i, 1])) for i in drive}
    arr_band = {i: None for i in drive}
    for t in range(MAXT):
        for i in drive:
            if w.k_alive[i]:
                w.k_vel[i, 0] = VX
        tick(w, c.dt)
        for i in drive:
            if arr_band[i] is None and w.k_alive[i] and w.k_pos[i, 0] > FARX:
                arr_band[i] = yband(float(w.k_pos[i, 1]))
    arrived = [i for i in drive if arr_band[i] is not None]
    correct = sum(1 for i in arrived if arr_band[i] == src_band[i])
    return dict(n=len(drive), arrived=len(arrived),
                acc=(correct / len(arrived) if arrived else 0.0))


if __name__ == "__main__":
    print(f"=== G113: matter transmission line — {M} atoms, K={K} y-bands, drive {MAXT} ticks ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: arrived={R[s]['arrived']}/{R[s]['n']} | symbol-acc(on arrivals)={R[s]['acc']:.2f} (chance={1.0/K:.2f})", flush=True)
    G113a = all(R[s]['arrived'] >= 0.5 * R[s]['n'] for s in seeds)
    G113b = all(R[s]['acc'] >= 0.85 for s in seeds)
    passed = G113a and G113b
    print("\n--- VERDICT ---", flush=True)
    print(f"G113a majority of atoms arrive (>=50%): {G113a}", flush=True)
    print(f"G113b symbol preserved (acc>=0.85)    : {G113b}", flush=True)
    if passed:
        print("G113: PASS - driven matter is a K-ary transmission line over distance (symbols recovered at the far end)", flush=True)
    elif G113a:
        print("G113: PARTIAL - atoms arrive but the symbol (y-band) is not reliably preserved", flush=True)
    else:
        print("G113: NULL - too few atoms complete the traverse", flush=True)
    out = __import__('pathlib').Path.home() / ".eqmod" / "bet" / "G113"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(__import__('json').dumps({"rows": {str(s): R[s] for s in seeds}, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

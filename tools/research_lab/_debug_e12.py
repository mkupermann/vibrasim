import math
import sys
sys.path.insert(0, "tools/research_lab")
import numpy as np
from core import make_state, N_STEPS, DT, LEAK, E_FORM, TAU_B

# geometries: (name, chi, gain)
geoms = [
    ("G1", 0.0, 1.2),
    ("G2", 0.5, 0.8),
    ("G3", 0.0, 0.3),
    ("G4", 1.2, 0.5),
]


def phi(chi):
    return 1.0 / (1.0 + (chi ** 2) * 2.5)


def run(seed0, feedback=True):
    states = [make_state(seed0 + i) for i in range(len(geoms))]
    for s in states:
        s.res[:] = 0.0
    pool = 0.3
    caps = [0.0] * len(geoms)
    bonds = [0.0] * len(geoms)
    for step in range(N_STEPS):
        pool += DT * 0.006
        draws = []
        for i, s in enumerate(states):
            live = s.bond_age >= 0.0
            g = (0.08 + geoms[i][2]) if (feedback and live) else 0.03
            draws.append(g * phi(geoms[i][1]))
        tot = sum(draws) + 1e-12
        for i, s in enumerate(states):
            deliv = pool * (draws[i] / tot)
            inc = deliv * 0.9
            s.res += inc
            caps[i] += inc
            pool -= deliv
        pool = max(0.0, pool - DT * 0.02 * pool)
        half = E_FORM
        for i, s in enumerate(states):
            funds = float(s.res[0] + s.res[1])
            if s.bond_age >= 0.0:
                s.bond_age += DT
                if s.bond_age >= TAU_B:
                    s.bond_age = -1.0
            elif funds >= half:
                s.res[:] = max(0.0, funds - half) * 0.5
                s.bond_age = 0.0
            s.res = np.minimum(np.maximum(s.res - DT * LEAK * s.res, 0.0), 0.04)
            if s.bond_age >= 0.0:
                bonds[i] += DT
    return {geoms[i][0]: bonds[i] for i in range(len(geoms))}, caps


# forecast: rank by phi*gain
score_map = {n: phi(c) * g for n, c, g in geoms}
order_pred = sorted(score_map, key=score_map.get, reverse=True)
print("predicted order", order_pred, "scores", {k: round(v, 3) for k, v in score_map.items()})

bonds, caps = run(370, True)
order_obs = sorted(bonds, key=bonds.get, reverse=True)
print("observed bonds", {k: round(v, 2) for k, v in bonds.items()}, "order", order_obs)
print("captured", {k: round(v, 3) for k, v in zip([g[0] for g in geoms], caps)})

bonds_off, _ = run(370, False)
spread = max(bonds.values()) - min(bonds.values())
spread_off = max(bonds_off.values()) - min(bonds_off.values())
print("spread", round(spread, 2), "off_spread", round(spread_off, 2))

# Spearman on 4 items
def spearman(a, b):
    n = len(a)
    ra = {k: i for i, k in enumerate(a)}
    rb = {k: i for i, k in enumerate(b)}
    d2 = sum((ra[k] - rb[k]) ** 2 for k in a)
    return 1 - 6 * d2 / (n * (n * n - 1))

print("F12.1 spearman", spearman(order_pred, order_obs), spearman(order_pred, order_obs) == 1)
print("F12.2 spread>=10", spread >= 10)
print("F12.3 top is G1", order_obs[0] == "G1")
print("F12.4 off spread<5", spread_off < 5)

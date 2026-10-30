import sys
sys.path.insert(0, "tools/research_lab")
import numpy as np
from core import make_state, N_STEPS, DT, LEAK, E_FORM, TAU_B

geoms = [("G1", 0.0, 1.2), ("G2", 0.5, 0.8), ("G3", 0.0, 0.3), ("G4", 1.2, 0.5)]


def phi(chi, flat=False):
    return 1.0 if flat else 1.0 / (1.0 + (chi ** 2) * 2.5)


def run(seed0, *, self_boost=True, use_phi=True, flat_phi=False, equal_transport=False):
    states = [make_state(seed0 + i) for i in range(4)]
    for s in states:
        s.res[:] = 0.0
    pool = 0.3
    bonds = [0.0] * 4
    for _ in range(N_STEPS):
        pool += DT * 0.006
        draws = []
        for i, s in enumerate(states):
            live = s.bond_age >= 0.0
            gain = 0.3 if equal_transport else geoms[i][2]
            if self_boost and live:
                g = 0.08 + gain
            else:
                g = 0.03
            p = phi(geoms[i][1], flat=flat_phi) if use_phi else 1.0
            draws.append(g * p)
        tot = sum(draws) + 1e-12
        pool_snapshot = pool
        for i, s in enumerate(states):
            deliv = pool_snapshot * (draws[i] / tot)
            s.res += deliv * 0.9
            pool -= deliv
        pool = max(0.0, pool - DT * 0.02 * pool)
        for i, s in enumerate(states):
            funds = float(s.res[0] + s.res[1])
            if s.bond_age >= 0.0:
                s.bond_age += DT
                if s.bond_age >= TAU_B:
                    s.bond_age = -1.0
            elif funds >= E_FORM:
                s.res[:] = max(0.0, funds - E_FORM) * 0.5
                s.bond_age = 0.0
            s.res = np.minimum(np.maximum(s.res - DT * LEAK * s.res, 0.0), 0.04)
            if s.bond_age >= 0.0:
                bonds[i] += DT
    return bonds


def ens(n=20, **kw):
    acc = np.zeros(4)
    for k in range(n):
        acc += np.array(run(400 + k * 10, **kw))
    return acc / n


# F14.1 single-seed true null
b1 = run(400, self_boost=False, use_phi=True, flat_phi=True, equal_transport=True)
print("F14.1 null single", [round(x, 1) for x in b1], "spread", round(max(b1) - min(b1), 2),
      max(b1) - min(b1) < 5)

# F14.2 ensemble identical, no self-boost
e_null = ens(20, self_boost=False, use_phi=True, flat_phi=True, equal_transport=True)
print("F14.2 ens null", [round(x, 2) for x in e_null], "range", round(e_null.max() - e_null.min(), 2),
      e_null.max() - e_null.min() < 5)

# F14.3 ensemble with self-boost, identical geometry
e_sb = ens(20, self_boost=True, use_phi=True, flat_phi=True, equal_transport=True)
print("F14.3 ens selfboost", [round(x, 2) for x in e_sb], "range", round(e_sb.max() - e_sb.min(), 2),
      e_sb.max() - e_sb.min() >= 10)

# F14.4 both maps
e_full = ens(20, self_boost=True, use_phi=True, flat_phi=False, equal_transport=False)
print("F14.4 ens full", [round(x, 2) for x in e_full], "G1 top", e_full[0] == e_full.max())

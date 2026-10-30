import sys
sys.path.insert(0, "tools/research_lab")
import numpy as np
from core import make_state, N_STEPS, DT, LEAK, E_FORM, TAU_B

geoms = [
    ("G1", 0.0, 1.2),
    ("G2", 0.5, 0.8),
    ("G3", 0.0, 0.3),
    ("G4", 1.2, 0.5),
]


def phi(chi, flat=False):
    return 1.0 if flat else 1.0 / (1.0 + (chi ** 2) * 2.5)


def run(seed0=380, *, use_phi=True, use_transport=True, flat_phi=False, equal_transport=False):
    states = [make_state(seed0 + i) for i in range(len(geoms))]
    for s in states:
        s.res[:] = 0.0
    pool = 0.3
    bonds = [0.0] * len(geoms)
    for step in range(N_STEPS):
        pool += DT * 0.006
        draws = []
        for i, s in enumerate(states):
            live = s.bond_age >= 0.0
            gain = 0.3 if equal_transport else geoms[i][2]
            g = (0.08 + gain) if (use_transport and live) else 0.03
            p = phi(geoms[i][1], flat=flat_phi) if use_phi else 1.0
            draws.append(g * p)
        tot = sum(draws) + 1e-12
        for i, s in enumerate(states):
            deliv = pool * (draws[i] / tot)
            s.res += deliv * 0.9
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
    return {geoms[i][0]: bonds[i] for i in range(len(geoms))}


def order(b):
    return sorted(b, key=b.get, reverse=True)


def spread(b):
    return max(b.values()) - min(b.values())


both = run(use_phi=True, use_transport=True)
t_only = run(use_phi=False, use_transport=True, equal_transport=False)
p_only = run(use_phi=True, use_transport=True, equal_transport=True, flat_phi=False)
# phi cut = flat, transport equal
neither = run(use_phi=True, use_transport=True, flat_phi=True, equal_transport=True)
# true both-cut: no live transport boost and no phi
both_cut = run(use_phi=False, use_transport=False)

print("both   ", {k: round(v, 1) for k, v in both.items()}, order(both))
print("t_only ", {k: round(v, 1) for k, v in t_only.items()}, order(t_only))
print("p_only ", {k: round(v, 1) for k, v in p_only.items()}, order(p_only))
print("flat+eq", {k: round(v, 1) for k, v in neither.items()}, "spread", spread(neither))
print("both_cut", {k: round(v, 1) for k, v in both_cut.items()}, "spread", spread(both_cut))

print("F13.1 cut transport only (phi remains)", spread(t_only) >= 10, spread(t_only))
# F13.2: flat phi + equal transport
print("F13.2 flat+eq spread<5", spread(neither) < 5, spread(neither))
print("F13.3 both-cut spread<5", spread(both_cut) < 5, spread(both_cut))
print("F13.4 restore matches G1 top", order(both)[0] == "G1")

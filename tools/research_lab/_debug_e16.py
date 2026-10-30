import sys
sys.path.insert(0, "tools/research_lab")
import numpy as np
from core import make_state, N_STEPS, DT, LEAK, E_FORM, TAU_B

# geometries
G1 = ("G1", 0.0, 1.2)   # chi, gain
G4 = ("G4", 1.2, 0.5)


def phi(chi):
    return 1.0 / (1.0 + (chi ** 2) * 2.5)


def run_pop(composition, seed0=600):
    """composition: list of geometry tuples length 4."""
    n = len(composition)
    states = [make_state(seed0 + i) for i in range(n)]
    for s in states:
        s.res[:] = 0.0
    pool = 0.3
    bonds = [0.0] * n
    for _ in range(N_STEPS):
        pool += DT * 0.006
        draws = []
        for i, s in enumerate(states):
            live = s.bond_age >= 0.0
            g = (0.08 + composition[i][2]) if live else 0.03
            draws.append(g * phi(composition[i][1]))
        tot = sum(draws) + 1e-12
        snap = pool
        for i, s in enumerate(states):
            deliv = snap * (draws[i] / tot)
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
    # aggregate by type
    g1 = sum(bonds[i] for i in range(n) if composition[i][0] == "G1")
    g4 = sum(bonds[i] for i in range(n) if composition[i][0] == "G4")
    total = g1 + g4 + 1e-12
    return g1, g4, g1 / total


def ens(comp, n=8):
    shares = []
    for k in range(n):
        g1, g4, sh = run_pop(comp, seed0=600 + k * 11)
        shares.append(sh)
    return float(np.mean(shares)), shares


for label, comp in [
    ("1G1+3G4", [G1, G4, G4, G4]),
    ("3G1+1G4", [G1, G1, G1, G4]),
    ("4G4", [G4, G4, G4, G4]),
    ("1G4+3G1", [G4, G1, G1, G1]),
]:
    mean_sh, raw = ens(comp)
    print("%s  mean_G1_share=%.3f  raw=%s" % (label, mean_sh, [round(x, 3) for x in raw[:3]]))

m1, _ = ens([G1, G4, G4, G4])
m2, _ = ens([G1, G1, G1, G4])
m3, _ = ens([G4, G4, G4, G4])
m4, _ = ens([G4, G1, G1, G1])
print("F16.1 1G1 share>=0.5", m1 >= 0.5, m1)
print("F16.2 3G1 share>=0.5", m2 >= 0.5, m2)
print("F16.3 4G4 ~0.25", abs(m3 - 0.25) < 0.05, m3)
print("F16.4 G4 minority share<0.25", (1 - m4) < 0.25, 1 - m4)

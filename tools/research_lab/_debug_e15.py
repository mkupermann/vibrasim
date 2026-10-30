import sys
sys.path.insert(0, "tools/research_lab")
import numpy as np
from core import make_state, N_STEPS, DT, LEAK, E_FORM, TAU_B


def phi(chi):
    return 1.0 / (1.0 + (chi ** 2) * 2.5)


def run_pair(seed0, *, chi_a, chi_b, gain_a, gain_b, self_boost=True):
    states = [make_state(seed0), make_state(seed0 + 1)]
    for s in states:
        s.res[:] = 0.0
    pool = 0.25
    bonds = [0.0, 0.0]
    chis = (chi_a, chi_b)
    gains = (gain_a, gain_b)
    for _ in range(N_STEPS):
        pool += DT * 0.006
        draws = []
        for i, s in enumerate(states):
            live = s.bond_age >= 0.0
            g = (0.08 + gains[i]) if (self_boost and live) else 0.03
            draws.append(g * phi(chis[i]))
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
    return bonds


def ens(n, **kw):
    acc = np.zeros(2)
    for k in range(n):
        acc += np.array(run_pair(500 + k * 7, **kw))
    return acc / n


print("dose-response (ensemble n=12)")
print("gain_dose  range")
for d in (0.0, 0.02, 0.05, 0.1, 0.2, 0.4):
    e = ens(12, chi_a=0.0, chi_b=0.0, gain_a=0.5 + d, gain_b=0.5)
    print("  dgain=%.2f  A=%.2f B=%.2f range=%.2f" % (d, e[0], e[1], e.max() - e.min()))

print("chi_dose   range")
for d in (0.0, 0.05, 0.1, 0.2, 0.4, 0.8):
    e = ens(12, chi_a=0.0, chi_b=d, gain_a=0.5, gain_b=0.5)
    print("  dchi=%.2f   A=%.2f B=%.2f range=%.2f" % (d, e[0], e[1], e.max() - e.min()))

e0 = ens(12, chi_a=0.0, chi_b=0.0, gain_a=0.5, gain_b=0.5)
e2 = ens(12, chi_a=0.0, chi_b=0.0, gain_a=0.52, gain_b=0.5)
print("F15.1 dgain=0.02 range>=5", e2.max() - e2.min() >= 5, e2.max() - e2.min())
e1 = ens(12, chi_a=0.0, chi_b=0.1, gain_a=0.5, gain_b=0.5)
print("F15.2 dchi=0.1 range>=5", e1.max() - e1.min() >= 5, e1.max() - e1.min())
print("F15.4 dose=0 range==0", abs(e0.max() - e0.min()) < 1e-9, e0.max() - e0.min())

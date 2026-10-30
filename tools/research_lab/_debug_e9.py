import sys
sys.path.insert(0, "tools/research_lab")
from core import run_resonant_competition

seeds = range(330, 333)


def gap(**kw):
    r = run_resonant_competition(seeds=seeds, inflow=0.006, **kw)
    return r


# 2x2: phi (detuned B) x transport (unequal gains)
cells = {
    "phi_on_t_on": gap(chi_a=0.0, chi_b=1.2, feedback=True,
                       phi_flat=False, gain_a=1.2, gain_b=0.3),
    "phi_off_t_on": gap(chi_a=0.0, chi_b=0.0, feedback=True,
                        phi_flat=True, gain_a=1.2, gain_b=0.3),
    "phi_on_t_off": gap(chi_a=0.0, chi_b=1.2, feedback=True,
                        phi_flat=False, gain_a=0.3, gain_b=0.3),
    "phi_off_t_off": gap(chi_a=0.0, chi_b=0.0, feedback=True,
                         phi_flat=True, gain_a=0.3, gain_b=0.3),
}

for name, r in cells.items():
    print("%s  A=%.2f B=%.2f gap=%.2f win=%s"
          % (name, r["mean_A"], r["mean_B"], r["gap"], r["winner"]))

g_tot = cells["phi_on_t_on"]["gap"]
g_phi = cells["phi_on_t_off"]["gap"]
g_t = cells["phi_off_t_on"]["gap"]
g_0 = cells["phi_off_t_off"]["gap"]
print("main_phi", round(g_tot - g_t, 2), "need >10")
print("main_t", round(g_tot - g_phi, 2), "need >10")
print("interaction", round(g_tot - g_phi - g_t + g_0, 2),
      "sub-additive if combined < g_phi+g_t:", g_tot, g_phi + g_t)
print("F9.1", (g_tot - g_t) > 10)
print("F9.2", (g_tot - g_phi) > 10)
print("F9.3", g_tot < (g_phi + g_t))
print("F9.4", cells["phi_on_t_on"]["winner"] == "A")

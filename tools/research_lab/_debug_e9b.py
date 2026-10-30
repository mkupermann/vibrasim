import sys
sys.path.insert(0, "tools/research_lab")
from core import run_resonant_competition

seeds = range(340, 343)


def cell(**kw):
    return run_resonant_competition(seeds=seeds, inflow=0.0025, **kw)


cells = {
    "both_on": cell(chi_a=0.0, chi_b=1.2, phi_flat=False, gain_a=1.2, gain_b=0.3),
    "phi_only": cell(chi_a=0.0, chi_b=1.2, phi_flat=False, gain_a=0.3, gain_b=0.3),
    "t_only": cell(chi_a=0.0, chi_b=0.0, phi_flat=True, gain_a=1.2, gain_b=0.3),
    "neither": cell(chi_a=0.0, chi_b=0.0, phi_flat=True, gain_a=0.3, gain_b=0.3),
}

print("=== low inflow 0.0025 (less ceiling) ===")
for name, r in cells.items():
    print("%s  S_A=%.1f S_B=%.1f gap=%.2f capA=%.3f capB=%.3f"
          % (name, r["mean_A"], r["mean_B"], r["gap"],
             r["captured_A"], r["captured_B"]))

# main effects on INCOME (not horizon-clipped S)
def cap_gap(r):
    return abs(r["captured_A"] - r["captured_B"])

print("income main_phi", cap_gap(cells["both_on"]) - cap_gap(cells["t_only"]))
print("income main_t", cap_gap(cells["both_on"]) - cap_gap(cells["phi_only"]))
print("F9.2 income main_t > 0.05", (cap_gap(cells["both_on"]) - cap_gap(cells["phi_only"])) > 0.05)

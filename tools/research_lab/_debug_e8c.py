import sys
sys.path.insert(0, "tools/research_lab")
from core import run_resonant_competition

on = run_resonant_competition(
    chi_a=0.0, chi_b=0.0, feedback=True, swap=False,
    phi_flat=True, gain_a=10.0, gain_b=0.01,
    seeds=range(320, 322), inflow=0.006)
print("extreme gains on", on["mean_A"], on["mean_B"], on["gap"], on["winner"])
print("wins", on["wins"], "capA", on["captured_A"], "capB", on["captured_B"])

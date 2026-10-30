import sys
sys.path.insert(0, "tools/research_lab")
from core import run_resonant_competition

for inf in (0.004, 0.006, 0.008):
    on = run_resonant_competition(
        chi_a=0.0, chi_b=0.0, feedback=True, swap=False,
        phi_flat=True, gain_a=1.2, gain_b=0.3,
        seeds=range(310, 312), inflow=inf)
    off = run_resonant_competition(
        chi_a=0.0, chi_b=0.0, feedback=False, swap=False,
        phi_flat=True, gain_a=1.2, gain_b=0.3,
        seeds=range(310, 312), inflow=inf)
    print("inflow=%.3f  on gap=%.2f A=%.1f B=%.1f  off gap=%.2f"
          % (inf, on["gap"], on["mean_A"], on["mean_B"], off["gap"]))

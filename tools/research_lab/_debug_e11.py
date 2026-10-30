import sys
sys.path.insert(0, "tools/research_lab")
import core
from core import run_law_R_curve, run_p2mini, N_STEPS

chis = [-0.8, -0.5, -0.3, -0.15, 0.0, 0.15, 0.3, 0.5, 0.8, 1.2]
base_eform = core.E_FORM
base_tau = core.TAU_B

results = []
for ratio in (0.003, 0.006, 0.012):
    # amortized cost = E_form / TAU_b; keep TAU_b=10, scale E_form
    core.E_FORM = ratio * core.TAU_B
    vals = run_law_R_curve(chis, seeds=range(360, 362))
    peak = chis[vals.index(max(vals))]
    spread = max(vals) - min(vals)
    lock = run_p2mini(0.5, feedback=True, driven=False, drive_amp=0.0, seeds=range(360, 362))
    nofb = run_p2mini(0.5, feedback=False, driven=False, drive_amp=0.0, seeds=range(360, 362))
    dlock = lock - nofb
    results.append((ratio, core.E_FORM, peak, spread, dlock))
    print("ratio=%.3f E_form=%.3f  peak=%+.2f  spread=%.2f  dlock=%+.2f"
          % (ratio, core.E_FORM, peak, spread, dlock))

core.E_FORM = base_eform

print("F11.1", all(abs(r[2]) <= 0.5 for r in results))
print("F11.2", all(r[4] <= 0 for r in results))
print("F11.3", all(r[3] >= 5 for r in results))

import sys
sys.path.insert(0, "tools/research_lab")
from core import run_competition

for fb, sw in [(True, False), (False, False), (True, True)]:
    r = run_competition(feedback=fb, swap=sw)
    print("fb=%s swap=%s  A=%.3f B=%.3f gap=%.4f win=%s capA=%.4f capB=%.4f" % (
        fb, sw, r["A_bond_time"], r["B_bond_time"], r["share_gap"],
        r["winner"], r["captured_A"], r["captured_B"]))

"""G131 — can the substrate LEARN an A->B association? (decisive learnability test)
Train: repeatedly present stimulus A (inject at loc A) then stimulus B (loc B), so STDP/BTSP/correlation
plasticity could wire A->B. Test: present A ALONE; measure B-region firing vs (i) an UNTRAINED control and
(ii) a CONTROL region C (specificity). If trained A-alone evokes B-region activity above untrained AND
specifically (B not C), the substrate learned. If not, it cannot learn associations -> no cognition.
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
AX, BX, CX = 7.0, 15.0, 23.0
N_TRAIN = 60
GAP = 3
REG = 3.0


def region_fire(w, cx):
    K_ = w.k_count
    if K_ == 0:
        return 0.0
    al = w.k_alive[:K_]; x = w.k_pos[:K_, 0]
    fired = getattr(w, 'k_fired', None)
    sel = al & (np.abs(x - cx) < REG)
    if fired is not None:
        return float((fired[:K_] & sel).sum())
    return float(np.abs(w.k_charge[:K_][sel]).sum())   # fallback: charge as activity proxy


def probe_A(w, c, box):
    inject_tight(w, c, box, AX, n=14)
    for _ in range(GAP):
        tick(w, c.dt)
    return region_fire(w, BX), region_fire(w, CX)


def run(seed, train):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c); box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    if train:
        for _ in range(N_TRAIN):
            inject_tight(w, c, box, AX, n=14)
            for _ in range(GAP):
                tick(w, c.dt)
            inject_tight(w, c, box, BX, n=14)      # A then B, repeatedly
            for _ in range(GAP):
                tick(w, c.dt)
    # PROBE: A alone, measure B vs C response
    bvals, cvals = [], []
    for _ in range(10):
        bf, cf = probe_A(w, c, box)
        bvals.append(bf); cvals.append(cf)
    return float(np.mean(bvals)), float(np.mean(cvals))


if __name__ == "__main__":
    print("=== G131: associative learning A->B (can the substrate learn?) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        bt, ct = run(s, train=True)
        bu, cu = run(s, train=False)
        R[s] = dict(trained_B=round(bt, 1), trained_C=round(ct, 1), untrained_B=round(bu, 1))
        print(f"  seed {s}: trained A->B response={bt:.1f} (ctrl-region C={ct:.1f}) | untrained A->B={bu:.1f}", flush=True)
    # learning: trained B > untrained B (by >50%) AND specific: trained B > trained C
    learned = all((R[s]['trained_B'] > 1.5 * max(R[s]['untrained_B'], 1.0)) and
                  (R[s]['trained_B'] > 1.5 * max(R[s]['trained_C'], 1.0)) for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G131 substrate learned A->B (trained>1.5x untrained AND >1.5x ctrl-region, both seeds): {learned}", flush=True)
    print(("G131: PASS - the substrate LEARNED an association (surprising; reopens cognition)"
           if learned else "G131: NULL - the substrate does NOT learn A->B; it cannot form associations -> no cognitive/communication capacity from its own dynamics (the boundary, with evidence)"), flush=True)
    print("DONE", flush=True)

"""G130 — within-run head-to-head validating the core discovery: ACTIVITY spreads, matter POSITION doesn't.
Place atoms at cell A, deposit charge into them (activate), run; measure (1) the ACTIVITY readout — summed
|charge| in the A-region vs the neighbour B-region (does activity spread A->B?), and (2) the POSITION
readout — atom count in A vs B (does the matter move to B?). If activity spreads to B while atoms stay at
A, the discovery's mechanism is validated: the same write leaks in the activity representation but stays
selective in the position representation.
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
AX, BX = 10.0, 18.0
REG = 2.5
Q = 6.0
T = 60


def region_charge(w, cx):
    K_ = w.k_count
    al = w.k_alive[:K_]; x = w.k_pos[:K_, 0]
    sel = al & (np.abs(x - cx) < REG)
    return float(np.abs(w.k_charge[:K_][sel]).sum())


def region_atoms(w, cx):
    K_ = w.k_count
    al = w.k_alive[:K_]; x = w.k_pos[:K_, 0]
    return int((al & (np.abs(x - cx) < REG)).sum())


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    # atoms present from the settled lattice; record initial A/B atom counts
    a_atoms0, b_atoms0 = region_atoms(w, AX), region_atoms(w, BX)
    # ACTIVATE: deposit charge into A-region atoms
    K_ = w.k_count
    al = w.k_alive[:K_]; x = w.k_pos[:K_, 0]
    aidx = np.where(al & (np.abs(x - AX) < REG))[0]
    w.k_charge[:K_][aidx] += Q
    aQ0 = region_charge(w, AX)
    for _ in range(T):
        tick(w, c.dt)
    aQ, bQ = region_charge(w, AX), region_charge(w, BX)
    a_atoms, b_atoms = region_atoms(w, AX), region_atoms(w, BX)
    return dict(aQ0=round(aQ0, 1), aQ=round(aQ, 1), bQ=round(bQ, 1),
                charge_spread=(bQ / aQ if aQ > 1e-6 else 0.0),
                b_atoms_gain=b_atoms - b_atoms0, a_atoms=a_atoms, b_atoms=b_atoms)


if __name__ == "__main__":
    print("=== G130: head-to-head — ACTIVITY spreads vs POSITION stays (validates the discovery) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: chargeA0={R[s]['aQ0']} -> chargeA={R[s]['aQ']} chargeB={R[s]['bQ']} "
              f"(spread B/A={R[s]['charge_spread']:.2f}) | B-region atom gain={R[s]['b_atoms_gain']}", flush=True)
    G130a = all(R[s]['charge_spread'] >= 0.2 for s in seeds)        # activity (charge) spreads A->B
    G130b = all(R[s]['b_atoms_gain'] <= 0 for s in seeds)           # position does NOT move to B
    passed = G130a and G130b
    print("\n--- VERDICT ---", flush=True)
    print(f"G130a ACTIVITY spreads A->B (charge B/A>=0.2 both)   : {G130a}", flush=True)
    print(f"G130b POSITION stays (no atom gain in B, both)       : {G130b}", flush=True)
    print(("G130: PASS - within one run: the activity (charge) of a written pattern SPREADS to the neighbour while the matter POSITION does NOT — the discovery's mechanism, directly validated"
           if passed else "G130: NULL/PARTIAL - the activity-spreads / position-stays asymmetry did not hold (see output)"), flush=True)
    print("DONE", flush=True)

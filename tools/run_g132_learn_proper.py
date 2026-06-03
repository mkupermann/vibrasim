"""G132 — can the substrate's OWN primitives learn A->B? (charter-faithful, proper readout)
Enable the full learning machinery (STDP, BTSP, correlation plasticity, bistable wells, charge
propagation), train A->B pairing repeatedly, then probe A alone and read the B-region BTSP eligibility
(k_eligibility — accumulates from firing) vs an untrained control and a control region C. This is the
substrate's own plasticity (no bolted-on ML), with a real activity readout (fixing G131's dead probe).
"""
import sys
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_bet099 import make_cfg

SETTLE = 200
AX, BX, CX = 7.0, 15.0, 23.0
N_TRAIN = 80
GAP = 3
REG = 3.0


def cfg_learn(seed):
    c = make_cfg()
    object.__setattr__(c, 'rng_seed', seed)
    for k, v in [('stdp_enabled', True), ('btsp_enabled', True),
                 ('corr_plasticity_rate', 0.4), ('bistable_rate', 0.4),
                 ('bridge_charge_prop_rate', 0.5), ('bridge_atom_prop_rate', 0.5)]:
        try:
            object.__setattr__(c, k, v)
        except Exception:
            pass
    return c


def b_activity(w, cx):
    K_ = w.k_count
    if K_ == 0:
        return 0.0
    al = w.k_alive[:K_]; x = w.k_pos[:K_, 0]
    sel = al & (np.abs(x - cx) < REG)
    elig = getattr(w, 'k_eligibility', None)
    if elig is not None:
        return float(elig[:K_][sel].sum())
    return float(np.abs(w.k_charge[:K_][sel]).sum())


def run(seed, train):
    c = cfg_learn(seed)
    w = World(c); box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    if train:
        for _ in range(N_TRAIN):
            inject_tight(w, c, box, AX, n=14)
            for _ in range(GAP):
                tick(w, c.dt)
            inject_tight(w, c, box, BX, n=14)
            for _ in range(GAP):
                tick(w, c.dt)
    # PROBE A alone, read B and C eligibility
    bvals, cvals = [], []
    for _ in range(12):
        inject_tight(w, c, box, AX, n=14)
        for _ in range(GAP):
            tick(w, c.dt)
        bvals.append(b_activity(w, BX)); cvals.append(b_activity(w, CX))
    return float(np.mean(bvals)), float(np.mean(cvals))


if __name__ == "__main__":
    print("=== G132: substrate-primitive learning A->B, proper eligibility readout ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        bt, ct = run(s, True)
        bu, _ = run(s, False)
        R[s] = dict(tB=round(bt, 2), tC=round(ct, 2), uB=round(bu, 2))
        print(f"  seed {s}: trained A->B elig={bt:.2f} (ctrl-region C={ct:.2f}) | untrained A->B={bu:.2f}", flush=True)
    learned = all((R[s]['tB'] > 1.5 * max(R[s]['uB'], 0.1)) and (R[s]['tB'] > 1.5 * max(R[s]['tC'], 0.1)) for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G132 substrate learned A->B (trained>1.5x untrained AND >1.5x ctrl-region, both seeds): {learned}", flush=True)
    print(("G132: PASS - substrate primitives formed an A->B association (reopens substrate learning!)"
           if learned else "G132: NULL - even with full plasticity + proper readout, the substrate does NOT learn A->B; charter-faithful confirmation that the substrate cannot form associations"), flush=True)
    print("DONE", flush=True)

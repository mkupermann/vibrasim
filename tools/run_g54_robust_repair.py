"""G54 — robust fluid self-repair. Strengthen G53's healing: longer window (500), stronger
edge-closure (2.0), rates {0.1, 0.15}. Does a fluid membrane robustly self-repair on both seeds?

Pre-registered bars in docs/amendments/g54_robust_fluid_repair.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg
from tools.run_g46_self_repair import component, wound, SETTLE

RATES = [0.1, 0.15]
REPAIR = 500


def run(seed, rate, do_wound):
    c = replace(cfg(seed), bond_turnover_rate=rate, node_thermal_speed=0.2, edge_closure_k=2.0)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    comp = component(w); n0 = len(comp)
    if n0 < 8:
        return dict(n0=n0, post=0, final=0, peak=0, heal=0.0, persist=0.0)
    post = n0
    if do_wound:
        wound(w, comp, np.asarray(c.box_size))
        post = len(component(w))
    sizes = []
    for t in range(REPAIR):
        tick(w, c.dt)
        if t % 20 == 19:
            sizes.append(len(component(w)))
    final = float(np.mean(sizes[-3:])) if len(sizes) >= 3 else (sizes[-1] if sizes else 0)
    peak = max(sizes + [n0])
    heal = (final - post) / max(n0 - post, 1) if do_wound else 0.0
    return dict(n0=n0, post=post, final=final, peak=peak, heal=heal, persist=final / max(peak, 1))


if __name__ == "__main__":
    print("=== G54: robust fluid self-repair (window 500, edge-closure 2.0) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        for rate in RATES:
            R[(s, rate, 'w')] = run(s, rate, True)
            R[(s, rate, 'u')] = run(s, rate, False)
            w_, u_ = R[(s, rate, 'w')], R[(s, rate, 'u')]
            print(f"  seed {s} rate={rate}: wounded N0={w_['n0']} post={w_['post']} final={w_['final']:.0f} "
                  f"heal={w_['heal']:.2f} | unwound persist={u_['persist']:.2f}", flush=True)

    working = [r for r in RATES
               if all(R[(s, r, 'w')]['heal'] >= 0.3 for s in seeds)
               and all(R[(s, r, 'u')]['persist'] >= 0.7 for s in seeds)]
    G54a = any(all(R[(s, r, 'w')]['heal'] >= 0.3 for s in seeds) for r in RATES)
    G54b = len(working) > 0
    passed = G54a and G54b

    print("\n--- VERDICT ---", flush=True)
    print(f"working rate(s) (heal>=0.3 AND persist>=0.7, both seeds): {working}", flush=True)
    print(f"G54a robust healing (>=0.3 both)  : {G54a}", flush=True)
    print(f"G54b heals AND stays intact       : {G54b}", flush=True)
    verdict = ("PASS - FLUID ROBUSTLY SELF-REPAIRING membrane (rigidity ceiling broken; self-renewing cell precursor)"
               if passed else "NULL/partial - robust self-repair not reached; G53 partial stands")
    print(f"\nG54: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G54"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {f"{k[0]}_r{k[1]}_{k[2]}": v for k, v in R.items()},
                                                  "working": working, "G54a": G54a, "G54b": G54b, "passed": passed},
                                                 indent=2, default=str))
    print("DONE", flush=True)

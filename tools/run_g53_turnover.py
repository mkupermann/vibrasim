"""G53 — bond turnover fluid membrane. Sweep bond_turnover_rate (+ mobility + edge-closure):
does a fluid membrane self-repair a wound while staying intact?

Pre-registered bars in docs/amendments/g53_bond_turnover_fluid.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg
from tools.run_g46_self_repair import component, wound, SETTLE, REPAIR

RATES = [0.0, 0.1, 0.3]


def run(seed, rate, do_wound):
    c = replace(cfg(seed), bond_turnover_rate=rate, node_thermal_speed=0.2, edge_closure_k=1.0)
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
        if t % 10 == 9:
            sizes.append(len(component(w)))
    final = float(np.mean(sizes[-3:])) if len(sizes) >= 3 else (sizes[-1] if sizes else 0)
    peak = max(sizes + [n0])
    heal = (final - post) / max(n0 - post, 1) if do_wound else 0.0
    return dict(n0=n0, post=post, final=final, peak=peak, heal=heal, persist=final / max(peak, 1))


if __name__ == "__main__":
    print("=== G53: bond-turnover fluid membrane (self-repair + stability) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        for rate in RATES:
            R[(s, rate, 'w')] = run(s, rate, True)
            R[(s, rate, 'u')] = run(s, rate, False)
            w_, u_ = R[(s, rate, 'w')], R[(s, rate, 'u')]
            print(f"  seed {s} rate={rate}: wounded N0={w_['n0']} post={w_['post']} final={w_['final']:.0f} "
                  f"heal={w_['heal']:.2f} | unwound persist={u_['persist']:.2f} (final {u_['final']:.0f})", flush=True)

    G53a = all(R[(s, 0.0, 'w')]['heal'] < 0.1 for s in seeds)
    working = [r for r in RATES if r > 0
               and all(R[(s, r, 'w')]['heal'] >= 0.3 for s in seeds)
               and all(R[(s, r, 'u')]['persist'] >= 0.7 for s in seeds)]
    G53b = any(r > 0 and all(R[(s, r, 'w')]['heal'] >= 0.3 for s in seeds) for r in RATES)
    G53c = len(working) > 0
    passed = G53a and G53c

    print("\n--- VERDICT ---", flush=True)
    print(f"working rate(s) (heal>=0.3 AND persist>=0.7, both seeds): {working}", flush=True)
    print(f"G53a rigid no heal (<0.1)         : {G53a}", flush=True)
    print(f"G53b some rate heals (>=0.3)      : {G53b}", flush=True)
    print(f"G53c heals AND stays intact       : {G53c}", flush=True)
    verdict = ("PASS - bond turnover yields a FLUID SELF-REPAIRING membrane (rigidity ceiling broken)"
               if passed else "NULL/partial - fluidity/stability trade-off (no rate both heals and persists)")
    print(f"\nG53: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G53"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {f"{k[0]}_r{k[1]}_{k[2]}": v for k, v in R.items()},
                                                  "working": working, "G53a": G53a, "G53b": G53b,
                                                  "G53c": G53c, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

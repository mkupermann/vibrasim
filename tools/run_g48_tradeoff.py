"""G48 — persistence vs self-repair trade-off. Vary fusion_bond_block in {0, 2} x {wounded,
unwounded}; relaxed commitment should HEAL but LOSE persistence.

Pre-registered bars in docs/amendments/g48_persistence_repair_tradeoff.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg
from tools.run_g46_self_repair import component, wound, SETTLE, REPAIR


def run(seed, block, do_wound):
    c = replace(cfg(seed), fusion_bond_block=block)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    comp = component(w)
    n0 = len(comp)
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
    persist = final / max(peak, 1)
    return dict(n0=n0, post=post, final=final, peak=peak, heal=heal, persist=persist)


if __name__ == "__main__":
    print("=== G48: persistence vs self-repair trade-off ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        for block in (0, 2):
            for wnd in (True, False):
                R[(s, block, wnd)] = run(s, block, wnd)
        b0w = R[(s, 0, True)]; b0u = R[(s, 0, False)]
        b2w = R[(s, 2, True)]; b2u = R[(s, 2, False)]
        print(f"  seed {s}:", flush=True)
        print(f"    block=0 wounded:  N0={b0w['n0']} post={b0w['post']} final={b0w['final']:.0f} heal={b0w['heal']:.2f}", flush=True)
        print(f"    block=0 unwound:  N0={b0u['n0']} final={b0u['final']:.0f} persist={b0u['persist']:.2f}", flush=True)
        print(f"    block=2 wounded:  N0={b2w['n0']} post={b2w['post']} final={b2w['final']:.0f} heal={b2w['heal']:.2f}", flush=True)
        print(f"    block=2 unwound:  N0={b2u['n0']} final={b2u['final']:.0f} persist={b2u['persist']:.2f}", flush=True)

    G48a = all(R[(s, 0, True)]['heal'] >= 0.3 for s in seeds)
    G48b = all(R[(s, 0, False)]['persist'] <= 0.7 for s in seeds)
    G48c = all(R[(s, 2, False)]['persist'] >= 0.9 for s in seeds)
    G48d = all(R[(s, 2, True)]['heal'] < 0.1 for s in seeds)
    passed = G48a and G48b and G48c and G48d

    print("\n--- VERDICT ---", flush=True)
    print(f"G48a relaxed heals (>=0.3)        : {G48a}", flush=True)
    print(f"G48b relaxed loses persist (<=0.7): {G48b}", flush=True)
    print(f"G48c committed persists (>=0.9)   : {G48c}", flush=True)
    print(f"G48d committed no heal (<0.1)     : {G48d}", flush=True)
    verdict = ("PASS - persistence vs self-repair trade-off CONFIRMED: commitment gives longevity "
               "but blocks healing; relaxing it gives healing but loses longevity") if passed else "NULL/partial"
    print(f"\nG48: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G48"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {f"{k[0]}_b{k[1]}_{'w' if k[2] else 'u'}": v for k, v in R.items()},
                                                  "G48a": G48a, "G48b": G48b, "G48c": G48c, "G48d": G48d, "passed": passed},
                                                 indent=2, default=str))
    print("DONE", flush=True)

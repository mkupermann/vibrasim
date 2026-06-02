"""G52 — fluid membrane probe. Re-run the self-repair test with atom mobility
(node_thermal_speed>0): does the wound heal while the membrane stays intact, or is bond-turnover
also required?

Pre-registered bars in docs/amendments/g52_fluid_membrane.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg
from tools.run_g46_self_repair import component, wound, SETTLE, REPAIR


def run(seed, thermal, do_wound):
    c = replace(cfg(seed), node_thermal_speed=thermal)
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
    print("=== G52: fluid membrane probe (atom mobility -> self-repair?) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[(s, 'mob', 'w')] = run(s, 0.5, True)
        R[(s, 'mob', 'u')] = run(s, 0.5, False)
        R[(s, 'rig', 'w')] = run(s, 0.0, True)
        mw, mu, rw = R[(s, 'mob', 'w')], R[(s, 'mob', 'u')], R[(s, 'rig', 'w')]
        print(f"  seed {s}: MOBILE wounded N0={mw['n0']} post={mw['post']} final={mw['final']:.0f} heal={mw['heal']:.2f} | "
              f"MOBILE unwound persist={mu['persist']:.2f} (final {mu['final']:.0f}/peak {mu['peak']}) | "
              f"RIGID wounded heal={rw['heal']:.2f}", flush=True)

    G52a = all(R[(s, 'mob', 'u')]['persist'] >= 0.7 for s in seeds)
    G52b = all(R[(s, 'mob', 'w')]['heal'] >= 0.3 for s in seeds)
    G52c = all(R[(s, 'rig', 'w')]['heal'] < 0.1 for s in seeds)
    passed = G52a and G52b and G52c

    print("\n--- VERDICT ---", flush=True)
    print(f"G52a mobile stays intact (>=0.7)  : {G52a}", flush=True)
    print(f"G52b mobility heals (>=0.3)       : {G52b}", flush=True)
    print(f"G52c rigid no heal (<0.1)         : {G52c}", flush=True)
    verdict = ("PASS - atom mobility gives a fluid SELF-REPAIRING membrane (rigidity ceiling broken)"
               if passed else "NULL/partial")
    print(f"\nG52: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G52"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {f"{k[0]}_{k[1]}_{k[2]}": v for k, v in R.items()},
                                                  "G52a": G52a, "G52b": G52b, "G52c": G52c, "passed": passed},
                                                 indent=2, default=str))
    print("DONE", flush=True)

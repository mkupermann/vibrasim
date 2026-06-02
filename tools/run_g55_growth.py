"""G55 — fluid membrane growth. Does bond turnover let the membrane accrete/enlarge (vs rigid,
size-locked), or is its size homeostatic? No wound; long window; fluid vs rigid.

Pre-registered bars in docs/amendments/g55_fluid_growth.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg
from tools.run_g46_self_repair import component, SETTLE

WINDOW = 500


def run(seed, rate):
    c = replace(cfg(seed), bond_turnover_rate=rate, node_thermal_speed=0.2, edge_closure_k=2.0)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    start = len(component(w))
    sizes = []
    for t in range(WINDOW):
        tick(w, c.dt)
        if t % 20 == 19:
            sizes.append(len(component(w)))
    final = float(np.mean(sizes[-3:])) if len(sizes) >= 3 else (sizes[-1] if sizes else 0)
    lowest = min(sizes) if sizes else 0
    return dict(start=start, final=final, peak=max(sizes + [start]), lowest=lowest,
                growth=final / max(start, 1), min_frac=lowest / max(start, 1))


if __name__ == "__main__":
    print("=== G55: fluid membrane growth (accretion vs size homeostasis) ===", flush=True)
    seeds = [42, 7]
    fl, rg = {}, {}
    for s in seeds:
        fl[s] = run(s, 0.15)
        rg[s] = run(s, 0.0)
        print(f"  seed {s}: FLUID start={fl[s]['start']} final={fl[s]['final']:.0f} growth={fl[s]['growth']:.2f} "
              f"(min_frac {fl[s]['min_frac']:.2f}) | RIGID start={rg[s]['start']} final={rg[s]['final']:.0f} "
              f"growth={rg[s]['growth']:.2f}", flush=True)

    G55a = all(fl[s]['min_frac'] >= 0.7 for s in seeds)
    G55b = all(fl[s]['growth'] >= 1.2 for s in seeds)
    G55c = all(rg[s]['growth'] <= 1.1 for s in seeds)
    passed = G55a and G55b and G55c

    print("\n--- VERDICT ---", flush=True)
    print(f"G55a fluid stays coherent (>=0.7) : {G55a}", flush=True)
    print(f"G55b fluid GROWS (>=1.2x)         : {G55b}", flush=True)
    print(f"G55c rigid size-locked (<=1.1x)   : {G55c}", flush=True)
    verdict = ("PASS - fluid membrane GROWS by accretion (rigid is locked): turnover enables growth"
               if passed else "NULL/partial - fluid membrane is size-HOMEOSTATIC (stable size), not growing")
    print(f"\nG55: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G55"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"fluid": fl, "rigid": rg,
                                                  "G55a": G55a, "G55b": G55b, "G55c": G55c, "passed": passed},
                                                 indent=2, default=str))
    print("DONE", flush=True)

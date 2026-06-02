"""G56 — fluid membrane fission. Strong spontaneous curvature on a fluid membrane: does one shell
split into >=2 (division)? Fluid (turnover) vs rigid control.

Pre-registered bars in docs/amendments/g56_fluid_division.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick, _fit_sphere
from tools.run_g43_protocell import cfg as g30_cfg
from tools.run_g51_population import all_components

TICKS = 400
MIN_SIZE = 30
SHELL_SIGMA = 0.45


def cfg(seed, turnover):
    base = g30_cfg(seed)
    return replace(base, box_size=(28.0, 28.0, 28.0), n_initial_vibrations=600,
                   n_nodes_max=4000, n_vibrations_max=3600,
                   bond_turnover_rate=turnover, node_thermal_speed=0.2,
                   curvature_k=4.0, edge_closure_k=2.0)


def shell_count(w):
    n = 0
    for comp in all_components(w):
        if len(comp) < MIN_SIZE:
            continue
        pts = w.k_pos[np.array(comp)]
        centre, radius = _fit_sphere(pts)
        if radius <= 1e-6:
            continue
        r = np.linalg.norm(pts - centre, axis=1)
        if float(np.std(r)) / radius < SHELL_SIGMA:
            n += 1
    return n


def run(seed, turnover):
    c = cfg(seed, turnover); w = World(c)
    counts = []
    for t in range(TICKS):
        tick(w, c.dt)
        if t % 20 == 19:
            counts.append(shell_count(w))
    return dict(max_shells=max(counts) if counts else 0, final_shells=counts[-1] if counts else 0,
                trajectory=counts)


if __name__ == "__main__":
    print("=== G56: fluid membrane fission (curvature-driven division) ===", flush=True)
    seeds = [42, 7]
    fl, rg = {}, {}
    for s in seeds:
        fl[s] = run(s, 0.15)
        rg[s] = run(s, 0.0)
        print(f"  seed {s}: FLUID max_shells={fl[s]['max_shells']} final={fl[s]['final_shells']} "
              f"traj={fl[s]['trajectory']} | RIGID max_shells={rg[s]['max_shells']}", flush=True)

    G56a = all(fl[s]['max_shells'] >= 1 for s in seeds)
    G56b = all(fl[s]['max_shells'] >= 2 for s in seeds)
    G56c = all(rg[s]['max_shells'] < 2 for s in seeds)
    passed = G56a and G56b and G56c

    print("\n--- VERDICT ---", flush=True)
    print(f"G56a membrane forms          : {G56a}", flush=True)
    print(f"G56b fission to >=2 (fluid)  : {G56b}", flush=True)
    print(f"G56c rigid stays single      : {G56c}", flush=True)
    verdict = ("PASS - strong curvature splits a fluid membrane into a population (fission/division)"
               if passed else "NULL/partial - fluid membrane stays a single shell (no fission)")
    print(f"\nG56: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G56"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"fluid": fl, "rigid": rg,
                                                  "G56a": G56a, "G56b": G56b, "G56c": G56c, "passed": passed},
                                                 indent=2, default=str))
    print("DONE", flush=True)

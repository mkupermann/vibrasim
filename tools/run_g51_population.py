"""G51 — multiple proto-cells. Does a larger substrate form a POPULATION of distinct closed
membranes, or coalesce to one? Enumerate all bridged components, count shell-like ones.

Pre-registered bars in docs/amendments/g51_multiple_protocells.md.
"""
import sys, json
from collections import defaultdict, deque
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick, _fit_sphere
from tools.run_g43_protocell import cfg as g30_cfg

TICKS = 300
MIN_SIZE = 30
SHELL_SIGMA = 0.4


def cfg(seed):
    base = g30_cfg(seed)
    return replace(base, box_size=(33.0, 33.0, 33.0),
                   n_initial_vibrations=900, n_nodes_max=6000, n_vibrations_max=5400)


def all_components(w):
    adj = defaultdict(set)
    for b in range(w.b_count):
        if w.b_alive[b]:
            i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
            adj[i].add(j); adj[j].add(i)
    comps, seen = [], set()
    for s in adj:
        if s in seen:
            continue
        comp, q = [], deque([s]); seen.add(s)
        while q:
            n = q.popleft(); comp.append(n)
            for nb in adj[n]:
                if nb not in seen:
                    seen.add(nb); q.append(nb)
        comps.append(comp)
    return comps


def count_shells(w):
    shells = []
    for comp in all_components(w):
        if len(comp) < MIN_SIZE:
            continue
        pts = w.k_pos[np.array(comp)]
        centre, radius = _fit_sphere(pts)
        if radius <= 1e-6:
            continue
        d = pts - centre
        r = np.linalg.norm(d, axis=1)
        sigma = float(np.std(r))
        if sigma / radius < SHELL_SIGMA:
            shells.append((len(comp), round(radius, 1), round(sigma / radius, 3)))
    return shells


def run(seed):
    c = cfg(seed); w = World(c)
    for _ in range(TICKS):
        tick(w, c.dt)
    return count_shells(w)


if __name__ == "__main__":
    print("=== G51: multiple proto-cells (population of membranes?) ===", flush=True)
    seeds = [42, 7]
    res = {}
    for s in seeds:
        shells = run(s)
        res[s] = shells
        print(f"  seed {s}: {len(shells)} shell-like component(s): {shells}", flush=True)

    G51a = all(len(res[s]) >= 1 for s in seeds)
    G51b = all(len(res[s]) >= 2 for s in seeds)
    passed = G51a and G51b

    print("\n--- VERDICT ---", flush=True)
    print(f"G51a >=1 shell both seeds   : {G51a}", flush=True)
    print(f"G51b >=2 shells both seeds  : {G51b}", flush=True)
    verdict = ("PASS - the substrate forms a POPULATION of distinct proto-cells at scale"
               if passed else "NULL/partial - single membrane (coalescence) or no population")
    print(f"\nG51: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G51"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"shells": {str(s): res[s] for s in seeds},
                                                  "G51a": G51a, "G51b": G51b, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

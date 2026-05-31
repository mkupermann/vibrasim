"""G30 — does a closed, stable membrane form on the rich substrate?

Broad frequency band NOT centred on 8% (freq_ratio=0.05, tol=0.045 -> pairs 0.5-9.5%
apart) + membrane machinery. Take the largest bridged atom component, fit a sphere,
measure shell-likeness (sigma/R), enclosed interior vibrations, and persistence.
"""
import json
import math
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick
from world.bridges import get_bridge_stats
from tools.detect_membranes import fit_sphere


def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=300, box_size=(22.0, 22.0, 22.0),
        n_nodes_max=2000, n_vibrations_max=1800,
        graceful_capacity=True, numba_jit_enabled=False, repulsion_k=0.0,
        rng_seed=seed, lambda_gen=0.001, lambda_dec=0.001,
        # broad band, NOT centred on 8%
        freq_ratio=0.05, freq_tolerance=0.045, node_freq_binding=True,
        atom_valence=3, fusion_bond_block=2, curvature_k=2.0, atom_repulsion_k=1.0,
        pair_decay_time=12.0, triad_decay_time=80.0,
    )


def largest_bridged_component(w):
    from collections import defaultdict, deque
    B = w.b_count
    adj = defaultdict(set)
    for b in range(B):
        if w.b_alive[b]:
            i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
            adj[i].add(j); adj[j].add(i)
    best = []
    seen = set()
    for s in adj:
        if s in seen:
            continue
        comp = []; q = deque([s]); seen.add(s)
        while q:
            n = q.popleft(); comp.append(n)
            for nb in adj[n]:
                if nb not in seen:
                    seen.add(nb); q.append(nb)
        if len(comp) > len(best):
            best = comp
    return best


def analyse(w):
    comp = largest_bridged_component(w)
    if len(comp) < 8:
        return dict(size=len(comp), sigma_norm=9.9, interior=0, radius=0.0)
    pts = w.k_pos[np.array(comp)]
    centre, radius, sigma_r = fit_sphere(pts)
    sigma_norm = sigma_r / radius if radius > 0 else 9.9
    # interior free vibrations within 0.6 R of centre
    sp = w.s_pos[w.s_alive[: w.s_pos.shape[0]]]
    d = np.linalg.norm(sp - centre, axis=1)
    interior = int((d < 0.6 * radius).sum())
    return dict(size=len(comp), sigma_norm=float(sigma_norm), interior=interior, radius=float(radius))


def run(seed, n_ticks=250):
    c = cfg(seed)
    w = World(c)
    peak_chain = 0
    for t in range(n_ticks):
        tick(w, c.dt)
        peak_chain = max(peak_chain, get_bridge_stats(w)["max_chain"])
    a = analyse(w)
    a["peak_chain"] = peak_chain
    return a


if __name__ == "__main__":
    print("=== G30: closed membrane on the rich substrate (broad band, not 8%) ===", flush=True)
    seeds = [42, 7]
    rows = []
    for s in seeds:
        a = run(s)
        rows.append((s, a))
        print(f"  seed {s}: comp_size={a['size']:4d} peak_chain={a['peak_chain']:4d} "
              f"sigma/R={a['sigma_norm']:.3f} R={a['radius']:.1f} interior={a['interior']:4d}", flush=True)

    G30a = all(a["size"] >= 50 for _, a in rows)            # large bridged component
    G30b = all(a["sigma_norm"] < 0.35 for _, a in rows)     # shell-like (atoms on a sphere)
    G30c = all(a["interior"] >= 10 for _, a in rows)        # encloses interior vibrations
    G30d = all(a["size"] >= 0.6 * a["peak_chain"] for _, a in rows)   # persists (final ~ peak)
    passed = G30a and G30b and G30c and G30d
    print("\n--- VERDICT ---", flush=True)
    print(f"G30a comp>=50      : {G30a}", flush=True)
    print(f"G30b shell-like    : {G30b} (sigma/R<0.35)", flush=True)
    print(f"G30c encloses>=10  : {G30c}", flush=True)
    print(f"G30d persists      : {G30d}", flush=True)
    verdict = ("PASS - a large closed membrane forms and persists on the rich substrate "
               "with a broad (non-8%) compatibility band") if passed else "NULL/partial"
    print(f"\nG30: {verdict}", flush=True)
    d = Path.home() / ".eqmod" / "bet" / "G30"; d.mkdir(parents=True, exist_ok=True)
    (d / "result.json").write_text(json.dumps({"rows": [(s, a) for s, a in rows], "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

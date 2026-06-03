"""G95 — structural memory: largest CONNECTED strong-bridge component per region (topology, not count).
G94 root: consolidation persists indiscriminately by COUNT. Hypothesis: the tight stim injection makes
one CONNECTED engram mesh while control contamination is SCATTERED isolated bridges. Read the size of
the largest connected component of strong bridges in stim vs control region, into POST.
Bars pre-registered in docs/amendments/g95_structural_memory.md.
"""
import sys, json, time
from collections import defaultdict, deque
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges
from tools.run_bet099 import make_cfg, WARMUP, STIM_END, HALF

N_INJ = 6
STRONG = 5.0


def largest_strong_component(w, cx, half=HALF):
    """Atom-count of the largest connected component of STRONG bridges with both atoms in [cx +/- half]."""
    adj = defaultdict(set)
    for b in range(w.b_count):
        if not w.b_alive[b] or w.b_strength[b] < STRONG:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if i >= w.k_count or j >= w.k_count or not w.k_alive[i] or not w.k_alive[j]:
            continue
        if abs(w.k_pos[i][0] - cx) < half + 1.0 and abs(w.k_pos[j][0] - cx) < half + 1.0:
            adj[i].add(j); adj[j].add(i)
    best, seen = 0, set()
    for s in list(adj):
        if s in seen:
            continue
        size, q = 0, deque([s]); seen.add(s)
        while q:
            n = q.popleft(); size += 1
            for nb in adj[n]:
                if nb not in seen:
                    seen.add(nb); q.append(nb)
        best = max(best, size)
    return best


def run(seed, budget=280):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    object.__setattr__(cfg, 'compartment_boundary', 15.0)
    object.__setattr__(cfg, 'emit_speed', 6.0)
    object.__setattr__(cfg, 't_refractory', 0.5)
    object.__setattr__(cfg, 'bridge_consolidate_threshold', 4.0)
    w = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size); STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    stim_end_size = None; series = []
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(w, keep_frac=0.0); blank_bridges(w, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)
            inject_tight(w, cfg, box, STIM_X, n=N_INJ)
        if step == STIM_END:
            cull_free_vibrations(w, keep_frac=0.0)
            stim_end_size = largest_strong_component(w, STIM_X)
        tick(w, dt)
        if step > STIM_END and step % 1000 == 999 and stim_end_size is not None:
            series.append((round((step + 1) * dt, 1),
                           largest_strong_component(w, STIM_X),
                           largest_strong_component(w, CTRL_X)))
        if time.time() - t0 > budget:
            break
    horizon = [s for s in series if s[0] >= STIM_END * dt + 2000]
    sH, cH = (horizon[-1][1], horizon[-1][2]) if horizon else (0, 0)
    return dict(stim_end=stim_end_size or 0, stim_horizon=sH, ctrl_horizon=cH)


if __name__ == "__main__":
    print("=== G95: structural memory (largest connected strong-bridge component) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: stim_end={R[s]['stim_end']} | horizon stim={R[s]['stim_horizon']} ctrl={R[s]['ctrl_horizon']}", flush=True)
    G95a = all(R[s]['stim_end'] >= 4 for s in seeds)
    G95b = all(R[s]['stim_horizon'] >= 3 for s in seeds)
    G95c = all(R[s]['ctrl_horizon'] <= 2 and (R[s]['stim_horizon'] - R[s]['ctrl_horizon']) >= 2 for s in seeds)
    passed = G95a and G95b and G95c
    print("\n--- VERDICT ---", flush=True)
    print(f"G95a stim connected engram (end>=4)   : {G95a}", flush=True)
    print(f"G95b engram persists (horizon>=3)     : {G95b}", flush=True)
    print(f"G95c selective topology (ctrl<=2,gap>=2): {G95c}", flush=True)
    print(("G95: PASS - STRUCTURAL memory is selective + persistent (connected engram mesh holds; control scattered)"
           if passed else "G95: NULL/partial"), flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G95"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

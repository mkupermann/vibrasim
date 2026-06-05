"""ER-01 — isolate the atom-erosion mechanism (structural root of the memory deadlock). Form a
structure, go quiet, and measure level>=4 atom count over time with constituent decay ON vs OFF.
Pre-registered bars in docs/amendments/er01_atom_erosion_root.md.
"""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg, SETTLE
from tools.run_bet093 import cull_free_vibrations

POST = 600
SAMPLE = 50


def n_atoms(w):
    K = w.k_count
    return int((w.k_alive[:K] & (w.k_level[:K] >= 4)).sum())


def run(seed, freeze_constituents):
    c = cfg(seed)
    if freeze_constituents:
        c = replace(c, pair_decay_time=1e9, triad_decay_time=1e9)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    n0 = n_atoms(w)
    # go quiet: stop ambient generation, cull free vibrations each tick
    object.__setattr__(w.config, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    series = []
    for step in range(POST):
        cull_free_vibrations(w, keep_frac=0.0)
        tick(w, w.config.dt)
        if step % SAMPLE == SAMPLE - 1:
            series.append(n_atoms(w))
    final = float(np.mean(series[-3:])) if len(series) >= 3 else (series[-1] if series else 0)
    return dict(n0=n0, final=final, retention=(final / n0 if n0 else 0.0), series=series)


if __name__ == "__main__":
    print("=== ER-01: atom erosion mechanism (level>=4 count in quiet substrate) ===", flush=True)
    seeds = [42, 7]
    D, F = {}, {}
    for s in seeds:
        D[s] = run(s, freeze_constituents=False)
        F[s] = run(s, freeze_constituents=True)
        print(f"  seed {s}: DEFAULT n0={D[s]['n0']} final={D[s]['final']:.0f} ret={D[s]['retention']:.2f} | "
              f"FROZEN n0={F[s]['n0']} final={F[s]['final']:.0f} ret={F[s]['retention']:.2f}", flush=True)

    ER01a = all(D[s]['retention'] <= 0.5 for s in seeds)
    ER01b = all(F[s]['retention'] >= 0.85 for s in seeds)
    ER01c = all(F[s]['retention'] - D[s]['retention'] >= 0.35 for s in seeds)
    passed = ER01a and ER01b and ER01c

    print("\n--- VERDICT ---", flush=True)
    print(f"ER01a erosion real in default (ret<=0.5)        : {ER01a}", flush=True)
    print(f"ER01b frozen constituents persist (ret>=0.85)   : {ER01b}", flush=True)
    print(f"ER01c attributable (frozen-default>=0.35)       : {ER01c}", flush=True)
    verdict = ("PASS - constituent (pair/triad) decay is the erosion mechanism; freezing it makes atoms "
               "persist in a quiet substrate (structural root + candidate fix)") if passed else "NULL/partial - mechanism is elsewhere"
    print(f"\nER-01: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "ER01"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"default": {str(s): D[s] for s in seeds},
                                                  "frozen": {str(s): F[s] for s in seeds}, "passed": passed,
                                                  "ER01a": ER01a, "ER01b": ER01b, "ER01c": ER01c}, indent=2, default=str))
    print("DONE", flush=True)

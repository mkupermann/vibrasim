"""G27 — find the balanced rule/limit regime where the full chain climbs robustly.

Hypothesis: a moderately wide vibration-binding window (+-2%) + atoms binding by
PROXIMITY (node_freq_binding off, since the 8% rule is no longer required) + enough
capacity + slightly longer intermediate lifetimes lets the substrate produce abundant
atoms AND multiple molecule species, where the narrow 8% baseline starves.
"""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick


def base(seed):
    return WorldConfig(
        n_initial_vibrations=300, box_size=(22.0, 22.0, 22.0),
        n_nodes_max=2500, n_vibrations_max=2000,
        graceful_capacity=True, numba_jit_enabled=False, repulsion_k=0.0,
        rng_seed=seed, lambda_gen=0.001, lambda_dec=0.001,
    )


def measure(overrides, seed, n_ticks=160):
    cfg = replace(base(seed), **overrides)
    w = World(cfg)
    peak_atom = peak_mol = 0
    species = set()
    for _ in range(n_ticks):
        tick(w, cfg.dt)
        lvl = w.k_level[: w.k_count][w.k_alive[: w.k_count]]
        peak_atom = max(peak_atom, int((lvl == 4).sum()))
        peak_mol = max(peak_mol, int((lvl >= 5).sum()))
        species |= set(int(x) for x in np.unique(lvl[lvl >= 5]))
    return peak_atom, peak_mol, len(species)


CONFIGS = {
    "baseline_8pct": dict(freq_ratio=0.08, freq_tolerance=0.005),
    "balanced":      dict(freq_ratio=0.08, freq_tolerance=0.02, node_freq_binding=False,
                          pair_decay_time=12.0, triad_decay_time=80.0),
}

if __name__ == "__main__":
    print("=== G27: balanced rule/limit regime (real physics) ===", flush=True)
    seeds = [42, 7]
    out = {}
    for name, ov in CONFIGS.items():
        atoms, mols, specs = [], [], []
        for s in seeds:
            pa, pm, ns = measure(ov, s)
            atoms.append(pa); mols.append(pm); specs.append(ns)
            print(f"  {name:14s} seed {s}: peak_atom={pa:4d} peak_mol={pm:4d} species={ns}", flush=True)
        out[name] = {"atoms": atoms, "mols": mols, "species": specs}

    b = out["baseline_8pct"]; g = out["balanced"]
    base_atom = np.mean(b["atoms"])
    G27a = all(a >= 3 * max(base_atom, 1) for a in g["atoms"])     # >=3x baseline atoms, both seeds
    G27b = all(s >= 5 for s in g["species"])                       # >=5 molecule species, both seeds
    G27c = all(m >= 20 for m in g["mols"])                         # abundant molecules
    passed = G27a and G27b and G27c
    print("\n--- VERDICT ---", flush=True)
    print(f"  baseline mean atoms={base_atom:.1f}; balanced atoms={g['atoms']} mols={g['mols']} species={g['species']}", flush=True)
    print(f"G27a >=3x baseline atoms : {G27a}", flush=True)
    print(f"G27b >=5 molecule species: {G27b}", flush=True)
    print(f"G27c >=20 molecules      : {G27c}", flush=True)
    verdict = ("PASS - balanced regime makes the full chain climb robustly (abundant "
               "atoms + >=5 molecule species) where the 8% baseline starves") if passed else "NULL/partial"
    print(f"\nG27: {verdict}", flush=True)
    d = Path.home() / ".eqmod" / "bet" / "G27"; d.mkdir(parents=True, exist_ok=True)
    (d / "result.json").write_text(json.dumps({**out, "passed": passed}, indent=2))
    print("DONE", flush=True)

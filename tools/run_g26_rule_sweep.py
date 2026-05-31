"""G26 — search the substrate's binding-rule / limit space for a regime that produces
rich, stable structure (the chain the narrow 8% rule starves).

Runs the REAL physics engine with config overrides and measures structural yield.
"""
import json
import sys
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick


def base_cfg(seed):
    return WorldConfig(
        n_initial_vibrations=250,
        box_size=(20.0, 20.0, 20.0),
        n_nodes_max=1200,         # bounded so flooding stays fast to measure
        n_vibrations_max=1500,
        graceful_capacity=True,   # don't crash on capacity; return -1 and continue
        numba_jit_enabled=False,  # avoid JIT compile overhead for the sweep
        repulsion_k=0.0,          # measure binding yield, not spatial sorting (faster)
        rng_seed=seed,
        lambda_gen=0.001,         # modest ambient supply (high values flood O(n^2) binding)
        lambda_dec=0.001,
    )


def measure(overrides, seed, n_ticks=120):
    cfg = replace(base_cfg(seed), **overrides)
    world = World(cfg)
    peak = {"e": 0, "pair": 0, "triad": 0, "atom": 0, "mol": 0}
    for _ in range(n_ticks):
        tick(world, cfg.dt)
        lvl = world.k_level[: world.k_count][world.k_alive[: world.k_count]]
        peak["e"] = max(peak["e"], int((lvl == 1).sum()))
        peak["pair"] = max(peak["pair"], int((lvl == 2).sum()))
        peak["triad"] = max(peak["triad"], int((lvl == 3).sum()))
        peak["atom"] = max(peak["atom"], int((lvl == 4).sum()))
        peak["mol"] = max(peak["mol"], int((lvl >= 5).sum()))
    lvl = world.k_level[: world.k_count][world.k_alive[: world.k_count]]
    final_atom = int((lvl == 4).sum())
    final_mol = int((lvl >= 5).sum())
    return peak, final_atom, final_mol


VARIANTS = {
    "baseline_8pct":   dict(freq_ratio=0.08, freq_tolerance=0.005),
    "wide_tol_2pct":   dict(freq_ratio=0.08, freq_tolerance=0.02),
    "wide_tol_5pct":   dict(freq_ratio=0.08, freq_tolerance=0.05),
    "band_0to15pct":   dict(freq_ratio=0.075, freq_tolerance=0.075),   # any pair 0-15% apart
    "low_ratio_3pct":  dict(freq_ratio=0.03, freq_tolerance=0.03),
}

if __name__ == "__main__":
    print("=== G26: binding-rule / limit sweep (real physics, structural yield) ===", flush=True)
    seeds = [42]
    results = {}
    for name, ov in VARIANTS.items():
        peaks_atom, peaks_mol, finals_atom = [], [], []
        for s in seeds:
            peak, fa, fm = measure(ov, s, n_ticks=120)
            peaks_atom.append(peak["atom"]); peaks_mol.append(peak["mol"]); finals_atom.append(fa)
        ma = float(np.mean(peaks_atom)); mm = float(np.mean(peaks_mol)); mfa = float(np.mean(finals_atom))
        results[name] = {"peak_atom": ma, "peak_mol": mm, "final_atom": mfa}
        print(f"  {name:18s} peak_atom={ma:6.1f}  peak_mol={mm:6.1f}  final_atom={mfa:6.1f}", flush=True)

    base = results["baseline_8pct"]["peak_atom"]
    best = max(results.items(), key=lambda kv: kv[1]["peak_atom"])
    print(f"\n  baseline peak atoms: {base:.1f}", flush=True)
    print(f"  best variant: {best[0]} with peak atoms {best[1]['peak_atom']:.1f} "
          f"({best[1]['peak_atom']/max(base,1):.1f}x baseline)", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G26"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(results, indent=2))
    print("DONE", flush=True)

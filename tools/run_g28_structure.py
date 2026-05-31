"""G28 — does the rich (G27) substrate lift the membrane/bridge element-count ceiling?

The memory programme (BET-089..099) was bounded by element count (~10-25 atoms / few
bridges). With the balanced binding window producing ~200 atoms, do bridges and the
largest connected bridged structure (membrane/memory precursor) grow far past that
ceiling? Compares the wide window vs the 8% baseline, both with membrane machinery.
"""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick
from world.bridges import get_bridge_stats


def base(seed):
    return WorldConfig(
        n_initial_vibrations=300, box_size=(22.0, 22.0, 22.0),
        n_nodes_max=2500, n_vibrations_max=2000,
        graceful_capacity=True, numba_jit_enabled=False, repulsion_k=0.0,
        rng_seed=seed, lambda_gen=0.001, lambda_dec=0.001,
        # membrane / bridge machinery (BET-086/091 style)
        atom_valence=3, fusion_bond_block=2,
        curvature_k=2.0, atom_repulsion_k=1.0,
    )


def measure(overrides, seed, n_ticks=200):
    cfg = replace(base(seed), **overrides)
    w = World(cfg)
    peak_atom = 0
    for _ in range(n_ticks):
        tick(w, cfg.dt)
        lvl = w.k_level[: w.k_count][w.k_alive[: w.k_count]]
        peak_atom = max(peak_atom, int((lvl == 4).sum()))
    st = get_bridge_stats(w)
    lvl = w.k_level[: w.k_count][w.k_alive[: w.k_count]]
    final_atom = int((lvl == 4).sum())
    return peak_atom, final_atom, st["n_bridges"], st["max_chain"]


CONFIGS = {
    "baseline_8pct": dict(freq_ratio=0.08, freq_tolerance=0.005),
    "wide_window":   dict(freq_ratio=0.08, freq_tolerance=0.02),
}

if __name__ == "__main__":
    print("=== G28: membrane/bridge structure on the rich substrate ===", flush=True)
    seeds = [42, 7]
    out = {}
    for name, ov in CONFIGS.items():
        rows = []
        for s in seeds:
            pa, fa, nb, mc = measure(ov, s)
            rows.append((s, pa, fa, nb, mc))
            print(f"  {name:14s} seed {s}: peak_atom={pa:4d} final_atom={fa:4d} bridges={nb:4d} max_chain={mc:4d}", flush=True)
        out[name] = rows

    base_chain = np.mean([r[4] for r in out["baseline_8pct"]])
    wide_chain = np.mean([r[4] for r in out["wide_window"]])
    base_br = np.mean([r[3] for r in out["baseline_8pct"]])
    wide_br = np.mean([r[3] for r in out["wide_window"]])
    G28a = all(r[4] >= 30 for r in out["wide_window"])             # largest bridged structure >= 30 atoms (past the ~25 ceiling)
    G28b = wide_chain >= 2 * max(base_chain, 1)                    # >= 2x baseline structure size
    G28c = all(r[3] >= 40 for r in out["wide_window"])             # many bridges (memory substrate not starved)
    passed = G28a and G28b and G28c
    print("\n--- VERDICT ---", flush=True)
    print(f"  baseline max_chain={base_chain:.0f} bridges={base_br:.0f} | wide max_chain={wide_chain:.0f} bridges={wide_br:.0f}", flush=True)
    print(f"G28a wide max_chain>=30 : {G28a}", flush=True)
    print(f"G28b wide >=2x baseline : {G28b}", flush=True)
    print(f"G28c wide bridges>=40   : {G28c}", flush=True)
    verdict = ("PASS - the rich substrate lifts the membrane/bridge element-count ceiling "
               "(far larger bridged structure than the 8% baseline)") if passed else "NULL/partial"
    print(f"\nG28: {verdict}", flush=True)
    d = Path.home() / ".eqmod" / "bet" / "G28"; d.mkdir(parents=True, exist_ok=True)
    (d / "result.json").write_text(json.dumps({"out": out, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

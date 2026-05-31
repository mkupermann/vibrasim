"""G29 — the 8% rule is GONE. Binding = proximity + polarity ONLY, no frequency gate
at any level. Does the substrate still climb to abundant stable atoms + a large bridged
structure, or collapse into undifferentiated noise?
"""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick
from world.bridges import get_bridge_stats


def cfg_no_rule(seed):
    return WorldConfig(
        n_initial_vibrations=300, box_size=(22.0, 22.0, 22.0),
        n_nodes_max=2500, n_vibrations_max=2000,
        graceful_capacity=True, numba_jit_enabled=False, repulsion_k=0.0,
        rng_seed=seed, lambda_gen=0.001, lambda_dec=0.001,
        # 8% RULE REMOVED: accept any frequency ratio (window [0, 100] ~ all pairs)
        freq_ratio=50.0, freq_tolerance=50.0,
        node_freq_binding=False,          # no frequency gate on node->node either
        # membrane / bridge machinery
        atom_valence=3, fusion_bond_block=2,
        curvature_k=2.0, atom_repulsion_k=1.0,
    )


def measure(seed, n_ticks=200):
    cfg = cfg_no_rule(seed)
    w = World(cfg)
    peak_atom = peak_mol = 0
    species = set()
    for _ in range(n_ticks):
        tick(w, cfg.dt)
        lvl = w.k_level[: w.k_count][w.k_alive[: w.k_count]]
        peak_atom = max(peak_atom, int((lvl == 4).sum()))
        peak_mol = max(peak_mol, int((lvl >= 5).sum()))
        species |= set(int(x) for x in np.unique(lvl[lvl >= 5]))
    st = get_bridge_stats(w)
    lvl = w.k_level[: w.k_count][w.k_alive[: w.k_count]]
    return peak_atom, int((lvl == 4).sum()), peak_mol, len(species), st["n_bridges"], st["max_chain"]


if __name__ == "__main__":
    print("=== G29: NO frequency rule — proximity + polarity binding only ===", flush=True)
    seeds = [42, 7, 99]
    rows = []
    for s in seeds:
        pa, fa, pm, sp, nb, mc = measure(s)
        rows.append(dict(seed=s, peak_atom=pa, final_atom=fa, peak_mol=pm, species=sp, bridges=nb, max_chain=mc))
        print(f"  seed {s}: peak_atom={pa:4d} final_atom={fa:4d} peak_mol={pm:4d} species={sp} bridges={nb:4d} max_chain={mc:4d}", flush=True)

    atoms = [r["peak_atom"] for r in rows]
    chains = [r["max_chain"] for r in rows]
    specs = [r["species"] for r in rows]
    G29a = all(a >= 100 for a in atoms)        # abundant stable atoms without the rule
    G29b = all(c >= 50 for c in chains)        # large bridged structure (past the old ~25 ceiling)
    G29c = all(s >= 5 for s in specs)          # still multiple molecule species (differentiation survives)
    passed = G29a and G29b and G29c
    print("\n--- VERDICT ---", flush=True)
    print(f"  atoms={atoms} max_chain={chains} species={specs}", flush=True)
    print(f"G29a atoms>=100 all seeds : {G29a}", flush=True)
    print(f"G29b max_chain>=50 all    : {G29b}", flush=True)
    print(f"G29c species>=5 all       : {G29c}", flush=True)
    verdict = ("PASS - with NO frequency rule (proximity+polarity only) the substrate "
               "still climbs to abundant atoms + a large bridged structure + multiple species") if passed else "NULL/partial"
    print(f"\nG29: {verdict}", flush=True)
    d = Path.home() / ".eqmod" / "bet" / "G29"; d.mkdir(parents=True, exist_ok=True)
    (d / "result.json").write_text(json.dumps({"rows": rows, "passed": passed}, indent=2))
    print("DONE", flush=True)

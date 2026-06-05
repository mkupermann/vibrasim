"""G49 — does reducing positional rigidity (curvature_k + atom_repulsion_k) enable wound re-closure?
Tests G48's corrected diagnosis (membrane static from RIGIDITY + no wound-targeting, not valence
commitment). Same formation in every arm; rigidity scaled by f during the post-formation window.

Pre-registered bars in docs/amendments/g49_fluidity_wound_reclosure.md.
"""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg
from tools.run_g46_self_repair import component, wound, SETTLE, REPAIR

PERSIST = REPAIR  # same window length for the unwounded persistence arm


def _scaled(c, f):
    return replace(c, curvature_k=c.curvature_k * f, atom_repulsion_k=c.atom_repulsion_k * f)


def heal_arm(seed, f):
    """Form rigid -> wound -> repair at scaled rigidity. Returns healing metrics."""
    c = cfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    comp_idx = component(w)
    n0 = len(comp_idx)
    if n0 < 8:
        return None
    wound(w, comp_idx, np.asarray(c.box_size))
    post = len(component(w))
    w.config = _scaled(c, f)
    sizes = []
    for t in range(REPAIR):
        tick(w, c.dt)
        if t % 10 == 9:
            sizes.append(len(component(w)))
    recovered = float(np.mean(sizes[-3:])) if len(sizes) >= 3 else (sizes[-1] if sizes else 0)
    healed = (recovered - post) / max(n0 - post, 1)
    return dict(n0=n0, post=post, recovered=recovered, peak=max(sizes) if sizes else 0,
                healed=float(healed), recov_frac=recovered / n0)


def persist_arm(seed, f):
    """Form rigid -> NO wound -> observe at scaled rigidity. Returns persistence P = end/N0."""
    c = cfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    n0 = len(component(w))
    if n0 < 8:
        return None
    w.config = _scaled(c, f)
    sizes = []
    for t in range(PERSIST):
        tick(w, c.dt)
        if t % 10 == 9:
            sizes.append(len(component(w)))
    end = float(np.mean(sizes[-3:])) if len(sizes) >= 3 else (sizes[-1] if sizes else 0)
    return dict(n0=n0, end=end, P=end / max(n0, 1))


if __name__ == "__main__":
    print("=== G49: fluidity (reduced rigidity) -> wound re-closure? ===", flush=True)
    seeds = [42, 7]
    fs = [1.0, 0.5, 0.25, 0.0]
    H, P = {}, {}
    for s in seeds:
        H[s], P[s] = {}, {}
        for f in fs:
            H[s][f] = heal_arm(s, f)
            P[s][f] = persist_arm(s, f)
            print(f"  seed {s} f={f}: N0={H[s][f]['n0']} post={H[s][f]['post']} "
                  f"healed={H[s][f]['healed']:.2f} (recov {H[s][f]['recovered']:.0f}, peak {H[s][f]['peak']}) "
                  f"| unwounded P={P[s][f]['P']:.2f}", flush=True)

    G49a = all(H[s][1.0]['n0'] >= 50 for s in seeds)
    G49b = all(H[s][1.0]['healed'] < 0.10 for s in seeds)
    # G49c: some f<1 heals >=0.30 on BOTH seeds (same f for both)
    heal_fs = [f for f in fs if f < 1.0 and all(H[s][f]['healed'] >= 0.30 for s in seeds)]
    G49c = len(heal_fs) > 0
    # G49d: at a healing f, membrane still stands unwounded (P>=0.7) and recovered>post, both seeds
    good_fs = [f for f in heal_fs
               if all(P[s][f]['P'] >= 0.70 and H[s][f]['recovered'] > H[s][f]['post'] for s in seeds)]
    G49d = len(good_fs) > 0
    passed = G49a and G49b and G49c and G49d

    print("\n--- VERDICT ---", flush=True)
    print(f"G49a membrane forms (N0>=50)             : {G49a}", flush=True)
    print(f"G49b rigid control no-heal (H<0.10)      : {G49b}", flush=True)
    print(f"G49c reduced rigidity heals (H>=0.30)    : {G49c}  (f: {heal_fs})", flush=True)
    print(f"G49d real re-closure not collapse        : {G49d}  (f: {good_fs})", flush=True)
    if passed:
        verdict = "PASS - reducing rigidity enables genuine wound re-closure (first self-repairing membrane)"
    elif G49c and not G49d:
        verdict = "PARTIAL - low-f regrows but also collapses unwounded; reformation, not targeted repair"
    else:
        verdict = "NULL - rigidity is NOT the blocker; sole cause is no wound-targeting"
    print(f"\nG49: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G49"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"H": {str(s): {str(f): H[s][f] for f in fs} for s in seeds},
         "P": {str(s): {str(f): P[s][f] for f in fs} for s in seeds},
         "passed": passed, "G49a": G49a, "G49b": G49b, "G49c": G49c, "G49d": G49d,
         "heal_fs": heal_fs, "good_fs": good_fs}, indent=2, default=str))
    print("DONE", flush=True)

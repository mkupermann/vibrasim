"""G49 — membrane self-repair via edge MOBILITY + targeting. G48 falsified the valence-commitment
trade-off and pointed at positional rigidity + no wound-targeting. This BET softens rigidity
(curvature_k, atom_repulsion_k) so wound edges can migrate, with edge_closure_k pulling them to
re-close. Three arms isolate mobility, targeting, and the G47 rigid baseline.

Pre-registered bars in docs/amendments/g49_mobility_targeted_repair.md.
"""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick, _fit_sphere
from tools.run_g43_protocell import cfg
from tools.run_g46_self_repair import component, wound, SETTLE, REPAIR


def _radius(w):
    idx = component(w)
    if len(idx) < 4:
        return 0.0
    _, r = _fit_sphere(w.k_pos[idx])
    return float(r)


def run_arm(seed, edge_k, curv_k, rep_k):
    c = cfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    comp_idx = component(w)
    n0 = len(comp_idx)
    if n0 < 8:
        return None
    r0 = _radius(w)
    wound(w, comp_idx, np.asarray(c.box_size))
    post = len(component(w))
    # swap config for the repair window only
    w.config = replace(c, edge_closure_k=edge_k, curvature_k=curv_k, atom_repulsion_k=rep_k)
    sizes, radii = [], []
    for t in range(REPAIR):
        tick(w, c.dt)
        if t % 10 == 9:
            sizes.append(len(component(w)))
            radii.append(_radius(w))
    recovered = float(np.mean(sizes[-3:])) if len(sizes) >= 3 else (sizes[-1] if sizes else 0)
    rfin = float(np.mean(radii[-3:])) if len(radii) >= 3 else (radii[-1] if radii else 0.0)
    healed = (recovered - post) / max(n0 - post, 1)
    return dict(n0=n0, post=post, recovered=recovered, peak=max(sizes) if sizes else 0,
                post_frac=post / n0, healed=float(healed),
                r0=r0, rfin=rfin, radius_keep=float(rfin / r0) if r0 > 1e-9 else 0.0)


if __name__ == "__main__":
    print("=== G49: membrane self-repair via edge mobility + targeting ===", flush=True)
    seeds = [42, 7]
    A, B, C = {}, {}, {}   # A mobility+targeting, B mobility-only, C targeting-only (G47 rigid)
    for s in seeds:
        A[s] = run_arm(s, edge_k=1.5, curv_k=0.5, rep_k=0.3)
        B[s] = run_arm(s, edge_k=0.0, curv_k=0.5, rep_k=0.3)
        C[s] = run_arm(s, edge_k=1.5, curv_k=2.0, rep_k=1.0)
        print(f"  seed {s}: N0={A[s]['n0']} post={A[s]['post']} | "
              f"A(mob+tgt) healed={A[s]['healed']:.2f} rkeep={A[s]['radius_keep']:.2f} | "
              f"B(mob) healed={B[s]['healed']:.2f} | C(rigid+tgt) healed={C[s]['healed']:.2f}", flush=True)

    G49a = all(A[s]['n0'] >= 50 for s in seeds)
    G49b = all(A[s]['post_frac'] <= 0.7 for s in seeds)
    G49c = all(A[s]['healed'] >= 0.30 and A[s]['radius_keep'] >= 0.6 for s in seeds)
    G49d = all(A[s]['healed'] >= B[s]['healed'] + 0.20 for s in seeds)
    G49e = all(A[s]['healed'] >= C[s]['healed'] + 0.20 for s in seeds)
    passed = G49a and G49b and G49c and G49d and G49e

    print("\n--- VERDICT ---", flush=True)
    print(f"G49a membrane forms (N0>=50)            : {G49a}", flush=True)
    print(f"G49b wound lands (<=0.7 N0)             : {G49b}", flush=True)
    print(f"G49c mob+tgt heals >=0.30, no collapse  : {G49c}", flush=True)
    print(f"G49d needs targeting (A >= B+0.20)      : {G49d}", flush=True)
    print(f"G49e mobility unlocks vs G47 (A >= C+.2): {G49e}", flush=True)
    if passed:
        verdict = "PASS - first genuine self-repair: mobility + edge-closure targeting re-closes the wound"
    elif G49c:
        verdict = "PARTIAL - heals, but via mobility/re-merging, not targeting (G49d/e fail)"
    else:
        verdict = "NULL - even mobile targeted edges do not re-close; negative deeper than rigidity"
    print(f"\nG49: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G49"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"A": A, "B": B, "C": C, "passed": passed,
                                                  "G49a": G49a, "G49b": G49b, "G49c": G49c,
                                                  "G49d": G49d, "G49e": G49e}, indent=2, default=str))
    print("DONE", flush=True)

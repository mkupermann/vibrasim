"""G46 — membrane self-repair. Wound the membrane (remove a polar cap of shell atoms) and
test whether the rich substrate heals it back to closure (regeneration on) vs not (off).

Pre-registered bars in docs/amendments/g46_membrane_self_repair.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick, _largest_bridged_component, _fit_sphere
from tools.run_g43_protocell import cfg

SETTLE = 250
REPAIR = 250


def component(w):
    comp = _largest_bridged_component(w)
    return np.array(comp) if comp else np.array([], dtype=int)


def wound(w, comp_idx, box):
    """Kill component atoms in a polar cap (x-Cx)>0.3R and the bridges touching them."""
    pts = w.k_pos[comp_idx]
    centre, radius = _fit_sphere(pts)
    cx = centre[0]
    killset = set()
    for ai in comp_idx:
        if (w.k_pos[ai][0] - cx) > 0.3 * radius:
            w.k_alive[ai] = False
            killset.add(int(ai))
    for b in range(w.b_count):
        if w.b_alive[b] and (int(w.b_atom_i[b]) in killset or int(w.b_atom_j[b]) in killset):
            w.b_alive[b] = False
    return centre, radius


def run_arm(seed, regenerate):
    c = cfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    comp_idx = component(w)
    n0 = len(comp_idx)
    if n0 < 8:
        return None
    wound(w, comp_idx, np.asarray(c.box_size))
    post = len(component(w))
    if not regenerate:
        w.config = replace(c, lambda_gen=0.0)
    sizes = []
    for t in range(REPAIR):
        tick(w, c.dt)
        if t % 10 == 9:
            sizes.append(len(component(w)))
    recovered = float(np.mean(sizes[-3:])) if len(sizes) >= 3 else (sizes[-1] if sizes else 0)
    return dict(n0=n0, post=post, recovered=recovered,
                post_frac=post / n0, recov_frac=recovered / n0, peak_recovered=max(sizes) if sizes else 0)


if __name__ == "__main__":
    print("=== G46: membrane self-repair (wound -> heal) ===", flush=True)
    seeds = [42, 7]
    rep, ctl = {}, {}
    for s in seeds:
        rep[s] = run_arm(s, regenerate=True)
        ctl[s] = run_arm(s, regenerate=False)
        print(f"  seed {s}: N0={rep[s]['n0']} post={rep[s]['post']} ({rep[s]['post_frac']:.2f}) | "
              f"REPAIR recovered={rep[s]['recovered']:.0f} ({rep[s]['recov_frac']:.2f}) | "
              f"CONTROL recovered={ctl[s]['recovered']:.0f} ({ctl[s]['recov_frac']:.2f})", flush=True)

    G46a = all(rep[s]['n0'] >= 50 for s in seeds)
    G46b = all(rep[s]['post_frac'] <= 0.7 for s in seeds)
    G46c = all(rep[s]['recov_frac'] >= 0.9 for s in seeds)
    G46d = all(ctl[s]['recov_frac'] <= 0.75 for s in seeds)
    passed = G46a and G46b and G46c and G46d

    print("\n--- VERDICT ---", flush=True)
    print(f"G46a membrane forms (N0>=50)        : {G46a}", flush=True)
    print(f"G46b wound lands (<=0.7 N0)         : {G46b}", flush=True)
    print(f"G46c self-repair (>=0.9 N0)         : {G46c}", flush=True)
    print(f"G46d control no heal (<=0.75 N0)    : {G46d}", flush=True)
    verdict = ("PASS - the membrane SELF-REPAIRS: a wounded shell heals back to closure via "
               "substrate regeneration; does not heal without it") if passed else "NULL/partial"
    print(f"\nG46: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G46"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"repair": rep, "control": ctl, "passed": passed,
                                                  "G46a": G46a, "G46b": G46b, "G46c": G46c, "G46d": G46d},
                                                 indent=2, default=str))
    print("DONE", flush=True)

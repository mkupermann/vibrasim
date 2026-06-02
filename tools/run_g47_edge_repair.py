"""G47 — self-repair with edge-closure. Same wound protocol as G46, but the repair arm enables
edge_closure_k (free-valence wound edges attract -> re-close). Control = edge_closure off.

Pre-registered bars in docs/amendments/g47_edge_closure_repair.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg
from tools.run_g46_self_repair import component, wound, SETTLE, REPAIR


def run_arm(seed, edge_k):
    c = cfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    comp_idx = component(w)
    n0 = len(comp_idx)
    if n0 < 8:
        return None
    wound(w, comp_idx, np.asarray(c.box_size))
    post = len(component(w))
    w.config = replace(c, edge_closure_k=edge_k)   # repair arm: edge-closure on
    sizes = []
    for t in range(REPAIR):
        tick(w, c.dt)
        if t % 10 == 9:
            sizes.append(len(component(w)))
    recovered = float(np.mean(sizes[-3:])) if len(sizes) >= 3 else (sizes[-1] if sizes else 0)
    return dict(n0=n0, post=post, recovered=recovered, peak=max(sizes) if sizes else 0,
                post_frac=post / n0, recov_frac=recovered / n0)


if __name__ == "__main__":
    print("=== G47: membrane self-repair via edge-closure ===", flush=True)
    seeds = [42, 7]
    rep, ctl = {}, {}
    for s in seeds:
        rep[s] = run_arm(s, edge_k=1.0)
        ctl[s] = run_arm(s, edge_k=0.0)
        heal_frac = (rep[s]['recovered'] - rep[s]['post']) / max(rep[s]['n0'] - rep[s]['post'], 1)
        print(f"  seed {s}: N0={rep[s]['n0']} post={rep[s]['post']} | edge-ON recovered={rep[s]['recovered']:.0f} "
              f"({rep[s]['recov_frac']:.2f}, healed {heal_frac:.2f} of damage, peak {rep[s]['peak']}) | "
              f"control recovered={ctl[s]['recovered']:.0f} ({ctl[s]['recov_frac']:.2f})", flush=True)

    G47a = all(rep[s]['n0'] >= 50 for s in seeds)
    G47b = all(rep[s]['post_frac'] <= 0.7 for s in seeds)
    G47c = all(rep[s]['recovered'] >= rep[s]['post'] + 0.3 * (rep[s]['n0'] - rep[s]['post']) for s in seeds)
    G47d = all(rep[s]['recovered'] >= 1.3 * max(ctl[s]['recovered'], 1e-9) for s in seeds)
    passed = G47a and G47b and G47c and G47d

    print("\n--- VERDICT ---", flush=True)
    print(f"G47a membrane forms (N0>=50)          : {G47a}", flush=True)
    print(f"G47b wound lands (<=0.7 N0)           : {G47b}", flush=True)
    print(f"G47c meaningful repair (>=30% damage) : {G47c}", flush=True)
    print(f"G47d attributable to edge-closure     : {G47d}", flush=True)
    verdict = ("PASS - edge-closure drives membrane self-repair (proto-cell becomes self-renewing)"
               ) if passed else "NULL/partial"
    print(f"\nG47: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G47"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"repair": rep, "control": ctl, "passed": passed,
                                                  "G47a": G47a, "G47b": G47b, "G47c": G47c, "G47d": G47d},
                                                 indent=2, default=str))
    print("DONE", flush=True)

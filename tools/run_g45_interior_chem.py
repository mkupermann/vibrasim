"""G45 — interior chemistry. Does bound structure (atoms) assemble inside the protected
proto-cell interior (r<0.6R), and does the channel's protection enable it (ON vs OFF)?

Pre-registered bars in docs/amendments/g45_interior_chemistry.md.
"""
import sys, json, math
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg, membrane_geom

SETTLE = 250
MEASURE = 220


def interior_atoms(w, centre, radius, box):
    """Count + concentration of bound atoms (level>=4) inside r<0.6R (excludes the shell)."""
    K = w.k_count
    if K == 0:
        return 0, 0.0
    alive = w.k_alive[:K]
    lvl = w.k_level[:K]
    pos = w.k_pos[:K]
    d = pos - centre
    d -= box * np.round(d / box)
    r = np.linalg.norm(d, axis=1)
    r_in = 0.6 * radius
    mask = alive & (lvl >= 4) & (r < r_in)
    n = int(mask.sum())
    v_in = (4.0 / 3.0) * math.pi * r_in ** 3
    return n, n / v_in


def run_arm(seed, channel):
    c = cfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    geom = membrane_geom(w)
    if geom is None:
        return None
    centre, radius, f_mem, comp0 = geom
    box = np.asarray(c.box_size, dtype=np.float64)
    if channel:
        w.config = replace(c, membrane_channel_k=1.0, membrane_channel_mode='atom',
                           membrane_channel_recompute=20)
    counts, concs = [], []
    for t in range(MEASURE):
        tick(w, c.dt)
        if t % 10 == 9:
            n, conc = interior_atoms(w, centre, radius, box)
            counts.append(n); concs.append(conc)
    last = slice(-(len(counts) // 3 or 1), None)
    return dict(comp0=comp0, radius=float(radius),
                mean_count=float(np.mean(counts[last])), mean_conc=float(np.mean(concs[last])))


if __name__ == "__main__":
    print("=== G45: interior chemistry — does the protected interior assemble structure? ===", flush=True)
    seeds = [42, 7]
    on, off = {}, {}
    for s in seeds:
        on[s] = run_arm(s, channel=True)
        off[s] = run_arm(s, channel=False)
        ratio = on[s]['mean_conc'] / off[s]['mean_conc'] if off[s]['mean_conc'] > 1e-12 else (9.9 if on[s]['mean_conc'] > 0 else 1.0)
        print(f"  seed {s}: comp={on[s]['comp0']} | ON interior_atoms={on[s]['mean_count']:.1f} "
              f"(conc {on[s]['mean_conc']:.4f}) | OFF interior_atoms={off[s]['mean_count']:.1f} "
              f"(conc {off[s]['mean_conc']:.4f}) | ON/OFF={ratio:.2f}", flush=True)

    G45a = all(on[s]['comp0'] >= 50 for s in seeds)
    G45b = all(on[s]['mean_count'] >= 5 for s in seeds)
    G45c = all((on[s]['mean_conc'] >= 1.5 * off[s]['mean_conc']) or (off[s]['mean_conc'] < 1e-12 and on[s]['mean_conc'] > 0) for s in seeds)
    passed = G45a and G45b and G45c

    print("\n--- VERDICT ---", flush=True)
    print(f"G45a membrane forms (>=50)            : {G45a}", flush=True)
    print(f"G45b interior assembles (>=5 atoms)   : {G45b}", flush=True)
    print(f"G45c channel enables (ON>=1.5x OFF)   : {G45c}", flush=True)
    verdict = ("PASS - the protected interior assembles its own bound structure, channel-enabled "
               "(proto-cell is a reaction chamber)") if passed else "NULL/partial"
    print(f"\nG45: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G45"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"on": on, "off": off, "passed": passed,
                                                  "G45a": G45a, "G45b": G45b, "G45c": G45c},
                                                 indent=2, default=str))
    print("DONE", flush=True)

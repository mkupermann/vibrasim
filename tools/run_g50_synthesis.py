"""G50 — channel-coupled synthesis. Does the uptake trap increase interior bound-atom assembly
(vs plain channel)? Decisive test for the proto-cell's metabolic potential.

Pre-registered bars in docs/amendments/g50_channel_coupled_synthesis.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg, membrane_geom
from tools.run_g45_interior_chem import interior_atoms, SETTLE, MEASURE


def run_arm(seed, channel_on, uptake):
    c = cfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    geom = membrane_geom(w)
    if geom is None:
        return None
    centre, radius, f_mem, comp0 = geom
    box = np.asarray(c.box_size, dtype=np.float64)
    if channel_on:
        w.config = replace(c, membrane_channel_k=1.0, membrane_channel_mode='atom',
                           membrane_channel_recompute=20, membrane_channel_uptake=uptake)
    counts = []
    for t in range(MEASURE):
        tick(w, c.dt)
        if t % 10 == 9:
            n, _ = interior_atoms(w, centre, radius, box)
            counts.append(n)
    last = counts[-(len(counts) // 3 or 1):]
    return dict(comp0=comp0, mean_count=float(np.mean(last)))


if __name__ == "__main__":
    print("=== G50: channel-coupled synthesis — does uptake increase interior assembly? ===", flush=True)
    seeds = [42, 7]
    up, plain, off = {}, {}, {}
    for s in seeds:
        up[s] = run_arm(s, channel_on=True, uptake=True)
        plain[s] = run_arm(s, channel_on=True, uptake=False)
        off[s] = run_arm(s, channel_on=False, uptake=False)
        ratio = up[s]['mean_count'] / plain[s]['mean_count'] if plain[s]['mean_count'] > 1e-9 else 9.9
        print(f"  seed {s}: comp={up[s]['comp0']} | UPTAKE atoms={up[s]['mean_count']:.1f} "
              f"PLAIN={plain[s]['mean_count']:.1f} OFF={off[s]['mean_count']:.1f} | uptake/plain={ratio:.2f}", flush=True)

    G50a = all(up[s]['comp0'] >= 50 for s in seeds)
    G50b = all(up[s]['mean_count'] >= 1.5 * plain[s]['mean_count'] for s in seeds)
    passed = G50a and G50b

    print("\n--- VERDICT ---", flush=True)
    print(f"G50a membrane forms (>=50)          : {G50a}", flush=True)
    print(f"G50b uptake increases assembly(1.5x): {G50b}", flush=True)
    verdict = ("PASS - the uptake channel drives MORE interior structure (channel-coupled synthesis)"
               ) if passed else "NULL/partial"
    print(f"\nG50: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G50"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"uptake": up, "plain": plain, "off": off,
                                                  "G50a": G50a, "G50b": G50b, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

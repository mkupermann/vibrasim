"""G32 — atom-proximity membrane channel on the REAL emergent G30 shell (fixes G31's
leak). Same protocol/metric/bars as G31; the only change is membrane_channel_mode='atom'
(reflect off the nearest real membrane atom, tracking the breathing shell)."""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g31_membrane_channel import (
    cfg, membrane_geom, inject_tracers, SETTLE, MEASURE,
)


def run_arm(seed, channel_k, mode):
    c = cfg(seed)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    geom = membrane_geom(w)
    if geom is None:
        return None
    centre, radius, f_mem, comp0 = geom
    rng = np.random.default_rng(1000 + seed)
    slots, band, centre = inject_tracers(w, centre, radius, f_mem, rng)

    w.config = replace(c, lambda_gen=0.0, membrane_channel_k=channel_k,
                       membrane_channel_recompute=20, membrane_channel_width=1.5,
                       membrane_channel_mode=mode)
    box = np.asarray(c.box_size, dtype=np.float64)
    ever_in = np.zeros(len(slots), dtype=bool)
    for _ in range(MEASURE):
        tick(w, c.dt)
        alive = w.s_alive[slots]
        d = w.s_pos[slots] - centre
        d -= box * np.round(d / box)
        r = np.linalg.norm(d, axis=1)
        ever_in |= alive & (r < radius)
    comp_final = membrane_geom(w)
    final_size = comp_final[3] if comp_final else 0
    return dict(comp0=comp0, radius=float(radius), f_mem=f_mem,
                crossed_compatible=float(ever_in[band == 0].mean()),
                crossed_incompatible=float(ever_in[band == 1].mean()),
                final_size=final_size)


if __name__ == "__main__":
    print("=== G32: atom-proximity membrane channel on the REAL emergent shell ===", flush=True)
    seeds = [42, 7]
    off, on = {}, {}
    for s in seeds:
        off[s] = run_arm(s, 0.0, "atom")          # channel off (control)
        on[s] = run_arm(s, 1.0, "atom")           # channel on, atom-proximity mode
        o, n = off[s], on[s]
        print(f"  seed {s} comp0={o['comp0']} R={o['radius']:.1f} f_mem={o['f_mem']:.3f}", flush=True)
        print(f"    OFF: comp={o['crossed_compatible']:.3f} incomp={o['crossed_incompatible']:.3f} final={o['final_size']}", flush=True)
        print(f"    ON : comp={n['crossed_compatible']:.3f} incomp={n['crossed_incompatible']:.3f} final={n['final_size']}", flush=True)

    off_c = np.mean([off[s]['crossed_compatible'] for s in seeds])
    off_i = np.mean([off[s]['crossed_incompatible'] for s in seeds])
    on_c = np.mean([on[s]['crossed_compatible'] for s in seeds])
    on_i = np.mean([on[s]['crossed_incompatible'] for s in seeds])

    G32a = (off_c > 0.5 and off_i > 0.5 and abs(off_c - off_i) < 0.20)
    G32b = on_i < 0.20
    G32c = on_c > 0.60
    G32d = (on_c - on_i) >= 0.40
    G32e = all(on[s]['final_size'] >= 0.6 * off[s]['final_size'] for s in seeds)
    passed = G32a and G32b and G32c and G32d and G32e
    print("\n--- VERDICT ---", flush=True)
    print(f"G32a control transparent       : {G32a} (c={off_c:.3f}, i={off_i:.3f})", flush=True)
    print(f"G32b blocks incompatible       : {G32b} ({on_i:.3f})", flush=True)
    print(f"G32c passes compatible         : {G32c} ({on_c:.3f})", flush=True)
    print(f"G32d selective on real shell   : {G32d} ({on_c-on_i:+.3f})", flush=True)
    print(f"G32e shell survives channel    : {G32e}", flush=True)
    verdict = ("PASS - atom-proximity reflector seals the emergent shell while staying "
               "selective and non-destabilising") if passed else "NULL/partial"
    print(f"\nG32: {verdict}", flush=True)
    d = Path.home() / ".eqmod" / "bet" / "G32"; d.mkdir(parents=True, exist_ok=True)
    (d / "result.json").write_text(json.dumps(
        {"off_c": off_c, "off_i": off_i, "on_c": on_c, "on_i": on_i,
         "off": off, "on": on, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

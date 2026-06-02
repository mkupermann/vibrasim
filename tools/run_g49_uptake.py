"""G49 — selective uptake. Does the 'uptake' channel mode (trap compatible inside) CONCENTRATE
a nutrient in the interior above exterior levels, vs the plain G32 channel (control)?

Pre-registered bars in docs/amendments/g49_selective_uptake.md.
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
MEASURE = 200


def compat_concentration(w, centre, radius, f_mem, c_lo, c_hi, box):
    """Interior vs exterior COMPATIBLE free-vibration concentration (count/volume)."""
    alive = w.s_alive[: w.s_pos.shape[0]]
    if not alive.any():
        return 0.0, 0.0
    pos = w.s_pos[alive]; freq = w.s_freq[alive]
    fmin = np.minimum(freq, f_mem)
    ratio = np.abs(freq - f_mem) / np.maximum(fmin, 1e-12)
    compatible = (ratio >= c_lo) & (ratio <= c_hi)
    d = pos - centre; d -= box * np.round(d / box)
    r = np.linalg.norm(d, axis=1)
    r_in = 0.6 * radius
    v_in = (4.0 / 3.0) * math.pi * r_in ** 3
    v_out = max(box[0] * box[1] * box[2] - v_in, 1e-9)
    n_in = int((compatible & (r < r_in)).sum())
    n_out = int((compatible & (r >= r_in)).sum())
    return n_in / v_in, n_out / v_out


def run_arm(seed, uptake):
    c = cfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    geom = membrane_geom(w)
    if geom is None:
        return None
    centre, radius, f_mem, comp0 = geom
    c_lo, c_hi = c.freq_ratio - c.freq_tolerance, c.freq_ratio + c.freq_tolerance
    box = np.asarray(c.box_size, dtype=np.float64)
    w.config = replace(c, membrane_channel_k=1.0, membrane_channel_mode='atom',
                       membrane_channel_recompute=20, membrane_channel_uptake=uptake)
    ratios = []
    for t in range(MEASURE):
        tick(w, c.dt)
        if t % 10 == 9:
            ci, ce = compat_concentration(w, centre, radius, f_mem, c_lo, c_hi, box)
            ratios.append(ci / ce if ce > 1e-12 else (9.9 if ci > 0 else 1.0))
    last = ratios[-(len(ratios) // 3 or 1):]
    return dict(comp0=comp0, mean_ratio=float(np.mean(last)))


if __name__ == "__main__":
    print("=== G49: selective uptake — does the membrane concentrate a nutrient? ===", flush=True)
    seeds = [42, 7]
    up, plain = {}, {}
    for s in seeds:
        up[s] = run_arm(s, uptake=True)
        plain[s] = run_arm(s, uptake=False)
        print(f"  seed {s}: comp={up[s]['comp0']} | UPTAKE interior/exterior compatible={up[s]['mean_ratio']:.2f} "
              f"| PLAIN={plain[s]['mean_ratio']:.2f}", flush=True)

    G49a = all(up[s]['comp0'] >= 50 for s in seeds)
    G49b = all(up[s]['mean_ratio'] >= 1.5 for s in seeds)
    G49c = all(plain[s]['mean_ratio'] <= 1.2 for s in seeds)
    passed = G49a and G49b and G49c

    print("\n--- VERDICT ---", flush=True)
    print(f"G49a membrane forms (>=50)         : {G49a}", flush=True)
    print(f"G49b uptake accumulates (>=1.5x)   : {G49b}", flush=True)
    print(f"G49c plain no accumulation (<=1.2) : {G49c}", flush=True)
    verdict = ("PASS - the membrane actively CONCENTRATES a nutrient interior above exterior "
               "(active uptake), only with the trap") if passed else "NULL/partial"
    print(f"\nG49: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G49"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"uptake": up, "plain": plain, "passed": passed,
                                                  "G49a": G49a, "G49b": G49b, "G49c": G49c}, indent=2, default=str))
    print("DONE", flush=True)

"""G63 — filter bank / frequency discrimination. Same mid-frequency drive to small (higher cutoff)
vs large (lower cutoff) membrane: the small passes it more -> discrimination by membrane size.

Pre-registered bars in docs/amendments/g63_filter_bank.md.
"""
import sys, json, math
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as cfg22, membrane_geom
from tools.run_g51_population import cfg as cfg33
from tools.run_g44_recovery import interior_incompat_conc
from tools.run_g59_rejection import inject_rate

SETTLE = 250
PRECLEAR = 60
WINDOW = 1000
BASE = 4
PERIOD = 600   # mid frequency: below small's cutoff (passes), near/below large's (attenuated more)


def amp_at(makecfg, seed):
    c = makecfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    geom = membrane_geom(w)
    if geom is None:
        return None
    centre, radius, f_mem, _ = geom
    c_lo, c_hi = c.freq_ratio - c.freq_tolerance, c.freq_ratio + c.freq_tolerance
    box = np.asarray(c.box_size, dtype=np.float64)
    w.config = replace(c, membrane_channel_k=1.0, membrane_channel_mode='atom', membrane_channel_recompute=20)
    for _ in range(PRECLEAR):
        tick(w, c.dt)
    rng = np.random.default_rng(1200 + seed)
    series = []
    for t in range(WINDOW):
        n = int(round(BASE * (1.0 + math.sin(2 * math.pi * t / PERIOD))))
        if n > 0:
            inject_rate(w, centre, radius, f_mem, box, rng, n)
        tick(w, c.dt)
        series.append(interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box))
    x = np.array(series); x = x - x.mean()
    t = np.arange(WINDOW); omega = 2 * math.pi / PERIOD
    return dict(radius=float(radius),
                amp=2.0 / WINDOW * math.hypot((x * np.cos(omega * t)).sum(), (x * np.sin(omega * t)).sum()))


if __name__ == "__main__":
    print("=== G63: filter bank / frequency discrimination by membrane size ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        sm = amp_at(cfg22, s)
        lg = amp_at(cfg33, s)
        R[s] = dict(small=sm, large=lg, ratio=(sm['amp'] / lg['amp'] if lg['amp'] > 1e-9 else 9.9))
        print(f"  seed {s}: SMALL R={sm['radius']:.1f} amp={sm['amp']:.4f} | LARGE R={lg['radius']:.1f} amp={lg['amp']:.4f} | small/large={R[s]['ratio']:.2f}", flush=True)

    G63a = all(R[s]['ratio'] >= 1.3 for s in seeds)
    passed = G63a

    print("\n--- VERDICT ---", flush=True)
    print(f"G63a discrimination (small/large >=1.3): {G63a}", flush=True)
    verdict = ("PASS - two membrane sizes form a filter bank: frequency discrimination by size"
               if passed else "NULL/partial - cutoffs too close to discriminate")
    print(f"\nG63: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G63"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "G63a": G63a, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

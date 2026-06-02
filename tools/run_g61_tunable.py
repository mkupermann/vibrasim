"""G61 — tunable cutoff. Measure interior clearance tau on the small (box-22) vs large (box-33)
emergent membrane. Does tau scale with membrane size (tunable low-pass cutoff)?

Pre-registered bars in docs/amendments/g61_tunable_cutoff.md.
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
from tools.run_g58_controller import inject

SETTLE = 250
PRECLEAR = 60
RECOVER = 260
BOLUS = 120


def measure_tau(makecfg, seed):
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
    rng = np.random.default_rng(950 + seed)
    inject(w, centre, radius, f_mem, box, rng, BOLUS)
    peak = interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box)
    series = []
    for t in range(RECOVER):
        tick(w, c.dt)
        series.append(interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box))
    target = peak / math.e
    tau = next((i + 1 for i, v in enumerate(series) if v <= target), len(series))
    end = float(np.mean(series[-3:])) if len(series) >= 3 else (series[-1] if series else 0)
    return dict(radius=float(radius), peak=peak, tau=tau, end_over_peak=(end / peak if peak > 1e-12 else 0.0))


if __name__ == "__main__":
    print("=== G61: tunable cutoff (tau vs membrane size) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[(s, 'small')] = measure_tau(cfg22, s)
        R[(s, 'large')] = measure_tau(cfg33, s)
        sm, lg = R[(s, 'small')], R[(s, 'large')]
        print(f"  seed {s}: SMALL R={sm['radius']:.1f} tau={sm['tau']} (end/peak {sm['end_over_peak']:.2f}) | "
              f"LARGE R={lg['radius']:.1f} tau={lg['tau']} (end/peak {lg['end_over_peak']:.2f}) | "
              f"tau_ratio={lg['tau']/max(sm['tau'],1):.2f}", flush=True)

    G61a = all(R[(s, k)]['end_over_peak'] <= 0.3 for s in seeds for k in ('small', 'large'))
    G61b = all(R[(s, 'large')]['tau'] / max(R[(s, 'small')]['tau'], 1) >= 1.3 for s in seeds)
    passed = G61a and G61b

    print("\n--- VERDICT ---", flush=True)
    print(f"G61a both recover                 : {G61a}", flush=True)
    print(f"G61b tau scales with size (>=1.3x): {G61b}", flush=True)
    verdict = ("PASS - filter time-constant scales with membrane size (tunable low-pass cutoff)"
               if passed else "NULL/partial - tau not set by membrane size")
    print(f"\nG61: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G61"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {f"{k[0]}_{k[1]}": v for k, v in R.items()},
                                                  "G61a": G61a, "G61b": G61b, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

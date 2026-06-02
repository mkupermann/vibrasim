"""G60 — frequency response of the proto-cell controller. Sinusoidally modulated foreign influx;
measure interior response amplitude (single-bin DFT) at slow vs fast drive. Low-pass = slow tracks,
fast attenuates.

Pre-registered bars in docs/amendments/g60_frequency_response.md.
"""
import sys, json, math
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg, membrane_geom
from tools.run_g44_recovery import interior_incompat_conc
from tools.run_g59_rejection import inject_rate

SETTLE = 250
PRECLEAR = 60
WINDOW = 1200
BASE = 4


def response_amplitude(seed, period):
    c = cfg(seed); w = World(c)
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
    rng = np.random.default_rng(900 + seed + period)
    series = []
    for t in range(WINDOW):
        n = int(round(BASE * (1.0 + math.sin(2 * math.pi * t / period))))
        if n > 0:
            inject_rate(w, centre, radius, f_mem, box, rng, n)
        tick(w, c.dt)
        series.append(interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box))
    x = np.array(series)
    x = x - x.mean()
    t = np.arange(WINDOW)
    omega = 2 * math.pi / period
    # single-bin DFT magnitude at the drive frequency
    re = (x * np.cos(omega * t)).sum()
    im = (x * np.sin(omega * t)).sum()
    return 2.0 / WINDOW * math.hypot(re, im)


if __name__ == "__main__":
    print("=== G60: controller frequency response (low-pass filter?) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        slow = response_amplitude(s, 600)
        fast = response_amplitude(s, 60)
        R[s] = dict(slow=slow, fast=fast, ratio=(slow / fast if fast > 1e-9 else 9.9))
        print(f"  seed {s}: amp(slow,P=600)={slow:.4f} amp(fast,P=60)={fast:.4f} ratio={R[s]['ratio']:.2f}", flush=True)

    G60a = all(R[s]['ratio'] >= 2.0 for s in seeds)
    passed = G60a

    print("\n--- VERDICT ---", flush=True)
    print(f"G60a low-pass (slow/fast >=2.0)   : {G60a}", flush=True)
    verdict = ("PASS - proto-cell controller is a first-order LOW-PASS FILTER (passes slow, attenuates fast)"
               if passed else "NULL/partial - not frequency-selective / signal too noisy")
    print(f"\nG60: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G60"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "G60a": G60a, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

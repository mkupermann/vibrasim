"""G62 — analog denoising. Drive the proto-cell interior with slow signal + fast noise (equal
amplitude); does the interior recover the signal (amp_signal >> amp_noise)?

Pre-registered bars in docs/amendments/g62_analog_denoising.md.
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
BASE = 6
P_SIG = 600
P_NOISE = 40


def dft_amp(x, period):
    x = x - x.mean()
    t = np.arange(len(x))
    omega = 2 * math.pi / period
    re = (x * np.cos(omega * t)).sum()
    im = (x * np.sin(omega * t)).sum()
    return 2.0 / len(x) * math.hypot(re, im)


def run(seed):
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
    rng = np.random.default_rng(1100 + seed)
    series = []
    for t in range(WINDOW):
        n = int(round(BASE * (1.0 + 0.4 * math.sin(2 * math.pi * t / P_SIG) + 0.4 * math.sin(2 * math.pi * t / P_NOISE))))
        if n > 0:
            inject_rate(w, centre, radius, f_mem, box, rng, n)
        tick(w, c.dt)
        series.append(interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box))
    x = np.array(series)
    a_sig = dft_amp(x, P_SIG)
    a_noise = dft_amp(x, P_NOISE)
    return dict(a_sig=a_sig, a_noise=a_noise, ratio=(a_sig / a_noise if a_noise > 1e-9 else 9.9))


if __name__ == "__main__":
    print("=== G62: analog denoising (recover signal from noise) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: amp_signal={R[s]['a_sig']:.4f} amp_noise={R[s]['a_noise']:.4f} SNR_gain={R[s]['ratio']:.2f}", flush=True)

    G62a = all(R[s]['ratio'] >= 3.0 for s in seeds)
    passed = G62a

    print("\n--- VERDICT ---", flush=True)
    print(f"G62a denoising gain (>=3.0)       : {G62a}", flush=True)
    verdict = ("PASS - the proto-cell DENOISES: recovers the slow signal, rejects fast noise (analog computation)"
               if passed else "NULL/partial - filtering too weak to denoise")
    print(f"\nG62: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G62"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "G62a": G62a, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

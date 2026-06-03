"""G76 — complete analog receiver: recover an AM envelope BURIED IN NOISE (denoise G62 + demodulate
G75 in one pass). Input = amplitude-modulated carrier + random broadband noise. Does the interior
recover the slow envelope while rejecting the noise?

Pre-registered bars in docs/amendments/g76_receiver.md.
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
BASE = 12
P_CARRIER = 40
P_ENV = 600
P_PROBE = 137   # off-signal frequency = noise floor reference


def dft_amp(x, period):
    x = x - x.mean(); t = np.arange(len(x)); w = 2 * math.pi / period
    return 2.0 / len(x) * math.hypot((x * np.cos(w * t)).sum(), (x * np.sin(w * t)).sum())


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
    rng = np.random.default_rng(1400 + seed)
    series = []
    for t in range(WINDOW):
        env = 0.5 + 0.5 * math.sin(2 * math.pi * t / P_ENV)
        carrier = 0.5 + 0.5 * math.sin(2 * math.pi * t / P_CARRIER)
        noise = rng.integers(0, BASE)                          # broadband random noise, comparable amplitude
        n = int(round(BASE * env * carrier)) + int(noise)
        if n > 0:
            inject_rate(w, centre, radius, f_mem, box, rng, n)
        tick(w, c.dt)
        series.append(interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box))
    x = np.array(series)
    return dict(env_amp=dft_amp(x, P_ENV), noise_floor=dft_amp(x, P_PROBE))


if __name__ == "__main__":
    print("=== G76: complete analog receiver (recover AM envelope buried in noise) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        snr = R[s]['env_amp'] / R[s]['noise_floor'] if R[s]['noise_floor'] > 1e-9 else 9.9
        R[s]['snr'] = snr
        print(f"  seed {s}: envelope_amp={R[s]['env_amp']:.4f} noise_floor={R[s]['noise_floor']:.4f} SNR={snr:.2f}", flush=True)

    G76a = all(R[s]['snr'] >= 3.0 and R[s]['env_amp'] >= 0.02 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G76a envelope recovered from noise (SNR>=3, env>=0.02): {G76a}", flush=True)
    verdict = ("PASS - the substrate is a complete analog RECEIVER: recovers an AM envelope buried in noise (denoise + demodulate)"
               if G76a else "NULL - envelope not cleanly recovered from noise")
    print(f"\nG76: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G76"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "passed": G76a}, indent=2, default=str))
    print("DONE", flush=True)

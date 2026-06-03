"""G75 — nonlinear computation: AM demodulation (envelope detection). Drive the interior with an
amplitude-modulated foreign influx: a FAST carrier (above the low-pass cutoff) whose amplitude is a
SLOW envelope. The envelope frequency is NOT present in the input spectrum (it lives only in the
modulation) — a LINEAR system outputs ~0 there. Only a NONLINEAR element (the saturation, G74) can
demodulate it. If the interior shows the envelope frequency, the substrate COMPUTED a nonlinear
function (something a filter alone cannot do).

Pre-registered bars in docs/amendments/g75_demodulation.md.
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
    rng = np.random.default_rng(1300 + seed)
    series = []
    for t in range(WINDOW):
        env = 0.5 + 0.5 * math.sin(2 * math.pi * t / P_ENV)        # slow envelope in [0,1]
        carrier = 0.5 + 0.5 * math.sin(2 * math.pi * t / P_CARRIER)  # fast carrier
        n = int(round(BASE * env * carrier))                        # AM: envelope modulates carrier amplitude
        if n > 0:
            inject_rate(w, centre, radius, f_mem, box, rng, n)
        tick(w, c.dt)
        series.append(interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box))
    x = np.array(series)
    return dict(env_amp=dft_amp(x, P_ENV), carrier_amp=dft_amp(x, P_CARRIER))


if __name__ == "__main__":
    print("=== G75: AM demodulation / envelope detection (nonlinear computation) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        ratio = R[s]['env_amp'] / R[s]['carrier_amp'] if R[s]['carrier_amp'] > 1e-9 else 9.9
        R[s]['ratio'] = ratio
        print(f"  seed {s}: envelope_amp={R[s]['env_amp']:.4f} carrier_amp={R[s]['carrier_amp']:.4f} env/carrier={ratio:.2f}", flush=True)

    G75a = all(R[s]['ratio'] >= 2.0 and R[s]['env_amp'] >= 0.02 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G75a envelope recovered (env/carrier>=2, env>=0.02): {G75a}", flush=True)
    verdict = ("PASS - the substrate DEMODULATES (envelope detection): a nonlinear computation a linear filter cannot do"
               if G75a else "NULL - no envelope recovered (no usable nonlinear demodulation)")
    print(f"\nG75: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G75"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "passed": G75a}, indent=2, default=str))
    print("DONE", flush=True)

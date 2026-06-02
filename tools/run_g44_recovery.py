"""G44 — homeostatic recovery. Inject a bolus of foreign (incompatible) vibrations INTO the
proto-cell interior; does it self-clear back to depleted (channel ON) vs stay contaminated
(channel OFF)?

Pre-registered bars in docs/amendments/g44_homeostatic_recovery.md.
"""
import sys, json, math
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick, _largest_bridged_component, _fit_sphere
from tools.run_g43_protocell import cfg, membrane_geom

SETTLE = 250
RECOVER = 220
BOLUS = 120


def interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box):
    alive = w.s_alive[: w.s_pos.shape[0]]
    if not alive.any():
        return 0.0
    pos = w.s_pos[alive]; freq = w.s_freq[alive]
    fmin = np.minimum(freq, f_mem)
    ratio = np.abs(freq - f_mem) / np.maximum(fmin, 1e-12)
    incompatible = ~((ratio >= c_lo) & (ratio <= c_hi))
    d = pos - centre; d -= box * np.round(d / box)
    r = np.linalg.norm(d, axis=1)
    r_in = 0.6 * radius
    v_in = (4.0 / 3.0) * math.pi * r_in ** 3
    return int(((r < r_in) & incompatible).sum()) / v_in


def inject_foreign_interior(w, centre, radius, f_mem, box, rng):
    """Place BOLUS incompatible vibrations inside r<0.5R, frozen. Frees slots first if the
    buffer is full (kill farthest-from-centre exterior vibrations — far-field ambient)."""
    free = np.where(~w.s_alive)[0]
    if len(free) < BOLUS:
        alive_idx = np.where(w.s_alive)[0]
        d = w.s_pos[alive_idx] - centre
        d -= box * np.round(d / box)
        r = np.linalg.norm(d, axis=1)
        kill = alive_idx[np.argsort(-r)][: (BOLUS - len(free))]
        w.s_alive[kill] = False
        free = np.where(~w.s_alive)[0]
    k = min(BOLUS, len(free))
    if k == 0:
        return
    sl = free[:k]
    dirs = rng.normal(size=(k, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    rad = rng.uniform(0.0, 0.5 * radius, k)[:, None]
    w.s_pos[sl] = (centre + dirs * rad) % box
    w.s_vel[sl] = rng.normal(0.0, 3.0, size=(k, 3))
    w.s_freq[sl] = f_mem * 3.0          # incompatible (ratio 2.0, far outside band)
    w.s_pol[sl] = rng.random(k) < 0.5
    w.s_alive[sl] = True
    w.n_alive = max(w.n_alive, int(sl.max()) + 1)


def run_arm(seed, channel):
    c = cfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    geom = membrane_geom(w)
    if geom is None:
        return None
    centre, radius, f_mem, comp0 = geom
    c_lo, c_hi = c.freq_ratio - c.freq_tolerance, c.freq_ratio + c.freq_tolerance
    box = np.asarray(c.box_size, dtype=np.float64)
    if channel:
        w.config = replace(c, membrane_channel_k=1.0, membrane_channel_mode='atom',
                           membrane_channel_recompute=20)
    # Pre-clear: let the channel establish the depleted set-point BEFORE perturbing, so the
    # bolus is a clean disturbance from baseline (proper homeostasis-recovery protocol).
    for _ in range(60):
        tick(w, c.dt)
    pre = interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box)
    rng = np.random.default_rng(500 + seed)
    inject_foreign_interior(w, centre, radius, f_mem, box, rng)
    peak = interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box)
    series = []
    for t in range(RECOVER):
        tick(w, c.dt)
        if t % 10 == 9:
            series.append(interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box))
    end = float(np.mean(series[-3:])) if len(series) >= 3 else (series[-1] if series else 0.0)
    return dict(comp0=comp0, pre=pre, peak=peak, end=end,
                end_over_peak=(end / peak if peak > 1e-12 else 0.0),
                peak_over_pre=(peak / pre if pre > 1e-12 else (9.9 if peak > 0 else 0.0)),
                series=series)


if __name__ == "__main__":
    print("=== G44: proto-cell homeostatic recovery after foreign-bolus perturbation ===", flush=True)
    seeds = [42, 7]
    on, off = {}, {}
    for s in seeds:
        on[s] = run_arm(s, channel=True)
        off[s] = run_arm(s, channel=False)
        print(f"  seed {s}: comp={on[s]['comp0']} | ON pre={on[s]['pre']:.4f} peak={on[s]['peak']:.4f} "
              f"end={on[s]['end']:.4f} end/peak={on[s]['end_over_peak']:.2f} | "
              f"OFF end/peak={off[s]['end_over_peak']:.2f}", flush=True)

    G44a = all(on[s]['peak_over_pre'] >= 3.0 or on[s]['pre'] < 1e-9 for s in seeds) and all(on[s]['peak'] > 0 for s in seeds)
    G44b = all(on[s]['end_over_peak'] <= 0.3 for s in seeds)
    G44c = all(off[s]['end_over_peak'] >= 0.6 for s in seeds)
    passed = G44a and G44b and G44c

    print("\n--- VERDICT ---", flush=True)
    print(f"G44a perturbation lands           : {G44a}", flush=True)
    print(f"G44b recovery ON (end<=0.3 peak)  : {G44b}", flush=True)
    print(f"G44c control no recovery (>=0.6)  : {G44c}", flush=True)
    verdict = ("PASS - the proto-cell actively RESTORES its interior after perturbation "
               "(homeostatic regulation); only with the channel") if passed else "NULL/partial"
    print(f"\nG44: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G44"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"on": on, "off": off, "passed": passed,
                                                  "G44a": G44a, "G44b": G44b, "G44c": G44c},
                                                 indent=2, default=str))
    print("DONE", flush=True)

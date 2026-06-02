"""G58 — homeostatic controller dynamics. Inject foreign boluses of different sizes; is interior
clearance first-order (time-constant independent of magnitude)?

Pre-registered bars in docs/amendments/g58_controller_dynamics.md.
"""
import sys, json, math
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg, membrane_geom
from tools.run_g44_recovery import interior_incompat_conc

SETTLE = 250
PRECLEAR = 60
RECOVER = 220
SIZES = [60, 120, 240]


def inject(w, centre, radius, f_mem, box, rng, n):
    free = np.where(~w.s_alive)[0]
    if len(free) < n:
        ai = np.where(w.s_alive)[0]
        d = w.s_pos[ai] - centre; d -= box * np.round(d / box)
        kill = ai[np.argsort(-np.linalg.norm(d, axis=1))][: (n - len(free))]
        w.s_alive[kill] = False
        free = np.where(~w.s_alive)[0]
    sl = free[:n]
    dirs = rng.normal(size=(n, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    w.s_pos[sl] = (centre + dirs * rng.uniform(0, 0.5 * radius, n)[:, None]) % box
    w.s_vel[sl] = rng.normal(0, 3.0, size=(n, 3))
    w.s_freq[sl] = f_mem * 3.0
    w.s_pol[sl] = rng.random(n) < 0.5
    w.s_alive[sl] = True
    w.n_alive = max(w.n_alive, int(sl.max()) + 1)


def tau_for_size(seed, n):
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
    rng = np.random.default_rng(700 + seed + n)
    inject(w, centre, radius, f_mem, box, rng, n)
    peak = interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box)
    series = []
    for t in range(RECOVER):
        tick(w, c.dt)
        series.append(interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box))
    # time-constant: first tick index where conc <= peak/e
    target = peak / math.e
    tau = next((i + 1 for i, v in enumerate(series) if v <= target), len(series))
    end = float(np.mean(series[-3:])) if len(series) >= 3 else (series[-1] if series else 0)
    return dict(peak=peak, tau=tau, end_over_peak=(end / peak if peak > 1e-12 else 0.0))


if __name__ == "__main__":
    print("=== G58: homeostatic controller dynamics (first-order clearance?) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        for n in SIZES:
            R[(s, n)] = tau_for_size(s, n)
            r = R[(s, n)]
            print(f"  seed {s} bolus={n}: peak={r['peak']:.3f} tau={r['tau']} ticks end/peak={r['end_over_peak']:.2f}", flush=True)

    G58a = all(R[(s, n)]['end_over_peak'] <= 0.3 for s in seeds for n in SIZES)
    def tau_ratio(s):
        taus = [R[(s, n)]['tau'] for n in SIZES]
        return max(taus) / max(min(taus), 1)
    G58b = all(tau_ratio(s) <= 1.6 for s in seeds)
    passed = G58a and G58b

    print("\n--- VERDICT ---", flush=True)
    for s in seeds:
        print(f"  seed {s}: taus={[R[(s,n)]['tau'] for n in SIZES]} ratio={tau_ratio(s):.2f}", flush=True)
    print(f"G58a recovers all magnitudes      : {G58a}", flush=True)
    print(f"G58b first-order (tau ratio<=1.6) : {G58b}", flush=True)
    verdict = ("PASS - proto-cell is a first-order LINEAR homeostatic controller (magnitude-independent clearance)"
               if passed else "NULL/partial - clearance is nonlinear/saturable")
    print(f"\nG58: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G58"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {f"{k[0]}_n{k[1]}": v for k, v in R.items()},
                                                  "G58a": G58a, "G58b": G58b, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

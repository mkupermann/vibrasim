"""G59 — steady-state disturbance rejection. Sustained foreign influx into the interior at varying
rates; does interior conc reach a bounded steady-state that scales linearly with influx (first-
order controller)?

Pre-registered bars in docs/amendments/g59_disturbance_rejection.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg, membrane_geom
from tools.run_g44_recovery import interior_incompat_conc

SETTLE = 250
PRECLEAR = 60
WINDOW = 200
RATES = [2, 4, 8]


def inject_rate(w, centre, radius, f_mem, box, rng, n):
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


def ss_for_rate(seed, rate):
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
    rng = np.random.default_rng(800 + seed + rate)
    series = []
    for t in range(WINDOW):
        inject_rate(w, centre, radius, f_mem, box, rng, rate)
        tick(w, c.dt)
        series.append(interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box))
    return float(np.mean(series[-WINDOW // 3:]))


if __name__ == "__main__":
    print("=== G59: steady-state disturbance rejection (proportional offset?) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        for rate in RATES:
            R[(s, rate)] = ss_for_rate(s, rate)
            print(f"  seed {s} influx={rate}/tick: ss interior conc={R[(s, rate)]:.3f}", flush=True)

    G59a = all(R[(s, rate)] < 0.5 for s in seeds for rate in RATES)
    def gain(s):
        return R[(s, 8)] / max(R[(s, 2)], 1e-9)
    G59b = all(2.5 <= gain(s) <= 5.5 for s in seeds)
    passed = G59a and G59b

    print("\n--- VERDICT ---", flush=True)
    for s in seeds:
        print(f"  seed {s}: ss={[round(R[(s,r)],3) for r in RATES]} gain(8/2)={gain(s):.2f}", flush=True)
    print(f"G59a bounded (<0.5 all rates)     : {G59a}", flush=True)
    print(f"G59b proportional (gain in [2.5,5.5]): {G59b}", flush=True)
    verdict = ("PASS - proto-cell rejects sustained disturbance with a bounded, proportional offset (complete first-order controller)"
               if passed else "NULL/partial - rejection not bounded/proportional")
    print(f"\nG59: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G59"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {f"{k[0]}_r{k[1]}": v for k, v in R.items()},
                                                  "G59a": G59a, "G59b": G59b, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)

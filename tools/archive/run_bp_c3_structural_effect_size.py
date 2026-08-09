"""BP-C3 — dual-drive structural effect size (headless)."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick
from world.state import World

N_SIDE, T_FULL, SEEDS, TRIALS = 400, 1200, (91, 93, 97), 3
MID = 40.0
LOW, HIGH, SAME = (100., 2000.), (500., 10000.), (100., 10000.)


def make_cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80., 50., 50.),
        n_vibrations_max=4096, n_nodes_max=4096, rng_seed=seed,
        r_1=5., r_2=28., freq_tolerance=0.03,
        pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=5., speed_max=25.,
    )


def inject(w, rng, start, n, x0, x1, f0, f1):
    for k in range(n):
        i = start + k
        w.s_pos[i] = [rng.uniform(x0, x1), rng.uniform(5, 45), rng.uniform(5, 45)]
        w.s_freq[i] = float(np.exp(rng.uniform(np.log(f0), np.log(f1))))
        w.s_pol[i] = k % 2 == 0
        z, phi = rng.uniform(-1, 1), rng.uniform(0, 2*np.pi)
        sq = float(np.sqrt(max(1 - z*z, 0)))
        sp = float(rng.uniform(5, 25))
        w.s_vel[i] = sp * np.array([sq*np.cos(phi), sq*np.sin(phi), z])
        w.s_alive[i] = True
    w.n_alive = max(w.n_alive, start + n)


def plant(w, seed, same):
    rng = np.random.default_rng(seed)
    bl, br = (SAME, SAME) if same else (LOW, HIGH)
    inject(w, rng, 0, N_SIDE, 5, 35, bl[0], bl[1])
    inject(w, rng, N_SIDE, N_SIDE, 45, 75, br[0], br[1])


def sides(w):
    L, R = [], []
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        d = int(math.floor(math.log10(max(float(w.k_freq[i]), 1))))
        (L if float(w.k_pos[i, 0]) < MID else R).append(d)
    mL = float(np.mean(L)) if L else None
    mR = float(np.mean(R)) if R else None
    return mL, mR, len(L) >= 1 and len(R) >= 1


def trial(seed, ti, same, ticks):
    w = World(make_cfg(seed))
    plant(w, seed * 1009 + ti * 17 + (3 if same else 0), same)
    dt = float(w.config.dt)
    for _ in range(ticks):
        tick(w, dt); w.t += dt
    mL, mR, pop = sides(w)
    dlt = (mR - mL) if (mL is not None and mR is not None) else None
    return {"mL": mL, "mR": mR, "delta": dlt, "pop": pop, "pos": dlt is not None and dlt > 0}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    if args.smoke:
        seeds, trials, ticks, smoke = (91,), 1, 500, True
    else:
        seeds, trials, ticks, smoke = SEEDS, TRIALS, T_FULL, False
    print(f"BP-C3 start smoke={smoke} seeds={seeds} trials={trials} T={ticks}")
    dual, same = [], []
    for s in seeds:
        for ti in range(trials):
            dual.append(trial(s, ti, False, ticks))
            same.append(trial(s, ti, True, ticks))
    d_vals = [r["delta"] for r in dual if r["delta"] is not None]
    s_vals = [abs(r["delta"]) for r in same if r["delta"] is not None]
    mean_d = float(np.mean(d_vals)) if d_vals else 0.0
    mean_s = float(np.mean(s_vals)) if s_vals else 0.0
    pop = float(sum(1 for r in dual if r["pop"]) / len(dual))
    posf = float(sum(1 for r in dual if r["pos"]) / len(dual))
    b1, b2, b3, b4 = mean_d >= 0.40, mean_s <= 0.20, pop >= 0.80, posf >= 0.70
    verdict = "PASS" if all([b1, b2, b3, b4]) else "NULL"
    result = {
        "id": "BP-C3", "smoke": smoke,
        "bars": {
            "B1_mean_delta": {"value": mean_d, "threshold": 0.40, "pass": b1},
            "B2_same_abs": {"value": mean_s, "threshold": 0.20, "pass": b2},
            "B3_pop": {"value": pop, "threshold": 0.80, "pass": b3},
            "B4_frac_pos": {"value": posf, "threshold": 0.70, "pass": b4},
        },
        "dual_sample": dual[:4], "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-C3"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-C3: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

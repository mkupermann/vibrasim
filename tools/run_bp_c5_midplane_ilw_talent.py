"""BP-C5 — structural specialisation with midplane + FREE vs ILW. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick, apply_ilw_port_event
from world.state import World

N_SIDE, T, SEEDS, TRIALS = 400, 1200, (201, 203, 207), 3
MID = 40.0
LOW, HIGH = (100.0, 2000.0), (500.0, 10000.0)
PORT_L, PORT_R = np.array([20., 25., 25.]), np.array([60., 25., 25.])
F_SEED_L, F_SEED_R = 500.0, 5000.0
N_ILW_EVENTS = 40


def cfg_base(seed, ilw=False):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80., 50., 50.),
        n_vibrations_max=8192, n_nodes_max=4096, rng_seed=seed,
        r_1=5., r_2=28., freq_tolerance=0.03,
        pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=5., speed_max=25.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=ilw, ilw_radius=8.0, ilw_delta_strength=0.5,
    )


def inject(w, rng, birth, n, x0, x1, f0, f1, tag):
    dead = np.where(~w.s_alive)[0]
    slots = dead[:n] if len(dead) >= n else np.arange(int(w.n_alive), min(int(w.n_alive)+n, w.config.n_vibrations_max))
    for k, i in enumerate(slots):
        i = int(i)
        w.s_pos[i] = [rng.uniform(x0, x1), rng.uniform(8, 42), rng.uniform(8, 42)]
        w.s_freq[i] = float(np.exp(rng.uniform(np.log(f0), np.log(f1))))
        w.s_pol[i] = k % 2 == 0
        z, phi = rng.uniform(-1, 1), rng.uniform(0, 2*np.pi)
        sq = float(np.sqrt(max(1-z*z, 0)))
        sp = float(rng.uniform(5, 25))
        w.s_vel[i] = sp * np.array([sq*np.cos(phi), sq*np.sin(phi), z])
        w.s_alive[i] = True
        if birth is not None:
            birth[i] = tag
    w.n_alive = int(w.s_alive.sum())


def sides_md(w):
    L, R = [], []
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        d = int(math.floor(math.log10(max(float(w.k_freq[i]), 1.0))))
        (L if float(w.k_pos[i, 0]) < MID else R).append(d)
    mL = float(np.mean(L)) if L else None
    mR = float(np.mean(R)) if R else None
    pop = len(L) >= 1 and len(R) >= 1
    ok = pop and mL is not None and mR is not None and mL < mR
    return mL, mR, pop, ok


def chi_measure(w, birth, ticks):
    dt = float(w.config.dt)
    wrong = free = 0
    for _ in range(ticks):
        for i in np.where(w.s_alive)[0]:
            tag = int(birth[i])
            if tag == 0:
                continue
            free += 1
            x = float(w.s_pos[i, 0])
            if tag == 1 and x >= MID:
                wrong += 1
            if tag == 2 and x < MID:
                wrong += 1
        tick(w, dt)
        w.t += dt
    return float(wrong / free) if free else 0.0


def run_free(seed, ti, ticks):
    w = World(cfg_base(seed, ilw=False))
    birth = np.zeros(w.config.n_vibrations_max, dtype=np.int8)
    rng = np.random.default_rng(seed * 1009 + ti * 13)
    inject(w, rng, birth, N_SIDE, 8, 32, LOW[0], LOW[1], 1)
    inject(w, rng, birth, N_SIDE, 48, 72, HIGH[0], HIGH[1], 2)
    chi = chi_measure(w, birth, ticks)
    mL, mR, pop, ok = sides_md(w)
    return {"arm": "FREE", "ok": ok, "pop": pop, "chi": chi, "mL": mL, "mR": mR}


def run_ilw(seed, ti, ticks):
    w = World(cfg_base(seed, ilw=True))
    rng = np.random.default_rng(seed * 1013 + ti * 17)
    period = max(1, ticks // N_ILW_EVENTS)
    dt = float(w.config.dt)
    for t in range(ticks):
        if t % period == 0:
            apply_ilw_port_event(w, PORT_L, rng, seed_freq=F_SEED_L)
            apply_ilw_port_event(w, PORT_R, rng, seed_freq=F_SEED_R)
        tick(w, dt)
        w.t += dt
    mL, mR, pop, ok = sides_md(w)
    return {"arm": "ILW", "ok": ok, "pop": pop, "chi": 0.0, "mL": mL, "mR": mR}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials, ticks = ((201,), 1, 300) if args.smoke else (SEEDS, TRIALS, T)
    print(f"BP-C5 start smoke={args.smoke} seeds={seeds} trials={trials} T={ticks}")
    free_rows, ilw_rows = [], []
    for s in seeds:
        for ti in range(trials):
            free_rows.append(run_free(s, ti, ticks))
            ilw_rows.append(run_ilw(s, ti, ticks))

    def rate(rows, key):
        return float(sum(1 for r in rows if r[key]) / len(rows)) if rows else 0.0

    b1 = rate(free_rows, "ok")
    b2 = rate(ilw_rows, "ok")
    b3 = rate(free_rows, "pop")
    b4 = rate(ilw_rows, "pop")
    chi = float(np.mean([r["chi"] for r in free_rows]))
    b5 = chi <= 0.15
    p1, p2, p3, p4, p5 = b1 >= 0.90, b2 >= 0.90, b3 >= 0.80, b4 >= 0.80, b5
    verdict = "PASS" if all([p1, p2, p3, p4, p5]) else "NULL"
    result = {
        "id": "BP-C5",
        "bars": {
            "B1_FREE_spec": {"value": b1, "threshold": 0.90, "pass": p1},
            "B2_ILW_spec": {"value": b2, "threshold": 0.90, "pass": p2},
            "B3_FREE_pop": {"value": b3, "threshold": 0.80, "pass": p3},
            "B4_ILW_pop": {"value": b4, "threshold": 0.80, "pass": p4},
            "B5_chi": {"value": chi, "threshold": 0.15, "pass": p5},
        },
        "free_sample": free_rows[:3],
        "ilw_sample": ilw_rows[:3],
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-C5"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-C5: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

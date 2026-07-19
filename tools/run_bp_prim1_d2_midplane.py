"""PRIM1-D2 midplane wall containment — headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick
from world.state import World

N_SIDE, T, SEEDS, TRIALS = 400, 1200, (171, 173), 2
MID, LOW, HIGH = 40.0, (100., 2000.), (500., 10000.)


def cfg(seed, wall):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80., 50., 50.),
        n_vibrations_max=8192, n_nodes_max=4096, rng_seed=seed,
        r_1=5., r_2=28., freq_tolerance=0.03,
        pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=5., speed_max=25.,
        midplane_wall_enabled=wall, midplane_wall_x=MID,
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
        birth[i] = tag
    w.n_alive = int(w.s_alive.sum())


def measure(w, birth, ticks):
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
    chi = float(wrong / free) if free else 0.0
    nL = nR = 0
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i]) >= 4:
            if float(w.k_pos[i, 0]) < MID:
                nL += 1
            else:
                nR += 1
    return chi, (nL >= 1 and nR >= 1)


def trial(seed, ti, wall, ticks):
    w = World(cfg(seed, wall))
    birth = np.zeros(w.config.n_vibrations_max, dtype=np.int8)
    rng = np.random.default_rng(seed * 1009 + ti * 17 + (20 if wall else 0))
    inject(w, rng, birth, N_SIDE, 8, 32, LOW[0], LOW[1], 1)
    inject(w, rng, birth, N_SIDE, 48, 72, HIGH[0], HIGH[1], 2)
    chi, pop = measure(w, birth, ticks)
    return {"wall": wall, "chi": chi, "pop": pop}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials, ticks = ((171,), 1, 200) if args.smoke else (SEEDS, TRIALS, T)
    print(f"PRIM1-D2 start smoke={args.smoke} seeds={seeds} T={ticks}")
    on, off = [], []
    for s in seeds:
        for ti in range(trials):
            on.append(trial(s, ti, True, ticks))
            off.append(trial(s, ti, False, ticks))
    chi_on = float(np.mean([r["chi"] for r in on]))
    chi_off = float(np.mean([r["chi"] for r in off]))
    pop = float(sum(1 for r in on if r["pop"]) / len(on))
    b1, b2, b3 = chi_on <= 0.15, pop >= 0.80, chi_on < chi_off
    verdict = "PASS" if (b1 and b2 and b3) else "NULL"
    result = {"id": "PRIM1-D2", "bars": {
        "P1_chi_on": {"value": chi_on, "threshold": 0.15, "pass": b1},
        "P2_pop": {"value": pop, "threshold": 0.80, "pass": b2},
        "P3_reduced": {"value": bool(b3), "chi_off": chi_off, "pass": b3},
    }, "verdict": verdict, "on": on, "off": off}
    out = Path.home()/".eqmod"/"bet"/"PRIM1-D2"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"  chi_on={chi_on:.4f} chi_off={chi_off:.4f} pop={pop:.4f}")
    for k, v in result["bars"].items():
        print(f"  {k}: {v}")
    print(f"--- VERDICT ---\nPRIM1-D2: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

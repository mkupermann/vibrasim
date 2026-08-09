"""BP-C7: correct vs scrambled ILW attractors + free dual inject. Headless."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from world.config import WorldConfig
from world.physics import apply_ilw_port_event, tick
from world.state import World

N_SIDE, T, SEEDS, TRIALS = 400, 1000, (751, 761, 771), 3
N_SEED_ILW = 8
MID = 40.0
LOW, HIGH = (100.0, 2000.0), (500.0, 10000.0)
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])


def cfg_base(seed: int) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 50.0, 50.0),
        n_vibrations_max=8192,
        n_nodes_max=4096,
        rng_seed=seed,
        r_1=5.0,
        r_2=28.0,
        freq_tolerance=0.03,
        pair_decay_time=60.0,
        triad_decay_time=600.0,
        lambda_gen=0.0,
        lambda_dec=0.0,
        speed_min=5.0,
        speed_max=25.0,
        midplane_wall_enabled=True,
        midplane_wall_x=MID,
        ilw_enabled=True,
        ilw_radius=8.0,
        ilw_delta_strength=0.5,
    )


def inject(w, rng, birth, n, x0, x1, f0, f1, tag):
    dead = np.where(~w.s_alive)[0]
    if len(dead) >= n:
        slots = dead[:n]
    else:
        slots = np.arange(
            int(w.n_alive),
            min(int(w.n_alive) + n, w.config.n_vibrations_max),
        )
    for k, i in enumerate(slots):
        i = int(i)
        w.s_pos[i] = [
            rng.uniform(x0, x1),
            rng.uniform(8, 42),
            rng.uniform(8, 42),
        ]
        w.s_freq[i] = float(np.exp(rng.uniform(np.log(f0), np.log(f1))))
        w.s_pol[i] = k % 2 == 0
        z, phi = rng.uniform(-1, 1), rng.uniform(0, 2 * np.pi)
        sq = float(np.sqrt(max(1 - z * z, 0)))
        sp = float(rng.uniform(5, 25))
        w.s_vel[i] = sp * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
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


def seed_attractors(w, rng, fL: float, fR: float):
    for _ in range(N_SEED_ILW):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=fL)
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=fR)


def run_arm(seed, ti, ticks, fL_seed: float, fR_seed: float):
    w = World(cfg_base(seed))
    birth = np.zeros(w.config.n_vibrations_max, dtype=np.int8)
    rng = np.random.default_rng(seed * 1201 + ti * 29 + int(fL_seed))
    seed_attractors(w, rng, fL_seed, fR_seed)
    inject(w, rng, birth, N_SIDE, 8, 32, LOW[0], LOW[1], 1)
    inject(w, rng, birth, N_SIDE, 48, 72, HIGH[0], HIGH[1], 2)
    chi = chi_measure(w, birth, ticks)
    mL, mR, pop, ok = sides_md(w)
    return {"ok": ok, "pop": pop, "chi": chi, "mL": mL, "mR": mR}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials, ticks = ((751,), 1, 250) if args.smoke else (SEEDS, TRIALS, T)
    print(f"BP-C7 start smoke={args.smoke} seeds={seeds} trials={trials} T={ticks}")
    correct, scrambled = [], []
    for s in seeds:
        for ti in range(trials):
            correct.append(run_arm(s, ti, ticks, 500.0, 5000.0))
            scrambled.append(run_arm(s, ti, ticks, 5000.0, 500.0))

    def rate(rows, key):
        return float(sum(1 for r in rows if r[key]) / len(rows)) if rows else 0.0

    b1 = rate(correct, "ok")
    b2 = rate(scrambled, "ok")
    b3 = rate(correct, "pop")
    chi = float(np.mean([r["chi"] for r in correct]))
    p1, p2, p3, p4 = b1 >= 0.90, b2 <= 0.55, b3 >= 0.80, chi <= 0.15
    verdict = "PASS" if all([p1, p2, p3, p4]) else "NULL"
    result = {
        "id": "BP-C7",
        "bars": {
            "B1_correct_seed": {"value": b1, "threshold": 0.90, "pass": p1},
            "B2_scrambled_seed": {"value": b2, "threshold": 0.55, "pass": p2},
            "B3_pop": {"value": b3, "threshold": 0.80, "pass": p3},
            "B4_chi": {"value": chi, "threshold": 0.15, "pass": p4},
        },
        "correct_sample": correct[:3],
        "scrambled_sample": scrambled[:3],
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-C7"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-C7: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

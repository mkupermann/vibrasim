"""PRIM2-D0 — ILW vs FREE write contamination contrast. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick, apply_ilw_port_event
from world.state import World

SEEDS, TRIALS, T, N_EVENTS = (181, 191), 2, 600, 30
MID = 40.0
PORT_L = np.array([20.0, 25.0, 25.0])


def cfg_free(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80., 50., 50.),
        n_vibrations_max=8192, n_nodes_max=4096, rng_seed=seed,
        r_1=5., r_2=28., freq_tolerance=0.03,
        pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=5., speed_max=20.,
        midplane_wall_enabled=False, ilw_enabled=False,
    )


def cfg_ilw(seed):
    c = cfg_free(seed)
    # rebuild with ilw on — WorldConfig is frozen
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80., 50., 50.),
        n_vibrations_max=8192, n_nodes_max=4096, rng_seed=seed,
        r_1=5., r_2=28., freq_tolerance=0.03,
        pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=5., speed_max=20.,
        midplane_wall_enabled=False, ilw_enabled=True,
        ilw_radius=8.0, ilw_delta_strength=0.5,
    )


def count_free_right(w):
    n = 0
    for i in np.where(w.s_alive)[0]:
        if float(w.s_pos[i, 0]) >= MID:
            n += 1
    return n


def count_l4_left(w):
    n = 0
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(w.k_pos[i, 0]) < MID:
            n += 1
    return n


def strength_left(w):
    s = 0.0
    for i in range(w.k_count):
        if w.k_alive[i] and float(w.k_pos[i, 0]) < MID:
            s += float(w.k_strength[i])
    return s


def inject_free_left(w, rng, n=200):
    dead = np.where(~w.s_alive)[0]
    slots = dead[:n] if len(dead) >= n else range(int(w.n_alive), min(int(w.n_alive)+n, w.config.n_vibrations_max))
    for k, i in enumerate(slots):
        i = int(i)
        w.s_pos[i] = [rng.uniform(5, 35), rng.uniform(5, 45), rng.uniform(5, 45)]
        w.s_freq[i] = float(np.exp(rng.uniform(np.log(100), np.log(2000))))
        w.s_pol[i] = k % 2 == 0
        z, phi = rng.uniform(-1, 1), rng.uniform(0, 2*np.pi)
        sq = float(np.sqrt(max(1-z*z, 0)))
        sp = float(rng.uniform(5, 20))
        w.s_vel[i] = sp * np.array([sq*np.cos(phi), sq*np.sin(phi), z])
        w.s_alive[i] = True
    w.n_alive = int(w.s_alive.sum())


def run_free(seed, ti, ticks):
    w = World(cfg_free(seed))
    rng = np.random.default_rng(seed * 17 + ti)
    fr0 = count_free_right(w)
    # N_EVENTS free bursts on left
    period = max(1, ticks // N_EVENTS)
    dt = float(w.config.dt)
    for t in range(ticks):
        if t % period == 0:
            inject_free_left(w, rng, 200)
        tick(w, dt)
        w.t += dt
    return {
        "arm": "FREE",
        "delta_free_right": count_free_right(w) - fr0,
        "delta_l4_left": count_l4_left(w),
        "delta_str_left": strength_left(w),
    }


def run_ilw(seed, ti, ticks):
    w = World(cfg_ilw(seed))
    rng = np.random.default_rng(seed * 19 + ti)
    fr0 = count_free_right(w)
    l4_0 = count_l4_left(w)
    str0 = strength_left(w)
    period = max(1, ticks // N_EVENTS)
    dt = float(w.config.dt)
    events = 0
    for t in range(ticks):
        if t % period == 0:
            apply_ilw_port_event(w, PORT_L, rng)
            events += 1
        tick(w, dt)
        w.t += dt
    return {
        "arm": "ILW",
        "delta_free_right": count_free_right(w) - fr0,
        "delta_l4_left": count_l4_left(w) - l4_0,
        "delta_str_left": strength_left(w) - str0,
        "events": events,
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials, ticks = ((181,), 1, 120) if args.smoke else (SEEDS, TRIALS, T)
    print(f"PRIM2-D0 start smoke={args.smoke} seeds={seeds} T={ticks}")
    free_rows, ilw_rows = [], []
    for s in seeds:
        for ti in range(trials):
            free_rows.append(run_free(s, ti, ticks))
            ilw_rows.append(run_ilw(s, ti, ticks))
    dfr_f = float(np.mean([r["delta_free_right"] for r in free_rows]))
    dfr_i = float(np.mean([r["delta_free_right"] for r in ilw_rows]))
    # I1: ILW free-right contamination low
    b_i1 = (dfr_i <= 5.0) or (dfr_f > 0 and dfr_i <= 0.5 * dfr_f)
    # I2: structural change left
    struct = [ (r["delta_str_left"] >= 1.0) or (r["delta_l4_left"] >= 1) for r in ilw_rows ]
    b_i2 = float(sum(struct) / len(struct)) >= 0.80
    # I3: FREE contaminates
    b_i3 = dfr_f >= 10.0
    verdict = "PASS" if (b_i1 and b_i2 and b_i3) else "NULL"
    result = {
        "id": "PRIM2-D0",
        "bars": {
            "I1_ilw_low_right_free": {"value": dfr_i, "free_arm": dfr_f, "threshold": "≤5 or ≤0.5*FREE", "pass": b_i1},
            "I2_ilw_structural": {"value": float(sum(struct)/len(struct)), "threshold": 0.80, "pass": b_i2},
            "I3_free_contaminates": {"value": dfr_f, "threshold": 10.0, "pass": b_i3},
        },
        "free_rows": free_rows, "ilw_rows": ilw_rows,
        "verdict": verdict,
    }
    out = Path.home()/".eqmod"/"bet"/"PRIM2-D0"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v}")
    print(f"--- VERDICT ---\nPRIM2-D0: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

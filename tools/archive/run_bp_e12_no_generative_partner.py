"""BP-E12: no generative partner after R kill. Headless."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from world.config import WorldConfig
from world.physics import apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (441, 451), 10
N_WRITE, T_IDLE, MID = 15, 100, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
PAIRS = ((400.0, 7000.0), (1500.0, 2500.0), (5000.0, 800.0))


def make_cfg(seed: int) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 50.0, 50.0),
        n_vibrations_max=2048,
        n_nodes_max=2048,
        rng_seed=seed,
        r_1=5.0,
        r_2=45.0,
        freq_tolerance=0.03,
        pair_decay_time=60.0,
        triad_decay_time=600.0,
        lambda_gen=0.0,
        lambda_dec=0.0,
        speed_min=0.0,
        speed_max=0.0,
        midplane_wall_enabled=True,
        midplane_wall_x=MID,
        ilw_enabled=True,
        ilw_radius=8.0,
        ilw_delta_strength=0.5,
        atom_valence=4,
        ilw_multislot_enabled=True,
        ilw_multislot_rel_freq=0.35,
    )


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)


def write_pair(w: World, rng, c: int) -> None:
    fL, fR = PAIRS[c]
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=fL)
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=fR)


def write_L_only(w: World, rng, c: int) -> None:
    fL = PAIRS[c][0]
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=fL)


def kill_right(w: World) -> None:
    for i in range(w.k_count):
        if not w.k_alive[i]:
            continue
        if int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) >= MID:
            w.k_alive[i] = False


def has_R_partner(w: World, c: int, tol: float = 0.30) -> bool:
    fR_tgt = PAIRS[c][1]
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) < MID:
            continue
        f = float(w.k_freq[i])
        if abs(f - fR_tgt) / max(fR_tgt, 1.0) < tol:
            return True
    return False


def L_class_ok(w: World, c: int) -> bool:
    fL_tgt = PAIRS[c][0]
    cents = np.array([p[0] for p in PAIRS])
    best_f, n = None, 0
    # mean L freq nearest
    s = 0.0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) >= MID:
            continue
        s += float(w.k_freq[i])
        n += 1
    if n == 0:
        return False
    m = s / n
    pred = int(np.argmin(np.abs(cents - m)))
    return pred == c


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((441,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E12 start smoke={args.smoke}")
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 28029 + ti * 101)
            c = int(rng.integers(0, 3))
            w = World(make_cfg(seed))
            write_pair(w, rng, c)
            idle(w, T_IDLE // 2)
            kill_right(w)
            write_L_only(w, rng, c)
            idle(w, T_IDLE // 2)
            b1s.append(has_R_partner(w, c))  # want rare
            b2s.append(L_class_ok(w, c))
            w2 = World(make_cfg(seed))
            write_pair(w2, rng, c)
            idle(w2, T_IDLE)
            b3s.append(has_R_partner(w2, c))
    a1, a2, a3 = float(np.mean(b1s)), float(np.mean(b2s)), float(np.mean(b3s))
    p1, p2, p3 = a1 <= 0.15, a2 >= 0.90, a3 >= 0.90
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "BP-E12",
        "bars": {
            "B1_R_after_kill": {"value": a1, "threshold": 0.15, "pass": p1},
            "B2_L_persists": {"value": a2, "threshold": 0.90, "pass": p2},
            "B3_ctrl_R": {"value": a3, "threshold": 0.90, "pass": p3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E12"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E12: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

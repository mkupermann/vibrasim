"""BP-E8 cross-midplane bridge after dual ILW. Headless."""
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

SEEDS, TRIALS = (341, 351), 12
N_WRITE, T_IDLE, MID = 15, 300, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])


def make_cfg(seed: int) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 50.0, 50.0),
        n_vibrations_max=2048,
        n_nodes_max=2048,
        rng_seed=seed,
        r_1=5.0,
        r_2=45.0,  # span port distance 40
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
        node_thermal_speed=0.0,
    )


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)


def pop_sides(w: World):
    nL = nR = 0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) < MID:
            nL += 1
        else:
            nR += 1
    return nL, nR


def count_cross_bridges(w: World) -> int:
    n = 0
    B = getattr(w, "b_count", 0) or 0
    if B <= 0 and hasattr(w, "b_alive"):
        B = len(w.b_alive)
    for b in range(B):
        if not w.b_alive[b]:
            continue
        i = int(w.b_atom_i[b])
        j = int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        xi = float(w.k_pos[i, 0])
        xj = float(w.k_pos[j, 0])
        if (xi < MID) != (xj < MID):
            n += 1
    return n


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((341,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E8 start smoke={args.smoke} seeds={seeds} trials={trials}")

    dual_x, one_x, pop = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 23011 + ti * 73)

            # dual
            w = World(make_cfg(seed))
            for _ in range(N_WRITE):
                apply_ilw_port_event(w, PORT_L, rng, seed_freq=500.0)
                apply_ilw_port_event(w, PORT_R, rng, seed_freq=5000.0)
            idle(w, T_IDLE)
            dual_x.append(count_cross_bridges(w) >= 1)
            nL, nR = pop_sides(w)
            pop.append(nL >= 1 and nR >= 1)

            # one-sided L
            w1 = World(make_cfg(seed))
            for _ in range(N_WRITE):
                apply_ilw_port_event(w1, PORT_L, rng, seed_freq=500.0)
            idle(w1, T_IDLE)
            one_x.append(count_cross_bridges(w1) >= 1)

    a1, a2, a3 = float(np.mean(dual_x)), float(np.mean(one_x)), float(np.mean(pop))
    b1, b2, b3 = a1 >= 0.85, a2 <= 0.15, a3 >= 0.90
    verdict = "PASS" if all([b1, b2, b3]) else "NULL"
    result = {
        "id": "BP-E8",
        "bars": {
            "B1_dual_cross": {"value": a1, "threshold": 0.85, "pass": b1},
            "B2_onesided_cross": {"value": a2, "threshold": 0.15, "pass": b2},
            "B3_pop": {"value": a3, "threshold": 0.90, "pass": b3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E8"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E8: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

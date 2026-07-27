"""PRIM6-D0: charge latch holds after idle; membrane does not. Headless."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (641, 651), 10
N_WRITE, T_PROP, T_END, MID = 12, 40, 80, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])


def make_cfg(seed: int, latch: bool) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 50.0, 50.0),
        n_vibrations_max=2048,
        n_nodes_max=2048,
        rng_seed=seed,
        r_1=5.0,
        r_2=28.0,
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
        atom_valence=0,
        ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True,
        ilw_pair_link_delta=1.0,
        neuron_dynamics_enabled=True,
        theta_fire=2.0,
        t_refractory=0.02,
        n_emit=0,
        bridge_charge_prop_rate=2.0,
        bridge_prop_min_strength=0.0,
        charge_latch_enabled=latch,
        charge_latch_tau=0.0,
    )


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)


def write_pair(w: World, rng) -> None:
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w, PORT_L, PORT_R, 500.0, 5000.0, rng)


def fire_L_prop(w: World) -> None:
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    for t in range(T_PROP):
        if t % 10 == 0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(w.k_pos[i, 0]) < MID:
                    w.k_charge[i] = thr + 5.0
        tick(w, dt)


def max_R_field(w: World, field: str) -> float:
    arr = w.k_latch if field == "latch" else w.k_charge
    m = 0.0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) < MID:
            continue
        m = max(m, float(arr[i]))
    return m


def free_count(w: World) -> int:
    return int(np.sum(w.s_alive))


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((641,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"PRIM6-D0 start smoke={args.smoke}")

    p1, p2, p3 = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 38071 + ti * 151)

            w = World(make_cfg(seed, True))
            f0 = free_count(w)
            write_pair(w, rng)
            idle(w, 30)
            fire_L_prop(w)
            idle(w, T_END)  # no re-drive
            p1.append(max_R_field(w, "latch") >= 1.0)
            p3.append(free_count(w) - f0 == 0)

            w0 = World(make_cfg(seed, False))
            write_pair(w0, rng)
            idle(w0, 30)
            fire_L_prop(w0)
            idle(w0, T_END)
            p2.append(max_R_field(w0, "charge") <= 0.25)

    a1, a2, a3 = float(np.mean(p1)), float(np.mean(p2)), float(np.mean(p3))
    b1, b2, b3 = a1 >= 0.90, a2 >= 0.90, a3 >= 0.90
    verdict = "PASS" if all([b1, b2, b3]) else "NULL"
    result = {
        "id": "PRIM6-D0",
        "bars": {
            "P1_latch_holds": {"value": a1, "threshold": 0.90, "pass": b1},
            "P2_membrane_gone": {"value": a2, "threshold": 0.90, "pass": b2},
            "P3_no_free": {"value": a3, "threshold": 0.90, "pass": b3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "PRIM6-D0"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nPRIM6-D0: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

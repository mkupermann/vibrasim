"""BP-E14 peak cross-mid charge during prop window. Headless."""
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

SEEDS, TRIALS = (481, 491), 10
N_WRITE, T_PROP, MID = 12, 60, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])


def make_cfg(seed: int, valence: int) -> WorldConfig:
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
        atom_valence=valence,
        neuron_dynamics_enabled=True,
        theta_fire=2.0,
        t_refractory=0.02,
        n_emit=0,
        bridge_charge_prop_rate=2.0,
        bridge_prop_min_strength=0.0,
    )


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)


def write_dual(w: World, rng) -> None:
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=500.0)
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=5000.0)


def mean_R(w: World) -> float:
    s, n = 0.0, 0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) < MID:
            continue
        s += float(w.k_charge[i])
        n += 1
    return s / n if n else 0.0


def n_cross(w: World) -> int:
    n = 0
    B = w.b_count if w.b_count > 0 else len(w.b_alive)
    for b in range(B):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        if (float(w.k_pos[i, 0]) < MID) != (float(w.k_pos[j, 0]) < MID):
            n += 1
    return n


def force_fire_left(w: World) -> None:
    thr = float(w.config.theta_fire)
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(w.k_pos[i, 0]) < MID:
            w.k_charge[i] = thr + 5.0


def peak_R_during_prop(w: World, n: int) -> float:
    dt = float(w.config.dt)
    peak = mean_R(w)
    for _ in range(n):
        tick(w, dt)
        peak = max(peak, mean_R(w))
        # re-drive L periodically so refractory doesn't silence all transfer
        if _ % 15 == 0:
            force_fire_left(w)
    return peak


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((481,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E14 start smoke={args.smoke}")
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 30037 + ti * 107)
            w = World(make_cfg(seed, 4))
            write_dual(w, rng)
            idle(w, 80)
            b3s.append(n_cross(w) >= 1)
            force_fire_left(w)
            peak = peak_R_during_prop(w, T_PROP)
            b1s.append(peak >= 1.0)
            w0 = World(make_cfg(seed, 0))
            write_dual(w0, rng)
            idle(w0, 80)
            force_fire_left(w0)
            peak0 = peak_R_during_prop(w0, T_PROP)
            b2s.append(peak0 <= 0.25)
    a1, a2, a3 = float(np.mean(b1s)), float(np.mean(b2s)), float(np.mean(b3s))
    p1, p2, p3 = a1 >= 0.85, a2 >= 0.85, a3 >= 0.90
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "BP-E14",
        "bars": {
            "B1_peak_R": {"value": a1, "threshold": 0.85, "pass": p1},
            "B2_nobridge_peak": {"value": a2, "threshold": 0.85, "pass": p2},
            "B3_cross": {"value": a3, "threshold": 0.90, "pass": p3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E14"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E14: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

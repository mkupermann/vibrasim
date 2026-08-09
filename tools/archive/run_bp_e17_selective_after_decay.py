"""BP-E17 selective recall after PRIM3 strength decay hold. Headless."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (561, 571), 10
N_WRITE, T_HOLD, T_PROP, MID = 12, 500, 60, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
PAIRS = ((400.0, 7000.0), (1500.0, 2500.0))


def make_cfg(seed: int, pair_link: bool) -> WorldConfig:
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
        ilw_multislot_rel_freq=0.35,
        ilw_pair_link_enabled=pair_link,
        ilw_pair_link_delta=1.0,
        ilw_strength_decay_tau=3.0,
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


def store(w: World, rng, pair_link: bool) -> None:
    for c in (0, 1):
        fL, fR = PAIRS[c]
        for _ in range(N_WRITE):
            if pair_link:
                apply_ilw_pair_write(w, PORT_L, PORT_R, fL, fR, rng)
            else:
                apply_ilw_port_event(w, PORT_L, rng, seed_freq=fL)
                apply_ilw_port_event(w, PORT_R, rng, seed_freq=fR)


def n_cross(w: World) -> int:
    n = 0
    for b in range(w.b_count):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if w.k_alive[i] and w.k_alive[j]:
            if (float(w.k_pos[i, 0]) < MID) != (float(w.k_pos[j, 0]) < MID):
                n += 1
    return n


def L_for_class(w: World, c: int) -> list[int]:
    tgt = PAIRS[c][0]
    out = []
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) >= MID:
            continue
        if abs(float(w.k_freq[i]) - tgt) / max(tgt, 1.0) < 0.35:
            out.append(i)
    return out


def peak_R(w: World, c: int, fire: list[int]) -> float:
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    tgt = PAIRS[c][1]
    peak = 0.0
    for t in range(T_PROP):
        if t % 15 == 0:
            for i in fire:
                if w.k_alive[i]:
                    w.k_charge[i] = thr + 5.0
        tick(w, dt)
        s, n = 0.0, 0
        for i in range(w.k_count):
            if not w.k_alive[i] or int(w.k_level[i]) < 4:
                continue
            if float(w.k_pos[i, 0]) < MID:
                continue
            if abs(float(w.k_freq[i]) - tgt) / max(tgt, 1.0) < 0.35:
                s += float(w.k_charge[i])
                n += 1
        if n:
            peak = max(peak, s / n)
    return peak


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((561,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E17 start smoke={args.smoke} T_hold={T_HOLD}")
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 34053 + ti * 131)
            w = World(make_cfg(seed, True))
            store(w, rng, True)
            idle(w, T_HOLD)
            b3s.append(n_cross(w) == 2)
            w.k_charge[: w.k_count] = 0.0
            f0 = L_for_class(w, 0)
            p0 = peak_R(w, 0, f0) if f0 else 0.0
            w2 = World(make_cfg(seed, True))
            store(w2, rng, True)
            idle(w2, T_HOLD)
            w2.k_charge[: w2.k_count] = 0.0
            f0b = L_for_class(w2, 0)
            p1 = peak_R(w2, 1, f0b) if f0b else 0.0
            b1s.append(p0 > p1)
            # no pair link control
            w3 = World(make_cfg(seed, False))
            store(w3, rng, False)
            idle(w3, T_HOLD)
            w3.k_charge[: w3.k_count] = 0.0
            f0c = L_for_class(w3, 0)
            p0c = peak_R(w3, 0, f0c) if f0c else 0.0
            w4 = World(make_cfg(seed, False))
            store(w4, rng, False)
            idle(w4, T_HOLD)
            w4.k_charge[: w4.k_count] = 0.0
            f0d = L_for_class(w4, 0)
            p1c = peak_R(w4, 1, f0d) if f0d else 0.0
            b2s.append(p0c > p1c)
    a1, a2, a3 = float(np.mean(b1s)), float(np.mean(b2s)), float(np.mean(b3s))
    p1, p2, p3 = a1 >= 0.75, a2 <= 0.55, a3 >= 0.80
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "BP-E17",
        "bars": {
            "B1_sel_after_hold": {"value": a1, "threshold": 0.75, "pass": p1},
            "B2_ctrl_nolink": {"value": a2, "threshold": 0.55, "pass": p2},
            "B3_bridges_hold": {"value": a3, "threshold": 0.80, "pass": p3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E17"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E17: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""BP-E15 selective cross-port recall via charge on matching R band. Headless."""
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

SEEDS, TRIALS = (501, 511), 12
N_WRITE, T_PROP, MID = 12, 60, 40.0
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


def write_pair(w: World, rng, c: int) -> None:
    fL, fR = PAIRS[c]
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=fL)
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=fR)


def store_two(w: World, rng) -> None:
    write_pair(w, rng, 0)
    write_pair(w, rng, 1)
    idle(w, 100)


def L_indices_for_class(w: World, c: int) -> list[int]:
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


def all_L(w: World) -> list[int]:
    return [
        i
        for i in range(w.k_count)
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(w.k_pos[i, 0]) < MID
    ]


def peak_R_class(w: World, c: int, n_ticks: int, fire_idx: list[int]) -> float:
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    tgt = PAIRS[c][1]
    peak = 0.0
    for t in range(n_ticks):
        if t % 15 == 0:
            for i in fire_idx:
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


def both_pairs(w: World) -> bool:
    """Crude: L has both class0 and class1 bands and R has both partners."""
    L0 = len(L_indices_for_class(w, 0)) >= 1
    L1 = len(L_indices_for_class(w, 1)) >= 1
    def R_has(c):
        tgt = PAIRS[c][1]
        for i in range(w.k_count):
            if not w.k_alive[i] or int(w.k_level[i]) < 4:
                continue
            if float(w.k_pos[i, 0]) < MID:
                continue
            if abs(float(w.k_freq[i]) - tgt) / max(tgt, 1.0) < 0.35:
                return True
        return False
    return L0 and L1 and R_has(0) and R_has(1)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((501,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E15 start smoke={args.smoke}")
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 31041 + ti * 109)
            w = World(make_cfg(seed))
            store_two(w, rng)
            b3s.append(both_pairs(w))
            # zero charges before probe
            w.k_charge[: w.k_count] = 0.0
            fire0 = L_indices_for_class(w, 0)
            if not fire0:
                b1s.append(False)
            else:
                p0 = peak_R_class(w, 0, T_PROP, fire0)
                # reset charge for fair class1 measure on same structure? re-store world
            # fresh world for clean peak compare on same protocol
            w = World(make_cfg(seed))
            store_two(w, rng)
            w.k_charge[: w.k_count] = 0.0
            fire0 = L_indices_for_class(w, 0)
            p0 = peak_R_class(w, 0, T_PROP, fire0) if fire0 else 0.0
            w2 = World(make_cfg(seed))
            store_two(w2, rng)
            w2.k_charge[: w2.k_count] = 0.0
            fire0b = L_indices_for_class(w2, 0)
            p1 = peak_R_class(w2, 1, T_PROP, fire0b) if fire0b else 0.0
            b1s.append(p0 > p1)

            # control fire all L
            w3 = World(make_cfg(seed))
            store_two(w3, rng)
            w3.k_charge[: w3.k_count] = 0.0
            fall = all_L(w3)
            p0c = peak_R_class(w3, 0, T_PROP, fall) if fall else 0.0
            w4 = World(make_cfg(seed))
            store_two(w4, rng)
            w4.k_charge[: w4.k_count] = 0.0
            fall4 = all_L(w4)
            p1c = peak_R_class(w4, 1, T_PROP, fall4) if fall4 else 0.0
            b2s.append(p0c > p1c)

    a1, a2, a3 = float(np.mean(b1s)), float(np.mean(b2s)), float(np.mean(b3s))
    p1, p2, p3 = a1 >= 0.80, a2 <= 0.60, a3 >= 0.80
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "BP-E15",
        "bars": {
            "B1_selective": {"value": a1, "threshold": 0.80, "pass": p1},
            "B2_fireall_ctrl": {"value": a2, "threshold": 0.60, "pass": p2},
            "B3_both_pairs": {"value": a3, "threshold": 0.80, "pass": p3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E15"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E15: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

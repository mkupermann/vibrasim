"""BP-E21 end-state partner via k_latch (PRIM6). Headless."""
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

SEEDS, TRIALS = (661, 671), 12
N_WRITE, T_TRAIN, T_PROP, T_END, MID = 10, 6, 50, 40, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
PAIRS = ((400.0, 7000.0), (1500.0, 2500.0))


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
        ilw_multislot_rel_freq=0.35,
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


def train(w: World, rng) -> None:
    for _ in range(T_TRAIN):
        c = int(rng.integers(0, 2))
        fL, fR = PAIRS[c]
        for __ in range(N_WRITE):
            apply_ilw_pair_write(w, PORT_L, PORT_R, fL, fR, rng)
        idle(w, 15)


def true_partner(fL: float) -> float:
    return 7000.0 if abs(fL - 400.0) < abs(fL - 1500.0) else 2500.0


def other_R(true_r: float) -> float:
    return 2500.0 if true_r == 7000.0 else 7000.0


def bridged_L(w: World) -> list[int]:
    out = set()
    for b in range(w.b_count):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        xi, xj = float(w.k_pos[i, 0]), float(w.k_pos[j, 0])
        if (xi < MID) == (xj < MID):
            continue
        if xi < MID:
            out.add(i)
        if xj < MID:
            out.add(j)
    return list(out)


def end_argmax_R_freq(w: World, L_idx: int, use_latch: bool) -> float:
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    w.k_charge[: w.k_count] = 0.0
    if use_latch and hasattr(w, "k_latch"):
        w.k_latch[: w.k_count] = 0.0
    for t in range(T_PROP):
        if t % 10 == 0 and w.k_alive[L_idx]:
            w.k_charge[L_idx] = thr + 5.0
        tick(w, dt)
    idle(w, T_END)  # no re-drive — end-state
    arr = w.k_latch if use_latch else w.k_charge
    best_i, best_v = -1, -1.0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) < MID:
            continue
        v = float(arr[i])
        if v > best_v:
            best_v = v
            best_i = i
    if best_i < 0 or best_v <= 0:
        return 0.0
    return float(w.k_freq[best_i])


def partner_ok(pred: float, true_r: float) -> bool:
    if pred <= 0:
        return False
    return abs(pred - true_r) < abs(pred - other_R(true_r))


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((661,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E21 start smoke={args.smoke}")

    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 39073 + ti * 157)

            w = World(make_cfg(seed, True))
            train(w, rng)
            Ls = bridged_L(w)
            b3s.append(len(Ls) >= 1)
            if not Ls:
                b1s.append(False)
            else:
                Li = int(rng.choice(Ls))
                pred = end_argmax_R_freq(w, Li, use_latch=True)
                b1s.append(partner_ok(pred, true_partner(float(w.k_freq[Li]))))

            w0 = World(make_cfg(seed, False))
            train(w0, rng)
            Ls0 = bridged_L(w0)
            if not Ls0:
                b2s.append(False)
            else:
                Li0 = int(rng.choice(Ls0))
                pred0 = end_argmax_R_freq(w0, Li0, use_latch=False)
                b2s.append(partner_ok(pred0, true_partner(float(w0.k_freq[Li0]))))

    a1, a2, a3 = float(np.mean(b1s)), float(np.mean(b2s)), float(np.mean(b3s))
    p1, p2, p3 = a1 >= 0.80, a2 <= 0.55, a3 >= 0.90
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "BP-E21",
        "bars": {
            "B1_latch_end": {"value": a1, "threshold": 0.80, "pass": p1},
            "B2_nolatch_end": {"value": a2, "threshold": 0.55, "pass": p2},
            "B3_bridged_L": {"value": a3, "threshold": 0.90, "pass": p3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E21"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E21: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

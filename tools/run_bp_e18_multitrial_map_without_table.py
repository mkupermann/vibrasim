"""BP-E18 multi-trial map; readout uses charge-weighted R freq only. Headless."""
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

SEEDS, TRIALS = (581, 591), 10
N_WRITE, T_TRAIN, T_PROP, MID = 8, 8, 50, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
PAIRS = ((400.0, 7000.0), (1500.0, 2500.0))
F_MID = 2000.0  # L low if < ~950? use geometric: low L < 900, high L > 900


def make_cfg(seed: int) -> WorldConfig:
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
        idle(w, 20)


def bands_present(w: World) -> bool:
    L = []
    R = []
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        f = float(w.k_freq[i])
        if float(w.k_pos[i, 0]) < MID:
            L.append(f)
        else:
            R.append(f)
    if len(L) < 2 or len(R) < 2:
        return False
    # both L centroids near 400 and 1500
    has_L0 = any(abs(f - 400) / 400 < 0.35 for f in L)
    has_L1 = any(abs(f - 1500) / 1500 < 0.35 for f in L)
    has_R0 = any(abs(f - 7000) / 7000 < 0.35 for f in R)
    has_R1 = any(abs(f - 2500) / 2500 < 0.35 for f in R)
    return has_L0 and has_L1 and has_R0 and has_R1


def true_partner_freq(fL: float) -> float:
    # scoring only
    if abs(fL - 400) < abs(fL - 1500):
        return 7000.0
    return 2500.0


def rewire_bridges(w: World, rng) -> None:
    """Randomly reassign R endpoints among R atoms for all cross bridges."""
    R_atoms = [
        i
        for i in range(w.k_count)
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(w.k_pos[i, 0]) >= MID
    ]
    if len(R_atoms) < 1:
        return
    for b in range(w.b_count):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        xi, xj = float(w.k_pos[i, 0]), float(w.k_pos[j, 0])
        if (xi < MID) == (xj < MID):
            continue
        # keep L end, randomize R end
        if xi < MID:
            w.b_atom_j[b] = int(rng.choice(R_atoms))
        else:
            w.b_atom_i[b] = int(rng.choice(R_atoms))


def charge_partner_freq(w: World, L_idx: int) -> float:
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    w.k_charge[: w.k_count] = 0.0
    for t in range(T_PROP):
        if t % 10 == 0 and w.k_alive[L_idx]:
            w.k_charge[L_idx] = thr + 5.0
        tick(w, dt)
    # charge-weighted mean R freq
    num = den = 0.0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) < MID:
            continue
        ch = float(w.k_charge[i])
        if ch <= 0:
            continue
        num += ch * float(w.k_freq[i])
        den += ch
    return num / den if den > 0 else 0.0


def L_atoms(w: World) -> list[int]:
    return [
        i
        for i in range(w.k_count)
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(w.k_pos[i, 0]) < MID
    ]


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((581,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E18 start smoke={args.smoke}")
    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 35059 + ti * 137)
            w = World(make_cfg(seed))
            train(w, rng)
            b3s.append(bands_present(w))
            Ls = L_atoms(w)
            if not Ls:
                b1s.append(False)
            else:
                Li = int(rng.choice(Ls))
                fL = float(w.k_freq[Li])
                pred = charge_partner_freq(w, Li)
                true = true_partner_freq(fL)
                # correct if pred closer to true than to the other R band
                other = 2500.0 if true == 7000.0 else 7000.0
                b1s.append(abs(pred - true) < abs(pred - other) and pred > 0)
            # control rewired
            w2 = World(make_cfg(seed))
            train(w2, rng)
            rewire_bridges(w2, rng)
            Ls2 = L_atoms(w2)
            if not Ls2:
                b2s.append(False)
            else:
                Li2 = int(rng.choice(Ls2))
                fL2 = float(w2.k_freq[Li2])
                pred2 = charge_partner_freq(w2, Li2)
                true2 = true_partner_freq(fL2)
                other2 = 2500.0 if true2 == 7000.0 else 7000.0
                b2s.append(abs(pred2 - true2) < abs(pred2 - other2) and pred2 > 0)
    a1, a2, a3 = float(np.mean(b1s)), float(np.mean(b2s)), float(np.mean(b3s))
    p1, p2, p3 = a1 >= 0.80, a2 <= 0.55, a3 >= 0.90
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "BP-E18",
        "bars": {
            "B1_graph_acc": {"value": a1, "threshold": 0.80, "pass": p1},
            "B2_rewire_ctrl": {"value": a2, "threshold": 0.55, "pass": p2},
            "B3_bands": {"value": a3, "threshold": 0.90, "pass": p3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E18"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E18: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

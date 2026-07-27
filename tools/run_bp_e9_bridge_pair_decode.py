"""BP-E9 pair class from cross-port bridge endpoints. Headless."""
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

SEEDS, TRIALS = (361, 371), 12
N_WRITE, T_IDLE, MID = 15, 300, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
PAIRS = (
    (400.0, 7000.0),
    (1500.0, 2500.0),
    (5000.0, 800.0),
)
K_CLASS = 3


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
        node_thermal_speed=0.0,
    )


def idle(w: World, n: int) -> None:
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)


def cross_endpoint_freqs(w: World) -> list[tuple[float, float]]:
    """List of (f_left, f_right) for each cross-mid bridge."""
    out = []
    B = w.b_count if w.b_count > 0 else len(w.b_alive)
    for b in range(B):
        if not w.b_alive[b]:
            continue
        i = int(w.b_atom_i[b])
        j = int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        xi, xj = float(w.k_pos[i, 0]), float(w.k_pos[j, 0])
        if (xi < MID) == (xj < MID):
            continue
        if xi < MID:
            fL, fR = float(w.k_freq[i]), float(w.k_freq[j])
        else:
            fL, fR = float(w.k_freq[j]), float(w.k_freq[i])
        out.append((fL, fR))
    return out


def nearest_pair(fL: float, fR: float) -> int:
    best, bd = 0, 1e18
    for c, (a, b) in enumerate(PAIRS):
        d = (fL - a) ** 2 + (fR - b) ** 2
        if d < bd:
            bd, best = d, c
    return best


def matches_any_exclusive(fL: float, fR: float, tol_frac: float = 0.25) -> bool:
    """True if (fL,fR) is close to some exclusive row (for control false-pair rate)."""
    for a, b in PAIRS:
        if abs(fL - a) / max(a, 1) < tol_frac and abs(fR - b) / max(b, 1) < tol_frac:
            return True
    return False


def write_pair(w: World, rng, fL: float, fR: float) -> None:
    for _ in range(N_WRITE):
        apply_ilw_port_event(w, PORT_L, rng, seed_freq=fL)
        apply_ilw_port_event(w, PORT_R, rng, seed_freq=fR)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((361,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E9 start smoke={args.smoke} seeds={seeds} trials={trials}")

    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 24013 + ti * 79)
            c = int(rng.integers(0, K_CLASS))
            fL, fR = PAIRS[c]
            w = World(make_cfg(seed))
            write_pair(w, rng, fL, fR)
            idle(w, T_IDLE)
            eps = cross_endpoint_freqs(w)
            b3s.append(len(eps) >= 1)
            if not eps:
                b1s.append(False)
            else:
                # majority vote over bridges
                preds = [nearest_pair(a, b) for a, b in eps]
                pred = max(set(preds), key=preds.count)
                b1s.append(pred == c)

            # control independent
            cL = int(rng.integers(0, K_CLASS))
            cR = int(rng.integers(0, K_CLASS))
            w2 = World(make_cfg(seed))
            write_pair(w2, rng, PAIRS[cL][0], PAIRS[cR][1])
            idle(w2, T_IDLE)
            eps2 = cross_endpoint_freqs(w2)
            if not eps2:
                b2s.append(False)  # no bridge → not a false exclusive match
            else:
                # any bridge looks like exclusive pair?
                b2s.append(any(matches_any_exclusive(a, b) for a, b in eps2))

    a1, a2, a3 = float(np.mean(b1s)), float(np.mean(b2s)), float(np.mean(b3s))
    p1, p2, p3 = a1 >= 0.85, a2 <= 0.45, a3 >= 0.90
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "BP-E9",
        "bars": {
            "B1_bridge_class": {"value": a1, "threshold": 0.85, "pass": p1},
            "B2_ctrl_false_pair": {"value": a2, "threshold": 0.45, "pass": p2},
            "B3_has_bridge": {"value": a3, "threshold": 0.90, "pass": p3},
        },
        "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E9"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E9: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

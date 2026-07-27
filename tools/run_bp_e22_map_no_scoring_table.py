"""BP-E22: multi-trial map scored only by self-consistency (no pair table). Headless."""
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

SEEDS, TRIALS = (681, 691), 12
N_WRITE, T_TRAIN, T_PROP, T_END, MID = 10, 6, 50, 40, 40.0
PORT_L = np.array([20.0, 25.0, 25.0])
PORT_R = np.array([60.0, 25.0, 25.0])
# Write-side only — never used for scoring
PAIRS = ((400.0, 7000.0), (1500.0, 2500.0))


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
        charge_latch_enabled=True,
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


def rewire(w: World, rng) -> None:
    R_atoms = [
        i
        for i in range(w.k_count)
        if w.k_alive[i] and int(w.k_level[i]) >= 4 and float(w.k_pos[i, 0]) >= MID
    ]
    if not R_atoms:
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
        rpick = int(rng.choice(R_atoms))
        if xi < MID:
            w.b_atom_j[b] = rpick
        else:
            w.b_atom_i[b] = rpick


def latch_partner_freq(w: World, L_idx: int) -> float:
    thr = float(w.config.theta_fire)
    dt = float(w.config.dt)
    w.k_charge[: w.k_count] = 0.0
    w.k_latch[: w.k_count] = 0.0
    for t in range(T_PROP):
        if t % 10 == 0 and w.k_alive[L_idx]:
            w.k_charge[L_idx] = thr + 5.0
        tick(w, dt)
    idle(w, T_END)
    best_i, best_v = -1, -1.0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i]) < 4:
            continue
        if float(w.k_pos[i, 0]) < MID:
            continue
        v = float(w.k_latch[i])
        if v > best_v:
            best_v = v
            best_i = i
    if best_i < 0 or best_v <= 0:
        return 0.0
    return float(w.k_freq[best_i])


def collect_routes(w: World, Ls: list[int]) -> list[tuple[float, float]]:
    routes = []
    for Li in Ls:
        fL = float(w.k_freq[Li])
        # fresh latch per probe on same structure: reset latch but keep bridges
        fR = latch_partner_freq(w, Li)
        if fR > 0:
            routes.append((fL, fR))
    return routes


def score_self_consistency(routes: list[tuple[float, float]]) -> tuple[float, float]:
    """Return (self_consistency, relative_modal_R_gap). No pair table."""
    if len(routes) < 2:
        return 0.0, 0.0
    fLs = np.array([r[0] for r in routes], dtype=np.float64)
    fRs = np.array([r[1] for r in routes], dtype=np.float64)
    med = float(np.median(fLs))
    g0 = fRs[fLs <= med]
    g1 = fRs[fLs > med]
    if len(g0) == 0 or len(g1) == 0:
        # all L on one side of median — fall back: use min/max L as two groups if 2+ distinct
        order = np.argsort(fLs)
        mid = len(order) // 2
        g0 = fRs[order[: max(1, mid)]]
        g1 = fRs[order[max(1, mid) :]]
        if len(g1) == 0:
            return 0.0, 0.0

    def mode_val(arr: np.ndarray) -> float:
        # continuous: use mean as mode proxy for small n
        return float(np.mean(arr))

    m0, m1 = mode_val(g0), mode_val(g1)
    # assign each route to group by fL median, check closer to group mean R
    ok = 0
    for fL, fR in routes:
        if fL <= med:
            ok += 1 if abs(fR - m0) <= abs(fR - m1) else 0
        else:
            ok += 1 if abs(fR - m1) <= abs(fR - m0) else 0
    cons = ok / len(routes)
    gap = abs(m0 - m1) / max(m0, m1, 1.0)
    return cons, gap


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((681,), 4) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E22 start smoke={args.smoke}")

    b1s, b2s, b3s = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 40079 + ti * 163)
            w = World(make_cfg(seed))
            train(w, rng)
            Ls = bridged_L(w)
            routes = collect_routes(w, Ls) if Ls else []
            cons, gap = score_self_consistency(routes)
            b1s.append(cons)
            b2s.append(gap)

            w2 = World(make_cfg(seed))
            train(w2, rng)
            rewire(w2, rng)
            Ls2 = bridged_L(w2)
            routes2 = collect_routes(w2, Ls2) if Ls2 else []
            cons2, _ = score_self_consistency(routes2)
            b3s.append(cons2)

    # aggregate: fraction of trials meeting bar, or mean of metrics?
    # Bars are on mean self-consistency across trials
    a1 = float(np.mean(b1s))
    a2 = float(np.mean(b2s))
    a3 = float(np.mean(b3s))
    p1, p2, p3 = a1 >= 0.80, a2 >= 0.25, a3 <= 0.55
    verdict = "PASS" if all([p1, p2, p3]) else "NULL"
    result = {
        "id": "BP-E22",
        "bars": {
            "B1_self_cons": {"value": a1, "threshold": 0.80, "pass": p1},
            "B2_modal_gap": {"value": a2, "threshold": 0.25, "pass": p2},
            "B3_rewire_cons": {"value": a3, "threshold": 0.55, "pass": p3},
        },
        "verdict": verdict,
        "n_trials": len(b1s),
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E22"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E22: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

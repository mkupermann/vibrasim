"""BP-E24: table-free K=3 map with multi-sample spatial slots. Headless."""
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

SEEDS, TRIALS = (781, 791), 10
N_WRITE, T_TRAIN, T_PROP, T_END, MID = 6, 9, 40, 30, 40.0
PAIRS = ((400.0, 7000.0), (1500.0, 2500.0), (5000.0, 800.0))
Y_SLOTS = (13.0, 37.0)  # |dy|=24 > 2*ilw_radius=16
K_CLASS = 3


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


def ports(y: float):
    return np.array([20.0, y, 25.0]), np.array([60.0, y, 25.0])


def train(w: World, rng) -> None:
    # cover all class×slot then random extras
    schedule = [(c, y) for c in range(K_CLASS) for y in Y_SLOTS]
    for _ in range(T_TRAIN - len(schedule)):
        schedule.append((int(rng.integers(0, K_CLASS)), float(rng.choice(Y_SLOTS))))
    rng.shuffle(schedule)
    for c, y in schedule:
        fL, fR = PAIRS[c]
        pl, pr = ports(float(y))
        for __ in range(N_WRITE):
            apply_ilw_pair_write(w, pl, pr, fL, fR, rng)
        idle(w, 8)


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
        fR = latch_partner_freq(w, Li)
        if fR > 0:
            routes.append((float(w.k_freq[Li]), fR))
    return routes


def multi_sample_ok(routes: list[tuple[float, float]]) -> bool:
    """≥2 L-freq bands with ≥2 samples each (approx by sorting fL)."""
    if len(routes) < 4:
        return False
    fLs = np.array([r[0] for r in routes])
    # 3-bin by quantiles
    qs = np.quantile(fLs, [0.0, 1 / 3, 2 / 3, 1.0])
    counts = []
    for a, b in zip(qs[:-1], qs[1:]):
        counts.append(int(np.sum((fLs >= a) & (fLs <= b + 1e-9))))
    # at least 2 bins with >=2
    return sum(1 for c in counts if c >= 2) >= 2


def score(routes: list[tuple[float, float]]) -> tuple[float, float]:
    """Self-consistency and min pairwise relative gap among 3 tertile groups."""
    if len(routes) < 3:
        return 0.0, 0.0
    fLs = np.array([r[0] for r in routes], dtype=np.float64)
    fRs = np.array([r[1] for r in routes], dtype=np.float64)
    # tertile edges
    t1, t2 = np.quantile(fLs, [1 / 3, 2 / 3])
    groups = []
    for lo, hi, left_open in (
        (-np.inf, t1, False),
        (t1, t2, True),
        (t2, np.inf, True),
    ):
        if left_open:
            mask = (fLs > lo) & (fLs <= hi if np.isfinite(hi) else fLs > lo)
            if not np.isfinite(hi):
                mask = fLs > lo
            else:
                mask = (fLs > lo) & (fLs <= hi)
        else:
            mask = fLs <= hi
        g = fRs[mask]
        if len(g) == 0:
            groups.append(None)
        else:
            groups.append(float(np.mean(g)))
    means = [g for g in groups if g is not None]
    if len(means) < 2:
        return 0.0, 0.0
    # min pairwise relative gap
    gaps = []
    for i in range(len(means)):
        for j in range(i + 1, len(means)):
            gaps.append(abs(means[i] - means[j]) / max(means[i], means[j], 1.0))
    min_gap = float(min(gaps)) if gaps else 0.0
    # consistency: closer to own tertile mean-R than to any other group mean
    ok = 0
    for fL, fR in routes:
        if fL <= t1:
            gi = 0
        elif fL <= t2:
            gi = 1
        else:
            gi = 2
        m = groups[gi]
        if m is None:
            continue
        own = abs(fR - m)
        good = True
        for k, g in enumerate(groups):
            if g is None or k == gi:
                continue
            if abs(fR - g) < own - 1e-9:
                good = False
                break
        ok += int(good)
    cons = ok / len(routes)
    return cons, min_gap


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((781,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E24 start smoke={args.smoke} seeds={seeds} trials={trials}")

    b1s, b2s, b3s, b4s = [], [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed * 42089 + ti * 173)
            w = World(make_cfg(seed))
            train(w, rng)
            routes = collect_routes(w, bridged_L(w))
            cons, gap = score(routes)
            b1s.append(cons)
            b2s.append(gap)
            b4s.append(multi_sample_ok(routes))

            w2 = World(make_cfg(seed))
            train(w2, rng)
            rewire(w2, rng)
            cons2, _ = score(collect_routes(w2, bridged_L(w2)))
            b3s.append(cons2)

    a1, a2, a3, a4 = map(float, (np.mean(b1s), np.mean(b2s), np.mean(b3s), np.mean(b4s)))
    p1, p2, p3, p4 = a1 >= 0.80, a2 >= 0.20, a3 <= 0.55, a4 >= 0.90
    verdict = "PASS" if all([p1, p2, p3, p4]) else "NULL"
    result = {
        "id": "BP-E24",
        "bars": {
            "B1_self_cons": {"value": a1, "threshold": 0.80, "pass": p1},
            "B2_min_gap": {"value": a2, "threshold": 0.20, "pass": p2},
            "B3_rewire_cons": {"value": a3, "threshold": 0.55, "pass": p3},
            "B4_multisample": {"value": a4, "threshold": 0.90, "pass": p4},
        },
        "verdict": verdict,
        "n_trials": len(b1s),
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-E24"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E24: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

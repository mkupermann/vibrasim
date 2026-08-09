"""BP-B2 — Emergent molecule species carry drive identity.

Pre-registered: docs/amendments/bp_b2_emergent_species.md
Official seeds {11, 23} held out from exploratory probes.

Usage:
    python tools/run_bp_b2_emergent_species.py
    python tools/run_bp_b2_emergent_species.py --smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.classify_molecules import species_fingerprint
from world.bet_live import run_ticks_live
from world.config import WorldConfig
from world.state import World


def ground_atom_decades_safe(
    world: World, node_idx: int, *, _visited: set[int] | None = None, _depth: int = 0,
) -> list[int]:
    """Walk composition to level-4 atoms; cycle-safe (CSR can self-reference under fusion)."""
    if _depth > 32 or node_idx < 0 or node_idx >= world.k_count:
        return []
    if _visited is None:
        _visited = set()
    if node_idx in _visited:
        return []
    _visited.add(node_idx)
    level = int(world.k_level[node_idx])
    if level == 4:
        import math
        return [int(math.floor(math.log10(max(float(world.k_freq[node_idx]), 1.0))))]
    if level < 4:
        return []
    out: list[int] = []
    start = int(world.k_comp_offset[node_idx])
    end = int(world.k_comp_end[node_idx])
    for j in range(start, end):
        child = int(world.k_comp_indices[j])
        out.extend(ground_atom_decades_safe(world, child, _visited=_visited, _depth=_depth + 1))
    return out

# --- Locked protocol ---
BAR_B1 = 0.90
BAR_B2 = 0.60
BAR_B3 = 0.60
BAR_B4 = 0.60
BAR_B5 = 0.80
SEEDS_FULL = (11, 23)
N_FULL = 20
T_FULL = 1200
MEAN_DECADE_THRESHOLD = 3.5
DRIVE_A = (100.0, 2000.0)
DRIVE_B = (500.0, 10000.0)
DRIVE_C1 = (100.0, 10000.0)  # identical band for both labels


def make_cfg(seed: int, freq_min: float, freq_max: float) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=800,
        box_size=(60.0, 60.0, 60.0),
        n_vibrations_max=2048,
        n_nodes_max=2048,
        rng_seed=seed,
        freq_min=freq_min,
        freq_max=freq_max,
        freq_distribution="log",
        r_1=5.0,
        r_2=28.0,
        freq_tolerance=0.030,
        pair_decay_time=60.0,
        triad_decay_time=600.0,
        lambda_gen=0.0,
        lambda_dec=0.0,
        lambda_dec_mol=0.0,
        node_thermal_speed=0.0,
        mol_fusion_enabled=False,
    )


def form_world(
    seed: int, freq_min: float, freq_max: float, n_ticks: int,
    *, live: bool = False, title: str = "BP-B2",
) -> World:
    cfg = make_cfg(seed, freq_min, freq_max)
    world = World(cfg)
    dt = float(cfg.dt)
    run_ticks_live(world, n_ticks, dt, live=live, title=title, ticks_per_frame=8)
    return world


def molecule_stats(world: World) -> dict:
    fps: dict[str, int] = {}
    decades: list[int] = []
    for i in range(world.k_count):
        if not world.k_alive[i]:
            continue
        if int(world.k_level[i]) < 5:
            continue
        d = ground_atom_decades_safe(world, i)
        decades.extend(d)
        fp = species_fingerprint(d)
        fps[fp] = fps.get(fp, 0) + 1
    n_mol = int(sum(fps.values()))
    mean_d = float(sum(decades) / len(decades)) if decades else None
    return {"n_mol": n_mol, "mean_decade": mean_d, "fps": fps, "decades": decades}


def decode_mean_decade(mean_d: float | None) -> str | None:
    if mean_d is None:
        return None
    return "A" if mean_d < MEAN_DECADE_THRESHOLD else "B"


def decode_count(n_mol: int, median_n: float) -> str:
    """C3: molecule-count-only heuristic (threshold = median of batch)."""
    return "B" if n_mol >= median_n else "A"


def label_schedule(n: int, rng: np.random.Generator) -> list[str]:
    half = n // 2
    labels = ["A"] * half + ["B"] * (n - half)
    rng.shuffle(labels)
    return labels


def drive_for_label(label: str, *, c1: bool) -> tuple[float, float]:
    if c1:
        return DRIVE_C1
    return DRIVE_A if label == "A" else DRIVE_B


def run_protocol(
    *, n_trials: int, t_form: int, seeds: tuple[int, ...], smoke: bool,
    live: bool = False, live_all: bool = False,
) -> dict:
    t_rows: list[dict] = []
    c1_rows: list[dict] = []
    live_used = False

    for seed in seeds:
        rng = np.random.default_rng(seed)
        schedule = label_schedule(n_trials, rng)
        for i, lab in enumerate(schedule):
            # Trial-unique seed so A/B draws differ within a schedule
            trial_seed = int(seed * 1_000_003 + i * 97 + (0 if lab == "A" else 1))

            use_live = False
            if live and (live_all or not live_used):
                use_live = True
                live_used = True

            lo_t, hi_t = drive_for_label(lab, c1=False)
            w_t = form_world(
                trial_seed, lo_t, hi_t, t_form,
                live=use_live, title=f"BP-B2 drive {lab} band=[{lo_t:.0f},{hi_t:.0f}]",
            )
            st_t = molecule_stats(w_t)
            pred_t = decode_mean_decade(st_t["mean_decade"])
            t_rows.append({
                "arm": "T",
                "label": lab,
                "seed": seed,
                "trial_i": i,
                "n_mol": st_t["n_mol"],
                "mean_decade": st_t["mean_decade"],
                "fps": st_t["fps"],
                "pred": pred_t,
                "correct": pred_t == lab,
            })

            lo_c, hi_c = drive_for_label(lab, c1=True)
            # Different trial_seed offset so C1 is independent physics
            w_c1 = form_world(
                trial_seed + 17, lo_c, hi_c, t_form,
                live=live_all, title=f"BP-B2 C1 same-band label={lab}",
            )
            st_c1 = molecule_stats(w_c1)
            pred_c1 = decode_mean_decade(st_c1["mean_decade"])
            c1_rows.append({
                "arm": "C1",
                "label": lab,
                "n_mol": st_c1["n_mol"],
                "mean_decade": st_c1["mean_decade"],
                "fps": st_c1["fps"],
                "pred": pred_c1,
                "correct": pred_c1 == lab,
            })

    # C2: shuffle labels on T fingerprints (fixed RNG, locked)
    rng_sh = np.random.default_rng(20260719)
    shuffled_labels = [r["label"] for r in t_rows]
    rng_sh.shuffle(shuffled_labels)
    c2_correct = []
    for r, lab_sh in zip(t_rows, shuffled_labels):
        pred = decode_mean_decade(r["mean_decade"])
        c2_correct.append(pred == lab_sh)

    # C3: molecule-count-only on T rows; median from T n_mol
    n_mols = [r["n_mol"] for r in t_rows]
    median_n = float(np.median(n_mols)) if n_mols else 0.0
    c3_correct = [
        decode_count(r["n_mol"], median_n) == r["label"] for r in t_rows
    ]

    def acc(flags: list[bool]) -> float:
        return float(sum(flags) / len(flags)) if flags else 0.0

    acc_t = acc([r["correct"] for r in t_rows])
    acc_c1 = acc([r["correct"] for r in c1_rows])
    acc_c2 = acc(c2_correct)
    acc_c3 = acc(c3_correct)
    surv = acc([r["n_mol"] >= 1 for r in t_rows])

    b1 = acc_t >= BAR_B1
    b2 = acc_c1 <= BAR_B2
    b3 = acc_c2 <= BAR_B3
    b4 = acc_c3 <= BAR_B4
    b5 = surv >= BAR_B5

    verdict = "PASS" if (b1 and b2 and b3 and b4 and b5) else "NULL"

    return {
        "id": "BP-B2",
        "smoke": smoke,
        "n_trials_per_seed": n_trials,
        "seeds": list(seeds),
        "t_form": t_form,
        "drive_A": DRIVE_A,
        "drive_B": DRIVE_B,
        "drive_C1": DRIVE_C1,
        "mean_decade_threshold": MEAN_DECADE_THRESHOLD,
        "bars": {
            "B1_treatment_acc": {"value": acc_t, "threshold": BAR_B1, "pass": b1},
            "B2_c1_same_band_acc": {"value": acc_c1, "threshold": BAR_B2, "pass": b2},
            "B3_c2_shuffle_acc": {"value": acc_c2, "threshold": BAR_B3, "pass": b3},
            "B4_c3_count_acc": {"value": acc_c3, "threshold": BAR_B4, "pass": b4},
            "B5_mol_formation": {"value": surv, "threshold": BAR_B5, "pass": b5},
        },
        "median_n_mol_T": median_n,
        "n_T": len(t_rows),
        "verdict": verdict,
        "sample_T": t_rows[:6],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="run_bp_b2_emergent_species")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--live", action="store_true", default=False,
                   help="optional PyVista 3D (off by default — lab is headless)")
    p.add_argument("--live-all", action="store_true", help="live-view every trial (slow)")
    args = p.parse_args(argv)

    if args.smoke:
        n_trials, t_form, seeds, smoke = 4, 400, (11,), True
    else:
        n_trials, t_form, seeds, smoke = N_FULL, T_FULL, SEEDS_FULL, False

    live = bool(args.live or args.live_all)
    print(f"BP-B2 start smoke={smoke} N={n_trials} T={t_form} seeds={seeds} live={live}")
    result = run_protocol(
        n_trials=n_trials, t_form=t_form, seeds=seeds, smoke=smoke,
        live=live, live_all=bool(args.live_all),
    )

    out_dir = Path.home() / ".eqmod" / "bet" / "BP-B2"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / ("result_smoke.json" if smoke else "result.json")
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("--- bars ---")
    for k, v in result["bars"].items():
        print(f"  {k}: value={v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print("--- VERDICT ---")
    print(f"BP-B2: {result['verdict']}")
    print(f"wrote {out_path}")
    print("DONE")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""BP-B1 — Molecules carry information (belief path Rung B).

Pre-registered bars: docs/amendments/bp_b1_molecule_information.md
Run AFTER that amendment was committed (bars predate data).

Usage:
    python tools/run_bp_b1_molecule_information.py           # full protocol
    python tools/run_bp_b1_molecule_information.py --smoke   # N=4, T=50, 1 seed
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

# Repo root on path
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from world.bet_live import run_ticks_live
from world.config import WorldConfig
from world.state import World
from tools.classify_molecules import _ground_atom_decades, species_fingerprint

# --- Locked protocol (must match docs/amendments/bp_b1_molecule_information.md) ---
BAR_B1 = 0.90
BAR_B2 = 0.60
BAR_B3 = 0.60
BAR_B4 = 0.60
BAR_B5 = 0.80
SEEDS_FULL = (42, 7)
N_FULL = 20
T_FULL = 500
FP_ALPHA = "A33"
FP_BETA = "A34"
LABELS = ("alpha", "beta")


def make_cfg(seed: int) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=0,
        box_size=(80.0, 80.0, 80.0),
        n_vibrations_max=64,
        n_nodes_max=256,
        rng_seed=seed,
        lambda_gen=0.0,
        lambda_dec=0.0,
        lambda_dec_mol=0.0,
        node_thermal_speed=0.0,
        mol_fusion_enabled=False,
        repulsion_k=0.0,
        speed_min=0.0,
        speed_max=0.0,
    )


def molecule_fingerprint(world: World, mol_idx: int) -> str:
    if mol_idx < 0 or mol_idx >= world.k_count:
        return "A?"
    if not world.k_alive[mol_idx]:
        return "A?"
    if int(world.k_level[mol_idx]) < 5:
        return "A?"
    decades = _ground_atom_decades(world, mol_idx)
    return species_fingerprint(decades)


def _freq_for_decade(decade: int, offset: float = 0.0) -> float:
    """Frequency strictly inside decade d: floor(log10(f)) == d."""
    # centre of decade band: 10^d * 3
    return float(10**decade * 3.0 + offset)


def plant_real_molecule(
    world: World,
    species: str,
    pos: np.ndarray,
    *,
    same_polarity: bool = True,
) -> int:
    """Plant a real level-5 molecule with two level-4 atom constituents.

    Atoms use the same polarity by default so bind_nodes_upward will not
    re-fuse them during the hold (opposite polarity + proximity would).
    """
    if species == "alpha":
        f0, f1 = _freq_for_decade(3, 0.0), _freq_for_decade(3, 100.0)
        assert int(math.floor(math.log10(f0))) == 3
        assert int(math.floor(math.log10(f1))) == 3
    elif species == "beta":
        f0, f1 = _freq_for_decade(3, 0.0), _freq_for_decade(4, 0.0)
        assert int(math.floor(math.log10(f0))) == 3
        assert int(math.floor(math.log10(f1))) == 4
    else:
        raise ValueError(species)

    # Park constituents far from each other and outside typical r_2 of the molecule
    # so they are not spatial content and do not re-bind with each other.
    box = np.asarray(world.config.box_size, dtype=np.float64)
    a0_pos = (pos + np.array([box[0] * 0.35, 0.0, 0.0])) % box
    a1_pos = (pos + np.array([0.0, box[1] * 0.35, 0.0])) % box
    pol0 = True
    pol1 = True if same_polarity else False

    a0 = world.allocate_node(
        pos=a0_pos, freq=f0, pol=pol0, level=4,
        constituents=np.array([], dtype=np.int32), comp_kind=1,
    )
    a1 = world.allocate_node(
        pos=a1_pos, freq=f1, pol=pol1, level=4,
        constituents=np.array([], dtype=np.int32), comp_kind=1,
    )
    mol_freq = f0 + f1
    mol = world.allocate_node(
        pos=pos.copy(), freq=mol_freq, pol=True, level=5,
        constituents=np.array([a0, a1], dtype=np.int32), comp_kind=1,
    )
    world.k_strength[mol] = 10.0
    return mol


def plant_empty_shell(world: World, pos: np.ndarray, freq: float = 6000.0) -> int:
    """Level-5 node with empty composition (synthetic — C1 control)."""
    mol = world.allocate_node(
        pos=pos.copy(), freq=freq, pol=True, level=5,
        constituents=np.array([], dtype=np.int32), comp_kind=1,
    )
    world.k_strength[mol] = 10.0
    return mol


def scramble_composition(world: World, mol_idx: int, write_label: str) -> None:
    """Rewrite constituent atom frequencies so fingerprint no longer matches write label."""
    start = int(world.k_comp_offset[mol_idx])
    end = int(world.k_comp_end[mol_idx])
    children = [int(world.k_comp_indices[j]) for j in range(start, end)]
    if len(children) < 2:
        return
    # Force the OTHER species fingerprint
    if write_label == "alpha":
        # make A34
        world.k_freq[children[0]] = _freq_for_decade(3)
        world.k_freq[children[1]] = _freq_for_decade(4)
    else:
        # make A33
        world.k_freq[children[0]] = _freq_for_decade(3, 0.0)
        world.k_freq[children[1]] = _freq_for_decade(3, 200.0)


def decode_by_fingerprint(fp: str) -> str | None:
    if fp == FP_ALPHA:
        return "alpha"
    if fp == FP_BETA:
        return "beta"
    return None


def decode_by_position(pos: np.ndarray, box: np.ndarray) -> str:
    """Fixed heuristic independent of write mapping — chance if positions random."""
    return "alpha" if pos[0] < 0.5 * box[0] else "beta"


def random_pos(rng: np.random.Generator, box: np.ndarray) -> np.ndarray:
    return rng.uniform(0.0, 1.0, size=3) * box


def hold(world: World, n_ticks: int, *, live: bool = False, title: str = "BP-B1") -> None:
    dt = float(world.config.dt)
    run_ticks_live(world, n_ticks, dt, live=live, title=title, ticks_per_frame=10)


def trial_treatment(seed: int, label: str, t_hold: int, trial_i: int, *, live: bool = False) -> dict:
    cfg = make_cfg(seed)
    world = World(cfg)
    rng = np.random.default_rng(seed * 1_000_003 + trial_i * 17 + (0 if label == "alpha" else 1))
    box = np.asarray(cfg.box_size, dtype=np.float64)
    pos = random_pos(rng, box)
    mol = plant_real_molecule(world, label, pos)
    fp0 = molecule_fingerprint(world, mol)
    hold(world, t_hold, live=live, title=f"BP-B1 treatment label={label}")
    alive = bool(world.k_alive[mol])
    fp1 = molecule_fingerprint(world, mol) if alive else "A?"
    pred = decode_by_fingerprint(fp1)
    composition_ok = alive and fp1 not in ("A?", "")
    return {
        "arm": "T",
        "label": label,
        "fp0": fp0,
        "fp1": fp1,
        "pred": pred,
        "correct": pred == label,
        "alive": alive,
        "composition_ok": composition_ok,
        "pos": pos.tolist(),
    }


def trial_c1_empty(seed: int, label: str, t_hold: int, trial_i: int, *, live: bool = False) -> dict:
    """Empty shell — fingerprint cannot carry the write label."""
    cfg = make_cfg(seed)
    world = World(cfg)
    rng = np.random.default_rng(seed * 1_000_003 + trial_i * 19 + 3)
    box = np.asarray(cfg.box_size, dtype=np.float64)
    pos = random_pos(rng, box)
    mol = plant_empty_shell(world, pos)
    hold(world, t_hold, live=live, title="BP-B1 C1 empty shell")
    alive = bool(world.k_alive[mol])
    fp1 = molecule_fingerprint(world, mol) if alive else "A?"
    pred = decode_by_fingerprint(fp1)
    return {
        "arm": "C1",
        "label": label,
        "fp1": fp1,
        "pred": pred,
        "correct": pred == label,
        "alive": alive,
    }


def trial_c2_scramble(seed: int, label: str, t_hold: int, trial_i: int, *, live: bool = False) -> dict:
    cfg = make_cfg(seed)
    world = World(cfg)
    rng = np.random.default_rng(seed * 1_000_003 + trial_i * 23 + 5)
    box = np.asarray(cfg.box_size, dtype=np.float64)
    pos = random_pos(rng, box)
    mol = plant_real_molecule(world, label, pos)
    scramble_composition(world, mol, label)
    hold(world, t_hold, live=live, title="BP-B1 C2 scramble")
    alive = bool(world.k_alive[mol])
    fp1 = molecule_fingerprint(world, mol) if alive else "A?"
    pred = decode_by_fingerprint(fp1)
    return {
        "arm": "C2",
        "label": label,
        "fp1": fp1,
        "pred": pred,
        "correct": pred == label,
        "alive": alive,
    }


def trial_c3_position(seed: int, label: str, t_hold: int, trial_i: int, *, live: bool = False) -> dict:
    cfg = make_cfg(seed)
    world = World(cfg)
    rng = np.random.default_rng(seed * 1_000_003 + trial_i * 29 + 7)
    box = np.asarray(cfg.box_size, dtype=np.float64)
    pos = random_pos(rng, box)
    mol = plant_real_molecule(world, label, pos)
    hold(world, t_hold, live=live, title="BP-B1 C3 position")
    alive = bool(world.k_alive[mol])
    pos_read = world.k_pos[mol] if alive else pos
    pred = decode_by_position(np.asarray(pos_read), box)
    return {
        "arm": "C3",
        "label": label,
        "pred": pred,
        "correct": pred == label,
        "alive": alive,
    }


def label_schedule(n: int, rng: np.random.Generator) -> list[str]:
    half = n // 2
    labels = ["alpha"] * half + ["beta"] * (n - half)
    rng.shuffle(labels)
    return labels


def run_protocol(
    *, n_trials: int, t_hold: int, seeds: tuple[int, ...], smoke: bool,
    live: bool = False, live_all: bool = False,
) -> dict:
    all_T: list[dict] = []
    all_C1: list[dict] = []
    all_C2: list[dict] = []
    all_C3: list[dict] = []
    live_used = False

    for seed in seeds:
        rng = np.random.default_rng(seed)
        schedule = label_schedule(n_trials, rng)
        for i, lab in enumerate(schedule):
            use_live = False
            if live and (live_all or not live_used):
                use_live = True
                live_used = True
            all_T.append(trial_treatment(seed, lab, t_hold, i, live=use_live))
            all_C1.append(trial_c1_empty(seed, lab, t_hold, i, live=live_all))
            all_C2.append(trial_c2_scramble(seed, lab, t_hold, i, live=live_all))
            all_C3.append(trial_c3_position(seed, lab, t_hold, i, live=live_all))

    def acc(rows: list[dict]) -> float:
        if not rows:
            return 0.0
        return float(sum(1 for r in rows if r["correct"])) / len(rows)

    def survival(rows: list[dict]) -> float:
        if not rows:
            return 0.0
        return float(sum(1 for r in rows if r.get("composition_ok"))) / len(rows)

    acc_T = acc(all_T)
    acc_C1 = acc(all_C1)
    acc_C2 = acc(all_C2)
    acc_C3 = acc(all_C3)
    surv = survival(all_T)

    b1 = acc_T >= BAR_B1
    b2 = acc_C1 <= BAR_B2
    b3 = acc_C2 <= BAR_B3
    b4 = acc_C3 <= BAR_B4
    b5 = surv >= BAR_B5

    if b1 and b2 and b3 and b4 and b5:
        verdict = "PASS"
    else:
        verdict = "NULL"

    result = {
        "id": "BP-B1",
        "smoke": smoke,
        "n_trials_per_seed": n_trials,
        "seeds": list(seeds),
        "t_hold": t_hold,
        "bars": {
            "B1_treatment_acc": {"value": acc_T, "threshold": BAR_B1, "pass": b1},
            "B2_c1_empty_acc": {"value": acc_C1, "threshold": BAR_B2, "pass": b2, "must_fail_content": True},
            "B3_c2_scramble_acc": {"value": acc_C2, "threshold": BAR_B3, "pass": b3, "must_fail_content": True},
            "B4_c3_position_acc": {"value": acc_C3, "threshold": BAR_B4, "pass": b4, "must_fail_content": True},
            "B5_survival": {"value": surv, "threshold": BAR_B5, "pass": b5},
        },
        "n_T": len(all_T),
        "fp0_match_alpha": sum(1 for r in all_T if r["label"] == "alpha" and r["fp0"] == FP_ALPHA),
        "fp0_match_beta": sum(1 for r in all_T if r["label"] == "beta" and r["fp0"] == FP_BETA),
        "verdict": verdict,
        "trials_T_sample": all_T[:4],
    }
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="run_bp_b1_molecule_information")
    p.add_argument("--smoke", action="store_true", help="N=4, T=50, seed 42 only")
    p.add_argument("--live", action="store_true", default=False,
                   help="optional PyVista 3D (off by default — lab is headless)")
    p.add_argument("--live-all", action="store_true", help="live-view every trial (slow)")
    args = p.parse_args(argv)

    if args.smoke:
        n_trials, t_hold, seeds, smoke = 4, 50, (42,), True
    else:
        n_trials, t_hold, seeds, smoke = N_FULL, T_FULL, SEEDS_FULL, False

    live = bool(args.live or args.live_all)
    print(f"BP-B1 start smoke={smoke} N={n_trials} T={t_hold} seeds={seeds} live={live}")
    result = run_protocol(
        n_trials=n_trials, t_hold=t_hold, seeds=seeds, smoke=smoke,
        live=live, live_all=bool(args.live_all),
    )

    out_dir = Path.home() / ".eqmod" / "bet" / "BP-B1"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / ("result_smoke.json" if smoke else "result.json")
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("--- bars ---")
    for k, v in result["bars"].items():
        print(f"  {k}: value={v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print("--- VERDICT ---")
    print(f"BP-B1: {result['verdict']}")
    print(f"wrote {out_path}")
    print("DONE")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""BET-002 — Active Inference + Cognitive Map. Pre-registered acceptance.

Bet pre-registration LOGBOOK 2026-05-22:
  T1 persistent topology change KL > 0.1
  T2 content discrimination KL > 0.1
  T3 sample-efficient (T1+T2 at ≤ 50 % corpus)
  T4 held-out generalization precision > 0.3
  T5 retention ≥ 50 % after 10k rest ticks
  Plus anti-trivial-plateau check (T0): spatial std(mu-field) > 0.05

Result.json verdict per dispatcher contract:
  passed = all six (T0-T5) PASS in this iteration  →  bet WIN trigger
  null   = subset PASS (expected mode)
  failed = implementation broke
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from world.flux.cognitive_map import (
    MapConfig, encode_sensor, evaluate_holdout, initialise, run,
)

# ---------- Pre-registered fixtures (locked) ----------
N_TICKS = 10_000
SAMPLES_PER_TICK = 16
SEED_A = 4242
SEED_B = 7777
WN_SEED = 9999
TARGET_RMS = 0.25
N_BINS = 32

OUT_DIR = Path.home() / ".eqmod/bet/BET-002"


def _make_white_noise(n_samples: int, target_rms: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _make_synthetic_english_like(n_samples: int, target_rms: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    w = rng.standard_normal(n_samples)
    pink = np.cumsum(w)
    pink -= pink.mean()
    n_silence = max(1, n_samples // 50)
    silence_starts = rng.integers(0, n_samples - 50, size=n_silence)
    for s0 in silence_starts:
        pink[s0:s0 + rng.integers(20, 80)] = 0.0
    rms_now = np.sqrt(np.mean(pink * pink))
    if rms_now > 0:
        pink = pink / rms_now * target_rms
    return pink.astype(np.float64)


def _hist_kl(a: np.ndarray, b: np.ndarray, n_bins: int = N_BINS) -> float:
    a_flat = a.ravel()
    b_flat = b.ravel()
    lo = min(a_flat.min(), b_flat.min())
    hi = max(a_flat.max(), b_flat.max())
    if hi - lo < 1e-12:
        return 0.0
    edges = np.linspace(lo, hi, n_bins + 1)
    ha, _ = np.histogram(a_flat, bins=edges)
    hb, _ = np.histogram(b_flat, bins=edges)
    pa = (ha + 1.0) / (ha.sum() + n_bins)
    pb = (hb + 1.0) / (hb.sum() + n_bins)
    return 0.5 * (float(np.sum(pa * np.log(pa / pb))) + float(np.sum(pb * np.log(pb / pa))))


def _write_result_json(verdict: str, measurements: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-002",
        "verdict": verdict,
        "measurements": measurements,
        "hypothesis": "Active Inference + Cognitive Map (Friston 2010 + Behrens 2018 + O'Keefe/Nadel 1978 + Whittington 2020)",
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))


# ---------- Fixtures: train substrates once, share across tests ----------
@pytest.fixture(scope="module")
def substrates():
    cfg = MapConfig()
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_half = (N_TICKS // 2) * SAMPLES_PER_TICK

    eng_full = _make_synthetic_english_like(n_audio, TARGET_RMS, SEED_A)
    eng_b = _make_synthetic_english_like(n_audio, TARGET_RMS, SEED_B)
    wn_full = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)

    state_init = initialise(cfg)
    mu_init = state_init["mu"].copy()

    state_eng = run(cfg, N_TICKS, eng_full)
    state_wn = run(cfg, N_TICKS, wn_full)
    state_neg = run(cfg, N_TICKS, None)

    # Sample-efficient (T3): half the corpus
    state_eng_half = run(cfg, N_TICKS // 2, eng_full[:n_half])
    state_wn_half = run(cfg, N_TICKS // 2, wn_full[:n_half])

    # Retention (T5): rest 10k ticks after eng training
    state_eng_rest = run(cfg, N_TICKS, None, state={
        "mu": state_eng["mu"].copy(),
        "Lambda": state_eng["Lambda"].copy(),
        "N": state_eng["N"].copy(),
    })

    # Held-out (T4): train on first half of eng_b, evaluate on the second half
    state_for_holdout = run(cfg, N_TICKS // 2, eng_b[:n_half])
    holdout_metrics = evaluate_holdout(state_for_holdout, eng_b[n_half:], cfg, tick_offset=N_TICKS // 2)

    return dict(
        cfg=cfg,
        mu_init=mu_init,
        state_eng=state_eng,
        state_wn=state_wn,
        state_neg=state_neg,
        state_eng_half=state_eng_half,
        state_wn_half=state_wn_half,
        state_eng_rest=state_eng_rest,
        holdout_metrics=holdout_metrics,
    )


# ---------- Locked tests ----------
def test_T0_anti_trivial_plateau_spatial_std(substrates):
    """Spatial std of mu-field across all voxels and feature dims > 0.05.
    Anti-trivial-plateau gate added after BET-001 NULL diagnostic."""
    mu = substrates["state_eng"]["mu"]
    s = float(mu.std())
    assert s > 0.05, f"T0 spatial std={s:.6f} ≤ 0.05 (substrate uniform — trivial plateau)"


def test_T1_persistence_vs_init(substrates):
    kl = _hist_kl(substrates["mu_init"], substrates["state_eng"]["mu"])
    assert kl > 0.1, f"T1 KL={kl:.6f} ≤ 0.1"


def test_T2_content_discrimination(substrates):
    kl = _hist_kl(substrates["state_eng"]["mu"], substrates["state_wn"]["mu"])
    assert kl > 0.1, f"T2 KL={kl:.6f} ≤ 0.1"


def test_T3_sample_efficiency_half_corpus(substrates):
    """T1 + T2 must still hold after seeing only 50% of the corpus."""
    mu_eng_half = substrates["state_eng_half"]["mu"]
    mu_wn_half = substrates["state_wn_half"]["mu"]
    kl_t1 = _hist_kl(substrates["mu_init"], mu_eng_half)
    kl_t2 = _hist_kl(mu_eng_half, mu_wn_half)
    assert kl_t1 > 0.1 and kl_t2 > 0.1, (
        f"T3 sample-efficiency NULL: kl_t1_half={kl_t1:.4f} kl_t2_half={kl_t2:.4f}"
    )


def test_T4_generalization_holdout_precision(substrates):
    """Held-out chunks evaluated against the trained map should have positive
    cosine similarity to the map's predictions in > 30 % of cases."""
    m = substrates["holdout_metrics"]
    assert m["precision"] > 0.3, (
        f"T4 generalization NULL: precision={m['precision']:.4f} n={m['n']}"
    )


def test_T5_retention_after_rest(substrates):
    """After 10k rest ticks, T1 and T2 must still satisfy at ≥ 50 % of the
    immediately-post-training KL value."""
    mu_eng = substrates["state_eng"]["mu"]
    mu_wn = substrates["state_wn"]["mu"]
    mu_eng_rest = substrates["state_eng_rest"]["mu"]
    mu_init = substrates["mu_init"]
    kl_t1_post = _hist_kl(mu_init, mu_eng)
    kl_t2_post = _hist_kl(mu_eng, mu_wn)
    kl_t1_rest = _hist_kl(mu_init, mu_eng_rest)
    kl_t2_rest = _hist_kl(mu_eng_rest, mu_wn)
    retention_t1 = kl_t1_rest / (kl_t1_post + 1e-9)
    retention_t2 = kl_t2_rest / (kl_t2_post + 1e-9)
    assert retention_t1 >= 0.5 and retention_t2 >= 0.5, (
        f"T5 retention NULL: t1_retention={retention_t1:.4f} t2_retention={retention_t2:.4f}"
    )


# ---------- Result.json writer (runs at session teardown) ----------
@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    mu_init = substrates["mu_init"]
    mu_eng = substrates["state_eng"]["mu"]
    mu_wn = substrates["state_wn"]["mu"]
    mu_neg = substrates["state_neg"]["mu"]
    mu_eng_half = substrates["state_eng_half"]["mu"]
    mu_wn_half = substrates["state_wn_half"]["mu"]
    mu_eng_rest = substrates["state_eng_rest"]["mu"]

    t0_std = float(mu_eng.std())
    kl_t1 = _hist_kl(mu_init, mu_eng)
    kl_t2 = _hist_kl(mu_eng, mu_wn)
    kl_t1_half = _hist_kl(mu_init, mu_eng_half)
    kl_t2_half = _hist_kl(mu_eng_half, mu_wn_half)
    kl_t1_rest = _hist_kl(mu_init, mu_eng_rest)
    kl_t2_rest = _hist_kl(mu_eng_rest, mu_wn)
    neg_kl = _hist_kl(mu_neg, mu_eng)
    holdout = substrates["holdout_metrics"]

    t0_pass = t0_std > 0.05
    t1_pass = kl_t1 > 0.1
    t2_pass = kl_t2 > 0.1
    t3_pass = kl_t1_half > 0.1 and kl_t2_half > 0.1
    t4_pass = holdout["precision"] > 0.3
    t5_pass = (
        (kl_t1_rest / (kl_t1 + 1e-9) >= 0.5)
        and (kl_t2_rest / (kl_t2 + 1e-9) >= 0.5)
    )

    all_pass = t0_pass and t1_pass and t2_pass and t3_pass and t4_pass and t5_pass

    measurements = {
        "T0_spatial_std_mu_eng": t0_std,
        "T0_threshold": 0.05,
        "T0_pass": t0_pass,
        "T1_kl_init_vs_eng": kl_t1,
        "T1_threshold": 0.1,
        "T1_pass": t1_pass,
        "T2_kl_eng_vs_wn": kl_t2,
        "T2_threshold": 0.1,
        "T2_pass": t2_pass,
        "T3_kl_init_vs_eng_half": kl_t1_half,
        "T3_kl_eng_vs_wn_half": kl_t2_half,
        "T3_pass": t3_pass,
        "T4_holdout_precision": holdout["precision"],
        "T4_holdout_n": holdout["n"],
        "T4_holdout_mean_cosine": holdout["mean_cosine"],
        "T4_threshold": 0.3,
        "T4_pass": t4_pass,
        "T5_t1_retention_ratio": kl_t1_rest / (kl_t1 + 1e-9),
        "T5_t2_retention_ratio": kl_t2_rest / (kl_t2 + 1e-9),
        "T5_threshold": 0.5,
        "T5_pass": t5_pass,
        "neg_control_kl_neg_vs_eng": neg_kl,
        "all_six_pass": all_pass,
    }
    verdict = "passed" if all_pass else "null"
    _write_result_json(verdict, measurements)

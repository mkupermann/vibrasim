"""BET-008 — Long-run validation of beta=0 cognitive_map substrate.

Pre-registered follow-up to BET-006's PASS verdict. Per LOGBOOK 2026-05-23:
"needs the long-run for full defensibility but the locked-test contract is met".
This file IS that long-run validation.

The locked 5/5 bar is unchanged. Only the tick count grows: 10_000 → 1_000_000
(100× scale-up). All other parameters identical to BET-006 beta=0 variant:
samples_per_tick=16, fft_bands=8, grid_dims=(30,15,8), beta_lateral=0.0,
R-7 corpus audio.

Pre-data prediction (locked before this iteration runs):

  T0 — More cells visited at 100× scale → spatial std grows. PASS expected.
  T1 — Trained mu deviates more from init-zero at 100× scale. PASS expected.
  T2 — Per-cell running means converge to dataset-mean of EN-vs-WN at scale.
       Variance within EN-mu and within WN-mu both shrink; KL grows or stays.
       PASS expected (was 0.88 at 10k).
  T3 — Half-corpus is 500k ticks. Same convergence argument applies at half.
       PASS expected.
  T4 — Hold-out precision is the real risk. R-7 acoustic stationarity across
       1M samples per slice (~62 s of audio per slice at 16 kHz, with samples_
       per_tick=16) is the open question. Could drop below 0.3 if the corpus
       has strong time-non-stationarity (multiple speakers, changing mic, …).
       Provisional PASS expected but this is the test that could break.
  T5 — beta=0 means NO update during rest (no input means no cell-visits).
       Retention is trivially 1.0 by construction. PASS guaranteed.

If T0..T5 all PASS at 100× scale: bet WIN is confirmed at scale. If any T
fails: BET-006's WIN was a small-scale artifact; operator decides whether
the locked-test contract is still considered MET (the bar said "on a single
substrate instance", not "at any scale") or whether additional iterations
are needed.

No threshold tuning — same 0.05/0.1/0.3/0.5 bars as BET-006.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.cognitive_map import (
    MapConfig, evaluate_holdout, initialise, run,
)

N_TICKS = 1_000_000   # 100× BET-006 scale-up
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
BETA_LATERAL = 0.0
WN_SEED = 9999
TARGET_RMS = 0.25
N_BINS = 32

OUT_DIR = Path.home() / ".eqmod/bet/BET-008"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples: int, target_rms: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


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
        "item_id": "BET-008",
        "verdict": verdict,
        "measurements": measurements,
        "hypothesis": "Long-run validation of beta=0 cognitive_map substrate at 100x BET-006 scale (1M ticks).",
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))


@pytest.fixture(scope="module")
def substrates():
    cfg = MapConfig(
        samples_per_tick=SAMPLES_PER_TICK,
        fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
        beta_lateral=BETA_LATERAL,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_half = (N_TICKS // 2) * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if 2 * n_audio > full.shape[0]:
        raise RuntimeError(
            f"R-7 corpus too short for BET-008: need {2 * n_audio}, have {full.shape[0]}"
        )
    eng_a = full[:n_audio].astype(np.float64)
    eng_b = full[n_audio:2 * n_audio].astype(np.float64)
    wn_full = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)

    state_init = initialise(cfg)
    mu_init = state_init["mu"].copy()

    state_eng = run(cfg, N_TICKS, eng_a)
    state_wn = run(cfg, N_TICKS, wn_full)
    state_neg = run(cfg, N_TICKS, None)

    state_eng_half = run(cfg, N_TICKS // 2, eng_a[:n_half])
    state_wn_half = run(cfg, N_TICKS // 2, wn_full[:n_half])

    state_eng_rest = run(cfg, N_TICKS, None, state={
        "mu": state_eng["mu"].copy(),
        "Lambda": state_eng["Lambda"].copy(),
        "N": state_eng["N"].copy(),
    })

    state_for_holdout = run(cfg, N_TICKS // 2, eng_b[:n_half])
    holdout_metrics = evaluate_holdout(
        state_for_holdout, eng_b[n_half:], cfg, tick_offset=N_TICKS // 2,
    )

    return dict(
        cfg=cfg, mu_init=mu_init,
        state_eng=state_eng, state_wn=state_wn, state_neg=state_neg,
        state_eng_half=state_eng_half, state_wn_half=state_wn_half,
        state_eng_rest=state_eng_rest,
        holdout_metrics=holdout_metrics,
    )


def test_T0_anti_trivial_plateau_spatial_std(substrates):
    s = float(substrates["state_eng"]["mu"].std())
    assert s > 0.05, f"T0 spatial std={s:.6f} ≤ 0.05 at scale"


def test_T1_persistence_vs_init(substrates):
    kl = _hist_kl(substrates["mu_init"], substrates["state_eng"]["mu"])
    assert kl > 0.1, f"T1 KL={kl:.6f} ≤ 0.1 at scale"


def test_T2_content_discrimination(substrates):
    kl = _hist_kl(substrates["state_eng"]["mu"], substrates["state_wn"]["mu"])
    assert kl > 0.1, f"T2 KL={kl:.6f} ≤ 0.1 at scale (BET-006 10k value was 0.88)"


def test_T3_sample_efficiency_half_corpus(substrates):
    mu_eng_half = substrates["state_eng_half"]["mu"]
    mu_wn_half = substrates["state_wn_half"]["mu"]
    kl_t1 = _hist_kl(substrates["mu_init"], mu_eng_half)
    kl_t2 = _hist_kl(mu_eng_half, mu_wn_half)
    assert kl_t1 > 0.1 and kl_t2 > 0.1, f"T3 at scale: kl_t1_half={kl_t1:.4f} kl_t2_half={kl_t2:.4f}"


def test_T4_generalization_holdout_precision(substrates):
    m = substrates["holdout_metrics"]
    assert m["precision"] > 0.3, (
        f"T4 at scale: precision={m['precision']:.4f} n={m['n']} — could indicate "
        "R-7 acoustic non-stationarity across longer time-windows"
    )


def test_T5_retention_after_rest(substrates):
    mu_init = substrates["mu_init"]
    mu_eng = substrates["state_eng"]["mu"]
    mu_wn = substrates["state_wn"]["mu"]
    mu_eng_rest = substrates["state_eng_rest"]["mu"]
    kl_t1_post = _hist_kl(mu_init, mu_eng)
    kl_t2_post = _hist_kl(mu_eng, mu_wn)
    kl_t1_rest = _hist_kl(mu_init, mu_eng_rest)
    kl_t2_rest = _hist_kl(mu_eng_rest, mu_wn)
    r1 = kl_t1_rest / (kl_t1_post + 1e-9)
    r2 = kl_t2_rest / (kl_t2_post + 1e-9)
    assert r1 >= 0.5 and r2 >= 0.5, f"T5 at scale: t1_ret={r1:.4f} t2_ret={r2:.4f}"


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
        "n_ticks": N_TICKS,
        "beta_lateral": BETA_LATERAL,
        "T0_spatial_std_mu_eng": t0_std, "T0_threshold": 0.05, "T0_pass": t0_pass,
        "T1_kl_init_vs_eng": kl_t1, "T1_threshold": 0.1, "T1_pass": t1_pass,
        "T2_kl_eng_vs_wn": kl_t2, "T2_threshold": 0.1, "T2_pass": t2_pass,
        "T3_kl_init_vs_eng_half": kl_t1_half, "T3_kl_eng_vs_wn_half": kl_t2_half, "T3_pass": t3_pass,
        "T4_holdout_precision": holdout["precision"], "T4_holdout_n": holdout["n"],
        "T4_holdout_mean_cosine": holdout["mean_cosine"], "T4_threshold": 0.3, "T4_pass": t4_pass,
        "T5_t1_retention_ratio": kl_t1_rest / (kl_t1 + 1e-9),
        "T5_t2_retention_ratio": kl_t2_rest / (kl_t2 + 1e-9),
        "T5_threshold": 0.5, "T5_pass": t5_pass,
        "neg_control_kl_neg_vs_eng": neg_kl,
        "audio_source": "R-7 corpus (manifest)",
        "all_six_pass": all_pass,
    }
    verdict = "passed" if all_pass else "null"
    _write_result_json(verdict, measurements)

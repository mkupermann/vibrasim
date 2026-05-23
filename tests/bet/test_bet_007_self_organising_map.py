"""BET-007 — Self-Organising Map (Kohonen 1982) as learning substrate.

Pre-conditional alternative path to BET-006: if the beta_lateral ablation
on cognitive_map NULLs (cognitive-map class cannot clear 5/5 by parameter
tuning alone), a substrate with a fundamentally different inductive bias is
tested. SOMs preserve topology BY CONSTRUCTION via competitive update.

Same encoder + same audio (R-7 corpus) + same grid shape (30,15,8) as
BET-002/004/006, so the only varying element is the substrate update rule:

  cognitive_map: position by content-hash, Bayesian update at that cell,
                 precision-weighted error propagated to 6 neighbours
                 (Friston active-inference cascade).

  SOM:           BMU by COMPETITION (argmin ||w-x|| over whole grid),
                 weight pulled toward x at BMU and in a Gaussian
                 neighbourhood with time-decaying radius (Kohonen
                 competitive learning).

Locked pre-registered tests T0-T5 with same thresholds as bet pre-registration
LOGBOOK 2026-05-22.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_substrate import (
    SOMConfig, evaluate_holdout, initialise, run,
)

# ---------- Pre-registered fixtures (locked) ----------
N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25
N_BINS = 32

OUT_DIR = Path.home() / ".eqmod/bet/BET-007"
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
        "item_id": "BET-007",
        "verdict": verdict,
        "measurements": measurements,
        "hypothesis": "Self-Organising Map (Kohonen 1982) substrate — competitive learning, topology preservation by construction.",
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMConfig(
        samples_per_tick=SAMPLES_PER_TICK,
        fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_half = (N_TICKS // 2) * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if 2 * n_audio > full.shape[0]:
        raise RuntimeError(
            f"R-7 corpus too short: need {2 * n_audio}, have {full.shape[0]}"
        )
    eng_a = full[:n_audio].astype(np.float64)
    eng_b = full[n_audio:2 * n_audio].astype(np.float64)
    wn_full = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)

    state_init = initialise(cfg)
    w_init = state_init["w"].copy()

    state_eng = run(cfg, N_TICKS, eng_a)
    state_wn = run(cfg, N_TICKS, wn_full)
    state_neg = run(cfg, N_TICKS, None)

    state_eng_half = run(cfg, N_TICKS // 2, eng_a[:n_half])
    state_wn_half = run(cfg, N_TICKS // 2, wn_full[:n_half])

    state_eng_rest = run(cfg, N_TICKS, None, state={
        "w": state_eng["w"].copy(),
        "N": state_eng["N"].copy(),
        "ii": state_eng["ii"],
        "jj": state_eng["jj"],
        "kk": state_eng["kk"],
    })

    state_for_holdout = run(cfg, N_TICKS // 2, eng_b[:n_half])
    holdout_metrics = evaluate_holdout(state_for_holdout, eng_b[n_half:], cfg)

    return dict(
        cfg=cfg, w_init=w_init,
        state_eng=state_eng, state_wn=state_wn, state_neg=state_neg,
        state_eng_half=state_eng_half, state_wn_half=state_wn_half,
        state_eng_rest=state_eng_rest,
        holdout_metrics=holdout_metrics,
    )


def test_T0_anti_trivial_plateau_spatial_std(substrates):
    s = float(substrates["state_eng"]["w"].std())
    assert s > 0.05, f"T0 spatial std={s:.6f} ≤ 0.05"


def test_T1_persistence_vs_init(substrates):
    kl = _hist_kl(substrates["w_init"], substrates["state_eng"]["w"])
    assert kl > 0.1, f"T1 KL={kl:.6f} ≤ 0.1"


def test_T2_content_discrimination(substrates):
    kl = _hist_kl(substrates["state_eng"]["w"], substrates["state_wn"]["w"])
    assert kl > 0.1, f"T2 KL={kl:.6f} ≤ 0.1"


def test_T3_sample_efficiency_half_corpus(substrates):
    w_eng_half = substrates["state_eng_half"]["w"]
    w_wn_half = substrates["state_wn_half"]["w"]
    kl_t1 = _hist_kl(substrates["w_init"], w_eng_half)
    kl_t2 = _hist_kl(w_eng_half, w_wn_half)
    assert kl_t1 > 0.1 and kl_t2 > 0.1, f"T3: kl_t1_half={kl_t1:.4f} kl_t2_half={kl_t2:.4f}"


def test_T4_generalization_holdout_precision(substrates):
    m = substrates["holdout_metrics"]
    assert m["precision"] > 0.3, f"T4 precision={m['precision']:.4f} n={m['n']}"


def test_T5_retention_after_rest(substrates):
    w_init = substrates["w_init"]
    w_eng = substrates["state_eng"]["w"]
    w_wn = substrates["state_wn"]["w"]
    w_eng_rest = substrates["state_eng_rest"]["w"]
    kl_t1_post = _hist_kl(w_init, w_eng)
    kl_t2_post = _hist_kl(w_eng, w_wn)
    kl_t1_rest = _hist_kl(w_init, w_eng_rest)
    kl_t2_rest = _hist_kl(w_eng_rest, w_wn)
    r1 = kl_t1_rest / (kl_t1_post + 1e-9)
    r2 = kl_t2_rest / (kl_t2_post + 1e-9)
    assert r1 >= 0.5 and r2 >= 0.5, f"T5: t1_ret={r1:.4f} t2_ret={r2:.4f}"


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    w_init = substrates["w_init"]
    w_eng = substrates["state_eng"]["w"]
    w_wn = substrates["state_wn"]["w"]
    w_neg = substrates["state_neg"]["w"]
    w_eng_half = substrates["state_eng_half"]["w"]
    w_wn_half = substrates["state_wn_half"]["w"]
    w_eng_rest = substrates["state_eng_rest"]["w"]

    t0_std = float(w_eng.std())
    kl_t1 = _hist_kl(w_init, w_eng)
    kl_t2 = _hist_kl(w_eng, w_wn)
    kl_t1_half = _hist_kl(w_init, w_eng_half)
    kl_t2_half = _hist_kl(w_eng_half, w_wn_half)
    kl_t1_rest = _hist_kl(w_init, w_eng_rest)
    kl_t2_rest = _hist_kl(w_eng_rest, w_wn)
    neg_kl = _hist_kl(w_neg, w_eng)
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
        "T0_spatial_std_w_eng": t0_std, "T0_threshold": 0.05, "T0_pass": t0_pass,
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

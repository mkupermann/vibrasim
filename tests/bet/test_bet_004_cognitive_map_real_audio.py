"""BET-004 — Active Inference + Cognitive Map with REAL R-7 corpus audio.

BET-002 + BET-003 NULLed on T2/T3 because the synthetic English generator
(cumsum(white_noise) + zero stretches) had a band-normalised spectrum
nearly identical to white noise. After ``band / band.sum()`` the
absolute-magnitude information that distinguishes pink-ish from
flat-spectrum noise was washed out.

Pre-check on real R-7 corpus audio (R-7 manifest at
~/.eqmod/training/EN/manifest.json, ~17779 s, 284M samples at 16 kHz):

    normalised 8-band spectrum:
      EN band-0 (low freq): 0.545  (speech-formant concentration)
      WN band-0:            0.125  (uniform across bands)
      L1 distance(EN, WN):  0.843

The data IS strongly distinguishable from matched-RMS white noise under
the encoder this substrate uses, even at samples_per_tick=16. The earlier
BET-002/003 NULLs were data-side artefacts, not substrate-side failures.

Substrate code unchanged. Encoder unchanged (samples_per_tick=16,
fft_bands=8). Only the audio source changes: load_corpus_waveform_from_manifest
replaces the synthetic generator.

If T2 + T3 PASS with real audio at otherwise-locked BET-002 parameters,
the cognitive-map-as-learning-substrate hypothesis passes all six bet
tests (T0+T1+T2+T3+T4+T5 simultaneously on a single substrate instance)
— that would be the bet's WIN condition under LOGBOOK 2026-05-22
pre-registration.
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

# ---------- Pre-registered fixtures (locked) ----------
N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS  # = 10
SEED_A = 4242
SEED_B = 7777
WN_SEED = 9999
TARGET_RMS = 0.25
N_BINS = 32

OUT_DIR = Path.home() / ".eqmod/bet/BET-004"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples: int, target_rms: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _load_real_english(n_samples: int, offset: int = 0) -> np.ndarray:
    """Load n_samples from the R-7 corpus starting at offset.

    The full corpus is ~284M samples (~17 779 s @ 16 kHz). We slice the
    requested chunk to keep memory bounded. RMS-normalisation already
    applied inside the loader (target 0.25, matching white-noise generator).
    """
    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if offset + n_samples > full.shape[0]:
        raise RuntimeError(
            f"R-7 corpus too short for offset={offset} + n={n_samples} "
            f"(corpus has {full.shape[0]} samples)"
        )
    return full[offset:offset + n_samples].astype(np.float64)


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
        "item_id": "BET-004",
        "verdict": verdict,
        "measurements": measurements,
        "hypothesis": "Active Inference + Cognitive Map with REAL R-7 corpus audio (vs BET-002/003 synthetic)",
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))


@pytest.fixture(scope="module")
def substrates():
    cfg = MapConfig(
        samples_per_tick=SAMPLES_PER_TICK,
        fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_half = (N_TICKS // 2) * SAMPLES_PER_TICK

    # Two independent slices of real R-7 audio for the SEED_A and SEED_B runs
    # (BET-002 simulated SEED_B as a different rng draw of the synthetic
    # generator; here we use a different audio offset to get independent
    # data while keeping the data-source identity).
    eng_a = _load_real_english(n_audio, offset=0)
    eng_b = _load_real_english(n_audio, offset=n_audio)  # disjoint slice
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

    # Held-out: train on first half of eng_b, evaluate on second half
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
    assert s > 0.05, f"T0 spatial std={s:.6f} ≤ 0.05"


def test_T1_persistence_vs_init(substrates):
    kl = _hist_kl(substrates["mu_init"], substrates["state_eng"]["mu"])
    assert kl > 0.1, f"T1 KL={kl:.6f} ≤ 0.1"


def test_T2_content_discrimination(substrates):
    kl = _hist_kl(substrates["state_eng"]["mu"], substrates["state_wn"]["mu"])
    assert kl > 0.1, f"T2 KL={kl:.6f} ≤ 0.1 (encoder still fails on real audio?)"


def test_T3_sample_efficiency_half_corpus(substrates):
    mu_eng_half = substrates["state_eng_half"]["mu"]
    mu_wn_half = substrates["state_wn_half"]["mu"]
    kl_t1 = _hist_kl(substrates["mu_init"], mu_eng_half)
    kl_t2 = _hist_kl(mu_eng_half, mu_wn_half)
    assert kl_t1 > 0.1 and kl_t2 > 0.1, f"T3: kl_t1_half={kl_t1:.4f} kl_t2_half={kl_t2:.4f}"


def test_T4_generalization_holdout_precision(substrates):
    m = substrates["holdout_metrics"]
    assert m["precision"] > 0.3, f"T4 precision={m['precision']:.4f} n={m['n']}"


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
    assert r1 >= 0.5 and r2 >= 0.5, f"T5: t1_ret={r1:.4f} t2_ret={r2:.4f}"


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

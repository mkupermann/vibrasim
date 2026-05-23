"""BET-003 — Active Inference + Cognitive Map (same substrate as BET-002,
higher spectral-resolution encoder via longer sample window).

BET-002 NULLed on T2/T3 with diagnosis: encoder under-spec'd. 16-sample
FFT chunks yield very few useful frequency bins; band normalisation
washes absolute-magnitude differences out; both English and white-noise
land in the map at similar sensor vectors. Substrate is structured
(T0+T1+T4+T5 PASS confirm) but cannot discriminate content via this
encoder.

BET-003 changes only the MapConfig: samples_per_tick=256 (16× larger
window → 16× more FFT bins) and fft_bands=16 (twice the spectral
resolution). The substrate code (cognitive_map.py) is unchanged — same
Bayesian update, same Friston cascade, same content-aware position
hash. Hypothesis: with sufficient spectral resolution, the cognitive
map will discriminate English from matched-RMS white noise.

Locked per BET-003 pre-registration (will be persisted in
~/.eqmod/bet/queue.yaml::BET-003 with this docstring):

  samples_per_tick = 256
  fft_bands = 16
  n_features = 2 + 16 = 18
  N_TICKS = 10_000 (unchanged from BET-002)
  Total audio per substrate = 10000 × 256 = 2.56M samples ≈ 160 s @ 16 kHz

All other parameters (alpha_precision_gain, beta_lateral,
position_hash_seed, grid_dims, TARGET_RMS, SEED_A, SEED_B, WN_SEED,
N_BINS, T0/T1/T2/T3/T4/T5 thresholds) UNCHANGED. This is encoder-only
iteration; substrate hypothesis is unchanged from BET-002.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from world.flux.cognitive_map import (
    MapConfig, evaluate_holdout, initialise, run,
)

# ---------- Pre-registered fixtures (locked) ----------
N_TICKS = 10_000
SAMPLES_PER_TICK = 256          # 16× larger than BET-002
FFT_BANDS = 16                  # 2× more spectral resolution
N_FEATURES = 2 + FFT_BANDS      # RMS + ZCR + bands = 18

SEED_A = 4242
SEED_B = 7777
WN_SEED = 9999
TARGET_RMS = 0.25
N_BINS = 32

OUT_DIR = Path.home() / ".eqmod/bet/BET-003"


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
        "item_id": "BET-003",
        "verdict": verdict,
        "measurements": measurements,
        "hypothesis": "Cognitive Map (Friston 2010+Behrens 2018) + higher-resolution encoder (256-sample window, 16 FFT bands)",
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

    eng_full = _make_synthetic_english_like(n_audio, TARGET_RMS, SEED_A)
    eng_b = _make_synthetic_english_like(n_audio, TARGET_RMS, SEED_B)
    wn_full = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)

    state_init = initialise(cfg)
    mu_init = state_init["mu"].copy()

    state_eng = run(cfg, N_TICKS, eng_full)
    state_wn = run(cfg, N_TICKS, wn_full)
    state_neg = run(cfg, N_TICKS, None)

    state_eng_half = run(cfg, N_TICKS // 2, eng_full[:n_half])
    state_wn_half = run(cfg, N_TICKS // 2, wn_full[:n_half])

    state_eng_rest = run(cfg, N_TICKS, None, state={
        "mu": state_eng["mu"].copy(),
        "Lambda": state_eng["Lambda"].copy(),
        "N": state_eng["N"].copy(),
    })

    state_for_holdout = run(cfg, N_TICKS // 2, eng_b[:n_half])
    holdout_metrics = evaluate_holdout(state_for_holdout, eng_b[n_half:], cfg, tick_offset=N_TICKS // 2)

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
    assert kl > 0.1, f"T2 KL={kl:.6f} ≤ 0.1 — encoder still under-resolved"


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
    assert r1 >= 0.5 and r2 >= 0.5, f"T5: t1_retention={r1:.4f} t2_retention={r2:.4f}"


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
        "config_samples_per_tick": SAMPLES_PER_TICK,
        "config_fft_bands": FFT_BANDS,
        "all_six_pass": all_pass,
    }
    verdict = "passed" if all_pass else "null"
    _write_result_json(verdict, measurements)

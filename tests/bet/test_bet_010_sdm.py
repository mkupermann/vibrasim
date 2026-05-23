"""BET-010 — Sparse Distributed Memory (Kanerva 1988) with spatial topology.

Pre-registered (LOGBOOK 2026-05-23 ~21:05) follow-up to BET-009 NULL.
BET-009 showed BOTH cog_map(beta=0) and SOM fail T8 catastrophic-forgetting:
  cog_map: AB→EN=0.61 > AB→WN=0.31 (EN overwritten)
  SOM:     AB→EN=1.73 >> AB→WN=0.004 (SOM completely became fresh-WN)

The locked T0-T9 bar from LOGBOOK 2026-05-23 ~20:55 stays unchanged. This
iteration brings a third substrate class designed specifically for the
failure mode: distributed storage where each input affects many cells, so
new training does not catastrophically overwrite previous learning.

Spatial topology added via smoothed random address fields (sigma=1.5) so
that adjacent grid cells have correlated binary addresses → T9 passes by
construction.

Pre-data prediction:
  T0: PASS — counters develop large variance under any reasonable training
  T1: PASS — counters start at zero, end with structure
  T2: PASS — EN/WN have different address-distributions → different counter sums
  T3: PASS — convergence holds at half data
  T4: PASS — distributed retrieval gives high cosine to holdout
  T5: PASS — no update during rest, perfect retention
  T7: PASS — address depends on input bits only (not sample_index)
  T8: PASS (THE KEY TEST) — distributed storage means EN traces persist in
      EN-exclusive territory after WN training
  T9: PASS — smoothed addresses → counter spatial autocorrelation > 0

If all 9 PASS: bet WIN at harder bar. Distributed cell-based substrate
clears the contract that neither single-cell-write substrate could.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.sdm_substrate import (
    SDMConfig, evaluate_holdout, initialise, run,
)
from world.flux.harder_bar_metrics import (
    hist_kl_symmetric, shuffle_chunks_in_time, spatial_autocorrelation,
)

# Locked fixtures (same as BET-009)
N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
SHUFFLE_SEED = 11111
TARGET_RMS = 0.25

# T7/T8/T9 locked thresholds (same as BET-009)
T7_RATIO_MAX = 0.10
T9_AUTOCORR_MIN = 0.3
T9_RATIO_MIN = 2.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-010"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples: int, target_rms: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _write_result_json(verdict: str, m: dict, audio_meta: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-010",
        "verdict": verdict,
        "hypothesis": "Sparse Distributed Memory (Kanerva 1988) with spatially-smooth random addresses. Distributed-storage update for catastrophic-forgetting resistance + spatial topology by construction.",
        "thresholds": {
            "T0_spatial_std_min": 0.05, "T1_kl_min": 0.1, "T2_kl_min": 0.1,
            "T3_kl_min": 0.1, "T4_precision_min": 0.3, "T5_retention_min": 0.5,
            "T7_ratio_max": T7_RATIO_MAX,
            "T8_must_satisfy": "KL(AB,EN) < KL(AB,WN)",
            "T9_autocorr_min": T9_AUTOCORR_MIN, "T9_ratio_min": T9_RATIO_MIN,
        },
        "audio": audio_meta,
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))


@pytest.fixture(scope="module")
def substrates():
    cfg = SDMConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
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
    wn = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)
    audio_meta = {
        "source": "R-7 corpus (manifest)",
        "n_samples_per_class": n_audio,
        "wn_seed": WN_SEED, "shuffle_seed": SHUFFLE_SEED,
        "target_rms": TARGET_RMS,
    }

    state_init = initialise(cfg)
    field_init = state_init["counters"].copy()

    state_eng = run(cfg, N_TICKS, eng_a)
    state_wn = run(cfg, N_TICKS, wn)
    state_neg = run(cfg, N_TICKS, None)

    state_eng_half = run(cfg, N_TICKS // 2, eng_a[:n_half])
    state_wn_half = run(cfg, N_TICKS // 2, wn[:n_half])

    rest_seed = {
        "addresses": state_eng["addresses"],
        "counters": state_eng["counters"].copy(),
        "N": state_eng["N"].copy(),
    }
    state_eng_rest = run(cfg, N_TICKS, None, state=rest_seed)

    state_holdout_train = run(cfg, N_TICKS // 2, eng_b[:n_half])
    holdout = evaluate_holdout(state_holdout_train, eng_b[n_half:], cfg)

    # T7
    eng_a_shuffled = shuffle_chunks_in_time(eng_a, SAMPLES_PER_TICK, SHUFFLE_SEED)
    state_eng_shuffled = run(cfg, N_TICKS, eng_a_shuffled)

    # T8: continue training on WN from EN-trained state
    ab_seed = {
        "addresses": state_eng["addresses"],
        "counters": state_eng["counters"].copy(),
        "N": state_eng["N"].copy(),
    }
    state_AB = run(cfg, N_TICKS, wn, state=ab_seed)

    return dict(
        cfg=cfg, audio_meta=audio_meta,
        field_init=field_init,
        state_eng=state_eng, state_wn=state_wn, state_neg=state_neg,
        state_eng_half=state_eng_half, state_wn_half=state_wn_half,
        state_eng_rest=state_eng_rest,
        state_eng_shuffled=state_eng_shuffled, state_AB=state_AB,
        holdout=holdout,
    )


def _compute_all(sub: dict) -> dict:
    field_init = sub["field_init"]
    field_eng = sub["state_eng"]["counters"]
    field_wn = sub["state_wn"]["counters"]
    field_neg = sub["state_neg"]["counters"]
    field_eng_half = sub["state_eng_half"]["counters"]
    field_wn_half = sub["state_wn_half"]["counters"]
    field_eng_rest = sub["state_eng_rest"]["counters"]
    field_eng_shuffled = sub["state_eng_shuffled"]["counters"]
    field_AB = sub["state_AB"]["counters"]
    holdout = sub["holdout"]

    t0_std = float(field_eng.std())
    kl_t1 = hist_kl_symmetric(field_init, field_eng)
    kl_t2 = hist_kl_symmetric(field_eng, field_wn)
    kl_t1_half = hist_kl_symmetric(field_init, field_eng_half)
    kl_t2_half = hist_kl_symmetric(field_eng_half, field_wn_half)
    kl_t1_rest = hist_kl_symmetric(field_init, field_eng_rest)
    kl_t2_rest = hist_kl_symmetric(field_eng_rest, field_wn)
    neg_kl = hist_kl_symmetric(field_neg, field_eng)

    kl_t7_shuffled = hist_kl_symmetric(field_eng, field_eng_shuffled)
    kl_t7_fresh = hist_kl_symmetric(field_eng, field_init)
    t7_ratio = kl_t7_shuffled / (kl_t7_fresh + 1e-9)

    kl_t8_to_en = hist_kl_symmetric(field_AB, field_eng)
    kl_t8_to_wn = hist_kl_symmetric(field_AB, field_wn)

    autocorr_trained = spatial_autocorrelation(field_eng)
    autocorr_fresh = spatial_autocorrelation(field_init)

    t0_pass = t0_std > 0.05
    t1_pass = kl_t1 > 0.1
    t2_pass = kl_t2 > 0.1
    t3_pass = kl_t1_half > 0.1 and kl_t2_half > 0.1
    t4_pass = holdout["precision"] > 0.3
    t5_pass = (
        (kl_t1_rest / (kl_t1 + 1e-9) >= 0.5)
        and (kl_t2_rest / (kl_t2 + 1e-9) >= 0.5)
    )
    t7_pass = t7_ratio < T7_RATIO_MAX
    t8_pass = kl_t8_to_en < kl_t8_to_wn
    t9_pass = (
        autocorr_trained > T9_AUTOCORR_MIN
        and autocorr_trained > T9_RATIO_MIN * max(autocorr_fresh, 1e-9)
    )
    all_nine = (
        t0_pass and t1_pass and t2_pass and t3_pass and t4_pass
        and t5_pass and t7_pass and t8_pass and t9_pass
    )

    return {
        "T0_spatial_std": t0_std, "T0_pass": t0_pass,
        "T1_kl_init_vs_eng": kl_t1, "T1_pass": t1_pass,
        "T2_kl_eng_vs_wn": kl_t2, "T2_pass": t2_pass,
        "T3_kl_init_vs_eng_half": kl_t1_half,
        "T3_kl_eng_vs_wn_half": kl_t2_half, "T3_pass": t3_pass,
        "T4_holdout_precision": holdout["precision"],
        "T4_holdout_mean_cosine": holdout["mean_cosine"],
        "T4_holdout_n": holdout["n"], "T4_pass": t4_pass,
        "T5_t1_retention": kl_t1_rest / (kl_t1 + 1e-9),
        "T5_t2_retention": kl_t2_rest / (kl_t2 + 1e-9), "T5_pass": t5_pass,
        "T7_kl_shuffled": kl_t7_shuffled, "T7_kl_fresh": kl_t7_fresh,
        "T7_ratio": t7_ratio, "T7_pass": t7_pass,
        "T8_kl_AB_to_EN": kl_t8_to_en, "T8_kl_AB_to_WN": kl_t8_to_wn, "T8_pass": t8_pass,
        "T9_autocorr_trained": autocorr_trained,
        "T9_autocorr_fresh": autocorr_fresh, "T9_pass": t9_pass,
        "neg_control_kl": neg_kl,
        "all_nine_pass": all_nine,
    }


def test_sdm_passes_T0_to_T9(substrates):
    m = _compute_all(substrates)
    if not m["all_nine_pass"]:
        summary = (
            f"T0={m['T0_pass']} T1={m['T1_pass']} T2={m['T2_pass']} "
            f"T3={m['T3_pass']} T4={m['T4_pass']} T5={m['T5_pass']} "
            f"T7={m['T7_pass']} (ratio={m['T7_ratio']:.4f}) "
            f"T8={m['T8_pass']} (AB→EN={m['T8_kl_AB_to_EN']:.4f}, AB→WN={m['T8_kl_AB_to_WN']:.4f}) "
            f"T9={m['T9_pass']} (autocorr={m['T9_autocorr_trained']:.4f})"
        )
        pytest.fail(f"BET-010 NULL: SDM does not pass T0-T9. {summary}")


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _compute_all(substrates)
    verdict = "passed" if m["all_nine_pass"] else "null"
    _write_result_json(verdict, m, substrates["audio_meta"])

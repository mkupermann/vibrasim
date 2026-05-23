"""BET-009 — Harder bar T0-T9. Pre-registered LOGBOOK 2026-05-23 ~20:55.

Tests BOTH substrate classes (cog_map at beta=0, SOM) through the full
ten-test bar:
  T0-T5: locked bar from LOGBOOK 2026-05-22 (re-confirmed for parity)
  T7:    content-driven structure (not position-artifacts)
  T8:    catastrophic-forgetting resistance
  T9:    emergent spatial organisation

(T6 was dropped during design — predictive-bit-rate is not architecturally
meaningful for cell-based substrates without sequence memory.)

Verdict: substrate "passes" if it satisfies T0..T9 all simultaneously
(9/9 with T6 absent). Either, both, or neither substrate may pass.

Pre-registered predictions:
  cog_map beta=0: PASS T0-T5; LIKELY FAIL T7 (sample_index in hash),
                  LIKELY FAIL T8 (running-mean overwrite), LIKELY FAIL T9
                  (no lateral → no spatial autocorrelation).
  SOM:            PASS T0-T5; UNCERTAIN T7 (depends on eta history),
                  LIKELY PASS T8 (eta decay protects), DEFINITELY PASS T9
                  (Gaussian neighbourhood = spatial autocorr by
                  construction).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.cognitive_map import (
    MapConfig, evaluate_holdout as cm_evaluate_holdout,
    initialise as cm_initialise, run as cm_run,
)
from world.flux.som_substrate import (
    SOMConfig, evaluate_holdout as som_evaluate_holdout,
    initialise as som_initialise, run as som_run,
)
from world.flux.harder_bar_metrics import (
    hist_kl_symmetric, shuffle_chunks_in_time, spatial_autocorrelation,
)

# Locked fixtures
N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
SHUFFLE_SEED = 11111
TARGET_RMS = 0.25
COG_MAP_BETA = 0.0

# T7/T8/T9 locked thresholds (pre-registered)
T7_RATIO_MAX = 0.10   # KL(S vs S_shuffled) < 0.10 * KL(S vs fresh)
T9_AUTOCORR_MIN = 0.3
T9_RATIO_MIN = 2.0    # autocorr_trained > 2 * autocorr_fresh

OUT_DIR = Path.home() / ".eqmod/bet/BET-009"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples: int, target_rms: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _load_audio():
    n_audio = N_TICKS * SAMPLES_PER_TICK
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
    return eng_a, eng_b, wn


def _state_field(state: dict, key: str) -> np.ndarray:
    """Return the substrate's learning field — mu for cog_map, w for SOM."""
    return state[key]


def _evaluate_substrate(name: str, cfg, initialise_fn, run_fn, holdout_fn,
                        eng_a: np.ndarray, eng_b: np.ndarray, wn: np.ndarray,
                        field_key: str, tick_offset_holdout: int) -> dict:
    """Run all training variants needed for T0..T9 against one substrate class."""
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_half = (N_TICKS // 2) * SAMPLES_PER_TICK

    # Initialisation
    state_init = initialise_fn(cfg)
    field_init = _state_field(state_init, field_key).copy()

    # Base trained substrates (used by T0-T5)
    state_eng = run_fn(cfg, N_TICKS, eng_a)
    state_wn = run_fn(cfg, N_TICKS, wn)
    state_neg = run_fn(cfg, N_TICKS, None)

    # Half-corpus (T3)
    state_eng_half = run_fn(cfg, N_TICKS // 2, eng_a[:n_half])
    state_wn_half = run_fn(cfg, N_TICKS // 2, wn[:n_half])

    # Retention (T5)
    if field_key == "mu":  # cog_map: copy mu/Lambda/N
        rest_seed_state = {
            "mu": state_eng["mu"].copy(),
            "Lambda": state_eng["Lambda"].copy(),
            "N": state_eng["N"].copy(),
        }
    else:  # SOM: copy w/N, share ii/jj/kk (precomputed grid)
        rest_seed_state = {
            "w": state_eng["w"].copy(),
            "N": state_eng["N"].copy(),
            "ii": state_eng["ii"],
            "jj": state_eng["jj"],
            "kk": state_eng["kk"],
        }
    state_eng_rest = run_fn(cfg, N_TICKS, None, state=rest_seed_state)

    # Holdout (T4)
    state_holdout_train = run_fn(cfg, N_TICKS // 2, eng_b[:n_half])
    if field_key == "mu":
        holdout = holdout_fn(state_holdout_train, eng_b[n_half:], cfg,
                             tick_offset=tick_offset_holdout)
    else:
        holdout = holdout_fn(state_holdout_train, eng_b[n_half:], cfg)

    # T7: chunk-shuffled training run
    eng_a_shuffled = shuffle_chunks_in_time(eng_a, SAMPLES_PER_TICK, SHUFFLE_SEED)
    state_eng_shuffled = run_fn(cfg, N_TICKS, eng_a_shuffled)

    # T8: continued training on WN after EN
    if field_key == "mu":
        ab_seed_state = {
            "mu": state_eng["mu"].copy(),
            "Lambda": state_eng["Lambda"].copy(),
            "N": state_eng["N"].copy(),
        }
    else:
        ab_seed_state = {
            "w": state_eng["w"].copy(),
            "N": state_eng["N"].copy(),
            "ii": state_eng["ii"],
            "jj": state_eng["jj"],
            "kk": state_eng["kk"],
        }
    state_AB = run_fn(cfg, N_TICKS, wn, state=ab_seed_state)

    # Extract fields
    field_eng = _state_field(state_eng, field_key)
    field_wn = _state_field(state_wn, field_key)
    field_neg = _state_field(state_neg, field_key)
    field_eng_half = _state_field(state_eng_half, field_key)
    field_wn_half = _state_field(state_wn_half, field_key)
    field_eng_rest = _state_field(state_eng_rest, field_key)
    field_eng_shuffled = _state_field(state_eng_shuffled, field_key)
    field_AB = _state_field(state_AB, field_key)

    # T0-T5 measurements
    t0_std = float(field_eng.std())
    kl_t1 = hist_kl_symmetric(field_init, field_eng)
    kl_t2 = hist_kl_symmetric(field_eng, field_wn)
    kl_t1_half = hist_kl_symmetric(field_init, field_eng_half)
    kl_t2_half = hist_kl_symmetric(field_eng_half, field_wn_half)
    kl_t1_rest = hist_kl_symmetric(field_init, field_eng_rest)
    kl_t2_rest = hist_kl_symmetric(field_eng_rest, field_wn)
    neg_kl = hist_kl_symmetric(field_neg, field_eng)

    t0_pass = t0_std > 0.05
    t1_pass = kl_t1 > 0.1
    t2_pass = kl_t2 > 0.1
    t3_pass = kl_t1_half > 0.1 and kl_t2_half > 0.1
    t4_pass = holdout["precision"] > 0.3
    t5_pass = (
        (kl_t1_rest / (kl_t1 + 1e-9) >= 0.5)
        and (kl_t2_rest / (kl_t2 + 1e-9) >= 0.5)
    )

    # T7: KL(S vs S_shuffled) < 0.10 * KL(S vs fresh)
    kl_t7_shuffled = hist_kl_symmetric(field_eng, field_eng_shuffled)
    kl_t7_fresh = hist_kl_symmetric(field_eng, field_init)
    t7_ratio = kl_t7_shuffled / (kl_t7_fresh + 1e-9)
    t7_pass = t7_ratio < T7_RATIO_MAX

    # T8: KL(S_AB vs fresh_EN) < KL(S_AB vs fresh_WN)
    kl_t8_to_en = hist_kl_symmetric(field_AB, field_eng)
    kl_t8_to_wn = hist_kl_symmetric(field_AB, field_wn)
    t8_pass = kl_t8_to_en < kl_t8_to_wn

    # T9: spatial autocorrelation
    autocorr_trained = spatial_autocorrelation(field_eng)
    autocorr_fresh = spatial_autocorrelation(field_init)
    t9_pass = (
        autocorr_trained > T9_AUTOCORR_MIN
        and autocorr_trained > T9_RATIO_MIN * max(autocorr_fresh, 1e-9)
    )

    all_locked = t0_pass and t1_pass and t2_pass and t3_pass and t4_pass and t5_pass
    all_harder = t7_pass and t8_pass and t9_pass
    all_ten = all_locked and all_harder

    return {
        "substrate": name,
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
        "T7_kl_shuffled": kl_t7_shuffled,
        "T7_kl_fresh": kl_t7_fresh,
        "T7_ratio": t7_ratio,
        "T7_threshold_max": T7_RATIO_MAX, "T7_pass": t7_pass,
        "T8_kl_AB_to_EN": kl_t8_to_en,
        "T8_kl_AB_to_WN": kl_t8_to_wn, "T8_pass": t8_pass,
        "T9_autocorr_trained": autocorr_trained,
        "T9_autocorr_fresh": autocorr_fresh,
        "T9_threshold_min": T9_AUTOCORR_MIN,
        "T9_ratio_threshold_min": T9_RATIO_MIN, "T9_pass": t9_pass,
        "neg_control_kl": neg_kl,
        "all_locked_T0_T5_pass": all_locked,
        "all_harder_T7_T9_pass": all_harder,
        "all_nine_pass": all_ten,
    }


def _write_result_json(verdict: str, per_substrate: list[dict], audio_meta: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-009",
        "verdict": verdict,
        "hypothesis": "Harder bar T0-T9 (T6 dropped): cog_map at beta=0 vs SOM through 9 tests including T7 (content vs position-artifacts), T8 (catastrophic-forgetting), T9 (spatial autocorrelation).",
        "thresholds": {
            "T0_spatial_std_min": 0.05,
            "T1_kl_min": 0.1, "T2_kl_min": 0.1, "T3_kl_min": 0.1,
            "T4_precision_min": 0.3, "T5_retention_min": 0.5,
            "T7_ratio_max": T7_RATIO_MAX,
            "T8_must_satisfy": "KL(AB,EN) < KL(AB,WN)",
            "T9_autocorr_min": T9_AUTOCORR_MIN, "T9_ratio_min": T9_RATIO_MIN,
        },
        "audio": audio_meta,
        "per_substrate": per_substrate,
        "winning_substrates": [s["substrate"] for s in per_substrate if s["all_nine_pass"]],
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))


@pytest.fixture(scope="module")
def harder_bar():
    eng_a, eng_b, wn = _load_audio()
    audio_meta = {
        "source": "R-7 corpus (manifest)",
        "n_samples_per_class": N_TICKS * SAMPLES_PER_TICK,
        "wn_seed": WN_SEED, "shuffle_seed": SHUFFLE_SEED,
        "target_rms": TARGET_RMS,
    }

    # cog_map beta=0
    cm_cfg = MapConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, beta_lateral=COG_MAP_BETA,
    )
    cm_result = _evaluate_substrate(
        name="cog_map_beta_0", cfg=cm_cfg,
        initialise_fn=cm_initialise, run_fn=cm_run,
        holdout_fn=cm_evaluate_holdout,
        eng_a=eng_a, eng_b=eng_b, wn=wn,
        field_key="mu", tick_offset_holdout=N_TICKS // 2,
    )

    # SOM
    som_cfg = SOMConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    som_result = _evaluate_substrate(
        name="som", cfg=som_cfg,
        initialise_fn=som_initialise, run_fn=som_run,
        holdout_fn=som_evaluate_holdout,
        eng_a=eng_a, eng_b=eng_b, wn=wn,
        field_key="w", tick_offset_holdout=0,
    )

    per_substrate = [cm_result, som_result]
    any_nine = any(s["all_nine_pass"] for s in per_substrate)
    return {"per_substrate": per_substrate, "any_nine_pass": any_nine, "audio_meta": audio_meta}


def test_any_substrate_passes_T0_to_T9(harder_bar):
    """Harder-bar bet WIN: ANY substrate satisfies T0-T9 simultaneously."""
    per = harder_bar["per_substrate"]
    if not harder_bar["any_nine_pass"]:
        lines = []
        for s in per:
            t_summary = ", ".join([
                f"T0={s['T0_pass']}", f"T1={s['T1_pass']}", f"T2={s['T2_pass']}",
                f"T3={s['T3_pass']}", f"T4={s['T4_pass']}", f"T5={s['T5_pass']}",
                f"T7={s['T7_pass']} (ratio={s['T7_ratio']:.4f})",
                f"T8={s['T8_pass']} (AB→EN={s['T8_kl_AB_to_EN']:.4f}, AB→WN={s['T8_kl_AB_to_WN']:.4f})",
                f"T9={s['T9_pass']} (autocorr={s['T9_autocorr_trained']:.4f})",
            ])
            lines.append(f"  {s['substrate']}: {t_summary}")
        pytest.fail(
            "BET-009 NULL: no substrate satisfies T0-T9 simultaneously.\n"
            + "\n".join(lines)
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(harder_bar):
    yield
    verdict = "passed" if harder_bar["any_nine_pass"] else "null"
    _write_result_json(verdict, harder_bar["per_substrate"], harder_bar["audio_meta"])

"""BET-012 — SOM with pseudo-rehearsal replay (Robins 1995).

Pre-reg LOGBOOK 2026-05-23 ~21:35. After BET-011 (SOM-saturating) failed
T8 due to too few cells reaching saturation, this iteration attacks T8
through a different self-determined-consolidation mechanism: internal
replay of recent inputs.

Buffer size locked at K=10000 = N_TICKS so EN inputs survive through
the entire WN training phase. Replay rate 1.0 means one replay update
per wake update — substrate sees its own past as often as new inputs.

T0-T9 bar same as BET-009/010/011 (locked since LOGBOOK 2026-05-23 ~20:55).

Pre-data prediction:
  T0-T5: PASS (SOM baseline + replay reinforces same structure)
  T7: PASS (content-driven, chunk-shuffling preserved by buffer
      because final state depends on multiset of inputs not order)
  T8 (THE CRITICAL TEST): PASS expected. During 10k WN wake-training,
      the buffer still contains the 10k EN inputs (FIFO, K=N_TICKS).
      Replay during WN-phase continuously reinforces EN-cells.
      Effective per-class exposure: ≈15k EN-style + ≈15k WN-style
      updates. S_AB should be roughly balanced between EN and WN
      patterns — but per the BET-010 diagnostic, histogram-KL on the
      WHOLE-FIELD is biased by WN's flat-spectrum spread. The test is:
      does replay swing the bias back toward EN?
  T9: PASS (Gaussian neighbourhood update gives spatial autocorr).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import (
    SOMReplayConfig, evaluate_holdout, initialise, run,
)
from world.flux.harder_bar_metrics import (
    hist_kl_symmetric, shuffle_chunks_in_time, spatial_autocorrelation,
)

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
SHUFFLE_SEED = 11111
TARGET_RMS = 0.25

T7_RATIO_MAX = 0.10
T9_AUTOCORR_MIN = 0.3
T9_RATIO_MIN = 2.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-012"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _write_result_json(verdict, m, audio_meta):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-012",
        "verdict": verdict,
        "hypothesis": "SOM with pseudo-rehearsal replay buffer (K=10000, rate=1.0). Robins 1995 mechanism for catastrophic-forgetting resistance via self-managed buffer of past inputs.",
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


def _copy_state(state):
    return {
        "w": state["w"].copy(),
        "N": state["N"].copy(),
        "ii": state["ii"],
        "jj": state["jj"],
        "kk": state["kk"],
        "buffer": state["buffer"].copy(),
        "buffer_head": state["buffer_head"],
        "buffer_fill": state["buffer_fill"],
        "global_tick": state["global_tick"],
    }


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_half = (N_TICKS // 2) * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if 2 * n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_a = full[:n_audio].astype(np.float64)
    eng_b = full[n_audio:2 * n_audio].astype(np.float64)
    wn = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)
    audio_meta = {
        "source": "R-7 corpus (manifest)",
        "n_samples_per_class": n_audio,
        "wn_seed": WN_SEED, "shuffle_seed": SHUFFLE_SEED,
        "target_rms": TARGET_RMS,
        "buffer_size": cfg.buffer_size, "replay_rate": cfg.replay_rate,
    }

    state_init = initialise(cfg)
    field_init = state_init["w"].copy()

    state_eng = run(cfg, N_TICKS, eng_a)
    state_wn = run(cfg, N_TICKS, wn)
    state_neg = run(cfg, N_TICKS, None)

    state_eng_half = run(cfg, N_TICKS // 2, eng_a[:n_half])
    state_wn_half = run(cfg, N_TICKS // 2, wn[:n_half])

    state_eng_rest = run(cfg, N_TICKS, None, state=_copy_state(state_eng))

    state_holdout_train = run(cfg, N_TICKS // 2, eng_b[:n_half])
    holdout = evaluate_holdout(state_holdout_train, eng_b[n_half:], cfg)

    eng_a_shuffled = shuffle_chunks_in_time(eng_a, SAMPLES_PER_TICK, SHUFFLE_SEED)
    state_eng_shuffled = run(cfg, N_TICKS, eng_a_shuffled)

    state_AB = run(cfg, N_TICKS, wn, state=_copy_state(state_eng))

    return dict(
        cfg=cfg, audio_meta=audio_meta, field_init=field_init,
        state_eng=state_eng, state_wn=state_wn, state_neg=state_neg,
        state_eng_half=state_eng_half, state_wn_half=state_wn_half,
        state_eng_rest=state_eng_rest,
        state_eng_shuffled=state_eng_shuffled, state_AB=state_AB,
        holdout=holdout,
    )


def _compute_all(sub):
    field_init = sub["field_init"]
    field_eng = sub["state_eng"]["w"]
    field_wn = sub["state_wn"]["w"]
    field_neg = sub["state_neg"]["w"]
    field_eng_half = sub["state_eng_half"]["w"]
    field_wn_half = sub["state_wn_half"]["w"]
    field_eng_rest = sub["state_eng_rest"]["w"]
    field_eng_shuffled = sub["state_eng_shuffled"]["w"]
    field_AB = sub["state_AB"]["w"]
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
    all_nine = all([t0_pass, t1_pass, t2_pass, t3_pass, t4_pass, t5_pass, t7_pass, t8_pass, t9_pass])

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
        "buffer_fill_after_EN": int(sub["state_eng"]["buffer_fill"]),
        "buffer_fill_after_AB": int(sub["state_AB"]["buffer_fill"]),
        "all_nine_pass": all_nine,
    }


def test_som_replay_passes_T0_to_T9(substrates):
    m = _compute_all(substrates)
    if not m["all_nine_pass"]:
        summary = (
            f"T0={m['T0_pass']} T1={m['T1_pass']} T2={m['T2_pass']} "
            f"T3={m['T3_pass']} T4={m['T4_pass']} T5={m['T5_pass']} "
            f"T7={m['T7_pass']} (ratio={m['T7_ratio']:.4f}) "
            f"T8={m['T8_pass']} (AB→EN={m['T8_kl_AB_to_EN']:.4f}, AB→WN={m['T8_kl_AB_to_WN']:.4f}) "
            f"T9={m['T9_pass']} (autocorr={m['T9_autocorr_trained']:.4f})"
        )
        pytest.fail(f"BET-012 NULL: SOM-replay does not pass T0-T9. {summary}")


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _compute_all(substrates)
    verdict = "passed" if m["all_nine_pass"] else "null"
    _write_result_json(verdict, m, substrates["audio_meta"])

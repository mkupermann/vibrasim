"""BET-013 — LR validation of BET-012's SOM+replay PASS verdict.

After BET-012 PASSED 9/9 at 10k ticks per class, LR validation tests
whether the harder-bar WIN survives a 10× scale-up (N_TICKS = 100_000
per class).

Locked parameters identical to BET-012 (NO retuning). Buffer K=10000
remains constant — at 100k ticks, the buffer turns over 10x, so the
substrate explicitly does NOT preserve all old inputs. The test is
whether the substrate's mechanism still satisfies T0-T9 at scale.

Pre-data prediction:
  T0-T5: PASS (more cells visited, structure grows).
  T7: PASS (content-driven update + buffer still rotates the same way).
  T8: UNCERTAIN at scale. Two effects compete:
       (a) Buffer is smaller relative to N_TICKS (10k of 100k = 10%),
           so EN inputs evict early in the WN phase — less continuous
           EN reinforcement during WN.
       (b) eta decays to ~zero before WN phase begins (eta_decay_tau=5000
           but global_tick=200k after EN with replay), so WN has near-
           zero effect on weights regardless. This favors EN preservation
           trivially.
       Net prediction: T8 likely PASS but for the eta-decay-saturation
       reason more than for the buffer-replay reason. Honest interpretation
       is: at scale, the substrate has frozen by the time WN training
       starts.
  T9: PASS (spatial autocorrelation builds in early SOM phase).

If BET-013 PASSES 9/9 at scale, the harder-bar WIN is confirmed at
100× the BET-012 scale. If T8 fails at scale, the BET-012 result was
small-scale artifact — buffer needs to scale with N_TICKS.
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

N_TICKS = 100_000   # 10× BET-012 scale-up
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
SHUFFLE_SEED = 11111
TARGET_RMS = 0.25

T7_RATIO_MAX = 0.10
T9_AUTOCORR_MIN = 0.3
T9_RATIO_MIN = 2.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-013"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _write_result_json(verdict, m, audio_meta):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-013",
        "verdict": verdict,
        "hypothesis": "10x LR validation of BET-012 SOM+replay 9/9 PASS at harder bar. Same locked params, N_TICKS=100000 per class.",
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
        raise RuntimeError(
            f"R-7 corpus too short for BET-013: need {2 * n_audio}, have {full.shape[0]}"
        )
    eng_a = full[:n_audio].astype(np.float64)
    eng_b = full[n_audio:2 * n_audio].astype(np.float64)
    wn = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)
    audio_meta = {
        "source": "R-7 corpus (manifest)",
        "n_samples_per_class": n_audio,
        "wn_seed": WN_SEED, "shuffle_seed": SHUFFLE_SEED,
        "target_rms": TARGET_RMS,
        "buffer_size": cfg.buffer_size, "replay_rate": cfg.replay_rate,
        "n_ticks": N_TICKS,
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
    f_init = sub["field_init"]
    f_eng = sub["state_eng"]["w"]
    f_wn = sub["state_wn"]["w"]
    f_neg = sub["state_neg"]["w"]
    f_eng_half = sub["state_eng_half"]["w"]
    f_wn_half = sub["state_wn_half"]["w"]
    f_eng_rest = sub["state_eng_rest"]["w"]
    f_eng_shuffled = sub["state_eng_shuffled"]["w"]
    f_AB = sub["state_AB"]["w"]
    holdout = sub["holdout"]

    t0_std = float(f_eng.std())
    kl_t1 = hist_kl_symmetric(f_init, f_eng)
    kl_t2 = hist_kl_symmetric(f_eng, f_wn)
    kl_t1_half = hist_kl_symmetric(f_init, f_eng_half)
    kl_t2_half = hist_kl_symmetric(f_eng_half, f_wn_half)
    kl_t1_rest = hist_kl_symmetric(f_init, f_eng_rest)
    kl_t2_rest = hist_kl_symmetric(f_eng_rest, f_wn)
    neg_kl = hist_kl_symmetric(f_neg, f_eng)
    kl_t7_shuffled = hist_kl_symmetric(f_eng, f_eng_shuffled)
    kl_t7_fresh = hist_kl_symmetric(f_eng, f_init)
    t7_ratio = kl_t7_shuffled / (kl_t7_fresh + 1e-9)
    kl_t8_en = hist_kl_symmetric(f_AB, f_eng)
    kl_t8_wn = hist_kl_symmetric(f_AB, f_wn)
    autocorr_tr = spatial_autocorrelation(f_eng)
    autocorr_fr = spatial_autocorrelation(f_init)

    t0p = t0_std > 0.05
    t1p = kl_t1 > 0.1
    t2p = kl_t2 > 0.1
    t3p = kl_t1_half > 0.1 and kl_t2_half > 0.1
    t4p = holdout["precision"] > 0.3
    t5p = (kl_t1_rest / (kl_t1 + 1e-9) >= 0.5) and (kl_t2_rest / (kl_t2 + 1e-9) >= 0.5)
    t7p = t7_ratio < T7_RATIO_MAX
    t8p = kl_t8_en < kl_t8_wn
    t9p = autocorr_tr > T9_AUTOCORR_MIN and autocorr_tr > T9_RATIO_MIN * max(autocorr_fr, 1e-9)
    all_pass = all([t0p, t1p, t2p, t3p, t4p, t5p, t7p, t8p, t9p])

    return {
        "n_ticks": N_TICKS,
        "T0_spatial_std": t0_std, "T0_pass": t0p,
        "T1_kl_init_vs_eng": kl_t1, "T1_pass": t1p,
        "T2_kl_eng_vs_wn": kl_t2, "T2_pass": t2p,
        "T3_kl_init_vs_eng_half": kl_t1_half,
        "T3_kl_eng_vs_wn_half": kl_t2_half, "T3_pass": t3p,
        "T4_holdout_precision": holdout["precision"],
        "T4_holdout_mean_cosine": holdout["mean_cosine"],
        "T4_holdout_n": holdout["n"], "T4_pass": t4p,
        "T5_t1_retention": kl_t1_rest / (kl_t1 + 1e-9),
        "T5_t2_retention": kl_t2_rest / (kl_t2 + 1e-9), "T5_pass": t5p,
        "T7_kl_shuffled": kl_t7_shuffled, "T7_kl_fresh": kl_t7_fresh,
        "T7_ratio": t7_ratio, "T7_pass": t7p,
        "T8_kl_AB_to_EN": kl_t8_en, "T8_kl_AB_to_WN": kl_t8_wn, "T8_pass": t8p,
        "T9_autocorr_trained": autocorr_tr,
        "T9_autocorr_fresh": autocorr_fr, "T9_pass": t9p,
        "neg_control_kl": neg_kl,
        "buffer_fill_after_EN": int(sub["state_eng"]["buffer_fill"]),
        "buffer_fill_after_AB": int(sub["state_AB"]["buffer_fill"]),
        "all_nine_pass": all_pass,
    }


def test_lr_passes_T0_to_T9(substrates):
    m = _compute_all(substrates)
    if not m["all_nine_pass"]:
        summary = (
            f"T0={m['T0_pass']} T1={m['T1_pass']} T2={m['T2_pass']} "
            f"T3={m['T3_pass']} T4={m['T4_pass']} T5={m['T5_pass']} "
            f"T7={m['T7_pass']} (ratio={m['T7_ratio']:.4f}) "
            f"T8={m['T8_pass']} (AB→EN={m['T8_kl_AB_to_EN']:.6f}, AB→WN={m['T8_kl_AB_to_WN']:.4f}) "
            f"T9={m['T9_pass']} (autocorr={m['T9_autocorr_trained']:.4f})"
        )
        pytest.fail(f"BET-013 NULL at scale: {summary}")


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _compute_all(substrates)
    verdict = "passed" if m["all_nine_pass"] else "null"
    _write_result_json(verdict, m, substrates["audio_meta"])

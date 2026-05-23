"""BET-014 — Disentanglement ablation: SOM without replay, eta_decay halved.

BET-012/013 PASSED 9/9 via combined mechanism: pseudo-rehearsal + eta-decay
acceleration from doubled global_tick. BET-007 (plain SOM, no replay,
eta_decay_tau=5000) FAILED T8 with AB→EN=1.73.

This iteration isolates the eta-decay contribution: SOM with NO replay
buffer + eta_decay_tau=2500 (half of BET-007's 5000). This produces
the SAME eta range during WN-phase as BET-012 had under replay-doubled
global_tick:

  BET-012 (replay rate 1.0, tau=5000): eta at WN-start = exp(-4) = 0.018
  BET-014 (no replay,         tau=2500): eta at WN-start = exp(-4) = 0.018

If BET-014 PASSES T8 → eta-decay timing alone is sufficient; pseudo-
rehearsal was incidental to the BET-012 PASS.

If BET-014 FAILS T8 → pseudo-rehearsal was essential; eta-decay alone
does not suffice. BET-012's WIN was a genuine replay-mechanism finding.

All other parameters locked at BET-007 baseline. T0-T9 bar locked from
LOGBOOK 2026-05-23 ~20:55.
"""
from __future__ import annotations

import json
from dataclasses import replace as dc_replace
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_substrate import (
    SOMConfig, evaluate_holdout, initialise, run,
)
from world.flux.harder_bar_metrics import (
    hist_kl_symmetric, shuffle_chunks_in_time, spatial_autocorrelation,
)

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
ETA_DECAY_TAU = 2500.0   # HALF of BET-007's 5000 — matches BET-012's effective tau
WN_SEED = 9999
SHUFFLE_SEED = 11111
TARGET_RMS = 0.25

T7_RATIO_MAX = 0.10
T9_AUTOCORR_MIN = 0.3
T9_RATIO_MIN = 2.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-014"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _write_result_json(verdict, m, audio_meta):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-014",
        "verdict": verdict,
        "hypothesis": "Disentanglement: SOM with no replay buffer + eta_decay_tau=2500 (halved). Tests whether BET-012's T8 PASS was due to eta-decay timing alone, or due to pseudo-rehearsal replay mechanism.",
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
    }


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
        eta_decay_tau=ETA_DECAY_TAU,   # 2500, half of default 5000
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
        "eta_decay_tau": ETA_DECAY_TAU,
        "ablation_arm": "no_replay_halved_eta_decay",
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
        "ablation_arm": "no_replay_halved_eta_decay",
        "eta_decay_tau": ETA_DECAY_TAU,
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
        "all_nine_pass": all_pass,
    }


def test_disentanglement(substrates):
    """Reports T0-T9 for SOM with halved eta-decay tau, no replay.

    Verdict semantics in result.json (not just this test):
      passed = all 9 pass → eta-decay-alone is sufficient (replay incidental)
      null   = at least one fail → replay was essential to BET-012 PASS
    """
    m = _compute_all(substrates)
    # Report and write result regardless; let dispatcher/operator interpret
    if not m["all_nine_pass"]:
        # Soft-fail: the disentanglement IS the result. Pytest fail conveys
        # "no_replay_arm does not pass alone → replay is essential to BET-012"
        summary = (
            f"T0={m['T0_pass']} T1={m['T1_pass']} T2={m['T2_pass']} "
            f"T3={m['T3_pass']} T4={m['T4_pass']} T5={m['T5_pass']} "
            f"T7={m['T7_pass']} T8={m['T8_pass']} "
            f"(AB→EN={m['T8_kl_AB_to_EN']:.6f}, AB→WN={m['T8_kl_AB_to_WN']:.4f}) "
            f"T9={m['T9_pass']}"
        )
        pytest.fail(
            f"BET-014 NULL: no-replay+halved-eta-decay does not pass T0-T9. "
            f"Interpretation: replay was essential to BET-012's T8 PASS. {summary}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _compute_all(substrates)
    verdict = "passed" if m["all_nine_pass"] else "null"
    _write_result_json(verdict, m, substrates["audio_meta"])

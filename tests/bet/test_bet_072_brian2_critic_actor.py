"""BET-072 — T56 Brian2 critic-actor R-STDP.

Frémaux-Gerstner 2016 architecture. Fixes BET-067 NULL by:
  - Eligibility traces per synapse (decay τ=500ms)
  - Critic population estimates value V(s)
  - TD = reward - V_estimate drives actor plasticity
  - Only synapses with non-zero eligibility AND matching pre·post
    causality receive TD-modulated update

T56 bar (LOCKED): balanced accuracy on actor-vote > 0.7
  (chance 0.5; bar matches BET-067 retry threshold).

Additional report-only metrics:
  - critic-estimate first-50 vs last-50: should rise (critic learns)
  - TD-history first-50 vs last-50: should shrink (predictions sharpen)
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pytest

warnings.filterwarnings('ignore')

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.brian2_critic_actor import Brian2CriticActorConfig, train_and_test

N_TRAIN_PER_CLASS = 100
N_TEST_PER_CLASS = 30
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T56_BALANCED_ACC_MIN = 0.7

OUT_DIR = Path.home() / ".eqmod/bet/BET-072"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


@pytest.fixture(scope="module")
def substrates():
    class _Cfg:
        n_features = N_FEATURES
        fft_bands = FFT_BANDS
        samples_per_tick = SAMPLES_PER_TICK
    encoder_cfg = _Cfg()

    n_train = N_TRAIN_PER_CLASS * SAMPLES_PER_TICK
    n_test = N_TEST_PER_CLASS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_train + n_test > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_train].astype(np.float64)
    eng_test = full[n_train:n_train + n_test].astype(np.float64)
    wn_train = _make_wn(n_train, TARGET_RMS, WN_SEED)
    wn_test = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)

    def chunks(audio, n):
        return [audio[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK] for k in range(n)]

    train_dict = {0: chunks(eng_train, N_TRAIN_PER_CLASS),
                  1: chunks(wn_train, N_TRAIN_PER_CLASS)}
    test_dict = {0: chunks(eng_test, N_TEST_PER_CLASS),
                 1: chunks(wn_test, N_TEST_PER_CLASS)}

    cfg = Brian2CriticActorConfig(chunk_duration_ms=100.0)
    return train_and_test(train_dict, test_dict, encoder_cfg,
                          N_TRAIN_PER_CLASS, N_TEST_PER_CLASS, cfg)


def _verdict(s):
    return {**s, "T56_pass": s["balanced_accuracy"] > T56_BALANCED_ACC_MIN}


def test_T56(substrates):
    m = _verdict(substrates)
    if not m["T56_pass"]:
        pytest.fail(
            f"BET-072 NULL T56 critic-actor R-STDP.\n"
            f"  balanced accuracy: {m['balanced_accuracy']:.4f} "
            f"(need > {T56_BALANCED_ACC_MIN})\n"
            f"  per-class: {m['accuracies']}\n"
            f"  train early/late acc: {m['train_early_accuracy']:.3f} -> {m['train_late_accuracy']:.3f}\n"
            f"  critic estimate first/last 50: {m['critic_estimate_first_50']:.3f} -> {m['critic_estimate_last_50']:.3f}\n"
            f"  TD first/last 50: {m['td_history_mean_first_50']:.3f} -> {m['td_history_mean_last_50']:.3f}\n"
            f"  confusion: {m['confusion_matrix']}\n"
            f"  W hidden→actor: {m['final_W_hidden_actor_mean']:.3f} ± {m['final_W_hidden_actor_std']:.3f}\n"
            f"  W hidden→critic: {m['final_W_hidden_critic_mean']:.3f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T56_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-072",
        "verdict": verdict,
        "hypothesis": "T56 Brian2 critic-actor R-STDP. Frémaux-Gerstner 2016 architecture. Eligibility traces + critic-estimated value + TD-modulated actor plasticity. Fixes BET-067 credit-assignment NULL. Bar: balanced accuracy > 0.7.",
        "thresholds": {"T56_balanced_accuracy_min": T56_BALANCED_ACC_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

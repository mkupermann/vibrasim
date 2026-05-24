"""BET-067 — T51 Brian2 R-STDP (reward-modulated brain-faithful).

After BET-065 unsupervised brain-faithful PASS (98%), add agency:
substrate has dopamine-like reward signal. Eligibility traces accumulate
during STDP. Reward modulates weight updates.

T51 bar (LOCKED): readout-vote accuracy > 0.7.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pytest

warnings.filterwarnings('ignore')

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.brian2_rstdp import Brian2RSTDPConfig, train_and_test

N_TRAIN_PER_CLASS = 100
N_TEST_PER_CLASS = 30
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T51_ACCURACY_MIN = 0.7

OUT_DIR = Path.home() / ".eqmod/bet/BET-067"
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

    def _chunks(audio, n):
        return [audio[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK] for k in range(n)]

    train_dict = {0: _chunks(eng_train, N_TRAIN_PER_CLASS),
                  1: _chunks(wn_train, N_TRAIN_PER_CLASS)}
    test_dict = {0: _chunks(eng_test, N_TEST_PER_CLASS),
                 1: _chunks(wn_test, N_TEST_PER_CLASS)}

    cfg = Brian2RSTDPConfig(chunk_duration_ms=100.0)
    result = train_and_test(
        train_dict, test_dict, encoder_cfg,
        N_TRAIN_PER_CLASS, N_TEST_PER_CLASS, cfg,
    )

    acc_en = result["accuracies"].get(0, 0.0)
    acc_wn = result["accuracies"].get(1, 0.0)
    balanced = (acc_en + acc_wn) / 2

    return dict(
        train_late_accuracy=result["train_late_accuracy"],
        accuracy_en=acc_en, accuracy_wn=acc_wn,
        balanced_accuracy=balanced,
        final_W_mean=result["final_W_hidden_readout_mean"],
        final_W_std=result["final_W_hidden_readout_std"],
        total_hidden_spikes=result["total_hidden_spikes"],
        total_readout_spikes=result["total_readout_spikes"],
    )


def _verdict(s):
    return {**s, "T51_pass": s["balanced_accuracy"] > T51_ACCURACY_MIN}


def test_T51(substrates):
    m = _verdict(substrates)
    if not m["T51_pass"]:
        pytest.fail(
            f"BET-067 NULL T51 Brian2 R-STDP.\n"
            f"  train late acc: {m['train_late_accuracy']:.4f}\n"
            f"  test acc_en: {m['accuracy_en']:.4f}, acc_wn: {m['accuracy_wn']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} (need > {T51_ACCURACY_MIN})\n"
            f"  hidden spikes: {m['total_hidden_spikes']}\n"
            f"  readout spikes: {m['total_readout_spikes']}\n"
            f"  W h→r mean: {m['final_W_mean']:.4f}, std: {m['final_W_std']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T51_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-067",
        "verdict": verdict,
        "hypothesis": "T51 Brian2 R-STDP brain-faithful substrate with reward (agency). Substrate learns class-specific readout via dopamine-modulated STDP. Bar: readout-vote acc > 0.7.",
        "thresholds": {"T51_accuracy_min": T51_ACCURACY_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

"""BET-064 — T48 Liquid State Machine (Maass 2002).

Last brain-faithful attempt in current budget. Reservoir of Izhikevich
spiking neurons (fixed recurrent connectivity, no STDP) + simple
linear readout via ridge regression. Avoids STDP-tuning-hell.

Substrate is spiking (brain-faithful) but readout is admitted to be
LLM-family-adjacent (linear regression on spike rates). Compromise.

T48 bar (LOCKED): balanced 2-class accuracy on held-out > 0.6.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.izhikevich_rstdp import IzhikevichRSTDPConfig, initialise, step
from world.flux.cognitive_map import encode_sensor

N_TRAIN_PER_CLASS = 500
N_TEST_PER_CLASS = 100
CHUNK_DURATION_MS = 50
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T48_ACCURACY_MIN = 0.6

OUT_DIR = Path.home() / ".eqmod/bet/BET-064"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _features_to_input(features, n_input):
    inp = np.zeros(n_input, dtype=np.float64)
    n = min(features.size, n_input)
    inp[:n] = np.clip(features[:n], 0, 1)
    return inp


def _present_chunk_get_spike_pattern(state, audio_chunk, cfg_enc):
    """Present chunk, return reservoir spike-count vector (hidden + output layers)."""
    izhi_cfg = state["cfg"]
    features = encode_sensor(audio_chunk, cfg_enc)
    input_current = _features_to_input(features, state["n_in"])
    # Sample hidden+output spike counts for the chunk duration
    h_idx = state["hidden_idx"]
    o_idx = state["output_idx"]
    pattern = np.zeros(len(h_idx) + len(o_idx), dtype=np.int64)
    n_steps = int(CHUNK_DURATION_MS / izhi_cfg.dt_ms)
    for _ in range(n_steps):
        spikes = step(state, input_current, reward=0.0)
        pattern[:len(h_idx)] += spikes[h_idx].astype(np.int64)
        pattern[len(h_idx):] += spikes[o_idx].astype(np.int64)
    return pattern


@pytest.fixture(scope="module")
def substrates():
    izhi_cfg = IzhikevichRSTDPConfig()

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

    state = initialise(izhi_cfg)

    # Collect spike patterns for training (no STDP — fixed reservoir, just record activity)
    # Disable STDP by zeroing eligibility accumulation: we can just NOT call reward
    train_patterns = []
    train_labels = []
    for trial in range(N_TRAIN_PER_CLASS):
        en_chunk = eng_train[trial * SAMPLES_PER_TICK:(trial + 1) * SAMPLES_PER_TICK]
        if en_chunk.size > 0:
            train_patterns.append(_present_chunk_get_spike_pattern(state, en_chunk, encoder_cfg))
            train_labels.append(0)
        wn_chunk = wn_train[trial * SAMPLES_PER_TICK:(trial + 1) * SAMPLES_PER_TICK]
        if wn_chunk.size > 0:
            train_patterns.append(_present_chunk_get_spike_pattern(state, wn_chunk, encoder_cfg))
            train_labels.append(1)
    train_patterns = np.array(train_patterns, dtype=np.float64)
    train_labels = np.array(train_labels, dtype=np.int64)

    # Test patterns
    test_patterns = []
    test_labels = []
    for k in range(N_TEST_PER_CLASS):
        chunk = eng_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        test_patterns.append(_present_chunk_get_spike_pattern(state, chunk, encoder_cfg))
        test_labels.append(0)
        chunk = wn_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        test_patterns.append(_present_chunk_get_spike_pattern(state, chunk, encoder_cfg))
        test_labels.append(1)
    test_patterns = np.array(test_patterns, dtype=np.float64)
    test_labels = np.array(test_labels, dtype=np.int64)

    # Ridge regression linear readout: train W_out on train_patterns→train_labels (one-hot)
    n_classes = 2
    y_train = np.eye(n_classes)[train_labels]  # one-hot
    ridge = 1.0
    XtX = train_patterns.T @ train_patterns + ridge * np.eye(train_patterns.shape[1])
    XtY = train_patterns.T @ y_train
    W_out = np.linalg.solve(XtX, XtY)

    # Predict
    train_preds = (train_patterns @ W_out).argmax(axis=1)
    test_preds = (test_patterns @ W_out).argmax(axis=1)
    train_acc = float((train_preds == train_labels).mean())
    test_acc_en = float((test_preds[test_labels == 0] == 0).mean())
    test_acc_wn = float((test_preds[test_labels == 1] == 1).mean())
    balanced = (test_acc_en + test_acc_wn) / 2

    return dict(
        n_reservoir=train_patterns.shape[1],
        train_accuracy=train_acc,
        test_accuracy_en=test_acc_en,
        test_accuracy_wn=test_acc_wn,
        balanced_accuracy=balanced,
        active_neurons=int((state["spike_history"] > 0).sum()),
        total_neurons=state["n_total"],
        train_pattern_mean=float(train_patterns.mean()),
        train_pattern_std=float(train_patterns.std()),
    )


def _verdict(s):
    return {**s, "T48_pass": s["balanced_accuracy"] > T48_ACCURACY_MIN}


def test_T48(substrates):
    m = _verdict(substrates)
    if not m["T48_pass"]:
        pytest.fail(
            f"BET-064 NULL T48 LSM.\n"
            f"  train acc: {m['train_accuracy']:.4f}\n"
            f"  test acc_en: {m['test_accuracy_en']:.4f}, acc_wn: {m['test_accuracy_wn']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} (need > {T48_ACCURACY_MIN})\n"
            f"  active: {m['active_neurons']}/{m['total_neurons']}\n"
            f"  pattern mean: {m['train_pattern_mean']:.4f}, std: {m['train_pattern_std']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T48_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-064",
        "verdict": verdict,
        "hypothesis": "T48 Liquid State Machine (Maass 2002). Reservoir of Izhikevich spiking neurons + linear ridge-regression readout. Avoids STDP tuning. Substrate-spiking, readout-statistical compromise. Bar: balanced 2-class > 0.6.",
        "thresholds": {"T48_accuracy_min": T48_ACCURACY_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

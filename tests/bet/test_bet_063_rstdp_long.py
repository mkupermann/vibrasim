"""BET-063 — T47 R-STDP with much longer training + continuous reward.

After BET-061 (collapse) and BET-062 (death) NULLs: try longer training
schedule + softer (graded continuous) reward instead of binary ±1
single-pulse.

50x more training: 5000 trials per class (10000 total). Reward
delivered continuously based on output-difference magnitude.

T47 bar (LOCKED): balanced 2-class acc > 0.6 on held-out.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.izhikevich_rstdp import IzhikevichRSTDPConfig, initialise, step
from world.flux.cognitive_map import encode_sensor

N_TRAIN_PER_CLASS = 5000   # 50x BET-061
N_TEST_PER_CLASS = 100
CHUNK_DURATION_MS = 30     # shorter chunk = more variety
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T47_ACCURACY_MIN = 0.6

OUT_DIR = Path.home() / ".eqmod/bet/BET-063"
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


def _present_and_classify(state, audio_chunk, cfg_enc, true_class=None,
                          continuous_reward=False):
    """Present chunk, optionally deliver graded reward.
    Returns (winner_class, output_spikes)."""
    izhi_cfg = state["cfg"]
    features = encode_sensor(audio_chunk, cfg_enc)
    input_current = _features_to_input(features, state["n_in"])
    o_idx = state["output_idx"]
    output_count = np.zeros(state["n_o"], dtype=np.int64)
    for _ in range(int(CHUNK_DURATION_MS / izhi_cfg.dt_ms)):
        spikes = step(state, input_current, reward=0.0)
        output_count += spikes[o_idx].astype(np.int64)
    winner = int(np.argmax(output_count))
    # Continuous reward proportional to confidence (output difference)
    if true_class is not None and continuous_reward:
        diff = float(output_count[true_class] - output_count[1 - true_class])
        # Normalize to [-1, +1] reward
        max_diff = max(int(output_count.max()), 1)
        reward = float(np.clip(diff / max_diff, -1, 1)) * 0.5
        # Deliver reward as single pulse
        step(state, input_current, reward=reward)
    return winner, output_count


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

    # Train with continuous reward shaping
    train_history = []
    for trial in range(N_TRAIN_PER_CLASS):
        en_chunk = eng_train[trial * SAMPLES_PER_TICK:(trial + 1) * SAMPLES_PER_TICK]
        if en_chunk.size > 0:
            winner, _ = _present_and_classify(state, en_chunk, encoder_cfg,
                                               true_class=0, continuous_reward=True)
            train_history.append(winner == 0)
        wn_chunk = wn_train[trial * SAMPLES_PER_TICK:(trial + 1) * SAMPLES_PER_TICK]
        if wn_chunk.size > 0:
            winner, _ = _present_and_classify(state, wn_chunk, encoder_cfg,
                                               true_class=1, continuous_reward=True)
            train_history.append(winner == 1)

    train_acc_late = sum(train_history[-200:]) / 200 if len(train_history) >= 200 else 0.0

    # Test
    correct_en = 0
    total_en = 0
    for k in range(N_TEST_PER_CLASS):
        chunk = eng_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        winner, _ = _present_and_classify(state, chunk, encoder_cfg)
        if winner == 0:
            correct_en += 1
        total_en += 1
    correct_wn = 0
    total_wn = 0
    for k in range(N_TEST_PER_CLASS):
        chunk = wn_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        winner, _ = _present_and_classify(state, chunk, encoder_cfg)
        if winner == 1:
            correct_wn += 1
        total_wn += 1

    acc_en = correct_en / max(total_en, 1)
    acc_wn = correct_wn / max(total_wn, 1)
    balanced = (acc_en + acc_wn) / 2

    return dict(
        n_total=state["n_total"],
        n_train_trials=N_TRAIN_PER_CLASS * 2,
        train_late_accuracy=train_acc_late,
        accuracy_en=acc_en, accuracy_wn=acc_wn,
        balanced_accuracy=balanced,
        total_spikes=int(state["spike_history"].sum()),
        active_neurons=int((state["spike_history"] > 0).sum()),
        W_mean=float(state["W"].mean()),
        W_std=float(state["W"].std()),
    )


def _verdict(s):
    return {**s, "T47_pass": s["balanced_accuracy"] > T47_ACCURACY_MIN}


def test_T47(substrates):
    m = _verdict(substrates)
    if not m["T47_pass"]:
        pytest.fail(
            f"BET-063 NULL T47 R-STDP long training.\n"
            f"  trained {m['n_train_trials']} trials\n"
            f"  train late acc (last 200): {m['train_late_accuracy']:.4f}\n"
            f"  test acc_en: {m['accuracy_en']:.4f}, acc_wn: {m['accuracy_wn']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} (need > {T47_ACCURACY_MIN})\n"
            f"  active: {m['active_neurons']}/{m['n_total']}\n"
            f"  W mean: {m['W_mean']:.4f}, std: {m['W_std']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T47_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-063",
        "verdict": verdict,
        "hypothesis": "T47 R-STDP with 50x training + continuous-graded reward instead of binary. After BET-061/062 collapse/death, test if longer + softer training rescues brain-faithful learning.",
        "thresholds": {"T47_accuracy_min": T47_ACCURACY_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

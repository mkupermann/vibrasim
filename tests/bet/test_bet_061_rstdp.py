"""BET-061 — T45 Izhikevich + R-STDP reward-driven learning.

BRAIN-FAITHFUL substrate. Izhikevich (2003) neurons + STDP eligibility
traces + dopamine-like reward (Izhikevich 2007).

Task: substrate hears 2-class audio chunks. Output layer has 2 neurons.
Reward = +1 if correct output neuron fires more in response to chunk,
else -1. R-STDP shapes synapses to produce class-correct firing.

T45 bar (LOCKED):
  After 200 training chunks (100 per class with reward feedback),
  output discrimination on 50 test chunks per class:
  fraction-correct > 0.6 (above chance 0.5)

Brain-criterion check:
  - Spiking neurons (✓ Izhikevich)
  - Plastic synapses (✓ STDP eligibility)
  - Reward-driven (✓ dopamine-like R-STDP)
  - Self-developing (✓ synapses change from random)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.izhikevich_rstdp import IzhikevichRSTDPConfig, initialise, step
from world.flux.cognitive_map import encode_sensor

N_TRAIN_PER_CLASS = 100
N_TEST_PER_CLASS = 50
CHUNK_DURATION_MS = 100  # ms per audio chunk
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T45_ACCURACY_MIN = 0.6

OUT_DIR = Path.home() / ".eqmod/bet/BET-061"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _features_to_input(features, cfg, n_input):
    """Map features to per-input-neuron drive (0-1)."""
    # Pad / truncate to n_input
    inp = np.zeros(n_input, dtype=np.float64)
    n = min(features.size, n_input)
    inp[:n] = np.clip(features[:n], 0, 1)  # already in roughly [0,1] range
    return inp


def _present_chunk(state, audio_chunk, cfg, reward_callback=None, true_class=None):
    """Present one audio chunk to substrate for CHUNK_DURATION_MS.
    Returns (output_spike_counts, winner_class)."""
    izhi_cfg = state["cfg"]
    features = encode_sensor(audio_chunk, cfg)
    input_current = _features_to_input(features, cfg, state["n_in"])
    # Run substrate for chunk duration
    output_spikes_per_step = np.zeros(state["n_o"], dtype=np.int64)
    for t_step in range(int(CHUNK_DURATION_MS / izhi_cfg.dt_ms)):
        # No reward during chunk; reward delivered at end
        spikes = step(state, input_current, reward=0.0)
        output_idx = state["output_idx"]
        output_spikes_per_step += spikes[output_idx].astype(np.int64)
    winner = int(np.argmax(output_spikes_per_step))
    # Deliver reward signal
    if reward_callback is not None and true_class is not None:
        reward = +1.0 if winner == true_class else -1.0
        # Single reward pulse
        spikes = step(state, input_current, reward=reward)
    return output_spikes_per_step, winner


@pytest.fixture(scope="module")
def substrates():
    izhi_cfg = IzhikevichRSTDPConfig()
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

    # Need separate cfg for encode_sensor — use minimal compat
    class _Cfg:
        n_features = N_FEATURES
        fft_bands = FFT_BANDS
        samples_per_tick = SAMPLES_PER_TICK
    encoder_cfg = _Cfg()

    state = initialise(izhi_cfg)

    # Training: alternating EN/WN chunks with reward feedback
    train_history = []
    for trial in range(N_TRAIN_PER_CLASS):
        # EN chunk
        chunk_en = eng_train[trial * SAMPLES_PER_TICK:(trial + 1) * SAMPLES_PER_TICK]
        if chunk_en.size > 0:
            _, winner = _present_chunk(state, chunk_en, encoder_cfg,
                                        reward_callback=True, true_class=0)
            train_history.append(('en', winner == 0))
        # WN chunk
        chunk_wn = wn_train[trial * SAMPLES_PER_TICK:(trial + 1) * SAMPLES_PER_TICK]
        if chunk_wn.size > 0:
            _, winner = _present_chunk(state, chunk_wn, encoder_cfg,
                                        reward_callback=True, true_class=1)
            train_history.append(('wn', winner == 1))

    train_acc_late = sum(1 for c, ok in train_history[-50:] if ok) / 50

    # Test: no reward
    correct_en = 0
    total_en = 0
    for k in range(N_TEST_PER_CLASS):
        chunk = eng_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        _, winner = _present_chunk(state, chunk, encoder_cfg)
        if winner == 0:
            correct_en += 1
        total_en += 1
    correct_wn = 0
    total_wn = 0
    for k in range(N_TEST_PER_CLASS):
        chunk = wn_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        _, winner = _present_chunk(state, chunk, encoder_cfg)
        if winner == 1:
            correct_wn += 1
        total_wn += 1

    acc_en = correct_en / max(total_en, 1)
    acc_wn = correct_wn / max(total_wn, 1)
    balanced = (acc_en + acc_wn) / 2

    return dict(
        n_total=state["n_total"],
        train_late_accuracy=train_acc_late,
        accuracy_en=acc_en, accuracy_wn=acc_wn,
        balanced_accuracy=balanced,
        total_spikes=int(state["spike_history"].sum()),
        active_neurons=int((state["spike_history"] > 0).sum()),
        W_mean=float(state["W"].mean()),
        W_std=float(state["W"].std()),
    )


def _verdict(s):
    return {**s, "T45_pass": s["balanced_accuracy"] > T45_ACCURACY_MIN}


def test_T45(substrates):
    m = _verdict(substrates)
    if not m["T45_pass"]:
        pytest.fail(
            f"BET-061 NULL T45 R-STDP.\n"
            f"  train late (last 50): {m['train_late_accuracy']:.4f}\n"
            f"  test acc_en: {m['accuracy_en']:.4f}\n"
            f"  test acc_wn: {m['accuracy_wn']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} (need > {T45_ACCURACY_MIN})\n"
            f"  active neurons: {m['active_neurons']}/{m['n_total']}\n"
            f"  W mean: {m['W_mean']:.4f}, std: {m['W_std']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T45_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-061",
        "verdict": verdict,
        "hypothesis": "T45 Izhikevich+R-STDP brain-faithful substrate. Spiking neurons, plastic synapses, dopamine-modulated learning. Substrate learns class-discrimination via reward feedback. Bar: balanced acc > 0.6.",
        "thresholds": {"T45_accuracy_min": T45_ACCURACY_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

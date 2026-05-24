"""BET-062 — T46 pure unsupervised SNN+STDP class-emergence.

Even simpler than BET-061: NO reward, NO labels, NO supervised
output assignment. Just substrate (Izhikevich + STDP) hearing audio,
and measure if hidden neurons develop different firing patterns
for EN vs WN.

T46 bar (LOCKED):
  Per-neuron firing-rate KL between EN-trained-response vs
  WN-trained-response distributions > 0.1.

If this NULLs: brain-faithful spike-based substrates don't develop
detectable class-emergence in single-iteration budget. Multi-day
research required.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.izhikevich_rstdp import IzhikevichRSTDPConfig, initialise, step
from world.flux.cognitive_map import encode_sensor

N_TRAIN_PER_CLASS = 500   # 5x BET-061 training
N_TEST_PER_CLASS = 100
CHUNK_DURATION_MS = 50
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T46_KL_MIN = 0.1

OUT_DIR = Path.home() / ".eqmod/bet/BET-062"
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


def _present_and_count_hidden(state, audio_chunk, cfg_enc):
    """Present chunk, return per-hidden-neuron spike count during chunk."""
    izhi_cfg = state["cfg"]
    features = encode_sensor(audio_chunk, cfg_enc)
    input_current = _features_to_input(features, state["n_in"])
    h_idx = state["hidden_idx"]
    hidden_count = np.zeros(state["n_h"], dtype=np.int64)
    for _ in range(int(CHUNK_DURATION_MS / izhi_cfg.dt_ms)):
        spikes = step(state, input_current, reward=0.0)
        hidden_count += spikes[h_idx].astype(np.int64)
    return hidden_count


def _hist_kl(a, b, n_bins=20):
    lo = min(a.min(), b.min())
    hi = max(a.max(), b.max())
    if hi - lo < 1e-12:
        return 0.0
    edges = np.linspace(lo, hi, n_bins + 1)
    ha, _ = np.histogram(a, bins=edges)
    hb, _ = np.histogram(b, bins=edges)
    pa = (ha + 1.0) / (ha.sum() + n_bins)
    pb = (hb + 1.0) / (hb.sum() + n_bins)
    return 0.5 * (float((pa * np.log(pa / pb)).sum())
                  + float((pb * np.log(pb / pa)).sum()))


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

    # Training: interleaved EN/WN, no reward, just STDP
    for k in range(N_TRAIN_PER_CLASS):
        en_chunk = eng_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if en_chunk.size > 0:
            _present_and_count_hidden(state, en_chunk, encoder_cfg)
        wn_chunk = wn_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if wn_chunk.size > 0:
            _present_and_count_hidden(state, wn_chunk, encoder_cfg)

    # Test: measure hidden response patterns
    en_responses = np.zeros((N_TEST_PER_CLASS, state["n_h"]), dtype=np.int64)
    wn_responses = np.zeros((N_TEST_PER_CLASS, state["n_h"]), dtype=np.int64)
    for k in range(N_TEST_PER_CLASS):
        en_responses[k] = _present_and_count_hidden(
            state, eng_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK], encoder_cfg)
        wn_responses[k] = _present_and_count_hidden(
            state, wn_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK], encoder_cfg)

    # Per-neuron mean firing rate per class
    en_mean = en_responses.mean(axis=0).astype(np.float64)
    wn_mean = wn_responses.mean(axis=0).astype(np.float64)
    kl_class = _hist_kl(en_mean, wn_mean)

    # Per-trial: full response vector KL
    kl_full = _hist_kl(en_responses.ravel().astype(np.float64),
                       wn_responses.ravel().astype(np.float64))

    # Selectivity: neurons that respond differently to EN vs WN
    differential = np.abs(en_mean - wn_mean)
    n_selective = int((differential > differential.mean() + differential.std()).sum())

    return dict(
        n_hidden=state["n_h"],
        active_neurons=int((state["spike_history"][state["hidden_idx"]] > 0).sum()),
        en_mean_response=float(en_mean.mean()),
        wn_mean_response=float(wn_mean.mean()),
        kl_class_means=kl_class,
        kl_full_distributions=kl_full,
        n_selective_neurons=n_selective,
        W_mean=float(state["W"].mean()),
        W_std=float(state["W"].std()),
    )


def _verdict(s):
    pass_ = (s["kl_class_means"] > T46_KL_MIN
             or s["kl_full_distributions"] > T46_KL_MIN)
    return {**s, "T46_pass": pass_}


def test_T46(substrates):
    m = _verdict(substrates)
    if not m["T46_pass"]:
        pytest.fail(
            f"BET-062 NULL T46 unsupervised STDP class emergence.\n"
            f"  active hidden: {m['active_neurons']}/{m['n_hidden']}\n"
            f"  EN mean response: {m['en_mean_response']:.4f}\n"
            f"  WN mean response: {m['wn_mean_response']:.4f}\n"
            f"  KL class-means: {m['kl_class_means']:.4f}\n"
            f"  KL full distributions: {m['kl_full_distributions']:.4f}\n"
            f"  (need either > {T46_KL_MIN})\n"
            f"  selective neurons: {m['n_selective_neurons']}\n"
            f"  W mean: {m['W_mean']:.4f}, std: {m['W_std']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T46_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-062",
        "verdict": verdict,
        "hypothesis": "T46 pure unsupervised Izhikevich+STDP class emergence. No reward, no labels — just spike-timing plasticity. If hidden neurons develop class-specific firing patterns: brain-faithful self-organization works on real audio.",
        "thresholds": {"T46_kl_min": T46_KL_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

"""BET-065 — T49 Brian2 SNN+STDP brain-faithful audio learning.

After 6 from-scratch numpy SNN NULLs, use Brian2 (proper SNN simulator).
Test if brain-faithful spiking substrate with library-grade
implementation learns EN-vs-WN discrimination.

T49 bar (LOCKED):
  KL between hidden firing patterns for EN vs WN test trials > 0.1.
  Plus: classification accuracy via simple distance-to-prototype > 0.6.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pytest

warnings.filterwarnings('ignore')

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.brian2_snn import Brian2SNNConfig, run_substrate
from world.flux.harder_bar_metrics import hist_kl_symmetric

N_TRAIN_PER_CLASS = 200
N_TEST_PER_CLASS = 50
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T49_KL_MIN = 0.1
T49_ACCURACY_MIN = 0.6

OUT_DIR = Path.home() / ".eqmod/bet/BET-065"
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

    # Split into per-chunk arrays
    en_train_chunks = [eng_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
                       for k in range(N_TRAIN_PER_CLASS)]
    wn_train_chunks = [wn_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
                       for k in range(N_TRAIN_PER_CLASS)]
    en_test_chunks = [eng_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
                      for k in range(N_TEST_PER_CLASS)]
    wn_test_chunks = [wn_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
                      for k in range(N_TEST_PER_CLASS)]

    cfg = Brian2SNNConfig(chunk_duration_ms=100.0)
    result = run_substrate(
        train_dict={0: en_train_chunks, 1: wn_train_chunks},
        test_dict={0: en_test_chunks, 1: wn_test_chunks},
        encoder_cfg=encoder_cfg,
        n_train_per_class=N_TRAIN_PER_CLASS,
        n_test_per_class=N_TEST_PER_CLASS,
        cfg=cfg,
    )

    en_patterns = result["test_patterns_by_class"][0]
    wn_patterns = result["test_patterns_by_class"][1]

    # Discrimination via KL
    kl = hist_kl_symmetric(en_patterns.astype(np.float64),
                           wn_patterns.astype(np.float64))

    # Classification via class-prototype distance
    proto_en = en_patterns.mean(axis=0)
    proto_wn = wn_patterns.mean(axis=0)
    correct = 0
    total = 0
    for p in en_patterns:
        d_en = float(np.linalg.norm(p - proto_en))
        d_wn = float(np.linalg.norm(p - proto_wn))
        if d_en < d_wn:
            correct += 1
        total += 1
    for p in wn_patterns:
        d_en = float(np.linalg.norm(p - proto_en))
        d_wn = float(np.linalg.norm(p - proto_wn))
        if d_wn < d_en:
            correct += 1
        total += 1
    accuracy = correct / max(total, 1)

    return dict(
        n_patterns_en=en_patterns.shape[0],
        n_patterns_wn=wn_patterns.shape[0],
        kl_distributions=kl,
        accuracy_proto_classify=accuracy,
        en_mean_response=float(en_patterns.mean()),
        wn_mean_response=float(wn_patterns.mean()),
        en_std=float(en_patterns.std()),
        wn_std=float(wn_patterns.std()),
        final_W_mean=result["final_W_mean"],
        final_W_std=result["final_W_std"],
        total_hidden_spikes=result["total_hidden_spikes"],
    )


def _verdict(s):
    kl_ok = s["kl_distributions"] > T49_KL_MIN
    acc_ok = s["accuracy_proto_classify"] > T49_ACCURACY_MIN
    return {**s, "T49_kl_ok": kl_ok, "T49_acc_ok": acc_ok,
            "T49_pass": kl_ok and acc_ok}


def test_T49(substrates):
    m = _verdict(substrates)
    if not m["T49_pass"]:
        pytest.fail(
            f"BET-065 NULL T49 Brian2 SNN.\n"
            f"  KL distributions: {m['kl_distributions']:.4f} (need > {T49_KL_MIN})\n"
            f"  accuracy: {m['accuracy_proto_classify']:.4f} (need > {T49_ACCURACY_MIN})\n"
            f"  EN mean: {m['en_mean_response']:.4f}, WN mean: {m['wn_mean_response']:.4f}\n"
            f"  W mean: {m['final_W_mean']:.4f}, std: {m['final_W_std']:.4f}\n"
            f"  hidden spikes: {m['total_hidden_spikes']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T49_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-065",
        "verdict": verdict,
        "hypothesis": "T49 Brian2-implemented SNN+STDP brain-faithful substrate. Real audio EN vs WN. After 6 numpy NULLs, test if proper library makes it work. Bar: KL > 0.1 AND prototype-classify acc > 0.6.",
        "thresholds": {"T49_kl_min": T49_KL_MIN, "T49_acc_min": T49_ACCURACY_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

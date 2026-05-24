"""BET-059 — T43 Hyperdimensional Computing substrate (Kanerva 2009).

Algebraic vector substrate — NOT statistical pattern matching, NOT
spiking/dynamical. Pure bind/superpose operations in fixed
high-dim space.

T43 protocol:
  Train HDC by storing 5000 EN chunks under class 0, 5000 WN under
  class 1. Test classify 1000 EN and 1000 WN held-out chunks.

T43 bar (LOCKED):
  balanced 2-class accuracy > 0.7.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.hdc import HDCConfig, initialise, store, classify

N_TICKS_PER_CLASS = 5_000
N_TEST_PER_CLASS = 1_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T43_ACCURACY_MIN = 0.7

OUT_DIR = Path.home() / ".eqmod/bet/BET-059"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


@pytest.fixture(scope="module")
def substrates():
    cfg = HDCConfig(samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
                    n_features=N_FEATURES, dimensionality=10_000)
    n_per = N_TICKS_PER_CLASS * SAMPLES_PER_TICK
    n_test = N_TEST_PER_CLASS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_per + n_test > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_per].astype(np.float64)
    eng_test = full[n_per:n_per + n_test].astype(np.float64)
    wn_train = _make_wn(n_per, TARGET_RMS, WN_SEED)
    wn_test = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)

    state = initialise(cfg)

    # Train: store chunks
    for k in range(N_TICKS_PER_CLASS):
        chunk = eng_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        store(state, chunk, 0, cfg)
    for k in range(N_TICKS_PER_CLASS):
        chunk = wn_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        store(state, chunk, 1, cfg)

    # Test classify
    correct_en = 0
    total_en = 0
    for k in range(N_TEST_PER_CLASS):
        chunk = eng_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        if classify(state, chunk, cfg) == 0:
            correct_en += 1
        total_en += 1
    correct_wn = 0
    total_wn = 0
    for k in range(N_TEST_PER_CLASS):
        chunk = wn_test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        if classify(state, chunk, cfg) == 1:
            correct_wn += 1
        total_wn += 1

    acc_en = correct_en / max(total_en, 1)
    acc_wn = correct_wn / max(total_wn, 1)
    balanced = (acc_en + acc_wn) / 2

    return dict(
        dimensionality=cfg.dimensionality,
        accuracy_en=acc_en, accuracy_wn=acc_wn,
        balanced_accuracy=balanced,
    )


def _verdict(s):
    return {**s, "T43_pass": s["balanced_accuracy"] > T43_ACCURACY_MIN}


def test_T43(substrates):
    m = _verdict(substrates)
    if not m["T43_pass"]:
        pytest.fail(
            f"BET-059 NULL T43 HDC.\n"
            f"  acc_en: {m['accuracy_en']:.4f}, acc_wn: {m['accuracy_wn']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} (need > {T43_ACCURACY_MIN})"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T43_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-059",
        "verdict": verdict,
        "hypothesis": "T43 Hyperdimensional Computing (Kanerva 2009) — algebraic vector substrate, bind+superpose in 10000-dim binary space. Qualitatively different from statistical/spiking.",
        "thresholds": {"T43_accuracy_min": T43_ACCURACY_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

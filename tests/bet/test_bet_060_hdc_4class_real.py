"""BET-060 — T44 HDC 4-class real multi-source audio.

After BET-059 HDC PASSED 97% on binary EN-vs-WN, test 4-class real
audio (EN-speech / DE-speech / Music / WN). Replaces killed BET-056
with the not-LLM-family substrate.

T44 bar (LOCKED): balanced 4-class accuracy > 0.5 (chance = 0.25).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.hdc import HDCConfig, initialise, store, classify

N_TRAIN_PER_CLASS = 2_000
N_TEST_PER_CLASS = 500
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T44_ACCURACY_MIN = 0.5

EN_MANIFEST = Path.home() / ".eqmod/training/EN/manifest.json"
DE_AUDIO = Path.home() / ".eqmod/babble/real-de-run/reference.wav"
MUSIC_AUDIO = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Agus Zack & Maikko - Glowing.mp3"

OUT_DIR = Path.home() / ".eqmod/bet/BET-060"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _load_wav(path, n_samples, offset=0):
    import soundfile as sf
    data, sr = sf.read(str(path))
    if data.ndim > 1:
        data = data.mean(axis=1)
    chunk = data[offset:offset + n_samples].astype(np.float64)
    rms = np.sqrt(np.mean(chunk ** 2))
    if rms > 0:
        chunk = chunk / rms * TARGET_RMS
    return chunk


def _load_mp3(path, n_samples, offset=0):
    import librosa
    audio, sr = librosa.load(str(path), sr=16000, offset=offset / 16000,
                              duration=n_samples / 16000)
    if audio.shape[0] < n_samples:
        audio = np.pad(audio, (0, n_samples - audio.shape[0]))
    audio = audio[:n_samples].astype(np.float64)
    rms = np.sqrt(np.mean(audio ** 2))
    if rms > 0:
        audio = audio / rms * TARGET_RMS
    return audio


def _classify_chunks(state, audio, cfg, true_class, n_test):
    correct = 0
    total = 0
    for k in range(n_test):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        if classify(state, chunk, cfg) == true_class:
            correct += 1
        total += 1
    return correct / max(total, 1)


@pytest.fixture(scope="module")
def substrates():
    cfg = HDCConfig(samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
                    n_features=N_FEATURES, dimensionality=10_000)
    n_train = N_TRAIN_PER_CLASS * SAMPLES_PER_TICK
    n_test = N_TEST_PER_CLASS * SAMPLES_PER_TICK

    # Load all sources
    en_full = load_corpus_waveform_from_manifest(
        EN_MANIFEST, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    eng_train = en_full[:n_train].astype(np.float64)
    eng_test = en_full[n_train:n_train + n_test].astype(np.float64)
    de_train = _load_wav(DE_AUDIO, n_train, offset=0)
    de_test = _load_wav(DE_AUDIO, n_test, offset=n_train)
    music_train = _load_mp3(MUSIC_AUDIO, n_train, offset=0)
    music_test = _load_mp3(MUSIC_AUDIO, n_test, offset=n_train)
    wn_train = _make_wn(n_train, TARGET_RMS, WN_SEED)
    wn_test = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)

    state = initialise(cfg)

    # Store training chunks per class
    for class_label, audio_train in [(0, eng_train), (1, de_train),
                                      (2, music_train), (3, wn_train)]:
        for k in range(N_TRAIN_PER_CLASS):
            chunk = audio_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
            if chunk.size == 0:
                continue
            store(state, chunk, class_label, cfg)

    # Test classify each class
    acc_en = _classify_chunks(state, eng_test, cfg, 0, N_TEST_PER_CLASS)
    acc_de = _classify_chunks(state, de_test, cfg, 1, N_TEST_PER_CLASS)
    acc_music = _classify_chunks(state, music_test, cfg, 2, N_TEST_PER_CLASS)
    acc_wn = _classify_chunks(state, wn_test, cfg, 3, N_TEST_PER_CLASS)
    balanced = (acc_en + acc_de + acc_music + acc_wn) / 4

    return dict(
        dimensionality=cfg.dimensionality,
        accuracy_en=acc_en, accuracy_de=acc_de,
        accuracy_music=acc_music, accuracy_wn=acc_wn,
        balanced_accuracy=balanced,
    )


def _verdict(s):
    return {**s, "T44_pass": s["balanced_accuracy"] > T44_ACCURACY_MIN}


def test_T44(substrates):
    m = _verdict(substrates)
    if not m["T44_pass"]:
        pytest.fail(
            f"BET-060 NULL T44 HDC 4-class.\n"
            f"  acc EN/DE/Music/WN: {m['accuracy_en']:.4f}/{m['accuracy_de']:.4f}/"
            f"{m['accuracy_music']:.4f}/{m['accuracy_wn']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} (need > {T44_ACCURACY_MIN}, chance=0.25)"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T44_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-060",
        "verdict": verdict,
        "hypothesis": "T44 HDC 4-class real audio (EN/DE/Music/WN). Replaces killed BET-056 with not-LLM-family substrate.",
        "thresholds": {"T44_accuracy_min": T44_ACCURACY_MIN, "chance": 0.25},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

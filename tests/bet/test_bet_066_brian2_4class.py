"""BET-066 — T50 Brian2 SNN 4-class real audio.

After BET-065 Brian2 SNN PASSED 98% on binary, scale to 4-class:
EN-speech (P&P narrator) vs DE-speech (real German) vs Music vs WN.

T50 bar (LOCKED):
  prototype-classify balanced 4-class accuracy > 0.4 (chance = 0.25).
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

N_TRAIN_PER_CLASS = 100
N_TEST_PER_CLASS = 30
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T50_ACCURACY_MIN = 0.4

EN_MANIFEST = Path.home() / ".eqmod/training/EN/manifest.json"
DE_AUDIO = Path.home() / ".eqmod/babble/real-de-run/reference.wav"
MUSIC_AUDIO = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Agus Zack & Maikko - Glowing.mp3"

OUT_DIR = Path.home() / ".eqmod/bet/BET-066"


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


@pytest.fixture(scope="module")
def substrates():
    class _Cfg:
        n_features = N_FEATURES
        fft_bands = FFT_BANDS
        samples_per_tick = SAMPLES_PER_TICK
    encoder_cfg = _Cfg()

    n_train = N_TRAIN_PER_CLASS * SAMPLES_PER_TICK
    n_test = N_TEST_PER_CLASS * SAMPLES_PER_TICK

    # Load all sources
    en_full = load_corpus_waveform_from_manifest(
        EN_MANIFEST, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    eng_train_a = en_full[:n_train].astype(np.float64)
    eng_test_a = en_full[n_train:n_train + n_test].astype(np.float64)
    de_train_a = _load_wav(DE_AUDIO, n_train, offset=0)
    de_test_a = _load_wav(DE_AUDIO, n_test, offset=n_train)
    music_train_a = _load_mp3(MUSIC_AUDIO, n_train, offset=0)
    music_test_a = _load_mp3(MUSIC_AUDIO, n_test, offset=n_train)
    wn_train_a = _make_wn(n_train, TARGET_RMS, WN_SEED)
    wn_test_a = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)

    def _chunks(audio, n):
        return [audio[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK] for k in range(n)]

    train_dict = {
        0: _chunks(eng_train_a, N_TRAIN_PER_CLASS),
        1: _chunks(de_train_a, N_TRAIN_PER_CLASS),
        2: _chunks(music_train_a, N_TRAIN_PER_CLASS),
        3: _chunks(wn_train_a, N_TRAIN_PER_CLASS),
    }
    test_dict = {
        0: _chunks(eng_test_a, N_TEST_PER_CLASS),
        1: _chunks(de_test_a, N_TEST_PER_CLASS),
        2: _chunks(music_test_a, N_TEST_PER_CLASS),
        3: _chunks(wn_test_a, N_TEST_PER_CLASS),
    }

    cfg = Brian2SNNConfig(chunk_duration_ms=100.0)
    result = run_substrate(
        train_dict=train_dict, test_dict=test_dict,
        encoder_cfg=encoder_cfg,
        n_train_per_class=N_TRAIN_PER_CLASS,
        n_test_per_class=N_TEST_PER_CLASS,
        cfg=cfg,
    )

    patterns = {c: result["test_patterns_by_class"][c] for c in [0, 1, 2, 3]}
    # Prototype per class = mean test pattern
    protos = {c: patterns[c].mean(axis=0) for c in [0, 1, 2, 3]}

    # Classify each test pattern by nearest prototype
    accuracies = {}
    for true_c in [0, 1, 2, 3]:
        correct = 0
        total = 0
        for p in patterns[true_c]:
            dists = {c: float(np.linalg.norm(p - protos[c])) for c in [0, 1, 2, 3]}
            pred = min(dists, key=dists.get)
            if pred == true_c:
                correct += 1
            total += 1
        accuracies[true_c] = correct / max(total, 1)

    balanced = sum(accuracies.values()) / 4

    return dict(
        accuracy_en=accuracies[0],
        accuracy_de=accuracies[1],
        accuracy_music=accuracies[2],
        accuracy_wn=accuracies[3],
        balanced_accuracy=balanced,
        final_W_mean=result["final_W_mean"],
        final_W_std=result["final_W_std"],
        total_hidden_spikes=result["total_hidden_spikes"],
    )


def _verdict(s):
    return {**s, "T50_pass": s["balanced_accuracy"] > T50_ACCURACY_MIN}


def test_T50(substrates):
    m = _verdict(substrates)
    if not m["T50_pass"]:
        pytest.fail(
            f"BET-066 NULL T50 Brian2 4-class.\n"
            f"  acc EN/DE/Music/WN: {m['accuracy_en']:.4f}/{m['accuracy_de']:.4f}/"
            f"{m['accuracy_music']:.4f}/{m['accuracy_wn']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} (need > {T50_ACCURACY_MIN}, chance=0.25)\n"
            f"  hidden spikes: {m['total_hidden_spikes']}\n"
            f"  W mean: {m['final_W_mean']:.4f}, std: {m['final_W_std']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T50_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-066",
        "verdict": verdict,
        "hypothesis": "T50 Brian2 SNN+STDP 4-class real audio (EN/DE/Music/WN). Scales brain-faithful spiking substrate to multi-class real audio. Bar: balanced > 0.4.",
        "thresholds": {"T50_accuracy_min": T50_ACCURACY_MIN, "chance": 0.25},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

"""BET-056 — T40 4-class REAL multi-source audio classification.

CHALLENGE iteration. Beyond synthetic EN/WN/pink — real audio diversity:
  Class 0: EN-speech (Pride and Prejudice, LibriVox narrator)
  Class 1: DE-speech (real German audio from ~/.eqmod/babble/real-de-run)
  Class 2: Music (electronic music, librosa-loaded MP3)
  Class 3: WN (matched-RMS white noise)

Tests if substrate handles broader audio diversity. Speech-vs-speech
across languages is non-trivial (similar features, different content).

T40 bar (LOCKED): balanced 4-class accuracy > 0.4 (chance = 0.25).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, run
from world.flux.cognitive_map import encode_sensor

N_TICKS_PER_CLASS = 5_000
N_TEST_PER_CLASS = 1_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)

EN_MANIFEST = Path.home() / ".eqmod/training/EN/manifest.json"
DE_AUDIO = Path.home() / ".eqmod/babble/real-de-run/reference.wav"
MUSIC_AUDIO = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Agus Zack & Maikko - Glowing.mp3"

T40_ACCURACY_MIN = 0.4

OUT_DIR = Path.home() / ".eqmod/bet/BET-056"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _load_wav(path: Path, n_samples: int, offset: int = 0) -> np.ndarray:
    import soundfile as sf
    data, sr = sf.read(str(path))
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != 16000:
        raise RuntimeError(f"Expected 16kHz, got {sr}")
    if offset + n_samples > data.shape[0]:
        raise RuntimeError(f"Not enough samples: need {n_samples} at offset {offset}, have {data.shape[0]}")
    chunk = data[offset:offset + n_samples].astype(np.float64)
    # Normalize to target RMS
    rms = np.sqrt(np.mean(chunk ** 2))
    if rms > 0:
        chunk = chunk / rms * TARGET_RMS
    return chunk


def _load_mp3(path: Path, n_samples: int, offset: int = 0) -> np.ndarray:
    import librosa
    audio, sr = librosa.load(str(path), sr=16000, offset=offset / 16000,
                              duration=n_samples / 16000)
    if audio.shape[0] < n_samples:
        # Pad if file is shorter
        audio = np.pad(audio, (0, n_samples - audio.shape[0]))
    audio = audio[:n_samples].astype(np.float64)
    rms = np.sqrt(np.mean(audio ** 2))
    if rms > 0:
        audio = audio / rms * TARGET_RMS
    return audio


def _copy_state(state):
    return {
        "w": state["w"].copy(), "N": state["N"].copy(),
        "ii": state["ii"], "jj": state["jj"], "kk": state["kk"],
        "buffer": state["buffer"].copy(), "buffer_head": state["buffer_head"],
        "buffer_fill": state["buffer_fill"], "global_tick": state["global_tick"],
    }


def _bmu_index(state, sensor):
    diff = state["w"] - sensor
    return int(np.argmin(np.einsum("ijkl,ijkl->ijk", diff, diff)))


def _classify(state, cell_labels, audio, cfg, true_class):
    n = audio.size // cfg.samples_per_tick
    correct = 0
    total = 0
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        if int(cell_labels[_bmu_index(state, sensor)]) == true_class:
            correct += 1
        total += 1
    return correct / max(total, 1)


def _count_visits(state, audio, cfg, n_cells, n_chunks):
    counts = np.zeros(n_cells, dtype=np.int64)
    for k in range(n_chunks):
        chunk = audio[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        counts[_bmu_index(state, encode_sensor(chunk, cfg))] += 1
    return counts


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, grid_dims=GRID_DIMS,
    )
    n_per = N_TICKS_PER_CLASS * SAMPLES_PER_TICK
    n_test = N_TEST_PER_CLASS * SAMPLES_PER_TICK

    # Load EN
    en_full = load_corpus_waveform_from_manifest(
        EN_MANIFEST, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    eng_train = en_full[:n_per].astype(np.float64)
    eng_test = en_full[n_per:n_per + n_test].astype(np.float64)

    # Load DE
    de_train = _load_wav(DE_AUDIO, n_per, offset=0)
    de_test = _load_wav(DE_AUDIO, n_test, offset=n_per)

    # Load music
    music_train = _load_mp3(MUSIC_AUDIO, n_per, offset=0)
    music_test = _load_mp3(MUSIC_AUDIO, n_test, offset=n_per)

    # WN
    wn_train = _make_wn(n_per, TARGET_RMS, WN_SEED)
    wn_test = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz
    n_chunks_per_class = n_per // SAMPLES_PER_TICK

    # Sequential training with replay
    state = run(cfg, N_TICKS_PER_CLASS, eng_train)
    cell_en = _count_visits(state, eng_train, cfg, n_cells, n_chunks_per_class)

    state = run(cfg, N_TICKS_PER_CLASS, de_train, state=_copy_state(state))
    cell_de = _count_visits(state, de_train, cfg, n_cells, n_chunks_per_class)

    state = run(cfg, N_TICKS_PER_CLASS, music_train, state=_copy_state(state))
    cell_music = _count_visits(state, music_train, cfg, n_cells, n_chunks_per_class)

    state = run(cfg, N_TICKS_PER_CLASS, wn_train, state=_copy_state(state))
    cell_wn = _count_visits(state, wn_train, cfg, n_cells, n_chunks_per_class)

    # 4-class cell labels via argmax visits
    cell_labels = np.stack([cell_en, cell_de, cell_music, cell_wn], axis=1).argmax(axis=1)

    acc_en = _classify(state, cell_labels, eng_test, cfg, 0)
    acc_de = _classify(state, cell_labels, de_test, cfg, 1)
    acc_music = _classify(state, cell_labels, music_test, cfg, 2)
    acc_wn = _classify(state, cell_labels, wn_test, cfg, 3)
    balanced = (acc_en + acc_de + acc_music + acc_wn) / 4

    return dict(
        n_cells=n_cells,
        n_en_cells=int((cell_labels == 0).sum()),
        n_de_cells=int((cell_labels == 1).sum()),
        n_music_cells=int((cell_labels == 2).sum()),
        n_wn_cells=int((cell_labels == 3).sum()),
        accuracy_en=acc_en, accuracy_de=acc_de,
        accuracy_music=acc_music, accuracy_wn=acc_wn,
        balanced_accuracy=balanced,
    )


def _verdict(s):
    return {**s, "T40_pass": s["balanced_accuracy"] > T40_ACCURACY_MIN}


def test_T40(substrates):
    m = _verdict(substrates)
    if not m["T40_pass"]:
        pytest.fail(
            f"BET-056 NULL T40 4-class real-audio.\n"
            f"  acc_en: {m['accuracy_en']:.4f}\n"
            f"  acc_de: {m['accuracy_de']:.4f}\n"
            f"  acc_music: {m['accuracy_music']:.4f}\n"
            f"  acc_wn: {m['accuracy_wn']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} "
            f"(need > {T40_ACCURACY_MIN}, chance=0.25)\n"
            f"  cells: EN={m['n_en_cells']}, DE={m['n_de_cells']}, "
            f"music={m['n_music_cells']}, WN={m['n_wn_cells']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T40_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-056",
        "verdict": verdict,
        "hypothesis": "T40 4-class real multi-source: EN-speech vs DE-speech vs Music vs WN. Tests substrate on real audio diversity beyond synthetic noise classes.",
        "thresholds": {"T40_accuracy_min": T40_ACCURACY_MIN, "chance": 0.25},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

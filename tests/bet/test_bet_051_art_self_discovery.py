"""BET-051 — T35 ART unsupervised category self-discovery.

After BET-046 NULL (vigilance=0.85 too lenient — only 9/4 cells),
test with higher vigilance. Substrate sees MIXED 3-class audio (EN +
WN + pink interleaved, no class labels). Does ART autonomously
discover ~3 stable categories that correspond to the acoustic
classes?

This is genuine "selbstständig lernend": substrate decides what
categories exist, no supervision.

Bar T35 (LOCKED):
  1) ART allocates between 3 and 50 cells (within reasonable range
     for 3-class problem)
  2) When ART cells are post-hoc labeled by majority class, 3-class
     classifier accuracy on novel test > 0.5 (better than chance 0.333)

Locked vigilance: 0.95 (vs BET-046's too-lenient 0.85).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.art_substrate import ARTConfig, run as art_run, classify
from world.flux.cognitive_map import encode_sensor

N_TICKS_PER_CLASS = 5_000
N_TEST_PER_CLASS = 1_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
VIGILANCE = 0.95
WN_SEED = 9999
WN_TEST_SEED = 8888
PINK_SEED = 7777
PINK_TEST_SEED = 6666
TARGET_RMS = 0.25
INTERLEAVE_SEED = 12345

T35_MIN_CELLS = 3
T35_MAX_CELLS = 50
T35_ACCURACY_MIN = 0.5

OUT_DIR = Path.home() / ".eqmod/bet/BET-051"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _make_pink(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    white = rng.standard_normal(n)
    fft = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n)
    freqs[0] = 1.0
    fft_pink = fft / np.sqrt(freqs)
    pink = np.fft.irfft(fft_pink, n=n)
    rms = np.sqrt(np.mean(pink * pink))
    if rms > 0:
        pink = pink / rms * target_rms
    return pink.astype(np.float64)


def _interleave(audios_with_labels, samples_per_tick, seed):
    """Interleave audio classes at chunk granularity, randomly ordered.
    audios_with_labels: list of (audio_array, label) tuples.
    Returns (interleaved_audio, labels_per_chunk)."""
    chunks = []
    chunk_labels = []
    for audio, label in audios_with_labels:
        n_chunks = audio.size // samples_per_tick
        for k in range(n_chunks):
            chunks.append(audio[k * samples_per_tick:(k + 1) * samples_per_tick])
            chunk_labels.append(label)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(chunks))
    interleaved = np.concatenate([chunks[i] for i in perm])
    labels = np.array([chunk_labels[i] for i in perm], dtype=np.int64)
    return interleaved, labels


def _classify_with_art(state, audio, cfg, true_class, cell_class_labels):
    n = audio.size // cfg.samples_per_tick
    correct = 0
    total = 0
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        bmu = classify(state, sensor, cfg)
        if bmu >= 0 and bmu < cell_class_labels.size:
            if int(cell_class_labels[bmu]) == true_class:
                correct += 1
        total += 1
    return correct / max(total, 1)


@pytest.fixture(scope="module")
def substrates():
    cfg = ARTConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, vigilance=VIGILANCE,
    )
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
    pink_train = _make_pink(n_per, TARGET_RMS, PINK_SEED)
    pink_test = _make_pink(n_test, TARGET_RMS, PINK_TEST_SEED)

    # Interleave for unsupervised training
    interleaved, true_labels = _interleave(
        [(eng_train, 0), (wn_train, 1), (pink_train, 2)],
        SAMPLES_PER_TICK, INTERLEAVE_SEED,
    )

    n_training_chunks = interleaved.size // SAMPLES_PER_TICK
    state = art_run(cfg, n_training_chunks, interleaved)
    n_cells = state["weights"].shape[0]

    # Post-hoc label cells by majority class of training visits
    # (this is the "post-hoc" supervised step that turns ART discovery
    # into a classifier; the SUBSTRATE learning was unsupervised)
    cell_class_counts = np.zeros((n_cells, 3), dtype=np.int64)
    for k in range(n_training_chunks):
        chunk = interleaved[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        bmu = classify(state, sensor, cfg)
        if bmu >= 0 and bmu < n_cells:
            cell_class_counts[bmu, true_labels[k]] += 1

    cell_class_labels = cell_class_counts.argmax(axis=1)

    # Classify novel test data
    acc_en = _classify_with_art(state, eng_test, cfg, 0, cell_class_labels)
    acc_wn = _classify_with_art(state, wn_test, cfg, 1, cell_class_labels)
    acc_pink = _classify_with_art(state, pink_test, cfg, 2, cell_class_labels)
    balanced = (acc_en + acc_wn + acc_pink) / 3

    return dict(
        n_cells=n_cells,
        vigilance=VIGILANCE,
        accuracy_en=acc_en, accuracy_wn=acc_wn, accuracy_pink=acc_pink,
        balanced_accuracy=balanced,
        cell_class_distribution=cell_class_counts.sum(axis=0).tolist(),
    )


def _verdict(s):
    range_ok = T35_MIN_CELLS <= s["n_cells"] <= T35_MAX_CELLS
    acc_ok = s["balanced_accuracy"] > T35_ACCURACY_MIN
    return {**s, "T35_cell_count_ok": range_ok,
            "T35_accuracy_ok": acc_ok,
            "T35_pass": range_ok and acc_ok}


def test_T35(substrates):
    m = _verdict(substrates)
    if not m["T35_pass"]:
        pytest.fail(
            f"BET-051 NULL T35 ART self-discovery.\n"
            f"  n_cells: {m['n_cells']} (need {T35_MIN_CELLS}-{T35_MAX_CELLS}) "
            f"pass={m['T35_cell_count_ok']}\n"
            f"  balanced accuracy: {m['balanced_accuracy']:.4f} "
            f"(need > {T35_ACCURACY_MIN}) pass={m['T35_accuracy_ok']}\n"
            f"  acc EN/WN/pink: {m['accuracy_en']:.4f}/{m['accuracy_wn']:.4f}/{m['accuracy_pink']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T35_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-051",
        "verdict": verdict,
        "hypothesis": "T35 ART unsupervised category self-discovery. Substrate sees mixed 3-class audio with no labels. ART autonomously allocates cells. Post-hoc cell-labeling tests if ART found acoustic structure.",
        "thresholds": {
            "T35_min_cells": T35_MIN_CELLS, "T35_max_cells": T35_MAX_CELLS,
            "T35_accuracy_min": T35_ACCURACY_MIN,
            "vigilance": VIGILANCE,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

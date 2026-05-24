"""BET-049 — T33 end-to-end EN-vs-pink classification (harder).

BET-048 PASSED 99.4% on EN-vs-WN (easy). BET-049 tests harder task:
EN vs pink noise (1/f spectrum, more naturalistic). Same substrate
pipeline, same protocol.

T33 bar (LOCKED): balanced accuracy > 0.6 (better than chance at
challenging task).
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
PINK_SEED = 8888
PINK_TEST_SEED = 7777
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)

T33_ACCURACY_MIN = 0.6

OUT_DIR = Path.home() / ".eqmod/bet/BET-049"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


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
    n_correct = 0
    n_total = 0
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        bmu = _bmu_index(state, sensor)
        predicted = int(cell_labels[bmu])
        if predicted == true_class:
            n_correct += 1
        n_total += 1
    return n_correct / max(n_total, 1)


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, grid_dims=GRID_DIMS,
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
    pink_train = _make_pink(n_per, TARGET_RMS, PINK_SEED)
    pink_test = _make_pink(n_test, TARGET_RMS, PINK_TEST_SEED)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz

    state = run(cfg, N_TICKS_PER_CLASS, eng_train)
    cell_en_visits = np.zeros(n_cells, dtype=np.int64)
    n_chunks_per_class = n_per // SAMPLES_PER_TICK
    for k in range(n_chunks_per_class):
        chunk = eng_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        cell_en_visits[_bmu_index(state, encode_sensor(chunk, cfg))] += 1

    state = run(cfg, N_TICKS_PER_CLASS, pink_train, state=_copy_state(state))
    cell_pink_visits = np.zeros(n_cells, dtype=np.int64)
    for k in range(n_chunks_per_class):
        chunk = pink_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        cell_pink_visits[_bmu_index(state, encode_sensor(chunk, cfg))] += 1

    cell_labels = np.where(cell_en_visits >= cell_pink_visits, 0, 1)

    acc_en = _classify(state, cell_labels, eng_test, cfg, 0)
    acc_pink = _classify(state, cell_labels, pink_test, cfg, 1)
    balanced = (acc_en + acc_pink) / 2

    return dict(
        n_cells=n_cells,
        n_en_cells=int((cell_labels == 0).sum()),
        n_pink_cells=int((cell_labels == 1).sum()),
        accuracy_en=acc_en, accuracy_pink=acc_pink,
        balanced_accuracy=balanced,
    )


def _verdict(s):
    pass_ = s["balanced_accuracy"] > T33_ACCURACY_MIN
    return {**s, "T33_pass": pass_}


def test_T33(substrates):
    m = _verdict(substrates)
    if not m["T33_pass"]:
        pytest.fail(
            f"BET-049 NULL T33 EN-vs-pink classification.\n"
            f"  acc_EN: {m['accuracy_en']:.4f}\n"
            f"  acc_pink: {m['accuracy_pink']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} (need > {T33_ACCURACY_MIN})\n"
            f"  EN-cells: {m['n_en_cells']}, pink-cells: {m['n_pink_cells']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T33_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-049",
        "verdict": verdict,
        "hypothesis": "T33 end-to-end EN-vs-pink-noise classification. Harder than BET-048 EN-vs-WN. Pink noise (1/f spectrum) more naturalistic. Bar: balanced accuracy > 0.6.",
        "thresholds": {"T33_accuracy_min": T33_ACCURACY_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

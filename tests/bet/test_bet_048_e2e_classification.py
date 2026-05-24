"""BET-048 — T32 end-to-end audio classification.

After 47 iterations testing substrate-properties in isolation, this
test integrates the substrate components into a working CLASSIFIER:

  Train: SOM+replay on EN + WN sequentially. Label each cell by
         majority training class (BET-040 mechanism).
  Test:  novel audio chunks → encode → BMU → vote based on cell-label.
         Compare to true class.

T32 bar (LOCKED):
  Classification accuracy on held-out balanced test set > 0.7
  (substrate as a working classifier achieves better than random)

Demonstrates pre-LLM substrate-pipeline as USABLE, not just measurable.
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

T32_ACCURACY_MIN = 0.7

OUT_DIR = Path.home() / ".eqmod/bet/BET-048"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


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
    """Classify each chunk via BMU lookup. Return accuracy."""
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
    wn_train = _make_wn(n_per, TARGET_RMS, WN_SEED)
    wn_test = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz

    # Train SOM+replay sequentially: EN then WN
    state = run(cfg, N_TICKS_PER_CLASS, eng_train)
    # Label cells visited during EN training
    cell_en_visits = np.zeros(n_cells, dtype=np.int64)
    n_chunks_train_per_class = n_per // SAMPLES_PER_TICK
    for k in range(n_chunks_train_per_class):
        chunk = eng_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        cell_en_visits[_bmu_index(state, encode_sensor(chunk, cfg))] += 1

    state = run(cfg, N_TICKS_PER_CLASS, wn_train, state=_copy_state(state))
    # Label cells visited during WN training
    cell_wn_visits = np.zeros(n_cells, dtype=np.int64)
    for k in range(n_chunks_train_per_class):
        chunk = wn_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        cell_wn_visits[_bmu_index(state, encode_sensor(chunk, cfg))] += 1

    # Cell labels: 0 = EN majority, 1 = WN majority
    cell_labels = np.where(cell_en_visits >= cell_wn_visits, 0, 1)

    # Classify novel test data
    acc_en = _classify(state, cell_labels, eng_test, cfg, true_class=0)
    acc_wn = _classify(state, cell_labels, wn_test, cfg, true_class=1)
    balanced_acc = (acc_en + acc_wn) / 2

    return dict(
        n_cells=n_cells,
        n_en_cells=int((cell_labels == 0).sum()),
        n_wn_cells=int((cell_labels == 1).sum()),
        accuracy_en=acc_en, accuracy_wn=acc_wn,
        balanced_accuracy=balanced_acc,
    )


def _verdict(s):
    pass_ = s["balanced_accuracy"] > T32_ACCURACY_MIN
    return {**s, "T32_pass": pass_}


def test_T32(substrates):
    m = _verdict(substrates)
    if not m["T32_pass"]:
        pytest.fail(
            f"BET-048 NULL T32 end-to-end classifier.\n"
            f"  acc_EN: {m['accuracy_en']:.4f}\n"
            f"  acc_WN: {m['accuracy_wn']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} "
            f"(need > {T32_ACCURACY_MIN})\n"
            f"  EN-cells: {m['n_en_cells']}, WN-cells: {m['n_wn_cells']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T32_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-048",
        "verdict": verdict,
        "hypothesis": "T32 end-to-end binary audio classification using substrate (SOM+replay trained sequentially EN+WN, cells labeled by majority training class, BMU vote). Demonstrates substrate as usable classifier.",
        "thresholds": {"T32_accuracy_min": T32_ACCURACY_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

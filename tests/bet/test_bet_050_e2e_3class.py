"""BET-050 — T34 end-to-end 3-class classification (EN + WN + pink).

Builds on BET-040 (T24 multi-class generation) + BET-048/049 (e2e
classification). Trains substrate sequentially on 3 classes with
replay-protection, classifies novel test set.

T34 bar (LOCKED):
  balanced accuracy across 3 classes > 0.5 (substantially better than
  chance which is 0.333 for 3-class).

Tests substrate's compositional capacity at 3 classes simultaneously.
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
PINK_SEED = 7777
PINK_TEST_SEED = 6666
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)

T34_ACCURACY_MIN = 0.5

OUT_DIR = Path.home() / ".eqmod/bet/BET-050"
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

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz
    n_chunks_per_class = n_per // SAMPLES_PER_TICK

    # Sequential training: EN, WN, pink with replay
    state = run(cfg, N_TICKS_PER_CLASS, eng_train)
    cell_en_visits = _count_visits(state, eng_train, cfg, n_cells, n_chunks_per_class)

    state = run(cfg, N_TICKS_PER_CLASS, wn_train, state=_copy_state(state))
    cell_wn_visits = _count_visits(state, wn_train, cfg, n_cells, n_chunks_per_class)

    state = run(cfg, N_TICKS_PER_CLASS, pink_train, state=_copy_state(state))
    cell_pink_visits = _count_visits(state, pink_train, cfg, n_cells, n_chunks_per_class)

    # 3-class cell labels: argmax of (en, wn, pink) visits
    visits_stack = np.stack([cell_en_visits, cell_wn_visits, cell_pink_visits], axis=1)
    cell_labels = visits_stack.argmax(axis=1)

    acc_en = _classify(state, cell_labels, eng_test, cfg, 0)
    acc_wn = _classify(state, cell_labels, wn_test, cfg, 1)
    acc_pink = _classify(state, cell_labels, pink_test, cfg, 2)
    balanced = (acc_en + acc_wn + acc_pink) / 3

    return dict(
        n_cells=n_cells,
        n_en_cells=int((cell_labels == 0).sum()),
        n_wn_cells=int((cell_labels == 1).sum()),
        n_pink_cells=int((cell_labels == 2).sum()),
        accuracy_en=acc_en, accuracy_wn=acc_wn, accuracy_pink=acc_pink,
        balanced_accuracy=balanced,
    )


def _verdict(s):
    return {**s, "T34_pass": s["balanced_accuracy"] > T34_ACCURACY_MIN}


def test_T34(substrates):
    m = _verdict(substrates)
    if not m["T34_pass"]:
        pytest.fail(
            f"BET-050 NULL T34 3-class.\n"
            f"  acc_EN: {m['accuracy_en']:.4f}\n"
            f"  acc_WN: {m['accuracy_wn']:.4f}\n"
            f"  acc_pink: {m['accuracy_pink']:.4f}\n"
            f"  balanced: {m['balanced_accuracy']:.4f} "
            f"(need > {T34_ACCURACY_MIN}, chance=0.333)\n"
            f"  cells: EN={m['n_en_cells']}, WN={m['n_wn_cells']}, pink={m['n_pink_cells']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T34_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-050",
        "verdict": verdict,
        "hypothesis": "T34 3-class end-to-end classification (EN/WN/pink). Substrate trained sequentially with replay, cells labeled by majority class, BMU-vote on test. Bar: balanced accuracy > 0.5 (chance=0.333).",
        "thresholds": {"T34_accuracy_min": T34_ACCURACY_MIN, "chance": 1/3},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

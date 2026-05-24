"""BET-053 — T37 cross-corpus-segment generalization.

Train substrate on first 10% of R-7 EN, test on last 10%. If R-7 has
acoustic non-stationarity (speakers change, topics shift, recording
conditions vary), substrate trained on slice-A might not generalize
to slice-Z.

Discrimination test still vs WN/pink (those don't change).

T37 bar (LOCKED): balanced 3-class accuracy on FAR-slice EN test
> 0.5 (still better than chance 0.333 even under distribution shift).
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

T37_ACCURACY_MIN = 0.5

OUT_DIR = Path.home() / ".eqmod/bet/BET-053"
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
    if 2 * n_per > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")

    # Train on FIRST 10% (or what fits), test on LAST 10%
    corpus_size = full.shape[0]
    # Training EN is from beginning
    eng_train = full[:n_per].astype(np.float64)
    # Test EN is from FAR END of corpus (different slice)
    eng_test_far = full[corpus_size - n_test:].astype(np.float64)
    # Also same-slice test for comparison
    eng_test_near = full[n_per:n_per + n_test].astype(np.float64)

    wn_train = _make_wn(n_per, TARGET_RMS, WN_SEED)
    wn_test = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)
    pink_train = _make_pink(n_per, TARGET_RMS, PINK_SEED)
    pink_test = _make_pink(n_test, TARGET_RMS, PINK_TEST_SEED)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz
    n_chunks_per_class = n_per // SAMPLES_PER_TICK

    state = run(cfg, N_TICKS_PER_CLASS, eng_train)
    cell_en = _count_visits(state, eng_train, cfg, n_cells, n_chunks_per_class)
    state = run(cfg, N_TICKS_PER_CLASS, wn_train, state=_copy_state(state))
    cell_wn = _count_visits(state, wn_train, cfg, n_cells, n_chunks_per_class)
    state = run(cfg, N_TICKS_PER_CLASS, pink_train, state=_copy_state(state))
    cell_pink = _count_visits(state, pink_train, cfg, n_cells, n_chunks_per_class)
    cell_labels = np.stack([cell_en, cell_wn, cell_pink], axis=1).argmax(axis=1)

    # Near-slice (comparison)
    acc_en_near = _classify(state, cell_labels, eng_test_near, cfg, 0)
    acc_wn = _classify(state, cell_labels, wn_test, cfg, 1)
    acc_pink = _classify(state, cell_labels, pink_test, cfg, 2)
    bal_near = (acc_en_near + acc_wn + acc_pink) / 3

    # Far-slice (the actual T37 test)
    acc_en_far = _classify(state, cell_labels, eng_test_far, cfg, 0)
    bal_far = (acc_en_far + acc_wn + acc_pink) / 3

    return dict(
        corpus_size=int(corpus_size),
        train_eng_offset=0, train_eng_n=n_per,
        test_eng_near_offset=n_per,
        test_eng_far_offset=int(corpus_size - n_test),
        accuracy_en_near=acc_en_near,
        accuracy_en_far=acc_en_far,
        accuracy_wn=acc_wn, accuracy_pink=acc_pink,
        balanced_near=bal_near,
        balanced_far=bal_far,
        accuracy_drop_pct=100 * (1 - bal_far / max(bal_near, 1e-9)),
    )


def _verdict(s):
    pass_ = s["balanced_far"] > T37_ACCURACY_MIN
    return {**s, "T37_pass": pass_}


def test_T37(substrates):
    m = _verdict(substrates)
    if not m["T37_pass"]:
        pytest.fail(
            f"BET-053 NULL T37 far-slice generalization.\n"
            f"  acc EN near: {m['accuracy_en_near']:.4f}\n"
            f"  acc EN far:  {m['accuracy_en_far']:.4f}\n"
            f"  balanced near: {m['balanced_near']:.4f}\n"
            f"  balanced far:  {m['balanced_far']:.4f} (need > {T37_ACCURACY_MIN})\n"
            f"  drop: {m['accuracy_drop_pct']:.1f}%"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T37_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-053",
        "verdict": verdict,
        "hypothesis": "T37 cross-corpus-segment generalization. Train on beginning of R-7, test on far end (different speakers/topics likely). Bar: balanced > 0.5.",
        "thresholds": {"T37_accuracy_min": T37_ACCURACY_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

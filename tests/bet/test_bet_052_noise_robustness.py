"""BET-052 — T36 feature-noise robustness.

Tests if substrate's end-to-end classifier degrades gracefully under
Gaussian feature noise. Real-world deployment condition.

Same protocol as BET-050 (3-class trained EN+WN+pink with replay)
but test-time: add Gaussian noise to each chunk's feature vector
before BMU lookup.

T36 bar (LOCKED):
  At noise sigma=0.1 (10% of feature range): balanced accuracy > 0.6
  At noise sigma=0.05 (5%): balanced accuracy > 0.8
  Both must pass.
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
NOISE_SEED = 12345
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)

T36_SIGMA_LOW = 0.05
T36_SIGMA_HIGH = 0.10
T36_ACC_LOW_MIN = 0.8
T36_ACC_HIGH_MIN = 0.6

OUT_DIR = Path.home() / ".eqmod/bet/BET-052"
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


def _classify_noisy(state, cell_labels, audio, cfg, true_class, sigma, seed):
    n = audio.size // cfg.samples_per_tick
    rng = np.random.default_rng(seed)
    correct = 0
    total = 0
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        noisy_sensor = sensor + rng.standard_normal(sensor.shape) * sigma
        if int(cell_labels[_bmu_index(state, noisy_sensor)]) == true_class:
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

    state = run(cfg, N_TICKS_PER_CLASS, eng_train)
    cell_en = _count_visits(state, eng_train, cfg, n_cells, n_chunks_per_class)
    state = run(cfg, N_TICKS_PER_CLASS, wn_train, state=_copy_state(state))
    cell_wn = _count_visits(state, wn_train, cfg, n_cells, n_chunks_per_class)
    state = run(cfg, N_TICKS_PER_CLASS, pink_train, state=_copy_state(state))
    cell_pink = _count_visits(state, pink_train, cfg, n_cells, n_chunks_per_class)
    cell_labels = np.stack([cell_en, cell_wn, cell_pink], axis=1).argmax(axis=1)

    # Noiseless baseline
    acc_en_0 = _classify_noisy(state, cell_labels, eng_test, cfg, 0, 0.0, NOISE_SEED)
    acc_wn_0 = _classify_noisy(state, cell_labels, wn_test, cfg, 1, 0.0, NOISE_SEED+1)
    acc_pink_0 = _classify_noisy(state, cell_labels, pink_test, cfg, 2, 0.0, NOISE_SEED+2)
    bal_0 = (acc_en_0 + acc_wn_0 + acc_pink_0) / 3

    # Low noise
    acc_en_low = _classify_noisy(state, cell_labels, eng_test, cfg, 0, T36_SIGMA_LOW, NOISE_SEED+3)
    acc_wn_low = _classify_noisy(state, cell_labels, wn_test, cfg, 1, T36_SIGMA_LOW, NOISE_SEED+4)
    acc_pink_low = _classify_noisy(state, cell_labels, pink_test, cfg, 2, T36_SIGMA_LOW, NOISE_SEED+5)
    bal_low = (acc_en_low + acc_wn_low + acc_pink_low) / 3

    # High noise
    acc_en_high = _classify_noisy(state, cell_labels, eng_test, cfg, 0, T36_SIGMA_HIGH, NOISE_SEED+6)
    acc_wn_high = _classify_noisy(state, cell_labels, wn_test, cfg, 1, T36_SIGMA_HIGH, NOISE_SEED+7)
    acc_pink_high = _classify_noisy(state, cell_labels, pink_test, cfg, 2, T36_SIGMA_HIGH, NOISE_SEED+8)
    bal_high = (acc_en_high + acc_wn_high + acc_pink_high) / 3

    return dict(
        n_cells=n_cells,
        balanced_noiseless=bal_0,
        balanced_low_sigma=bal_low,
        balanced_high_sigma=bal_high,
        sigma_low=T36_SIGMA_LOW, sigma_high=T36_SIGMA_HIGH,
    )


def _verdict(s):
    low_ok = s["balanced_low_sigma"] > T36_ACC_LOW_MIN
    high_ok = s["balanced_high_sigma"] > T36_ACC_HIGH_MIN
    return {**s, "T36_low_pass": low_ok, "T36_high_pass": high_ok,
            "T36_pass": low_ok and high_ok}


def test_T36(substrates):
    m = _verdict(substrates)
    if not m["T36_pass"]:
        pytest.fail(
            f"BET-052 NULL T36 noise robustness.\n"
            f"  baseline (sigma=0):    {m['balanced_noiseless']:.4f}\n"
            f"  low noise (sigma={T36_SIGMA_LOW}): {m['balanced_low_sigma']:.4f} "
            f"(need > {T36_ACC_LOW_MIN}) pass={m['T36_low_pass']}\n"
            f"  high noise (sigma={T36_SIGMA_HIGH}): {m['balanced_high_sigma']:.4f} "
            f"(need > {T36_ACC_HIGH_MIN}) pass={m['T36_high_pass']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T36_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-052",
        "verdict": verdict,
        "hypothesis": "T36 substrate noise robustness. 3-class classifier under Gaussian feature noise (sigma 0.05/0.1). Real-world deployment test.",
        "thresholds": {"T36_sigma_low": T36_SIGMA_LOW, "T36_sigma_high": T36_SIGMA_HIGH,
                       "T36_acc_low_min": T36_ACC_LOW_MIN, "T36_acc_high_min": T36_ACC_HIGH_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

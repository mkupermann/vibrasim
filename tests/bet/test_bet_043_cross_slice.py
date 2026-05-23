"""BET-043 — T27 bigram cross-slice consistency.

Tests whether substrate's bigram statistics REUSABLE across different
EN slices (general EN structure) vs slice-specific (memorization).

Protocol:
  1. Train SOM (100 cells) on EN slice 1 → bigram_1
  2. Train fresh SOM on EN slice 2 → bigram_2
  3. Train fresh SOM on WN → bigram_wn (negative control)
  4. Compare bigram_1 vs bigram_2 (same-class) and bigram_1 vs bigram_wn
     (cross-class) via average row-KL.

T27 bar (LOCKED):
  KL(bigram_1, bigram_2) < 0.5 * KL(bigram_1, bigram_wn)
  (same-class bigrams more similar than cross-class)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, run
from world.flux.cognitive_map import encode_sensor

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)

OUT_DIR = Path.home() / ".eqmod/bet/BET-043"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _quantize(state, audio, cfg):
    n = audio.size // cfg.samples_per_tick
    tokens = np.zeros(n, dtype=np.int64)
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        diff = state["w"] - sensor
        tokens[k] = int(np.argmin(np.einsum("ijkl,ijkl->ijk", diff, diff)))
    return tokens


def _bigram(tokens, n_cells, alpha=0.01):
    B = np.zeros((n_cells, n_cells), dtype=np.float64)
    for t in range(tokens.size - 1):
        B[tokens[t], tokens[t + 1]] += 1
    B += alpha
    return B / B.sum(axis=1, keepdims=True)


def _bigram_kl(B1, B2):
    """Symmetric row-averaged KL."""
    eps = 1e-30
    kl1 = np.sum(B1 * np.log((B1 + eps) / (B2 + eps)), axis=1)
    kl2 = np.sum(B2 * np.log((B2 + eps) / (B1 + eps)), axis=1)
    return float(0.5 * (kl1.mean() + kl2.mean()))


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, grid_dims=GRID_DIMS,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if 2 * n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_1 = full[:n_audio].astype(np.float64)
    eng_2 = full[n_audio:2 * n_audio].astype(np.float64)
    wn = _make_wn(n_audio, TARGET_RMS, WN_SEED)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz

    s1 = run(cfg, N_TICKS, eng_1)
    s2 = run(cfg, N_TICKS, eng_2)
    swn = run(cfg, N_TICKS, wn)

    t1 = _quantize(s1, eng_1, cfg)
    t2 = _quantize(s2, eng_2, cfg)
    twn = _quantize(swn, wn, cfg)

    b1 = _bigram(t1, n_cells)
    b2 = _bigram(t2, n_cells)
    bwn = _bigram(twn, n_cells)

    kl_same_class = _bigram_kl(b1, b2)
    kl_cross_class_1 = _bigram_kl(b1, bwn)
    kl_cross_class_2 = _bigram_kl(b2, bwn)
    kl_cross_class_avg = 0.5 * (kl_cross_class_1 + kl_cross_class_2)

    return dict(
        n_cells=n_cells,
        kl_same_class=kl_same_class,
        kl_cross_class_1=kl_cross_class_1,
        kl_cross_class_2=kl_cross_class_2,
        kl_cross_class_avg=kl_cross_class_avg,
        ratio_same_over_cross=kl_same_class / max(kl_cross_class_avg, 1e-9),
    )


def test_T27(substrates):
    s = substrates
    # Pass: same-class < 0.5 * cross-class
    pass_ = s["ratio_same_over_cross"] < 0.5
    if not pass_:
        pytest.fail(
            f"BET-043 NULL T27 cross-slice consistency.\n"
            f"  KL(EN_slice1, EN_slice2) = {s['kl_same_class']:.4f}\n"
            f"  KL(EN_slice1, WN) = {s['kl_cross_class_1']:.4f}\n"
            f"  KL(EN_slice2, WN) = {s['kl_cross_class_2']:.4f}\n"
            f"  ratio same/cross-avg = {s['ratio_same_over_cross']:.4f} "
            f"(need < 0.5)"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    s = substrates
    pass_ = s["ratio_same_over_cross"] < 0.5
    verdict = "passed" if pass_ else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-043",
        "verdict": verdict,
        "hypothesis": "T27 bigram cross-slice consistency. Same-class bigrams should be more similar than cross-class.",
        "thresholds": {"T27_ratio_max": 0.5},
        "measurements": {**s, "T27_pass": pass_},
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

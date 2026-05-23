"""BET-034 — N-gram with smaller SOM vocab.

BET-033 NULL because 3600-token vocab from 10k training chunks gives
sparse bigram matrix → smoothing noise dominates. Standard NLM
practice: vocab size << sqrt(training data).

For 10k training chunks, ideal vocab is ~100 tokens (10k transitions
to estimate ~10k bigram cells). Use SOM grid 10×10×1 = 100 cells.

T21 perplexity bar (LOCKED, same as BET-033):
  bigram_PPL / unigram_PPL < 0.7
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
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)  # 100 cells, much smaller than (30,15,8)=3600

T21_RATIO_MAX = 0.7

OUT_DIR = Path.home() / ".eqmod/bet/BET-034"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


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


def _bigram(tokens, n_cells, smoothing=0.01):
    B = np.zeros((n_cells, n_cells), dtype=np.float64)
    for t in range(tokens.size - 1):
        B[tokens[t], tokens[t + 1]] += 1
    B += smoothing
    return B / B.sum(axis=1, keepdims=True)


def _unigram(tokens, n_cells, smoothing=0.01):
    counts = np.bincount(tokens, minlength=n_cells).astype(np.float64) + smoothing
    return counts / counts.sum()


def _ppl_bi(tokens, P, U):
    log_probs = np.log(U[tokens[0]] + 1e-30)
    for t in range(tokens.size - 1):
        log_probs += np.log(P[tokens[t], tokens[t + 1]] + 1e-30)
    return float(np.exp(-log_probs / tokens.size))


def _ppl_uni(tokens, U):
    return float(np.exp(-np.sum(np.log(U[tokens] + 1e-30)) / tokens.size))


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
    eng_train = full[:n_audio].astype(np.float64)
    eng_held = full[n_audio:2 * n_audio].astype(np.float64)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz  # 100

    state = run(cfg, N_TICKS, eng_train)
    train_tokens = _quantize(state, eng_train, cfg)
    held_tokens = _quantize(state, eng_held, cfg)

    P_bi = _bigram(train_tokens, n_cells)
    U = _unigram(train_tokens, n_cells)
    ppl_uni = _ppl_uni(held_tokens, U)
    ppl_bi = _ppl_bi(held_tokens, P_bi, U)

    return dict(
        n_cells=n_cells,
        n_train_tokens=int(train_tokens.size),
        n_held_tokens=int(held_tokens.size),
        n_unique_train=int(np.unique(train_tokens).size),
        n_unique_held=int(np.unique(held_tokens).size),
        ppl_unigram=ppl_uni,
        ppl_bigram=ppl_bi,
        perplexity_ratio=ppl_bi / ppl_uni,
    )


def test_T21_small_vocab(substrates):
    s = substrates
    if s["perplexity_ratio"] >= T21_RATIO_MAX:
        pytest.fail(
            f"BET-034 NULL T21 small vocab.\n"
            f"  n_cells: {s['n_cells']}, unique trained: {s['n_unique_train']}\n"
            f"  ppl_unigram: {s['ppl_unigram']:.4f}\n"
            f"  ppl_bigram:  {s['ppl_bigram']:.4f}\n"
            f"  ratio: {s['perplexity_ratio']:.4f} (need < {T21_RATIO_MAX})"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    s = substrates
    pass_ = s["perplexity_ratio"] < T21_RATIO_MAX
    verdict = "passed" if pass_ else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-034",
        "verdict": verdict,
        "hypothesis": "T21 perplexity reduction at smaller vocab (10x10x1=100 cells). Addresses BET-033 data sparsity (3600 vocab on 10k tokens).",
        "thresholds": {"T21_ratio_max": T21_RATIO_MAX},
        "measurements": {**s, "T21_pass": pass_},
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

"""BET-033 — bigram perplexity vs unigram perplexity on SOM-tokens.

BET-032 NULL because top-1 bigram dominated by marginal frequency.
Standard N-gram-LM metric is perplexity (or equivalently cross-entropy):

  PPL = exp(-1/N sum_t log P(token_t | history))

Lower perplexity = better predictive model. Bigram PPL < Unigram PPL
shows bigram uses temporal info beyond marginal distribution.

T21 bar (LOCKED):
  bigram_perplexity / unigram_perplexity < 0.7
  (bigram captures substantial temporal info: 30%+ perplexity reduction)
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

T21_RATIO_MAX = 0.7

OUT_DIR = Path.home() / ".eqmod/bet/BET-033"
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


def _perplexity_bigram(tokens, P, U):
    """Bigram perplexity on held-out tokens. Use unigram for first token."""
    n = tokens.size - 1
    log_probs = np.log(U[tokens[0]] + 1e-30)
    for t in range(n):
        log_probs += np.log(P[tokens[t], tokens[t + 1]] + 1e-30)
    return float(np.exp(-log_probs / tokens.size))


def _perplexity_unigram(tokens, U):
    log_probs = np.sum(np.log(U[tokens] + 1e-30))
    return float(np.exp(-log_probs / tokens.size))


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if 2 * n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)
    eng_held = full[n_audio:2 * n_audio].astype(np.float64)

    Lx, Ly, Lz = cfg.grid_dims
    n_cells = Lx * Ly * Lz

    state = run(cfg, N_TICKS, eng_train)
    train_tokens = _quantize(state, eng_train, cfg)
    held_tokens = _quantize(state, eng_held, cfg)

    P_bi = _bigram(train_tokens, n_cells)
    U = _unigram(train_tokens, n_cells)

    ppl_unigram = _perplexity_unigram(held_tokens, U)
    ppl_bigram = _perplexity_bigram(held_tokens, P_bi, U)
    perplexity_ratio = ppl_bigram / ppl_unigram

    return dict(
        n_cells=n_cells,
        n_train_tokens=int(train_tokens.size),
        n_held_tokens=int(held_tokens.size),
        n_unique_train=int(np.unique(train_tokens).size),
        n_unique_held=int(np.unique(held_tokens).size),
        ppl_unigram=ppl_unigram, ppl_bigram=ppl_bigram,
        perplexity_ratio=perplexity_ratio,
        cross_entropy_unigram_nats=float(np.log(ppl_unigram)),
        cross_entropy_bigram_nats=float(np.log(ppl_bigram)),
    )


def test_T21(substrates):
    s = substrates
    if s["perplexity_ratio"] >= T21_RATIO_MAX:
        pytest.fail(
            f"BET-033 NULL T21 perplexity.\n"
            f"  unigram perplexity: {s['ppl_unigram']:.4f}\n"
            f"  bigram perplexity:  {s['ppl_bigram']:.4f}\n"
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
        "item_id": "BET-033",
        "verdict": verdict,
        "hypothesis": "T21 bigram perplexity reduction over unigram baseline on SOM-tokens. Standard NLM metric for temporal info content.",
        "thresholds": {"T21_ratio_max": T21_RATIO_MAX},
        "measurements": {**s, "T21_pass": pass_},
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

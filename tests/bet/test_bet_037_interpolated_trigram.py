"""BET-037 — T23 trigram with interpolated backoff.

BET-036 NULL because pure trigram over-fits on sparse contexts (3760
unique contexts from 10k tokens). Standard fix (Jelinek & Mercer 1980,
pre-LLM): interpolate trigram + bigram + unigram with mixture weights.

  P(z|xy) = lambda3 * P_tri(z|xy) + lambda2 * P_bi(z|y) + lambda1 * P_uni(z)

Locked weights pre-data: lambda3=0.5, lambda2=0.3, lambda1=0.2.

T23-interp bar (LOCKED):
  interpolated_trigram_PPL / bigram_PPL < 0.95
  (mild improvement; bigram is already strong at this scale)
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
GRID_DIMS = (10, 10, 1)

LAMBDA_TRI = 0.5
LAMBDA_BI = 0.3
LAMBDA_UNI = 0.2
T23_RATIO_MAX = 0.95

OUT_DIR = Path.home() / ".eqmod/bet/BET-037"
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


def _bigram(tokens, n_cells, alpha=0.01):
    B = np.zeros((n_cells, n_cells), dtype=np.float64)
    for t in range(tokens.size - 1):
        B[tokens[t], tokens[t + 1]] += 1
    B += alpha
    return B / B.sum(axis=1, keepdims=True)


def _trigram(tokens, n_cells):
    """Returns dict (x,y) -> array of counts over next token (n_cells,)."""
    counts = {}
    for t in range(tokens.size - 2):
        ctx = (int(tokens[t]), int(tokens[t + 1]))
        if ctx not in counts:
            counts[ctx] = np.zeros(n_cells, dtype=np.float64)
        counts[ctx][int(tokens[t + 2])] += 1
    # Convert to probability with Laplace
    probs = {}
    for ctx, c in counts.items():
        c_smooth = c + 0.01
        probs[ctx] = c_smooth / c_smooth.sum()
    return probs


def _interp_prob(tri_probs, ctx, z, P_bi, U, n_cells):
    """Interpolated P(z | ctx)."""
    p_uni = U[z]
    p_bi = P_bi[ctx[1], z]
    if ctx in tri_probs:
        p_tri = tri_probs[ctx][z]
    else:
        p_tri = 1.0 / n_cells
    return LAMBDA_TRI * p_tri + LAMBDA_BI * p_bi + LAMBDA_UNI * p_uni


def _ppl_interp(tokens, tri_probs, P_bi, U, n_cells):
    """Interpolated trigram perplexity on held-out tokens."""
    log_probs = np.log(U[tokens[0]] + 1e-30)
    log_probs += np.log(P_bi[tokens[0], tokens[1]] + 1e-30)
    for t in range(tokens.size - 2):
        ctx = (int(tokens[t]), int(tokens[t + 1]))
        z = int(tokens[t + 2])
        p = _interp_prob(tri_probs, ctx, z, P_bi, U, n_cells)
        log_probs += np.log(p + 1e-30)
    return float(np.exp(-log_probs / tokens.size))


def _ppl_bi(tokens, P, U):
    lp = np.log(U[tokens[0]] + 1e-30)
    for t in range(tokens.size - 1):
        lp += np.log(P[tokens[t], tokens[t + 1]] + 1e-30)
    return float(np.exp(-lp / tokens.size))


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
    n_cells = Lx * Ly * Lz

    state = run(cfg, N_TICKS, eng_train)
    train_tokens = _quantize(state, eng_train, cfg)
    held_tokens = _quantize(state, eng_held, cfg)

    counts = np.bincount(train_tokens, minlength=n_cells).astype(np.float64) + 0.01
    U = counts / counts.sum()
    P_bi = _bigram(train_tokens, n_cells)
    tri_probs = _trigram(train_tokens, n_cells)

    ppl_bi = _ppl_bi(held_tokens, P_bi, U)
    ppl_interp = _ppl_interp(held_tokens, tri_probs, P_bi, U, n_cells)
    ratio = ppl_interp / ppl_bi

    return dict(
        n_cells=n_cells,
        n_train_tokens=int(train_tokens.size),
        n_held_tokens=int(held_tokens.size),
        n_trigram_contexts=len(tri_probs),
        ppl_bigram=ppl_bi,
        ppl_interpolated_trigram=ppl_interp,
        interp_over_bi_ratio=ratio,
    )


def test_T23_interp(substrates):
    s = substrates
    if s["interp_over_bi_ratio"] >= T23_RATIO_MAX:
        pytest.fail(
            f"BET-037 NULL T23 interpolated.\n"
            f"  ppl_bigram:     {s['ppl_bigram']:.4f}\n"
            f"  ppl_interp_tri: {s['ppl_interpolated_trigram']:.4f}\n"
            f"  ratio: {s['interp_over_bi_ratio']:.4f} (need < {T23_RATIO_MAX})"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    s = substrates
    pass_ = s["interp_over_bi_ratio"] < T23_RATIO_MAX
    verdict = "passed" if pass_ else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-037",
        "verdict": verdict,
        "hypothesis": "T23 interpolated trigram with Jelinek-Mercer mixing (tri 0.5 / bi 0.3 / uni 0.2). Tests multi-step temporal info beyond bigram on sparse data.",
        "thresholds": {"T23_ratio_max": T23_RATIO_MAX,
                       "lambdas": [LAMBDA_TRI, LAMBDA_BI, LAMBDA_UNI]},
        "measurements": {**s, "T23_pass": pass_},
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

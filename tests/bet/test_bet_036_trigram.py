"""BET-036 — T23 trigram perplexity reduction.

After BET-034 (bigram 41% PPL reduction) + BET-035 (generation works),
test if substrate has multi-step temporal structure (longer-than-pair
context).

If trigram further reduces PPL, sequence captures 3-token dependencies
beyond 2-token. If not, audio-token statistics are essentially pairwise.

T23 bar (LOCKED):
  trigram_PPL / bigram_PPL < 0.85
  (trigram must capture 15%+ additional PPL reduction beyond bigram)

At 100-vocab × 10000 tokens, trigram has 100^2=10000 contexts and
about 10000 observations → ~1 observation per context on average.
Smoothing matters; Laplace smoothing applied (alpha=0.01).
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

T23_RATIO_MAX = 0.85

OUT_DIR = Path.home() / ".eqmod/bet/BET-036"
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


def _trigram_dict(tokens, alpha=0.01):
    """Trigram as nested dict: tri[(t-2, t-1)][t] = count.
    Returns: dict of context -> normalized prob dict."""
    counts = {}
    for t in range(tokens.size - 2):
        ctx = (int(tokens[t]), int(tokens[t + 1]))
        nxt = int(tokens[t + 2])
        if ctx not in counts:
            counts[ctx] = np.zeros(0)  # placeholder, replaced
        if not isinstance(counts[ctx], dict):
            counts[ctx] = {}
        counts[ctx][nxt] = counts[ctx].get(nxt, 0) + 1
    return counts


def _trigram_prob(tri_counts, ctx, next_tok, n_cells, alpha):
    """P(next_tok | ctx) with Laplace smoothing."""
    if ctx in tri_counts:
        ctx_counts = tri_counts[ctx]
        total = sum(ctx_counts.values()) + alpha * n_cells
        return (ctx_counts.get(next_tok, 0) + alpha) / total
    else:
        # unseen context — fall back to uniform
        return 1.0 / n_cells


def _ppl_trigram(tokens, tri_counts, P_bi, U, n_cells, alpha=0.01):
    """Trigram PPL: first token unigram, second bigram, rest trigram."""
    log_probs = np.log(U[tokens[0]] + 1e-30)
    log_probs += np.log(P_bi[tokens[0], tokens[1]] + 1e-30)
    for t in range(tokens.size - 2):
        ctx = (int(tokens[t]), int(tokens[t + 1]))
        p = _trigram_prob(tri_counts, ctx, int(tokens[t + 2]), n_cells, alpha)
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

    counts_uni = np.bincount(train_tokens, minlength=n_cells).astype(np.float64) + 0.01
    U = counts_uni / counts_uni.sum()
    P_bi = _bigram(train_tokens, n_cells)
    tri_counts = _trigram_dict(train_tokens)

    ppl_bi = _ppl_bi(held_tokens, P_bi, U)
    ppl_tri = _ppl_trigram(held_tokens, tri_counts, P_bi, U, n_cells)

    return dict(
        n_cells=n_cells,
        n_train_tokens=int(train_tokens.size),
        n_held_tokens=int(held_tokens.size),
        n_unique_trigram_contexts=len(tri_counts),
        ppl_bigram=ppl_bi,
        ppl_trigram=ppl_tri,
        trigram_over_bigram_ratio=ppl_tri / ppl_bi,
    )


def test_T23(substrates):
    s = substrates
    if s["trigram_over_bigram_ratio"] >= T23_RATIO_MAX:
        pytest.fail(
            f"BET-036 NULL T23 trigram.\n"
            f"  ppl_bigram:  {s['ppl_bigram']:.4f}\n"
            f"  ppl_trigram: {s['ppl_trigram']:.4f}\n"
            f"  ratio:       {s['trigram_over_bigram_ratio']:.4f} (need < {T23_RATIO_MAX})\n"
            f"  unique trigram contexts: {s['n_unique_trigram_contexts']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    s = substrates
    pass_ = s["trigram_over_bigram_ratio"] < T23_RATIO_MAX
    verdict = "passed" if pass_ else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-036",
        "verdict": verdict,
        "hypothesis": "T23 trigram further perplexity reduction over bigram (>15%). Tests multi-step temporal structure beyond pairwise.",
        "thresholds": {"T23_ratio_max": T23_RATIO_MAX},
        "measurements": {**s, "T23_pass": pass_},
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

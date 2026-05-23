"""BET-035 — T22 substrate generation via bigram sampling.

After BET-034 PASS (bigram captures 41% perplexity reduction at vocab=100),
test substrate's GENERATIVE capability: sample new token sequences via
bigram model, compare statistics to training distribution.

Protocol:
  1. Train SOM (10×10×1=100 cells) + bigram on EN audio.
  2. Sample N=10000 new tokens via bigram Monte Carlo:
     start with random token; then token_t+1 ~ P(. | token_t).
  3. Compute generated token marginal distribution.
  4. Compare to training token marginal: KL.
  5. Compute generated bigram transition statistics.
  6. Compare to training bigram statistics: KL.

T22 bar (LOCKED):
  KL(generated unigram, training unigram) < 0.5 (generation matches
                                                  learned marginal)
  KL(generated bigram, training bigram) < 0.5 (generation matches
                                                learned transitions)

If T22 PASSES: substrate AUTONOMOUSLY GENERATES sequences that carry
its learned statistics. This is generative communication: substrate
"speaks" what it learned, not just retrieves stored chunks.
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
N_GENERATE = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)  # 100-cell vocab (from BET-034)
GEN_SEED = 5555

T22_UNIGRAM_KL_MAX = 0.5
T22_BIGRAM_KL_MAX = 0.5

OUT_DIR = Path.home() / ".eqmod/bet/BET-035"
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


def _generate(P_bigram, n_tokens, n_cells, seed):
    """Bigram Monte Carlo sampling."""
    rng = np.random.default_rng(seed)
    tokens = np.zeros(n_tokens, dtype=np.int64)
    tokens[0] = rng.integers(0, n_cells)
    for t in range(1, n_tokens):
        tokens[t] = rng.choice(n_cells, p=P_bigram[tokens[t - 1]])
    return tokens


def _kl_categorical(p, q, eps=1e-30):
    """KL(p || q) symmetric."""
    p_s = p + eps
    q_s = q + eps
    return 0.5 * (float(np.sum(p_s * np.log(p_s / q_s))) +
                  float(np.sum(q_s * np.log(q_s / p_s))))


def _kl_matrix(P, Q):
    """Average row-wise KL between two transition matrices."""
    row_kls = []
    for i in range(P.shape[0]):
        if P[i].sum() > 0 and Q[i].sum() > 0:
            row_kls.append(_kl_categorical(P[i], Q[i]))
    return float(np.mean(row_kls)) if row_kls else 0.0


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
    if n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz

    state = run(cfg, N_TICKS, eng_train)
    train_tokens = _quantize(state, eng_train, cfg)

    P_bi_train = _bigram(train_tokens, n_cells)
    U_train = _unigram(train_tokens, n_cells)

    # Generate
    gen_tokens = _generate(P_bi_train, N_GENERATE, n_cells, GEN_SEED)
    U_gen = _unigram(gen_tokens, n_cells)
    P_bi_gen = _bigram(gen_tokens, n_cells)

    kl_unigram = _kl_categorical(U_gen, U_train)
    kl_bigram = _kl_matrix(P_bi_gen, P_bi_train)

    return dict(
        n_cells=n_cells, n_train_tokens=int(train_tokens.size),
        n_generated=int(gen_tokens.size),
        n_unique_train=int(np.unique(train_tokens).size),
        n_unique_generated=int(np.unique(gen_tokens).size),
        kl_unigram_gen_vs_train=kl_unigram,
        kl_bigram_gen_vs_train=kl_bigram,
        T22_unigram_pass=(kl_unigram < T22_UNIGRAM_KL_MAX),
        T22_bigram_pass=(kl_bigram < T22_BIGRAM_KL_MAX),
    )


def test_T22(substrates):
    s = substrates
    pass_ = s["T22_unigram_pass"] and s["T22_bigram_pass"]
    if not pass_:
        pytest.fail(
            f"BET-035 NULL T22 generation.\n"
            f"  KL(gen unigram, train unigram) = {s['kl_unigram_gen_vs_train']:.4f} "
            f"(need < {T22_UNIGRAM_KL_MAX}) pass={s['T22_unigram_pass']}\n"
            f"  KL(gen bigram, train bigram) = {s['kl_bigram_gen_vs_train']:.4f} "
            f"(need < {T22_BIGRAM_KL_MAX}) pass={s['T22_bigram_pass']}\n"
            f"  unique tokens train={s['n_unique_train']}, generated={s['n_unique_generated']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    s = substrates
    pass_ = s["T22_unigram_pass"] and s["T22_bigram_pass"]
    verdict = "passed" if pass_ else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-035",
        "verdict": verdict,
        "hypothesis": "T22 substrate generation: bigram-sampled token sequence matches training token distribution (unigram + bigram KL). Generative communication.",
        "thresholds": {"T22_unigram_kl_max": T22_UNIGRAM_KL_MAX, "T22_bigram_kl_max": T22_BIGRAM_KL_MAX},
        "measurements": s,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

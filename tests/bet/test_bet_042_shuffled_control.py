"""BET-042 — T26 shuffled-token negative control for T21.

CRITICAL hostile-reader test. BET-034/039 PASSED with 41-67% PPL
reduction. Is this REALLY temporal structure, or is it some other
artifact (e.g., overfitting)?

Test: shuffle training token order before building bigram. If bigram
still gives substantial PPL reduction on held-out, then T21 isn't
measuring temporal structure — it's measuring something else.

If bigram on SHUFFLED training gives PPL ratio ≈ 1.0 on held-out
(no improvement over unigram), then T21 IS validating temporal
structure.

T26 bar (LOCKED):
  shuffled_bigram_PPL / unigram_PPL > 0.95
  (shuffled bigram doesn't capture meaningful PPL reduction)

Plus reports the trained-bigram ratio for comparison.
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
SHUFFLE_SEED = 42

T26_SHUFFLED_RATIO_MIN = 0.95

OUT_DIR = Path.home() / ".eqmod/bet/BET-042"
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


def _unigram(tokens, n_cells, alpha=0.01):
    counts = np.bincount(tokens, minlength=n_cells).astype(np.float64) + alpha
    return counts / counts.sum()


def _ppl_bi(tokens, P, U):
    lp = np.log(U[tokens[0]] + 1e-30)
    for t in range(tokens.size - 1):
        lp += np.log(P[tokens[t], tokens[t + 1]] + 1e-30)
    return float(np.exp(-lp / tokens.size))


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
    n_cells = Lx * Ly * Lz

    state = run(cfg, N_TICKS, eng_train)
    train_tokens = _quantize(state, eng_train, cfg)
    held_tokens = _quantize(state, eng_held, cfg)

    # Shuffle training token order
    rng = np.random.default_rng(SHUFFLE_SEED)
    shuffled_tokens = train_tokens.copy()
    rng.shuffle(shuffled_tokens)

    U = _unigram(train_tokens, n_cells)
    P_bi_trained = _bigram(train_tokens, n_cells)
    P_bi_shuffled = _bigram(shuffled_tokens, n_cells)

    ppl_uni = _ppl_uni(held_tokens, U)
    ppl_bi_trained = _ppl_bi(held_tokens, P_bi_trained, U)
    ppl_bi_shuffled = _ppl_bi(held_tokens, P_bi_shuffled, U)

    return dict(
        n_cells=n_cells,
        n_train_tokens=int(train_tokens.size),
        n_held_tokens=int(held_tokens.size),
        ppl_unigram=ppl_uni,
        ppl_bigram_trained=ppl_bi_trained,
        ppl_bigram_shuffled=ppl_bi_shuffled,
        trained_ratio=ppl_bi_trained / ppl_uni,
        shuffled_ratio=ppl_bi_shuffled / ppl_uni,
    )


def test_T26(substrates):
    s = substrates
    # Shuffled bigram must NOT show meaningful PPL reduction
    if s["shuffled_ratio"] < T26_SHUFFLED_RATIO_MIN:
        pytest.fail(
            f"BET-042 NULL T26: shuffled bigram unexpectedly reduces PPL.\n"
            f"  trained bigram ratio: {s['trained_ratio']:.4f}\n"
            f"  shuffled bigram ratio: {s['shuffled_ratio']:.4f} "
            f"(need >= {T26_SHUFFLED_RATIO_MIN})\n"
            f"  → T21 finding is NOT validated as temporal!"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    s = substrates
    pass_ = s["shuffled_ratio"] >= T26_SHUFFLED_RATIO_MIN
    verdict = "passed" if pass_ else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-042",
        "verdict": verdict,
        "hypothesis": "T26 shuffled-token negative control for T21 temporal-info claim. If shuffled bigram doesn't reduce PPL, T21 IS measuring temporal structure.",
        "thresholds": {"T26_shuffled_ratio_min": T26_SHUFFLED_RATIO_MIN},
        "measurements": {**s, "T26_pass": pass_},
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

"""BET-038 — scale test: 400-vocab SOM + bigram on 50k training tokens.

BET-034/037 PASSED at small scale (100 vocab, 10k tokens). Tests if
substrate's temporal-info finding scales with more training + larger vocab.

400 vocab needs ~400^2 / 50k = 3.2 obs per transition on average, vs
BET-034's 100^2/10k = 1.0 obs. Should still allow bigram to work.

T21 bar (LOCKED, same as BET-034):
  bigram_PPL / unigram_PPL < 0.7

Also reports raw PPL values for comparison with BET-034.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, run
from world.flux.cognitive_map import encode_sensor

N_TICKS = 50_000  # 5x BET-034
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
TARGET_RMS = 0.25
GRID_DIMS = (20, 10, 2)  # 400 cells, 4x BET-034

T21_RATIO_MAX = 0.7

OUT_DIR = Path.home() / ".eqmod/bet/BET-038"
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

    P_bi = _bigram(train_tokens, n_cells)
    U = _unigram(train_tokens, n_cells)
    ppl_uni = _ppl_uni(held_tokens, U)
    ppl_bi = _ppl_bi(held_tokens, P_bi, U)

    return dict(
        n_cells=n_cells,
        n_train_tokens=int(train_tokens.size),
        n_held_tokens=int(held_tokens.size),
        n_unique_train=int(np.unique(train_tokens).size),
        ppl_unigram=ppl_uni,
        ppl_bigram=ppl_bi,
        ratio=ppl_bi / ppl_uni,
    )


def test_T21_scaled(substrates):
    s = substrates
    if s["ratio"] >= T21_RATIO_MAX:
        pytest.fail(
            f"BET-038 NULL scale test.\n"
            f"  n_cells={s['n_cells']} (vocab), n_train={s['n_train_tokens']}\n"
            f"  unique_trained: {s['n_unique_train']}\n"
            f"  ppl_unigram: {s['ppl_unigram']:.4f}\n"
            f"  ppl_bigram:  {s['ppl_bigram']:.4f}\n"
            f"  ratio: {s['ratio']:.4f} (need < {T21_RATIO_MAX})"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    s = substrates
    pass_ = s["ratio"] < T21_RATIO_MAX
    verdict = "passed" if pass_ else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-038",
        "verdict": verdict,
        "hypothesis": "T21 scale test: 400-vocab SOM + bigram on 50k training tokens. Tests substrate scaling beyond BET-034's small-scale finding.",
        "thresholds": {"T21_ratio_max": T21_RATIO_MAX},
        "measurements": {**s, "T21_pass": pass_},
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

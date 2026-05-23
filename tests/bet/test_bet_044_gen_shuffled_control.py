"""BET-044 — T28 shuffled-bigram generation negative control.

Validates BET-035 T22 finding (substrate generates sequences matching
learned statistics). If we generate from SHUFFLED-tokens bigram, the
generated sequence's bigram should NOT match training bigram (because
shuffled bigram has no real transition structure).

T28 bar (LOCKED):
  KL(gen-shuffled bigram, training bigram) > 0.5 * KL(gen-trained bigram,
                                                       training bigram-shuffled)
  AND KL(gen-shuffled bigram, training bigram) > KL(gen-trained bigram,
                                                     training bigram)

Tests that T22's match is NOT trivially achieved by random bigrams.
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
N_GEN = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)
SHUFFLE_SEED = 42
GEN_SEED = 5555

OUT_DIR = Path.home() / ".eqmod/bet/BET-044"
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


def _generate(P, n_tokens, n_cells, seed):
    rng = np.random.default_rng(seed)
    tokens = np.zeros(n_tokens, dtype=np.int64)
    tokens[0] = rng.integers(0, n_cells)
    for t in range(1, n_tokens):
        tokens[t] = rng.choice(n_cells, p=P[tokens[t - 1]])
    return tokens


def _bigram_kl(B1, B2):
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
    if n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz

    state = run(cfg, N_TICKS, eng_train)
    train_tokens = _quantize(state, eng_train, cfg)

    # Trained-bigram
    P_trained = _bigram(train_tokens, n_cells)

    # Shuffled-bigram (negative control)
    rng = np.random.default_rng(SHUFFLE_SEED)
    shuffled_tokens = train_tokens.copy()
    rng.shuffle(shuffled_tokens)
    P_shuffled = _bigram(shuffled_tokens, n_cells)

    # Generation: from trained bigram (T22 baseline) AND from shuffled bigram (negative)
    gen_from_trained = _generate(P_trained, N_GEN, n_cells, GEN_SEED)
    gen_from_shuffled = _generate(P_shuffled, N_GEN, n_cells, GEN_SEED)

    # Build bigrams of generated sequences
    P_gen_trained = _bigram(gen_from_trained, n_cells)
    P_gen_shuffled = _bigram(gen_from_shuffled, n_cells)

    # KLs against TRAINED bigram (the "truth")
    kl_gen_trained = _bigram_kl(P_gen_trained, P_trained)
    kl_gen_shuffled = _bigram_kl(P_gen_shuffled, P_trained)

    return dict(
        n_cells=n_cells, n_train=int(train_tokens.size),
        n_gen=N_GEN,
        kl_gen_from_trained_vs_trained=kl_gen_trained,
        kl_gen_from_shuffled_vs_trained=kl_gen_shuffled,
        validation_ratio=kl_gen_shuffled / max(kl_gen_trained, 1e-9),
    )


def test_T28(substrates):
    s = substrates
    pass_ = s["validation_ratio"] > 2.0
    if not pass_:
        pytest.fail(
            f"BET-044 NULL T28 gen-shuffled validation.\n"
            f"  KL(gen-from-trained, trained): {s['kl_gen_from_trained_vs_trained']:.4f}\n"
            f"  KL(gen-from-shuffled, trained): {s['kl_gen_from_shuffled_vs_trained']:.4f}\n"
            f"  validation ratio: {s['validation_ratio']:.4f} (need > 2.0)"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    s = substrates
    pass_ = s["validation_ratio"] > 2.0
    verdict = "passed" if pass_ else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-044",
        "verdict": verdict,
        "hypothesis": "T28 generation shuffled-control. Validates T22 isn't trivial: shuffled-bigram-gen should fit training bigram WORSE than trained-bigram-gen does.",
        "thresholds": {"T28_ratio_min": 2.0},
        "measurements": {**s, "T28_pass": pass_},
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

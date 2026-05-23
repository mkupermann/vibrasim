"""BET-032 — N-gram temporal modeling on SOM-BMU tokens.

After BET-030/031 NULL (ESN doesn't beat persistence on raw audio
features), shift to discrete-token temporal modeling. Pre-LLM-era
classic: Linde-Buzo-Gray vector quantization (1980s) + bigram/trigram
statistics (Shannon 1948). No LLM/transformer/embedding/BPE.

Protocol:
  1. Train SOM+replay on EN (10k ticks, BET-012 baseline).
  2. Quantize each training chunk to BMU cell index 0..3599 → token stream.
  3. Build BIGRAM count matrix: B[i,j] = count of transitions i→j.
  4. Normalize rows to probability: P[i,j] = P(next=j | curr=i).
  5. For held-out EN, quantize to token stream.
  6. Predict next-token via bigram MAP: argmax_j P[token_t, j].
  7. Compare to:
     - Uniform random baseline: 1/3600
     - Unigram baseline: argmax_j P(j) (= most-frequent BMU)

T20 bar (LOCKED PRE-DATA):
  Bigram top-1 accuracy > 2 × unigram top-1 accuracy
  (bigram must USE temporal info beyond marginal token distribution)

  Bigram top-5 accuracy > 5 × random (chance)

Pre-data prediction: bigram-acc ~5%, unigram-acc ~1-2%, random ~0.03%.
T20 PASSES if bigram > 2x unigram.

Substantive AI claim: substrate-quantized audio HAS token-level temporal
structure that bigram captures. First test in bet programme of DISCRETE
temporal modeling.
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

T20_BIGRAM_OVER_UNIGRAM_MIN = 2.0
T20_TOP5_OVER_RANDOM_MIN = 5.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-032"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _quantize(state, audio, cfg):
    """Encode each chunk + BMU index. Returns 1D array of token indices."""
    n_chunks = audio.size // cfg.samples_per_tick
    tokens = np.zeros(n_chunks, dtype=np.int64)
    for k in range(n_chunks):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        diff = state["w"] - sensor
        tokens[k] = int(np.argmin(np.einsum("ijkl,ijkl->ijk", diff, diff)))
    return tokens


def _build_bigram(tokens, n_cells):
    """Bigram counts + row-normalized probability."""
    B = np.zeros((n_cells, n_cells), dtype=np.float64)
    for t in range(tokens.size - 1):
        B[tokens[t], tokens[t + 1]] += 1
    # Laplace smoothing
    B += 1.0 / n_cells
    P = B / B.sum(axis=1, keepdims=True)
    return P


def _evaluate(tokens, P):
    """Bigram next-token prediction: top-1 + top-5 accuracy."""
    top1_correct = 0
    top5_correct = 0
    n = tokens.size - 1
    for t in range(n):
        curr = tokens[t]
        true_next = tokens[t + 1]
        probs = P[curr]
        # top-5
        top5 = np.argpartition(probs, -5)[-5:]
        if true_next in top5:
            top5_correct += 1
        # top-1
        if int(np.argmax(probs)) == true_next:
            top1_correct += 1
    return top1_correct / n, top5_correct / n


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

    # Bigram model on training tokens
    P_bigram = _build_bigram(train_tokens, n_cells)
    bigram_top1, bigram_top5 = _evaluate(held_tokens, P_bigram)

    # Unigram baseline: row-broadcast marginal probability
    # All bigram rows are P(next | curr=i). Unigram model: P(next) marginal.
    unigram_counts = np.bincount(train_tokens, minlength=n_cells).astype(np.float64) + 1.0
    P_unigram_vec = unigram_counts / unigram_counts.sum()
    most_freq_token = int(np.argmax(P_unigram_vec))
    unigram_top1 = float(np.mean(held_tokens[1:] == most_freq_token))
    # Top-5 unigram = held tokens that are in top-5 most-frequent
    top5_unigram_set = set(np.argpartition(P_unigram_vec, -5)[-5:])
    unigram_top5 = float(np.mean([int(t) in top5_unigram_set for t in held_tokens[1:]]))

    random_baseline_top1 = 1.0 / n_cells
    random_baseline_top5 = 5.0 / n_cells

    return dict(
        n_cells=n_cells,
        n_train_tokens=int(train_tokens.size),
        n_held_tokens=int(held_tokens.size),
        n_unique_train_tokens=int(np.unique(train_tokens).size),
        bigram_top1=bigram_top1, bigram_top5=bigram_top5,
        unigram_top1=unigram_top1, unigram_top5=unigram_top5,
        random_top1=random_baseline_top1, random_top5=random_baseline_top5,
        bigram_over_unigram=bigram_top1 / max(unigram_top1, 1e-12),
        bigram_top5_over_random=bigram_top5 / random_baseline_top5,
        most_freq_token=most_freq_token,
        most_freq_token_count=int(unigram_counts[most_freq_token] - 1),
    )


def _verdict(s):
    pass_top1 = s["bigram_over_unigram"] > T20_BIGRAM_OVER_UNIGRAM_MIN
    pass_top5 = s["bigram_top5_over_random"] > T20_TOP5_OVER_RANDOM_MIN
    return {
        "T20_bigram_top1_accuracy": s["bigram_top1"],
        "T20_unigram_top1_accuracy": s["unigram_top1"],
        "T20_random_top1_baseline": s["random_top1"],
        "T20_bigram_over_unigram": s["bigram_over_unigram"],
        "T20_bigram_over_unigram_min": T20_BIGRAM_OVER_UNIGRAM_MIN,
        "T20_top1_pass": pass_top1,
        "T20_bigram_top5": s["bigram_top5"],
        "T20_random_top5_baseline": s["random_top5"],
        "T20_bigram_top5_over_random": s["bigram_top5_over_random"],
        "T20_bigram_top5_over_random_min": T20_TOP5_OVER_RANDOM_MIN,
        "T20_top5_pass": pass_top5,
        "T20_pass": pass_top1 and pass_top5,
        "n_cells": s["n_cells"],
        "n_unique_train_tokens": s["n_unique_train_tokens"],
        "n_train_tokens": s["n_train_tokens"],
        "n_held_tokens": s["n_held_tokens"],
    }


def test_T20(substrates):
    m = _verdict(substrates)
    if not m["T20_pass"]:
        pytest.fail(
            f"BET-032 NULL T20.\n"
            f"  Bigram top1: {m['T20_bigram_top1_accuracy']:.4f}\n"
            f"  Unigram top1: {m['T20_unigram_top1_accuracy']:.4f}\n"
            f"  Random top1: {m['T20_random_top1_baseline']:.5f}\n"
            f"  Bigram/Unigram ratio: {m['T20_bigram_over_unigram']:.4f} "
            f"(need > {T20_BIGRAM_OVER_UNIGRAM_MIN}) pass={m['T20_top1_pass']}\n"
            f"  Bigram top5: {m['T20_bigram_top5']:.4f}\n"
            f"  Bigram top5 / random: {m['T20_bigram_top5_over_random']:.4f} "
            f"(need > {T20_TOP5_OVER_RANDOM_MIN}) pass={m['T20_top5_pass']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T20_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-032",
        "verdict": verdict,
        "hypothesis": "T20 N-gram temporal modeling on SOM-BMU tokens. Substrate quantizes audio to discrete tokens; bigram statistics predict next-token significantly better than unigram marginal.",
        "thresholds": {
            "T20_bigram_over_unigram_min": T20_BIGRAM_OVER_UNIGRAM_MIN,
            "T20_top5_over_random_min": T20_TOP5_OVER_RANDOM_MIN,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

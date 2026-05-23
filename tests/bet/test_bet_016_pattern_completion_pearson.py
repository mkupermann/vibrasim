"""BET-016 — T10 pattern completion with Pearson correlation metric.

BET-015 revealed cosine-on-non-negative-features is intrinsically
positive-biased. Pearson correlation (mean-subtracted cosine) removes
this bias. This is a pre-data-knowable mathematical property of the
metric, not a result-driven choice. The pre-registration is legitimate.

Locked: same protocol as BET-015 except the metric. T10 bar:
  Positive (trained EN, query EN partial): pearson > 0.5
  Negative (trained WN, query EN partial): pearson < 0.2
  Both must pass.

Pre-data prediction: positive ~0.7, negative ~0.05.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import (
    SOMReplayConfig, initialise, run, predict_from_partial,
)
from world.flux.cognitive_map import encode_sensor

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
N_HIDDEN = 5
WN_SEED = 9999
ZERO_SEED = 33333
TARGET_RMS = 0.25
N_HOLDOUT_CHUNKS = 1000

T10_POSITIVE_MIN = 0.5
T10_NEGATIVE_MAX = 0.2

OUT_DIR = Path.home() / ".eqmod/bet/BET-016"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _partial_query_pattern(cfg, seed):
    rng = np.random.default_rng(seed)
    perm = rng.permutation(cfg.n_features)
    known_mask = np.zeros(cfg.n_features, dtype=bool)
    known_mask[perm[:cfg.n_features - N_HIDDEN]] = True
    return known_mask


def _pearson(a, b):
    a_c = a - a.mean()
    b_c = b - b.mean()
    denom = np.linalg.norm(a_c) * np.linalg.norm(b_c) + 1e-12
    return float(np.dot(a_c, b_c) / denom) if denom > 0 else 0.0


def _evaluate(state, holdout_audio, cfg):
    n_chunks = min(N_HOLDOUT_CHUNKS, holdout_audio.size // cfg.samples_per_tick)
    pearsons = []
    for k in range(n_chunks):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = holdout_audio[i0:i1]
        if chunk.size == 0:
            continue
        full = encode_sensor(chunk, cfg)
        known_mask = _partial_query_pattern(cfg, ZERO_SEED + k)
        partial = np.where(known_mask, full, 0.0)
        pred = predict_from_partial(state, partial, known_mask)
        hidden = ~known_mask
        if hidden.sum() < 2:
            continue
        r = _pearson(full[hidden], pred[hidden])
        pearsons.append(r)
    arr = np.array(pearsons) if pearsons else np.array([0.0])
    return {
        "n": len(pearsons),
        "mean_pearson": float(arr.mean()),
        "median_pearson": float(np.median(arr)),
        "fraction_positive": float((arr > 0).mean()),
    }


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
    eng_a = full[:n_audio].astype(np.float64)
    eng_b = full[n_audio:2 * n_audio].astype(np.float64)
    wn = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)

    state_eng = run(cfg, N_TICKS, eng_a)
    state_wn = run(cfg, N_TICKS, wn)

    pos = _evaluate(state_eng, eng_b, cfg)
    neg = _evaluate(state_wn, eng_b, cfg)

    return dict(
        cfg=cfg,
        positive=pos, negative=neg,
        audio_meta={
            "source": "R-7 corpus", "n_samples_per_train": n_audio,
            "n_holdout_chunks": N_HOLDOUT_CHUNKS, "n_hidden_dims": N_HIDDEN,
            "zero_seed": ZERO_SEED, "metric": "pearson_correlation",
        },
    )


def _verdict(sub):
    pos = sub["positive"]["mean_pearson"]
    neg = sub["negative"]["mean_pearson"]
    pos_pass = pos > T10_POSITIVE_MIN
    neg_pass = neg < T10_NEGATIVE_MAX
    return {
        "T10_positive_mean_pearson": pos,
        "T10_positive_threshold_min": T10_POSITIVE_MIN,
        "T10_positive_pass": pos_pass,
        "T10_negative_mean_pearson": neg,
        "T10_negative_threshold_max": T10_NEGATIVE_MAX,
        "T10_negative_pass": neg_pass,
        "T10_positive_detail": sub["positive"],
        "T10_negative_detail": sub["negative"],
        "T10_pass": pos_pass and neg_pass,
    }


def test_T10_pearson(substrates):
    m = _verdict(substrates)
    if not m["T10_pass"]:
        pytest.fail(
            f"BET-016 NULL: T10 Pearson does not satisfy bar.\n"
            f"  positive: {m['T10_positive_mean_pearson']:.4f} (need > {T10_POSITIVE_MIN}) pass={m['T10_positive_pass']}\n"
            f"  negative: {m['T10_negative_mean_pearson']:.4f} (need < {T10_NEGATIVE_MAX}) pass={m['T10_negative_pass']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T10_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-016",
        "verdict": verdict,
        "hypothesis": "T10 pattern completion with Pearson correlation (mean-subtracted cosine) replacing BET-015 cosine. Pearson removes positive-feature bias that caused BET-015 NULL.",
        "thresholds": {"T10_positive_min": T10_POSITIVE_MIN, "T10_negative_max": T10_NEGATIVE_MAX},
        "audio": substrates["audio_meta"],
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

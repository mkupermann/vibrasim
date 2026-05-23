"""BET-015 — T10 pattern completion test (output-side "kommunizierend").

Pre-registered LOGBOOK 2026-05-23 ~21:50. Communication-relevant property:
given partial input (5 of 10 feature dims zeroed), the substrate fills in
the missing 5 from its stored content via partial-distance BMU + full
weight-vector retrieval.

Tests:
  - Trained-on-EN substrate, queried with eng_b partial chunks:
    mean cosine on zeroed dims > 0.3 (substrate uses learned EN content)
  - Trained-on-WN substrate, queried with eng_b partial chunks:
    mean cosine on zeroed dims < 0.15 (different-class substrate poor)
  - Both bars must be met → T10 PASS

Locked: substrate = SOM+replay (BET-012 baseline), N_TICKS=10000, K=10000,
replay_rate=1.0, hidden-dim count = 5 of 10 (50% missing), zeroing seed
locked at 33333 for reproducibility.
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
N_HIDDEN = 5     # 5 of 10 dims zeroed
WN_SEED = 9999
ZERO_SEED = 33333
TARGET_RMS = 0.25
N_HOLDOUT_CHUNKS = 1000

T10_POSITIVE_MIN = 0.3
T10_NEGATIVE_MAX = 0.15

OUT_DIR = Path.home() / ".eqmod/bet/BET-015"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _partial_query_pattern(cfg: SOMReplayConfig, seed: int) -> np.ndarray:
    """Return boolean known_mask of shape (n_features,) — True for known dims.
    Deterministic from seed."""
    rng = np.random.default_rng(seed)
    perm = rng.permutation(cfg.n_features)
    known_mask = np.zeros(cfg.n_features, dtype=bool)
    n_known = cfg.n_features - N_HIDDEN
    known_mask[perm[:n_known]] = True
    return known_mask


def _evaluate_pattern_completion(state: dict, holdout_audio: np.ndarray, cfg: SOMReplayConfig) -> dict:
    """For each holdout chunk: compute full feature, zero out 5 dims, predict, measure cosine on zeroed dims."""
    n_chunks = min(N_HOLDOUT_CHUNKS, holdout_audio.size // cfg.samples_per_tick)
    cosines_on_hidden = []
    for k in range(n_chunks):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = holdout_audio[i0:i1]
        if chunk.size == 0:
            continue
        full_sensor = encode_sensor(chunk, cfg)
        known_mask = _partial_query_pattern(cfg, ZERO_SEED + k)  # per-chunk mask
        partial_sensor = np.where(known_mask, full_sensor, 0.0)
        predicted = predict_from_partial(state, partial_sensor, known_mask)
        # Cosine on the HIDDEN dimensions only
        hidden_idx = ~known_mask
        true_hidden = full_sensor[hidden_idx]
        pred_hidden = predicted[hidden_idx]
        denom = np.linalg.norm(true_hidden) * np.linalg.norm(pred_hidden) + 1e-12
        if denom > 0:
            cos = float(np.dot(true_hidden, pred_hidden) / denom)
        else:
            cos = 0.0
        cosines_on_hidden.append(cos)
    arr = np.array(cosines_on_hidden) if cosines_on_hidden else np.array([0.0])
    return {
        "n": len(cosines_on_hidden),
        "mean_cosine_hidden": float(arr.mean()),
        "median_cosine_hidden": float(np.median(arr)),
        "fraction_positive_cosine": float((arr > 0).mean()),
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

    pos_metrics = _evaluate_pattern_completion(state_eng, eng_b, cfg)
    neg_metrics = _evaluate_pattern_completion(state_wn, eng_b, cfg)

    return dict(
        cfg=cfg,
        positive=pos_metrics, negative=neg_metrics,
        audio_meta={
            "source": "R-7 corpus",
            "n_samples_per_train": n_audio,
            "n_holdout_chunks": N_HOLDOUT_CHUNKS,
            "n_hidden_dims": N_HIDDEN,
            "zero_seed": ZERO_SEED,
        },
    )


def _compute_verdict(sub):
    pos = sub["positive"]["mean_cosine_hidden"]
    neg = sub["negative"]["mean_cosine_hidden"]
    pos_pass = pos > T10_POSITIVE_MIN
    neg_pass = neg < T10_NEGATIVE_MAX
    return {
        "T10_positive_mean_cosine_hidden": pos,
        "T10_positive_threshold_min": T10_POSITIVE_MIN,
        "T10_positive_pass": pos_pass,
        "T10_negative_mean_cosine_hidden": neg,
        "T10_negative_threshold_max": T10_NEGATIVE_MAX,
        "T10_negative_pass": neg_pass,
        "T10_positive_detail": sub["positive"],
        "T10_negative_detail": sub["negative"],
        "T10_pass": pos_pass and neg_pass,
    }


def test_T10_pattern_completion(substrates):
    m = _compute_verdict(substrates)
    if not m["T10_pass"]:
        pytest.fail(
            f"BET-015 NULL: T10 pattern completion does not satisfy bar.\n"
            f"  positive (trained EN, query EN partial): "
            f"mean cosine on hidden dims = {m['T10_positive_mean_cosine_hidden']:.4f} "
            f"(need > {T10_POSITIVE_MIN})\n"
            f"  negative (trained WN, query EN partial): "
            f"mean cosine on hidden dims = {m['T10_negative_mean_cosine_hidden']:.4f} "
            f"(need < {T10_NEGATIVE_MAX})\n"
            f"  positive_pass={m['T10_positive_pass']} negative_pass={m['T10_negative_pass']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _compute_verdict(substrates)
    verdict = "passed" if m["T10_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-015",
        "verdict": verdict,
        "hypothesis": "T10 pattern completion: given 5 of 10 features as partial query, substrate (SOM+replay trained on EN) fills in the missing 5 with positive cosine to the true full feature; control substrate (trained on WN) does NOT.",
        "thresholds": {
            "T10_positive_min": T10_POSITIVE_MIN,
            "T10_negative_max": T10_NEGATIVE_MAX,
        },
        "audio": substrates["audio_meta"],
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

"""BET-017 — T11 class-discrimination at output.

Pre-registered LOGBOOK 2026-05-24 00:00. Tests communication-as-
classification: given input, substrate retrieves an output. Does the
output align with substrate's trained class more than with the
contrasting class?

Protocol: build class-centroid vectors c_EN, c_WN from fresh substrates
trained on each class. For 1000 holdout chunks, retrieve via BMU on the
substrate-under-test, compute distances to both centroids, vote for
closer. Bar: trained-EN substrate votes EN >70% of time; trained-WN
substrate votes WN >70% of time.

Substrate: SOM + replay (BET-012 baseline).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import (
    SOMReplayConfig, initialise, run,
)
from world.flux.cognitive_map import encode_sensor

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25
N_HOLDOUT_CHUNKS = 1000

T11_POSITIVE_FRACTION_MIN = 0.7
T11_NEGATIVE_FRACTION_MIN = 0.7  # i.e., trained-WN substrate must vote WN >= 70%

OUT_DIR = Path.home() / ".eqmod/bet/BET-017"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _retrieve(state, sensor):
    """BMU full weight retrieval."""
    diff = state["w"] - sensor
    dist_sq = np.einsum("ijkl,ijkl->ijk", diff, diff)
    bmu = np.unravel_index(int(np.argmin(dist_sq)), dist_sq.shape)
    return state["w"][bmu]


def _vote_class(retrieved, c_EN, c_WN) -> str:
    d_en = float(np.linalg.norm(retrieved - c_EN))
    d_wn = float(np.linalg.norm(retrieved - c_WN))
    return "EN" if d_en < d_wn else "WN"


def _classify_holdout(state_under_test, holdout_audio, cfg, c_EN, c_WN):
    n_chunks = min(N_HOLDOUT_CHUNKS, holdout_audio.size // cfg.samples_per_tick)
    votes_EN = 0
    votes_WN = 0
    for k in range(n_chunks):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = holdout_audio[i0:i1]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        r = _retrieve(state_under_test, sensor)
        v = _vote_class(r, c_EN, c_WN)
        if v == "EN":
            votes_EN += 1
        else:
            votes_WN += 1
    total = votes_EN + votes_WN
    return {
        "n": total,
        "fraction_EN": votes_EN / total if total else 0.0,
        "fraction_WN": votes_WN / total if total else 0.0,
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

    # Build the two reference substrates and extract class centroids
    state_EN = run(cfg, N_TICKS, eng_a)
    state_WN = run(cfg, N_TICKS, wn)
    c_EN = state_EN["w"].reshape(-1, cfg.n_features).mean(axis=0)
    c_WN = state_WN["w"].reshape(-1, cfg.n_features).mean(axis=0)

    # Positive arm: substrate trained on EN, queried with eng_b
    classification_EN = _classify_holdout(state_EN, eng_b, cfg, c_EN, c_WN)
    # Negative arm: substrate trained on WN, queried with eng_b
    classification_WN = _classify_holdout(state_WN, eng_b, cfg, c_EN, c_WN)

    return dict(
        cfg=cfg,
        classification_EN=classification_EN,
        classification_WN=classification_WN,
        c_EN_norm=float(np.linalg.norm(c_EN)),
        c_WN_norm=float(np.linalg.norm(c_WN)),
        centroid_distance=float(np.linalg.norm(c_EN - c_WN)),
    )


def _verdict(sub):
    pos = sub["classification_EN"]["fraction_EN"]
    neg = sub["classification_WN"]["fraction_WN"]
    pos_pass = pos > T11_POSITIVE_FRACTION_MIN
    neg_pass = neg > T11_NEGATIVE_FRACTION_MIN
    return {
        "T11_positive_fraction_EN_vote": pos,
        "T11_positive_threshold_min": T11_POSITIVE_FRACTION_MIN,
        "T11_positive_pass": pos_pass,
        "T11_negative_fraction_WN_vote": neg,
        "T11_negative_threshold_min": T11_NEGATIVE_FRACTION_MIN,
        "T11_negative_pass": neg_pass,
        "T11_positive_detail": sub["classification_EN"],
        "T11_negative_detail": sub["classification_WN"],
        "c_EN_norm": sub["c_EN_norm"],
        "c_WN_norm": sub["c_WN_norm"],
        "centroid_distance": sub["centroid_distance"],
        "T11_pass": pos_pass and neg_pass,
    }


def test_T11_class_discrimination(substrates):
    m = _verdict(substrates)
    if not m["T11_pass"]:
        pytest.fail(
            f"BET-017 NULL: T11 class-discrimination fails bar.\n"
            f"  positive (S trained EN, queried with EN, votes EN): "
            f"{m['T11_positive_fraction_EN_vote']:.4f} (need > {T11_POSITIVE_FRACTION_MIN}) "
            f"pass={m['T11_positive_pass']}\n"
            f"  negative (S trained WN, queried with EN, votes WN): "
            f"{m['T11_negative_fraction_WN_vote']:.4f} (need > {T11_NEGATIVE_FRACTION_MIN}) "
            f"pass={m['T11_negative_pass']}\n"
            f"  centroid_distance = {m['centroid_distance']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T11_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-017",
        "verdict": verdict,
        "hypothesis": "T11 class-discrimination at output. Substrate trained on class X, queried with EN chunks: retrieved BMU should be closer to fresh-X centroid than to fresh-other centroid in >70% of cases.",
        "thresholds": {
            "T11_positive_min": T11_POSITIVE_FRACTION_MIN,
            "T11_negative_min": T11_NEGATIVE_FRACTION_MIN,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

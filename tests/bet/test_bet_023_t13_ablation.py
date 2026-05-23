"""BET-023 — T13 ablation: SOM with replay vs without replay.

If plain SOM (no replay) passes T13: replay is NOT essential for the
output-side discrimination. T13 PASS comes from BMU competitive routing
itself.

If plain SOM fails T13: replay drives the BMU diversity that gives
class-specific coverage.

This test isolates the contribution of replay to T13.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_substrate import SOMConfig, initialise as som_init, run as som_run
from world.flux.som_replay import (
    SOMReplayConfig, initialise as somr_init, run as somr_run,
)
from world.flux.cognitive_map import encode_sensor

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25
N_QUERIES_PER_CLASS = 1000

T13_COVERAGE_EN_MIN = 0.10
T13_RATIO_MIN = 2.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-023"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _bmu_idx(state, sensor):
    diff = state["w"] - sensor
    return int(np.argmin(np.einsum("ijkl,ijkl->ijk", diff, diff)))


def _gather(state, audio, cfg, n_queries):
    n = min(n_queries, audio.size // cfg.samples_per_tick)
    out = np.zeros(n, dtype=np.int64)
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        out[k] = _bmu_idx(state, encode_sensor(chunk, cfg))
    return out


def _t13_for_state(state, eng_q, wn_q, cfg, n_cells):
    bmu_en = _gather(state, eng_q, cfg, N_QUERIES_PER_CLASS)
    bmu_wn = _gather(state, wn_q, cfg, N_QUERIES_PER_CLASS)
    n_u_en = int(np.unique(bmu_en).size)
    n_u_wn = int(np.unique(bmu_wn).size)
    cov_en = n_u_en / n_cells
    cov_wn = n_u_wn / n_cells
    ratio = cov_en / max(cov_wn, 1e-9)
    return {
        "n_unique_en": n_u_en, "n_unique_wn": n_u_wn,
        "coverage_en": cov_en, "coverage_wn": cov_wn,
        "ratio": ratio,
        "T13_pass": cov_en > T13_COVERAGE_EN_MIN and ratio > T13_RATIO_MIN,
    }


@pytest.fixture(scope="module")
def substrates():
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_query = N_QUERIES_PER_CLASS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_audio + n_query > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)
    eng_q = full[n_audio:n_audio + n_query].astype(np.float64)
    wn_q = _make_white_noise(n_query, TARGET_RMS, WN_SEED + 1)

    # Arm 1: plain SOM (BET-007 baseline, no replay)
    cfg_plain = SOMConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_cells = cfg_plain.grid_dims[0] * cfg_plain.grid_dims[1] * cfg_plain.grid_dims[2]
    state_plain = som_run(cfg_plain, N_TICKS, eng_train)
    t13_plain = _t13_for_state(state_plain, eng_q, wn_q, cfg_plain, n_cells)

    # Arm 2: SOM + replay
    cfg_replay = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    state_replay = somr_run(cfg_replay, N_TICKS, eng_train)
    t13_replay = _t13_for_state(state_replay, eng_q, wn_q, cfg_replay, n_cells)

    return {
        "n_cells": n_cells,
        "plain_som": t13_plain,
        "som_replay": t13_replay,
    }


def test_T13_ablation(substrates):
    """The test exposes WHICH substrate passes T13. Result IS the finding —
    no single pass/fail bar (both arms reported)."""
    plain_pass = substrates["plain_som"]["T13_pass"]
    replay_pass = substrates["som_replay"]["T13_pass"]
    if not (plain_pass or replay_pass):
        pytest.fail(
            f"BET-023 NULL: neither arm passes T13.\n"
            f"  plain SOM: cov_EN={substrates['plain_som']['coverage_en']:.4f}, ratio={substrates['plain_som']['ratio']:.4f}\n"
            f"  SOM+replay: cov_EN={substrates['som_replay']['coverage_en']:.4f}, ratio={substrates['som_replay']['ratio']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    plain_pass = substrates["plain_som"]["T13_pass"]
    replay_pass = substrates["som_replay"]["T13_pass"]
    verdict = "passed" if (plain_pass or replay_pass) else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-023",
        "verdict": verdict,
        "hypothesis": "T13 ablation: does plain SOM (no replay) pass T13? If yes, replay is incidental to T13. If no, replay drives BMU diversity.",
        "thresholds": {"T13_coverage_en_min": T13_COVERAGE_EN_MIN, "T13_ratio_min": T13_RATIO_MIN},
        "measurements": {
            "n_cells": substrates["n_cells"],
            "plain_som_T13": substrates["plain_som"],
            "som_replay_T13": substrates["som_replay"],
            "interpretation": (
                "plain SOM pass AND replay pass → T13 not replay-dependent" if plain_pass and replay_pass else
                "only plain SOM pass → T13 doesn't need replay" if plain_pass else
                "only replay pass → replay is essential for T13" if replay_pass else
                "neither pass → T13 needs something else"
            ),
        },
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

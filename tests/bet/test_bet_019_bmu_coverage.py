"""BET-019 — T13 BMU coverage ratio test.

Pre-registered LOGBOOK 2026-05-24 00:10. Substrate trained on class X
should cover X richly (many unique BMU cells used) and not-X sparsely
(few cells). The ratio is intrinsic — no reference vectors, no metric
tuning, no positivity artifact.

BET-018 already showed for trained substrate: 437 unique BMUs for EN
queries, 114 for WN queries (ratio 3.83x). This iteration formalises
the test with a locked bar and includes the fresh-substrate negative
control (which should give ratio ~1).

T13 bar (LOCKED):
  coverage_EN > 0.10 (10% of 3600 = 360 cells minimum)
  coverage_EN / coverage_WN > 2.0
  Both must pass.

Plus negative control on fresh substrate (informational, not bar).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, initialise, run
from world.flux.cognitive_map import encode_sensor

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25
N_QUERIES_PER_CLASS = 1000

T13_COVERAGE_EN_MIN = 0.10  # 10% of cells (>= 360 of 3600)
T13_RATIO_MIN = 2.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-019"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _retrieve_bmu_index(state, sensor):
    diff = state["w"] - sensor
    dist_sq = np.einsum("ijkl,ijkl->ijk", diff, diff)
    return int(np.argmin(dist_sq))


def _gather_bmu_indices(state, audio, cfg, n_queries):
    n = min(n_queries, audio.size // cfg.samples_per_tick)
    bmu_indices = np.zeros(n, dtype=np.int64)
    for k in range(n):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = audio[i0:i1]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        bmu_indices[k] = _retrieve_bmu_index(state, sensor)
    return bmu_indices


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_query = N_QUERIES_PER_CLASS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_audio + n_query > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)
    eng_queries = full[n_audio:n_audio + n_query].astype(np.float64)
    wn_queries = _make_white_noise(n_query, TARGET_RMS, WN_SEED + 1)

    Lx, Ly, Lz = cfg.grid_dims
    n_cells = Lx * Ly * Lz

    state_trained = run(cfg, N_TICKS, eng_train)
    bmu_trained_en = _gather_bmu_indices(state_trained, eng_queries, cfg, N_QUERIES_PER_CLASS)
    bmu_trained_wn = _gather_bmu_indices(state_trained, wn_queries, cfg, N_QUERIES_PER_CLASS)

    state_fresh = initialise(cfg)
    bmu_fresh_en = _gather_bmu_indices(state_fresh, eng_queries, cfg, N_QUERIES_PER_CLASS)
    bmu_fresh_wn = _gather_bmu_indices(state_fresh, wn_queries, cfg, N_QUERIES_PER_CLASS)

    n_unique_trained_en = int(np.unique(bmu_trained_en).size)
    n_unique_trained_wn = int(np.unique(bmu_trained_wn).size)
    n_unique_fresh_en = int(np.unique(bmu_fresh_en).size)
    n_unique_fresh_wn = int(np.unique(bmu_fresh_wn).size)

    coverage_trained_en = n_unique_trained_en / n_cells
    coverage_trained_wn = n_unique_trained_wn / n_cells
    coverage_fresh_en = n_unique_fresh_en / n_cells
    coverage_fresh_wn = n_unique_fresh_wn / n_cells

    ratio_trained = coverage_trained_en / max(coverage_trained_wn, 1e-9)
    ratio_fresh = coverage_fresh_en / max(coverage_fresh_wn, 1e-9)

    return dict(
        cfg=cfg, n_cells=n_cells,
        n_unique_trained_en=n_unique_trained_en,
        n_unique_trained_wn=n_unique_trained_wn,
        n_unique_fresh_en=n_unique_fresh_en,
        n_unique_fresh_wn=n_unique_fresh_wn,
        coverage_trained_en=coverage_trained_en,
        coverage_trained_wn=coverage_trained_wn,
        coverage_fresh_en=coverage_fresh_en,
        coverage_fresh_wn=coverage_fresh_wn,
        ratio_trained=ratio_trained,
        ratio_fresh=ratio_fresh,
    )


def _verdict(sub):
    cov_pass = sub["coverage_trained_en"] > T13_COVERAGE_EN_MIN
    ratio_pass = sub["ratio_trained"] > T13_RATIO_MIN
    return {
        "T13_coverage_trained_en": sub["coverage_trained_en"],
        "T13_coverage_trained_wn": sub["coverage_trained_wn"],
        "T13_coverage_en_threshold_min": T13_COVERAGE_EN_MIN,
        "T13_coverage_en_pass": cov_pass,
        "T13_ratio_trained": sub["ratio_trained"],
        "T13_ratio_threshold_min": T13_RATIO_MIN,
        "T13_ratio_pass": ratio_pass,
        "T13_coverage_fresh_en": sub["coverage_fresh_en"],
        "T13_coverage_fresh_wn": sub["coverage_fresh_wn"],
        "T13_ratio_fresh_control": sub["ratio_fresh"],
        "n_unique_trained_en": sub["n_unique_trained_en"],
        "n_unique_trained_wn": sub["n_unique_trained_wn"],
        "n_unique_fresh_en": sub["n_unique_fresh_en"],
        "n_unique_fresh_wn": sub["n_unique_fresh_wn"],
        "n_cells_total": sub["n_cells"],
        "T13_pass": cov_pass and ratio_pass,
    }


def test_T13_bmu_coverage(substrates):
    m = _verdict(substrates)
    if not m["T13_pass"]:
        pytest.fail(
            f"BET-019 NULL: T13 BMU coverage.\n"
            f"  trained coverage EN: {m['T13_coverage_trained_en']:.4f} "
            f"(need > {T13_COVERAGE_EN_MIN}) pass={m['T13_coverage_en_pass']}\n"
            f"  trained ratio EN/WN: {m['T13_ratio_trained']:.4f} "
            f"(need > {T13_RATIO_MIN}) pass={m['T13_ratio_pass']}\n"
            f"  fresh control ratio: {m['T13_ratio_fresh_control']:.4f}\n"
            f"  unique BMUs trained: EN={m['n_unique_trained_en']}, WN={m['n_unique_trained_wn']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T13_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-019",
        "verdict": verdict,
        "hypothesis": "T13 BMU coverage ratio. Trained substrate covers its trained class richly (many unique BMU cells) and contrasting class sparsely. Intrinsic routing-capacity metric.",
        "thresholds": {
            "T13_coverage_en_min": T13_COVERAGE_EN_MIN,
            "T13_ratio_min": T13_RATIO_MIN,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

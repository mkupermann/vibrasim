"""BET-020 — LR validation of T13 BMU coverage ratio at 100k ticks."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, initialise, run
from world.flux.cognitive_map import encode_sensor

N_TICKS = 100_000   # 10x BET-019 scale-up
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25
N_QUERIES_PER_CLASS = 1000

T13_COVERAGE_EN_MIN = 0.10
T13_RATIO_MIN = 2.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-020"
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


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS, n_features=N_FEATURES,
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
    bmu_en = _gather(state_trained, eng_queries, cfg, N_QUERIES_PER_CLASS)
    bmu_wn = _gather(state_trained, wn_queries, cfg, N_QUERIES_PER_CLASS)

    state_fresh = initialise(cfg)
    bmu_fresh_en = _gather(state_fresh, eng_queries, cfg, N_QUERIES_PER_CLASS)
    bmu_fresh_wn = _gather(state_fresh, wn_queries, cfg, N_QUERIES_PER_CLASS)

    n_u_t_en = int(np.unique(bmu_en).size)
    n_u_t_wn = int(np.unique(bmu_wn).size)
    n_u_f_en = int(np.unique(bmu_fresh_en).size)
    n_u_f_wn = int(np.unique(bmu_fresh_wn).size)

    cov_t_en = n_u_t_en / n_cells
    cov_t_wn = n_u_t_wn / n_cells
    ratio_t = cov_t_en / max(cov_t_wn, 1e-9)

    return dict(
        n_cells=n_cells,
        coverage_trained_en=cov_t_en, coverage_trained_wn=cov_t_wn,
        ratio_trained=ratio_t,
        coverage_fresh_en=n_u_f_en / n_cells, coverage_fresh_wn=n_u_f_wn / n_cells,
        ratio_fresh=(n_u_f_en / max(n_u_f_wn, 1)),
        n_unique_trained_en=n_u_t_en, n_unique_trained_wn=n_u_t_wn,
    )


def test_T13_lr(substrates):
    cov_pass = substrates["coverage_trained_en"] > T13_COVERAGE_EN_MIN
    ratio_pass = substrates["ratio_trained"] > T13_RATIO_MIN
    if not (cov_pass and ratio_pass):
        pytest.fail(
            f"BET-020 NULL at LR scale: cov_EN={substrates['coverage_trained_en']:.4f}, "
            f"ratio={substrates['ratio_trained']:.4f}, "
            f"unique BMUs trained EN={substrates['n_unique_trained_en']}, "
            f"WN={substrates['n_unique_trained_wn']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    cov_pass = substrates["coverage_trained_en"] > T13_COVERAGE_EN_MIN
    ratio_pass = substrates["ratio_trained"] > T13_RATIO_MIN
    all_pass = cov_pass and ratio_pass
    verdict = "passed" if all_pass else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-020",
        "verdict": verdict,
        "hypothesis": "LR validation of T13 BMU coverage at 100k ticks.",
        "thresholds": {"T13_coverage_en_min": T13_COVERAGE_EN_MIN, "T13_ratio_min": T13_RATIO_MIN},
        "measurements": {
            "n_ticks": N_TICKS,
            **substrates,
            "T13_coverage_en_pass": cov_pass,
            "T13_ratio_pass": ratio_pass,
            "T13_pass": all_pass,
        },
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

"""BET-025 — T15 quantization quality (domain-expertise test).

Substrate trained on EN. For EN queries, BMU's weight should be close
to the input (low quantization error). For WN queries (off-distribution),
BMU's weight is the closest cell but still far. Ratio measures domain
expertise.

T15 bar (LOCKED):
  E_train_EN < 0.5 * E_test_WN  (EN inputs reconstructed 2× better
  than WN inputs)
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

T15_RATIO_MAX = 0.5  # E_train_EN < 0.5 * E_test_WN

OUT_DIR = Path.home() / ".eqmod/bet/BET-025"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _quantize(state, sensor):
    """Return quantization error = || sensor - w_BMU ||."""
    diff = state["w"] - sensor
    dist_sq = np.einsum("ijkl,ijkl->ijk", diff, diff)
    bmu = np.unravel_index(int(np.argmin(dist_sq)), dist_sq.shape)
    w_bmu = state["w"][bmu]
    return float(np.linalg.norm(sensor - w_bmu))


def _mean_quant_error(state, audio, cfg, n_queries):
    n = min(n_queries, audio.size // cfg.samples_per_tick)
    errs = []
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        errs.append(_quantize(state, sensor))
    return float(np.mean(errs)) if errs else 0.0


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

    state = run(cfg, N_TICKS, eng_train)

    e_en = _mean_quant_error(state, eng_queries, cfg, N_QUERIES_PER_CLASS)
    e_wn = _mean_quant_error(state, wn_queries, cfg, N_QUERIES_PER_CLASS)
    ratio = e_en / max(e_wn, 1e-9)

    return {"E_EN": e_en, "E_WN": e_wn, "ratio_EN_over_WN": ratio}


def test_T15_quant(substrates):
    if substrates["ratio_EN_over_WN"] >= T15_RATIO_MAX:
        pytest.fail(
            f"BET-025 NULL: T15 quantization ratio = {substrates['ratio_EN_over_WN']:.4f} "
            f">= {T15_RATIO_MAX} (substrate doesn't specialise on EN)\n"
            f"  E_EN = {substrates['E_EN']:.6f}\n"
            f"  E_WN = {substrates['E_WN']:.6f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    verdict = "passed" if substrates["ratio_EN_over_WN"] < T15_RATIO_MAX else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-025",
        "verdict": verdict,
        "hypothesis": "T15 quantization-quality: substrate's BMU reconstruction error on EN (trained) is <50% of error on WN (off-distribution). Domain-expertise test.",
        "thresholds": {"T15_ratio_max": T15_RATIO_MAX},
        "measurements": substrates,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

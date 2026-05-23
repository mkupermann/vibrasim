"""BET-022 — SOM+replay robustness check with rng_seed=42.

Verify BET-012/019/020 result holds across seed perturbation. Same
substrate, same protocol; only rng_seed differs (42 vs locked 0).

Tests T0-T9 + T13. If passes: result is seed-robust. If fails:
BET-012's PASS was a lucky seed and substrate-design needs revision.

Pre-data prediction: PASS.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import (
    SOMReplayConfig, evaluate_holdout, initialise, run,
)
from world.flux.cognitive_map import encode_sensor
from world.flux.harder_bar_metrics import (
    hist_kl_symmetric, shuffle_chunks_in_time, spatial_autocorrelation,
)

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
RNG_SEED = 42  # changed from default 0
WN_SEED = 9999
SHUFFLE_SEED = 11111
TARGET_RMS = 0.25
N_QUERIES_PER_CLASS = 1000

T7_RATIO_MAX = 0.10
T9_AUTOCORR_MIN = 0.3
T9_RATIO_MIN = 2.0
T13_COVERAGE_EN_MIN = 0.10
T13_RATIO_MIN = 2.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-022"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _copy_state(state):
    return {
        "w": state["w"].copy(),
        "N": state["N"].copy(),
        "ii": state["ii"],
        "jj": state["jj"],
        "kk": state["kk"],
        "buffer": state["buffer"].copy(),
        "buffer_head": state["buffer_head"],
        "buffer_fill": state["buffer_fill"],
        "global_tick": state["global_tick"],
    }


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
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, rng_seed=RNG_SEED,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_half = (N_TICKS // 2) * SAMPLES_PER_TICK
    n_query = N_QUERIES_PER_CLASS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if 2 * n_audio + n_query > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_a = full[:n_audio].astype(np.float64)
    eng_b = full[n_audio:2 * n_audio].astype(np.float64)
    wn = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)
    eng_queries = full[2 * n_audio:2 * n_audio + n_query].astype(np.float64)
    wn_queries = _make_white_noise(n_query, TARGET_RMS, WN_SEED + 1)

    state_init = initialise(cfg)
    field_init = state_init["w"].copy()

    state_eng = run(cfg, N_TICKS, eng_a)
    state_wn = run(cfg, N_TICKS, wn)
    state_neg = run(cfg, N_TICKS, None)
    state_eng_half = run(cfg, N_TICKS // 2, eng_a[:n_half])
    state_wn_half = run(cfg, N_TICKS // 2, wn[:n_half])
    state_eng_rest = run(cfg, N_TICKS, None, state=_copy_state(state_eng))
    state_holdout_train = run(cfg, N_TICKS // 2, eng_b[:n_half])
    holdout = evaluate_holdout(state_holdout_train, eng_b[n_half:], cfg)
    eng_a_shuffled = shuffle_chunks_in_time(eng_a, SAMPLES_PER_TICK, SHUFFLE_SEED)
    state_eng_shuffled = run(cfg, N_TICKS, eng_a_shuffled)
    state_AB = run(cfg, N_TICKS, wn, state=_copy_state(state_eng))

    # T13
    Lx, Ly, Lz = cfg.grid_dims
    n_cells = Lx * Ly * Lz
    bmu_eng = _gather(state_eng, eng_queries, cfg, N_QUERIES_PER_CLASS)
    bmu_wn = _gather(state_eng, wn_queries, cfg, N_QUERIES_PER_CLASS)

    return dict(
        cfg=cfg, n_cells=n_cells, field_init=field_init,
        state_eng=state_eng, state_wn=state_wn, state_neg=state_neg,
        state_eng_half=state_eng_half, state_wn_half=state_wn_half,
        state_eng_rest=state_eng_rest, state_eng_shuffled=state_eng_shuffled,
        state_AB=state_AB, holdout=holdout,
        n_unique_en=int(np.unique(bmu_eng).size),
        n_unique_wn=int(np.unique(bmu_wn).size),
    )


def _compute(sub):
    f_init = sub["field_init"]
    f_eng = sub["state_eng"]["w"]
    f_wn = sub["state_wn"]["w"]
    f_neg = sub["state_neg"]["w"]
    f_eng_half = sub["state_eng_half"]["w"]
    f_wn_half = sub["state_wn_half"]["w"]
    f_eng_rest = sub["state_eng_rest"]["w"]
    f_eng_shuffled = sub["state_eng_shuffled"]["w"]
    f_AB = sub["state_AB"]["w"]
    holdout = sub["holdout"]
    n_cells = sub["n_cells"]

    t0_std = float(f_eng.std())
    kl_t1 = hist_kl_symmetric(f_init, f_eng)
    kl_t2 = hist_kl_symmetric(f_eng, f_wn)
    kl_t1_half = hist_kl_symmetric(f_init, f_eng_half)
    kl_t2_half = hist_kl_symmetric(f_eng_half, f_wn_half)
    kl_t1_rest = hist_kl_symmetric(f_init, f_eng_rest)
    kl_t2_rest = hist_kl_symmetric(f_eng_rest, f_wn)
    neg_kl = hist_kl_symmetric(f_neg, f_eng)
    kl_t7_shuf = hist_kl_symmetric(f_eng, f_eng_shuffled)
    kl_t7_fresh = hist_kl_symmetric(f_eng, f_init)
    t7_ratio = kl_t7_shuf / (kl_t7_fresh + 1e-9)
    kl_t8_en = hist_kl_symmetric(f_AB, f_eng)
    kl_t8_wn = hist_kl_symmetric(f_AB, f_wn)
    autocorr_tr = spatial_autocorrelation(f_eng)
    autocorr_fr = spatial_autocorrelation(f_init)
    cov_en = sub["n_unique_en"] / n_cells
    cov_wn = sub["n_unique_wn"] / n_cells
    ratio_t13 = cov_en / max(cov_wn, 1e-9)

    return {
        "substrate": "som_replay_seed42",
        "T0_spatial_std": t0_std, "T0_pass": t0_std > 0.05,
        "T1_kl_init_vs_eng": kl_t1, "T1_pass": kl_t1 > 0.1,
        "T2_kl_eng_vs_wn": kl_t2, "T2_pass": kl_t2 > 0.1,
        "T3_kl_init_vs_eng_half": kl_t1_half, "T3_kl_eng_vs_wn_half": kl_t2_half,
        "T3_pass": kl_t1_half > 0.1 and kl_t2_half > 0.1,
        "T4_holdout_precision": holdout["precision"], "T4_pass": holdout["precision"] > 0.3,
        "T5_t1_retention": kl_t1_rest / (kl_t1 + 1e-9),
        "T5_t2_retention": kl_t2_rest / (kl_t2 + 1e-9),
        "T5_pass": (kl_t1_rest / (kl_t1 + 1e-9) >= 0.5) and (kl_t2_rest / (kl_t2 + 1e-9) >= 0.5),
        "T7_ratio": t7_ratio, "T7_pass": t7_ratio < T7_RATIO_MAX,
        "T8_kl_AB_to_EN": kl_t8_en, "T8_kl_AB_to_WN": kl_t8_wn,
        "T8_pass": kl_t8_en < kl_t8_wn,
        "T9_autocorr_trained": autocorr_tr, "T9_autocorr_fresh": autocorr_fr,
        "T9_pass": autocorr_tr > T9_AUTOCORR_MIN and autocorr_tr > T9_RATIO_MIN * max(autocorr_fr, 1e-9),
        "T13_coverage_en": cov_en, "T13_coverage_wn": cov_wn, "T13_ratio": ratio_t13,
        "T13_pass": cov_en > T13_COVERAGE_EN_MIN and ratio_t13 > T13_RATIO_MIN,
        "rng_seed": RNG_SEED,
        "neg_control_kl": neg_kl,
    }


def test_seed_robust(substrates):
    m = _compute(substrates)
    all_pass = all(m[f"T{t}_pass"] for t in [0,1,2,3,4,5,7,8,9,13])
    if not all_pass:
        flags = ", ".join(f"T{t}={m[f'T{t}_pass']}" for t in [0,1,2,3,4,5,7,8,9,13])
        pytest.fail(
            f"BET-022 NULL: SOM+replay with seed=42 doesn't pass T0-T9+T13.\n  {flags}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _compute(substrates)
    all_pass = all(m[f"T{t}_pass"] for t in [0,1,2,3,4,5,7,8,9,13])
    verdict = "passed" if all_pass else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-022", "verdict": verdict,
        "hypothesis": "Robustness check: SOM+replay with rng_seed=42 (vs locked 0) tested against T0-T9+T13.",
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

"""BET-024 — multi-seed robustness: SOM+replay at 4 seeds (0, 42, 1337, 271828).

For each seed, run SOM+replay full T0-T9+T13 suite. Report pass rate.

Bar (LOCKED): at least 3 of 4 seeds pass T0-T9+T13 simultaneously.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import (
    SOMReplayConfig, initialise, run, evaluate_holdout,
)
from world.flux.cognitive_map import encode_sensor
from world.flux.harder_bar_metrics import (
    hist_kl_symmetric, shuffle_chunks_in_time, spatial_autocorrelation,
)

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
SEEDS = (0, 42, 1337, 271828)
WN_SEED = 9999
SHUFFLE_SEED = 11111
TARGET_RMS = 0.25
N_QUERIES_PER_CLASS = 1000

T7_RATIO_MAX = 0.10
T9_AUTOCORR_MIN = 0.3
T9_RATIO_MIN = 2.0
T13_COVERAGE_EN_MIN = 0.10
T13_RATIO_MIN = 2.0

PASS_RATE_MIN = 3  # 3 of 4 seeds

OUT_DIR = Path.home() / ".eqmod/bet/BET-024"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _copy_state(state):
    return {
        "w": state["w"].copy(), "N": state["N"].copy(),
        "ii": state["ii"], "jj": state["jj"], "kk": state["kk"],
        "buffer": state["buffer"].copy(), "buffer_head": state["buffer_head"],
        "buffer_fill": state["buffer_fill"], "global_tick": state["global_tick"],
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


def _run_one_seed(seed: int, eng_a, eng_b, wn, eng_queries, wn_queries):
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, rng_seed=seed,
    )
    n_half = (N_TICKS // 2) * SAMPLES_PER_TICK
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

    Lx, Ly, Lz = cfg.grid_dims
    n_cells = Lx * Ly * Lz
    bmu_eng = _gather(state_eng, eng_queries, cfg, N_QUERIES_PER_CLASS)
    bmu_wn = _gather(state_eng, wn_queries, cfg, N_QUERIES_PER_CLASS)
    n_u_en = int(np.unique(bmu_eng).size)
    n_u_wn = int(np.unique(bmu_wn).size)

    f_eng = state_eng["w"]
    f_wn = state_wn["w"]
    f_eng_half = state_eng_half["w"]
    f_wn_half = state_wn_half["w"]
    f_eng_rest = state_eng_rest["w"]
    f_eng_shuffled = state_eng_shuffled["w"]
    f_AB = state_AB["w"]

    t0_std = float(f_eng.std())
    kl_t1 = hist_kl_symmetric(field_init, f_eng)
    kl_t2 = hist_kl_symmetric(f_eng, f_wn)
    kl_t1_half = hist_kl_symmetric(field_init, f_eng_half)
    kl_t2_half = hist_kl_symmetric(f_eng_half, f_wn_half)
    kl_t1_rest = hist_kl_symmetric(field_init, f_eng_rest)
    kl_t2_rest = hist_kl_symmetric(f_eng_rest, f_wn)
    kl_t7_shuf = hist_kl_symmetric(f_eng, f_eng_shuffled)
    kl_t7_fresh = hist_kl_symmetric(f_eng, field_init)
    t7_ratio = kl_t7_shuf / (kl_t7_fresh + 1e-9)
    kl_t8_en = hist_kl_symmetric(f_AB, f_eng)
    kl_t8_wn = hist_kl_symmetric(f_AB, f_wn)
    autocorr_tr = spatial_autocorrelation(f_eng)
    autocorr_fr = spatial_autocorrelation(field_init)
    cov_en = n_u_en / n_cells
    cov_wn = n_u_wn / n_cells
    ratio_t13 = cov_en / max(cov_wn, 1e-9)

    flags = {
        "T0": t0_std > 0.05,
        "T1": kl_t1 > 0.1,
        "T2": kl_t2 > 0.1,
        "T3": kl_t1_half > 0.1 and kl_t2_half > 0.1,
        "T4": holdout["precision"] > 0.3,
        "T5": (kl_t1_rest / (kl_t1 + 1e-9) >= 0.5) and (kl_t2_rest / (kl_t2 + 1e-9) >= 0.5),
        "T7": t7_ratio < T7_RATIO_MAX,
        "T8": kl_t8_en < kl_t8_wn,
        "T9": autocorr_tr > T9_AUTOCORR_MIN and autocorr_tr > T9_RATIO_MIN * max(autocorr_fr, 1e-9),
        "T13": cov_en > T13_COVERAGE_EN_MIN and ratio_t13 > T13_RATIO_MIN,
    }
    all_pass = all(flags.values())
    return {
        "seed": seed,
        "flags": flags,
        "all_pass": all_pass,
        "T2_kl": kl_t2,
        "T8_AB_to_EN": kl_t8_en,
        "T8_AB_to_WN": kl_t8_wn,
        "T9_autocorr": autocorr_tr,
        "T13_ratio": ratio_t13,
        "T13_coverage_en": cov_en,
    }


@pytest.fixture(scope="module")
def substrates():
    n_audio = N_TICKS * SAMPLES_PER_TICK
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

    results = [_run_one_seed(s, eng_a, eng_b, wn, eng_queries, wn_queries) for s in SEEDS]
    return {
        "results": results,
        "n_pass": sum(1 for r in results if r["all_pass"]),
        "n_total": len(results),
    }


def test_multi_seed(substrates):
    if substrates["n_pass"] < PASS_RATE_MIN:
        lines = []
        for r in substrates["results"]:
            fl = " ".join(f"{k}={v}" for k,v in r['flags'].items())
            lines.append(f"  seed={r['seed']}: all={r['all_pass']} flags={fl}")
        pytest.fail(
            f"BET-024 NULL: only {substrates['n_pass']}/{substrates['n_total']} seeds pass T0-T9+T13.\n"
            + "\n".join(lines)
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    pass_rate = substrates["n_pass"] / substrates["n_total"]
    verdict = "passed" if substrates["n_pass"] >= PASS_RATE_MIN else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-024",
        "verdict": verdict,
        "hypothesis": "Multi-seed robustness: SOM+replay across 4 seeds (0,42,1337,271828) on T0-T9+T13. Bar: at least 3 of 4 pass.",
        "thresholds": {"pass_rate_min": PASS_RATE_MIN, "n_seeds": len(SEEDS)},
        "measurements": {
            "n_pass": substrates["n_pass"],
            "n_total": substrates["n_total"],
            "pass_rate": pass_rate,
            "per_seed": substrates["results"],
        },
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

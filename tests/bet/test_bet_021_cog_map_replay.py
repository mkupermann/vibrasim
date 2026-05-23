"""BET-021 — cog_map β=0 + replay through T0-T9 + T13.

Cross-substrate-class robustness check. If pseudo-rehearsal replay
fixes T8 catastrophic-forgetting universally, cog_map β=0 + replay
should pass T8 too. T13 (BMU coverage) also tested for output-side
discrimination.

Locked bar: T0-T9 (from LOGBOOK 2026-05-23 ~20:55) + T13 (from
LOGBOOK 2026-05-24 00:10). Same thresholds as BET-012/019.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.cog_map_replay import (
    CogMapReplayConfig, initialise, run, evaluate_holdout,
)
from world.flux.cognitive_map import encode_sensor, position_hash
from world.flux.harder_bar_metrics import (
    hist_kl_symmetric, shuffle_chunks_in_time, spatial_autocorrelation,
)

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
SHUFFLE_SEED = 11111
TARGET_RMS = 0.25
N_QUERIES_PER_CLASS = 1000

T7_RATIO_MAX = 0.10
T9_AUTOCORR_MIN = 0.3
T9_RATIO_MIN = 2.0
T13_COVERAGE_EN_MIN = 0.10
T13_RATIO_MIN = 2.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-021"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _copy_state(state):
    return {
        "mu": state["mu"].copy(),
        "Lambda": state["Lambda"].copy(),
        "N": state["N"].copy(),
        "buffer": {
            "sensors": state["buffer"]["sensors"].copy(),
            "sample_indices": state["buffer"]["sample_indices"].copy(),
            "sample_values": state["buffer"]["sample_values"].copy(),
            "head": state["buffer"]["head"], "fill": state["buffer"]["fill"],
        },
        "global_tick": state["global_tick"],
    }


def _bmu_position(state, sensor, sample_index, sample_value, cfg) -> int:
    """For cog_map: the 'BMU' is the position-hash output (deterministic from content)."""
    pos = position_hash(sample_index, sample_value, cfg)
    Lx, Ly, Lz = cfg.grid_dims
    return pos[0] * Ly * Lz + pos[1] * Lz + pos[2]


def _gather_positions(audio, cfg, n_queries, tick_offset=0):
    n = min(n_queries, audio.size // cfg.samples_per_tick)
    positions = np.zeros(n, dtype=np.int64)
    for k in range(n):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = audio[i0:i1]
        if chunk.size == 0:
            continue
        sample_index = (tick_offset + k) * cfg.samples_per_tick + (chunk.size - 1)
        sample_value = float(chunk[-1])
        positions[k] = _bmu_position(None, None, sample_index, sample_value, cfg)
    return positions


@pytest.fixture(scope="module")
def substrates():
    cfg = CogMapReplayConfig()
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
    field_init = state_init["mu"].copy()

    state_eng = run(cfg, N_TICKS, eng_a)
    state_wn = run(cfg, N_TICKS, wn)
    state_neg = run(cfg, N_TICKS, None)

    state_eng_half = run(cfg, N_TICKS // 2, eng_a[:n_half])
    state_wn_half = run(cfg, N_TICKS // 2, wn[:n_half])

    state_eng_rest = run(cfg, N_TICKS, None, state=_copy_state(state_eng))

    state_holdout_train = run(cfg, N_TICKS // 2, eng_b[:n_half])
    holdout = evaluate_holdout(
        state_holdout_train, eng_b[n_half:], cfg, tick_offset=N_TICKS // 2,
    )

    eng_a_shuffled = shuffle_chunks_in_time(eng_a, SAMPLES_PER_TICK, SHUFFLE_SEED)
    state_eng_shuffled = run(cfg, N_TICKS, eng_a_shuffled)

    state_AB = run(cfg, N_TICKS, wn, state=_copy_state(state_eng))

    # T13: gather BMU-positions for class queries
    Lx, Ly, Lz = cfg.grid_dims
    n_cells = Lx * Ly * Lz
    pos_en = _gather_positions(eng_queries, cfg, N_QUERIES_PER_CLASS, tick_offset=2 * N_TICKS)
    pos_wn = _gather_positions(wn_queries, cfg, N_QUERIES_PER_CLASS, tick_offset=2 * N_TICKS)
    n_unique_en = int(np.unique(pos_en).size)
    n_unique_wn = int(np.unique(pos_wn).size)

    return dict(
        cfg=cfg, n_cells=n_cells, field_init=field_init,
        state_eng=state_eng, state_wn=state_wn, state_neg=state_neg,
        state_eng_half=state_eng_half, state_wn_half=state_wn_half,
        state_eng_rest=state_eng_rest, state_eng_shuffled=state_eng_shuffled,
        state_AB=state_AB, holdout=holdout,
        n_unique_en=n_unique_en, n_unique_wn=n_unique_wn,
    )


def _compute_all(sub):
    field_init = sub["field_init"]
    field_eng = sub["state_eng"]["mu"]
    field_wn = sub["state_wn"]["mu"]
    field_neg = sub["state_neg"]["mu"]
    field_eng_half = sub["state_eng_half"]["mu"]
    field_wn_half = sub["state_wn_half"]["mu"]
    field_eng_rest = sub["state_eng_rest"]["mu"]
    field_eng_shuffled = sub["state_eng_shuffled"]["mu"]
    field_AB = sub["state_AB"]["mu"]
    holdout = sub["holdout"]
    n_cells = sub["n_cells"]

    t0_std = float(field_eng.std())
    kl_t1 = hist_kl_symmetric(field_init, field_eng)
    kl_t2 = hist_kl_symmetric(field_eng, field_wn)
    kl_t1_half = hist_kl_symmetric(field_init, field_eng_half)
    kl_t2_half = hist_kl_symmetric(field_eng_half, field_wn_half)
    kl_t1_rest = hist_kl_symmetric(field_init, field_eng_rest)
    kl_t2_rest = hist_kl_symmetric(field_eng_rest, field_wn)
    neg_kl = hist_kl_symmetric(field_neg, field_eng)
    kl_t7_shuf = hist_kl_symmetric(field_eng, field_eng_shuffled)
    kl_t7_fresh = hist_kl_symmetric(field_eng, field_init)
    t7_ratio = kl_t7_shuf / (kl_t7_fresh + 1e-9)
    kl_t8_en = hist_kl_symmetric(field_AB, field_eng)
    kl_t8_wn = hist_kl_symmetric(field_AB, field_wn)
    autocorr_tr = spatial_autocorrelation(field_eng)
    autocorr_fr = spatial_autocorrelation(field_init)
    coverage_en = sub["n_unique_en"] / n_cells
    coverage_wn = sub["n_unique_wn"] / n_cells
    ratio = coverage_en / max(coverage_wn, 1e-9)

    return {
        "substrate": "cog_map_replay (β=0)",
        "T0_spatial_std": t0_std, "T0_pass": t0_std > 0.05,
        "T1_kl_init_vs_eng": kl_t1, "T1_pass": kl_t1 > 0.1,
        "T2_kl_eng_vs_wn": kl_t2, "T2_pass": kl_t2 > 0.1,
        "T3_kl_init_vs_eng_half": kl_t1_half,
        "T3_kl_eng_vs_wn_half": kl_t2_half,
        "T3_pass": kl_t1_half > 0.1 and kl_t2_half > 0.1,
        "T4_holdout_precision": holdout["precision"],
        "T4_pass": holdout["precision"] > 0.3,
        "T5_t1_retention": kl_t1_rest / (kl_t1 + 1e-9),
        "T5_t2_retention": kl_t2_rest / (kl_t2 + 1e-9),
        "T5_pass": (kl_t1_rest / (kl_t1 + 1e-9) >= 0.5) and (kl_t2_rest / (kl_t2 + 1e-9) >= 0.5),
        "T7_ratio": t7_ratio, "T7_pass": t7_ratio < T7_RATIO_MAX,
        "T8_kl_AB_to_EN": kl_t8_en, "T8_kl_AB_to_WN": kl_t8_wn,
        "T8_pass": kl_t8_en < kl_t8_wn,
        "T9_autocorr_trained": autocorr_tr,
        "T9_autocorr_fresh": autocorr_fr,
        "T9_pass": autocorr_tr > T9_AUTOCORR_MIN and autocorr_tr > T9_RATIO_MIN * max(autocorr_fr, 1e-9),
        "T13_coverage_en": coverage_en, "T13_coverage_wn": coverage_wn,
        "T13_ratio": ratio,
        "T13_pass": coverage_en > T13_COVERAGE_EN_MIN and ratio > T13_RATIO_MIN,
        "n_unique_en": sub["n_unique_en"], "n_unique_wn": sub["n_unique_wn"],
        "neg_control_kl": neg_kl,
        "all_locked_T0_T5_pass": False,  # filled below
        "all_harder_T7_T9_pass": False,
        "all_ten_T0_T9_pass": False,
        "all_eleven_T0_T9_T13_pass": False,
    }


def _attach_aggregates(m):
    m["all_locked_T0_T5_pass"] = (
        m["T0_pass"] and m["T1_pass"] and m["T2_pass"] and m["T3_pass"]
        and m["T4_pass"] and m["T5_pass"]
    )
    m["all_harder_T7_T9_pass"] = m["T7_pass"] and m["T8_pass"] and m["T9_pass"]
    m["all_ten_T0_T9_pass"] = m["all_locked_T0_T5_pass"] and m["all_harder_T7_T9_pass"]
    m["all_eleven_T0_T9_T13_pass"] = m["all_ten_T0_T9_pass"] and m["T13_pass"]
    return m


def test_cog_map_replay_passes_T0_T9_T13(substrates):
    m = _attach_aggregates(_compute_all(substrates))
    if not m["all_eleven_T0_T9_T13_pass"]:
        summary = ", ".join([
            f"T{t}={m[f'T{t}_pass']}" for t in [0,1,2,3,4,5,7,8,9,13]
        ])
        pytest.fail(
            f"BET-021 NULL: cog_map+replay does not pass T0-T9+T13.\n"
            f"  {summary}\n"
            f"  T8 detail: AB→EN={m['T8_kl_AB_to_EN']:.4e}, AB→WN={m['T8_kl_AB_to_WN']:.4f}\n"
            f"  T9 autocorr: trained={m['T9_autocorr_trained']:.4f}, fresh={m['T9_autocorr_fresh']:.4f}\n"
            f"  T13 coverage EN={m['T13_coverage_en']:.4f}, ratio={m['T13_ratio']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _attach_aggregates(_compute_all(substrates))
    verdict = "passed" if m["all_eleven_T0_T9_T13_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-021",
        "verdict": verdict,
        "hypothesis": "cog_map β=0 + pseudo-rehearsal replay through T0-T9+T13. Cross-substrate-class verification that replay mechanism is universal, not SOM-specific.",
        "thresholds": {
            "T0_std_min": 0.05, "T1_T2_T3_kl_min": 0.1,
            "T4_precision_min": 0.3, "T5_retention_min": 0.5,
            "T7_ratio_max": T7_RATIO_MAX,
            "T8_must": "KL(AB,EN) < KL(AB,WN)",
            "T9_autocorr_min": T9_AUTOCORR_MIN, "T9_ratio_min": T9_RATIO_MIN,
            "T13_coverage_min": T13_COVERAGE_EN_MIN, "T13_ratio_min": T13_RATIO_MIN,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

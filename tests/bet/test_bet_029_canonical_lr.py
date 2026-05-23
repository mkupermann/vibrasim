"""BET-029 — canonical T0-T17 at 100k ticks (LR scale).

BET-028 at 10k showed 11/12 PASS but T15 NULL with ratio 0.517 (just
above 0.5 bar) because far query slice has higher quantization error
than near query slice. At 100k training, substrate covers more of
corpus → T15 should improve.
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

N_TICKS = 100_000   # 10x BET-028
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
SHUFFLE_SEED = 11111
TARGET_RMS = 0.25
N_QUERIES_PER_CLASS = 1000

OUT_DIR = Path.home() / ".eqmod/bet/BET-029"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
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


def _gather(state, audio, cfg, n):
    out = np.zeros(n, dtype=np.int64)
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        out[k] = _bmu_idx(state, encode_sensor(chunk, cfg))
    return out


def _quant_err(state, audio, cfg, n):
    errs = []
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        diff = state["w"] - sensor
        bmu = np.unravel_index(int(np.argmin(np.einsum("ijkl,ijkl->ijk", diff, diff))), diff.shape[:3])
        errs.append(float(np.linalg.norm(sensor - state["w"][bmu])))
    return float(np.mean(errs)) if errs else 0.0


def _sample_features(audio, cfg, n):
    feats = np.zeros((n, cfg.n_features), dtype=np.float64)
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        feats[k] = encode_sensor(chunk, cfg)
    return feats


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_half = (N_TICKS // 2) * SAMPLES_PER_TICK
    n_query = N_QUERIES_PER_CLASS * SAMPLES_PER_TICK
    n_sample = 10_000 * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if 2 * n_audio + n_query + n_sample > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_a = full[:n_audio].astype(np.float64)
    eng_b = full[n_audio:2 * n_audio].astype(np.float64)
    wn = _make_wn(n_audio, TARGET_RMS, WN_SEED)
    eng_queries = full[2 * n_audio:2 * n_audio + n_query].astype(np.float64)
    wn_queries = _make_wn(n_query, TARGET_RMS, WN_SEED + 1)
    eng_sample = full[2 * n_audio + n_query:2 * n_audio + n_query + n_sample].astype(np.float64)

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
    quant_e_en = _quant_err(state_eng, eng_queries, cfg, N_QUERIES_PER_CLASS)
    quant_e_wn = _quant_err(state_eng, wn_queries, cfg, N_QUERIES_PER_CLASS)
    en_input_features = _sample_features(eng_sample, cfg, 10_000)

    return dict(
        cfg=cfg, n_cells=n_cells, field_init=field_init,
        state_eng=state_eng, state_wn=state_wn, state_neg=state_neg,
        state_eng_half=state_eng_half, state_wn_half=state_wn_half,
        state_eng_rest=state_eng_rest, state_eng_shuffled=state_eng_shuffled,
        state_AB=state_AB, holdout=holdout,
        n_u_en=int(np.unique(bmu_eng).size), n_u_wn=int(np.unique(bmu_wn).size),
        quant_e_en=quant_e_en, quant_e_wn=quant_e_wn,
        en_input_features=en_input_features,
    )


def _compute(sub):
    f_init = sub["field_init"]
    f_eng = sub["state_eng"]["w"]
    f_wn = sub["state_wn"]["w"]
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
    kl_t7_shuf = hist_kl_symmetric(f_eng, f_eng_shuffled)
    kl_t7_fresh = hist_kl_symmetric(f_eng, f_init)
    t7_ratio = kl_t7_shuf / (kl_t7_fresh + 1e-9)
    kl_t8_en = hist_kl_symmetric(f_AB, f_eng)
    kl_t8_wn = hist_kl_symmetric(f_AB, f_wn)
    ac_t = spatial_autocorrelation(f_eng)
    ac_f = spatial_autocorrelation(f_init)
    cov_en = sub["n_u_en"] / n_cells
    cov_wn = sub["n_u_wn"] / n_cells
    ratio_t13 = cov_en / max(cov_wn, 1e-9)
    t15_ratio = sub["quant_e_en"] / max(sub["quant_e_wn"], 1e-9)
    kl_t17 = hist_kl_symmetric(f_eng, sub["en_input_features"])
    kl_t17_neg = hist_kl_symmetric(f_wn, sub["en_input_features"])

    bars = {
        "T0": t0_std > 0.05, "T1": kl_t1 > 0.1, "T2": kl_t2 > 0.1,
        "T3": kl_t1_half > 0.1 and kl_t2_half > 0.1,
        "T4": holdout["precision"] > 0.3,
        "T5": (kl_t1_rest / (kl_t1 + 1e-9) >= 0.5) and (kl_t2_rest / (kl_t2 + 1e-9) >= 0.5),
        "T7": t7_ratio < 0.10, "T8": kl_t8_en < kl_t8_wn,
        "T9": ac_t > 0.3 and ac_t > 2.0 * max(ac_f, 1e-9),
        "T13": cov_en > 0.10 and ratio_t13 > 2.0,
        "T15": t15_ratio < 0.5,
        "T17": kl_t17 < 0.5 and kl_t17_neg > kl_t17,
    }
    return {
        "n_ticks": N_TICKS,
        "substrate": "SOM+replay LR",
        "bars": bars,
        "n_pass": sum(bars.values()),
        "n_total": len(bars),
        "all_pass": all(bars.values()),
        "T15_E_EN": sub["quant_e_en"], "T15_E_WN": sub["quant_e_wn"], "T15_ratio": t15_ratio,
        "T13_coverage_en": cov_en, "T13_ratio": ratio_t13,
        "T8_AB_EN": kl_t8_en, "T8_AB_WN": kl_t8_wn,
        "T9_autocorr_trained": ac_t,
        "T17_kl_en_cells_vs_inputs": kl_t17,
        "kl_t1": kl_t1, "kl_t2": kl_t2,
    }


def test_canonical_lr(substrates):
    m = _compute(substrates)
    if not m["all_pass"]:
        failed = [k for k,v in m["bars"].items() if not v]
        pytest.fail(f"BET-029 NULL at LR: {m['n_pass']}/{m['n_total']} pass; failed: {failed}")


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _compute(substrates)
    verdict = "passed" if m["all_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-029",
        "verdict": verdict,
        "hypothesis": "LR validation of canonical full bar: T0-T9+T13+T15+T17 at 100k ticks.",
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

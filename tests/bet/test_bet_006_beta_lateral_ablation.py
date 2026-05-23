"""BET-006 — Pre-registered ablation: beta_lateral ∈ {0.0, 0.05, 0.1, 0.2}.

BET-005 diagnostic identified the lateral propagation in the Friston cascade
(_lateral_propagate at beta_lateral=0.1) as the dominant factor stripping
per-cell content discrimination. Without lateral, aggregate histogram-KL on
mu-field reached 0.882; with lateral, 0.002.

This iteration is a SINGLE-FACTOR ablation: vary beta_lateral, hold everything
else at BET-002 baseline (samples_per_tick=16, fft_bands=8, n_features=10,
grid_dims=(30,15,8), R-7 corpus audio). Per variant, compute the locked
T0-T5 measurements with the bet-pre-registered thresholds.

Pre-data prediction (locked in BET-005 postmortem before this file existed):
  beta=0.0  → T0,T1,T2,T3 PASS (T2≈0.88), T4 risky (no neighbour smoothing → cells
              that never received a sample during training give worthless predictions
              for content-hashed positions outside their visit set), T5 risky.
  beta=0.05 → T2 should be much better than 0.1's near-zero but smaller than 0.0.
  beta=0.1  → BET-002/003/004 baseline, T2 known FAIL.
  beta=0.2  → T2 even worse than 0.1 (more averaging-out across cells).

If ANY variant passes T0+T1+T2+T3+T4+T5 simultaneously: bet WIN candidate,
pytest exits 0 + result.json verdict='passed'. Else verdict='null'.

No threshold tuning is permitted. The 0.05/0.1/0.3/0.5 bars from LOGBOOK
2026-05-22 are the bars used here.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.cognitive_map import (
    MapConfig, evaluate_holdout, initialise, run,
)

# ---------- Pre-registered fixtures (locked before any iteration runs) ----------
BETA_VALUES = (0.0, 0.05, 0.1, 0.2)
N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25
N_BINS = 32

OUT_DIR = Path.home() / ".eqmod/bet/BET-006"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples: int, target_rms: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _hist_kl(a: np.ndarray, b: np.ndarray, n_bins: int = N_BINS) -> float:
    a_flat = a.ravel()
    b_flat = b.ravel()
    lo = min(a_flat.min(), b_flat.min())
    hi = max(a_flat.max(), b_flat.max())
    if hi - lo < 1e-12:
        return 0.0
    edges = np.linspace(lo, hi, n_bins + 1)
    ha, _ = np.histogram(a_flat, bins=edges)
    hb, _ = np.histogram(b_flat, bins=edges)
    pa = (ha + 1.0) / (ha.sum() + n_bins)
    pb = (hb + 1.0) / (hb.sum() + n_bins)
    return 0.5 * (float(np.sum(pa * np.log(pa / pb))) + float(np.sum(pb * np.log(pb / pa))))


def _run_variant(beta: float, eng_a: np.ndarray, eng_b: np.ndarray, wn_full: np.ndarray) -> dict:
    """Train + evaluate one beta_lateral variant. Returns per-variant measurements."""
    cfg = MapConfig(
        samples_per_tick=SAMPLES_PER_TICK,
        fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
        beta_lateral=beta,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_half = (N_TICKS // 2) * SAMPLES_PER_TICK

    state_init = initialise(cfg)
    mu_init = state_init["mu"].copy()

    state_eng = run(cfg, N_TICKS, eng_a)
    state_wn = run(cfg, N_TICKS, wn_full)
    state_neg = run(cfg, N_TICKS, None)

    state_eng_half = run(cfg, N_TICKS // 2, eng_a[:n_half])
    state_wn_half = run(cfg, N_TICKS // 2, wn_full[:n_half])

    state_eng_rest = run(cfg, N_TICKS, None, state={
        "mu": state_eng["mu"].copy(),
        "Lambda": state_eng["Lambda"].copy(),
        "N": state_eng["N"].copy(),
    })

    state_for_holdout = run(cfg, N_TICKS // 2, eng_b[:n_half])
    holdout = evaluate_holdout(
        state_for_holdout, eng_b[n_half:], cfg, tick_offset=N_TICKS // 2,
    )

    mu_eng = state_eng["mu"]
    mu_wn = state_wn["mu"]
    mu_eng_half = state_eng_half["mu"]
    mu_wn_half = state_wn_half["mu"]
    mu_eng_rest = state_eng_rest["mu"]
    mu_neg = state_neg["mu"]

    t0_std = float(mu_eng.std())
    kl_t1 = _hist_kl(mu_init, mu_eng)
    kl_t2 = _hist_kl(mu_eng, mu_wn)
    kl_t1_half = _hist_kl(mu_init, mu_eng_half)
    kl_t2_half = _hist_kl(mu_eng_half, mu_wn_half)
    kl_t1_rest = _hist_kl(mu_init, mu_eng_rest)
    kl_t2_rest = _hist_kl(mu_eng_rest, mu_wn)
    neg_kl = _hist_kl(mu_neg, mu_eng)

    t0_pass = t0_std > 0.05
    t1_pass = kl_t1 > 0.1
    t2_pass = kl_t2 > 0.1
    t3_pass = kl_t1_half > 0.1 and kl_t2_half > 0.1
    t4_pass = holdout["precision"] > 0.3
    t5_pass = (
        (kl_t1_rest / (kl_t1 + 1e-9) >= 0.5)
        and (kl_t2_rest / (kl_t2 + 1e-9) >= 0.5)
    )
    all_six = t0_pass and t1_pass and t2_pass and t3_pass and t4_pass and t5_pass

    return {
        "beta_lateral": beta,
        "T0_spatial_std_mu_eng": t0_std, "T0_pass": t0_pass,
        "T1_kl_init_vs_eng": kl_t1, "T1_pass": t1_pass,
        "T2_kl_eng_vs_wn": kl_t2, "T2_pass": t2_pass,
        "T3_kl_init_vs_eng_half": kl_t1_half,
        "T3_kl_eng_vs_wn_half": kl_t2_half, "T3_pass": t3_pass,
        "T4_holdout_precision": holdout["precision"],
        "T4_holdout_n": holdout["n"],
        "T4_holdout_mean_cosine": holdout["mean_cosine"], "T4_pass": t4_pass,
        "T5_t1_retention_ratio": kl_t1_rest / (kl_t1 + 1e-9),
        "T5_t2_retention_ratio": kl_t2_rest / (kl_t2 + 1e-9), "T5_pass": t5_pass,
        "neg_control_kl_neg_vs_eng": neg_kl,
        "all_six_pass": all_six,
    }


def _write_result_json(verdict: str, per_variant: list[dict], audio_meta: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-006",
        "verdict": verdict,
        "hypothesis": "Pre-registered beta_lateral ablation on cognitive-map substrate (BET-002 baseline). 4 variants in {0.0, 0.05, 0.1, 0.2}.",
        "thresholds": {
            "T0_spatial_std_min": 0.05, "T1_kl_min": 0.1, "T2_kl_min": 0.1,
            "T3_kl_min": 0.1, "T4_precision_min": 0.3, "T5_retention_min": 0.5,
        },
        "audio": audio_meta,
        "per_variant": per_variant,
        "winning_variant": next(
            (v["beta_lateral"] for v in per_variant if v["all_six_pass"]),
            None,
        ),
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))


@pytest.fixture(scope="module")
def ablation():
    """Run all 4 beta_lateral variants once, return aggregate result + per-variant detail."""
    n_audio = N_TICKS * SAMPLES_PER_TICK
    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if 2 * n_audio > full.shape[0]:
        raise RuntimeError(
            f"R-7 corpus too short for ablation: need 2*{n_audio} samples, have {full.shape[0]}"
        )
    eng_a = full[:n_audio].astype(np.float64)
    eng_b = full[n_audio:2 * n_audio].astype(np.float64)
    wn_full = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)
    audio_meta = {
        "source": "R-7 corpus (manifest)",
        "eng_a_offset": 0, "eng_b_offset": n_audio,
        "n_samples_per_variant_train": n_audio,
        "wn_seed": WN_SEED, "target_rms": TARGET_RMS,
    }

    per_variant = [_run_variant(b, eng_a, eng_b, wn_full) for b in BETA_VALUES]
    any_six = any(v["all_six_pass"] for v in per_variant)
    return {"per_variant": per_variant, "any_six_pass": any_six, "audio_meta": audio_meta}


def test_any_variant_passes_all_six(ablation):
    """Bet-WIN condition: ANY beta_lateral variant satisfies T0+T1+T2+T3+T4+T5 simultaneously.

    Per-variant detail is in result.json regardless of this test's outcome.
    Dispatcher reads verdict from result.json (pytest exit code is secondary).
    """
    per = ablation["per_variant"]
    if not ablation["any_six_pass"]:
        lines = []
        for v in per:
            lines.append(
                f"  beta={v['beta_lateral']:.2f}: T0={v['T0_pass']} T1={v['T1_pass']} "
                f"T2={v['T2_pass']} (kl={v['T2_kl_eng_vs_wn']:.4f}) "
                f"T3={v['T3_pass']} T4={v['T4_pass']} (prec={v['T4_holdout_precision']:.3f}) "
                f"T5={v['T5_pass']}"
            )
        pytest.fail(
            "BET-006 NULL: no beta_lateral variant satisfies all six tests.\n"
            + "\n".join(lines)
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(ablation):
    yield
    verdict = "passed" if ablation["any_six_pass"] else "null"
    _write_result_json(verdict, ablation["per_variant"], ablation["audio_meta"])

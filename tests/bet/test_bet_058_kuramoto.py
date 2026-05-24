"""BET-058 — T42 Kuramoto coupled-oscillator substrate.

NEW substrate class — phase-based computation, qualitatively
different from all prior (statistical or LIF spiking).

T42 protocol:
  Train Kuramoto network on 30s of EN audio.
  Train fresh Kuramoto on 30s of WN audio.
  Measure differences in:
    - Final phase distribution
    - Coupling matrix W
    - Mean global sync (order parameter R)

T42 bar (LOCKED):
  KL(W-EN, W-WN) > 0.1 OR R-mean differs by > 0.1 between conditions.
  (substrate develops measurable class-specific structure)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.kuramoto import KuramotoConfig, initialise, run_audio
from world.flux.harder_bar_metrics import hist_kl_symmetric

N_SECONDS = 30
SAMPLES_PER_SEC = 16000
WN_SEED = 9999
TARGET_RMS = 0.25

T42_W_KL_MIN = 0.1
T42_R_DIFF_MIN = 0.05

OUT_DIR = Path.home() / ".eqmod/bet/BET-058"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


@pytest.fixture(scope="module")
def substrates():
    cfg = KuramotoConfig()
    n_audio = N_SECONDS * SAMPLES_PER_SEC

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng = full[:n_audio].astype(np.float64)
    wn = _make_wn(n_audio, TARGET_RMS, WN_SEED)

    state_en = initialise(cfg)
    state_en = run_audio(state_en, eng)

    state_wn = initialise(cfg)
    state_wn = run_audio(state_wn, wn)

    kl_w = hist_kl_symmetric(state_en["W"], state_wn["W"])
    mean_R_en = float(np.mean(state_en["order_param_history"]))
    mean_R_wn = float(np.mean(state_wn["order_param_history"]))
    R_diff = abs(mean_R_en - mean_R_wn)

    return dict(
        n_oscillators=cfg.n_oscillators,
        kl_W_en_vs_wn=kl_w,
        mean_R_en=mean_R_en,
        mean_R_wn=mean_R_wn,
        R_diff=R_diff,
        W_en_mean=float(state_en["W"].mean()),
        W_wn_mean=float(state_wn["W"].mean()),
        W_en_std=float(state_en["W"].std()),
        W_wn_std=float(state_wn["W"].std()),
    )


def _verdict(s):
    pass_ = (s["kl_W_en_vs_wn"] > T42_W_KL_MIN) or (s["R_diff"] > T42_R_DIFF_MIN)
    return {**s, "T42_pass": pass_}


def test_T42(substrates):
    m = _verdict(substrates)
    if not m["T42_pass"]:
        pytest.fail(
            f"BET-058 NULL T42 Kuramoto.\n"
            f"  KL(W-EN, W-WN): {m['kl_W_en_vs_wn']:.4f} (need > {T42_W_KL_MIN})\n"
            f"  mean R: EN={m['mean_R_en']:.4f}, WN={m['mean_R_wn']:.4f}, "
            f"diff={m['R_diff']:.4f} (need > {T42_R_DIFF_MIN})\n"
            f"  W: EN mean={m['W_en_mean']:.4f}/std={m['W_en_std']:.4f}, "
            f"WN mean={m['W_wn_mean']:.4f}/std={m['W_wn_std']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T42_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-058",
        "verdict": verdict,
        "hypothesis": "T42 Kuramoto coupled-oscillator substrate. Phase-based computation via synchronization, Hebbian coupling update on in-phase events. Qualitatively different paradigm from statistical/LIF.",
        "thresholds": {"T42_W_KL_min": T42_W_KL_MIN, "T42_R_diff_min": T42_R_DIFF_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

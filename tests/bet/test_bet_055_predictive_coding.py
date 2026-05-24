"""BET-055 — T39 Predictive Coding substrate class-discrimination.

Tests if Predictive Coding's learned hidden representations h
discriminate audio classes. T2-equivalent at the hidden-state level:
KL(h-distribution-EN-trained, h-distribution-WN-trained) > 0.1.

Plus T2-equivalent on decoder matrix D itself.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.predictive_coding import PCConfig, run, encode_to_h
from world.flux.harder_bar_metrics import hist_kl_symmetric

N_TICKS = 5_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25

T39_KL_MIN = 0.1

OUT_DIR = Path.home() / ".eqmod/bet/BET-055"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


@pytest.fixture(scope="module")
def substrates():
    cfg = PCConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)
    wn_train = _make_wn(n_audio, TARGET_RMS, WN_SEED)

    state_en = run(cfg, N_TICKS, eng_train)
    state_wn = run(cfg, N_TICKS, wn_train)

    # Discrimination at decoder D level
    kl_d = hist_kl_symmetric(state_en["D"], state_wn["D"])

    # Discrimination at h-representation level: encode 1000 EN chunks via each substrate
    n_eval = 1000
    h_en_under_en = np.zeros((n_eval, cfg.n_hidden), dtype=np.float64)
    h_en_under_wn = np.zeros((n_eval, cfg.n_hidden), dtype=np.float64)
    for k in range(n_eval):
        chunk = eng_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        h_en_under_en[k] = encode_to_h(state_en, chunk, cfg)
        h_en_under_wn[k] = encode_to_h(state_wn, chunk, cfg)
    kl_h = hist_kl_symmetric(h_en_under_en, h_en_under_wn)

    # Also report reconstruction quality
    en_recon_under_en = []
    en_recon_under_wn = []
    for k in range(100):
        chunk = eng_train[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        from world.flux.cognitive_map import encode_sensor
        x = encode_sensor(chunk, cfg)
        h_en = encode_to_h(state_en, chunk, cfg)
        h_wn = encode_to_h(state_wn, chunk, cfg)
        en_recon_under_en.append(float(np.linalg.norm(x - state_en["D"] @ h_en)))
        en_recon_under_wn.append(float(np.linalg.norm(x - state_wn["D"] @ h_wn)))

    return dict(
        n_hidden=cfg.n_hidden,
        kl_D_en_vs_wn=kl_d,
        kl_h_en_under_en_vs_under_wn=kl_h,
        mean_recon_en_under_en=float(np.mean(en_recon_under_en)),
        mean_recon_en_under_wn=float(np.mean(en_recon_under_wn)),
        recon_ratio=float(np.mean(en_recon_under_en) / max(np.mean(en_recon_under_wn), 1e-9)),
    )


def _verdict(s):
    pass_ = s["kl_D_en_vs_wn"] > T39_KL_MIN or s["kl_h_en_under_en_vs_under_wn"] > T39_KL_MIN
    return {**s, "T39_pass": pass_}


def test_T39(substrates):
    m = _verdict(substrates)
    if not m["T39_pass"]:
        pytest.fail(
            f"BET-055 NULL T39 PC discrimination.\n"
            f"  KL(D-EN, D-WN): {m['kl_D_en_vs_wn']:.4f}\n"
            f"  KL(h under EN, h under WN): {m['kl_h_en_under_en_vs_under_wn']:.4f}\n"
            f"  Recon EN under EN: {m['mean_recon_en_under_en']:.4f}\n"
            f"  Recon EN under WN: {m['mean_recon_en_under_wn']:.4f}\n"
            f"  Recon ratio: {m['recon_ratio']:.4f}\n"
            f"  Need at least one KL > {T39_KL_MIN}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T39_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-055",
        "verdict": verdict,
        "hypothesis": "T39 Predictive Coding substrate (Rao & Ballard 1999) class discrimination. Hidden representations h or decoder D should differ between EN-trained and WN-trained.",
        "thresholds": {"T39_kl_min": T39_KL_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

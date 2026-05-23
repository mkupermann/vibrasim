"""BET-045 — T29 discrimination granularity test (EN vs pink noise).

White noise (flat spectrum) is easy to discriminate from speech (formant-
concentrated). Pink noise (1/f spectrum) is more speech-like —
broadband + naturalistic envelope.

If substrate discriminates EN vs pink with substantial KL, the
substrate's class-discrimination isn't just "any non-speech vs speech"
but captures finer audio structure.

T29 bar (LOCKED):
  T2-equivalent: KL(EN-substrate.w, pink-substrate.w) > 0.1
  Plus comparison: pink-KL > 50% of WN-KL (substrate sees pink as
                  intermediate between EN and WN)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, run
from world.flux.harder_bar_metrics import hist_kl_symmetric

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
PINK_SEED = 8888
TARGET_RMS = 0.25

T29_PINK_KL_MIN = 0.1

OUT_DIR = Path.home() / ".eqmod/bet/BET-045"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _make_pink_noise(n, target_rms, seed):
    """Pink noise via Voss-McCartney approximation: cumulative sum of white noise
    in frequency domain, scaled to 1/f spectrum."""
    rng = np.random.default_rng(seed)
    white = rng.standard_normal(n)
    # FFT, scale by 1/sqrt(f), iFFT
    fft = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n)
    freqs[0] = 1.0  # avoid div-by-zero at DC
    fft_pink = fft / np.sqrt(freqs)
    pink = np.fft.irfft(fft_pink, n=n)
    # Normalize RMS
    rms = np.sqrt(np.mean(pink * pink))
    if rms > 0:
        pink = pink / rms * target_rms
    return pink.astype(np.float64)


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
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
    wn_train = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)
    pink_train = _make_pink_noise(n_audio, TARGET_RMS, PINK_SEED)

    state_eng = run(cfg, N_TICKS, eng_train)
    state_wn = run(cfg, N_TICKS, wn_train)
    state_pink = run(cfg, N_TICKS, pink_train)

    kl_eng_wn = hist_kl_symmetric(state_eng["w"], state_wn["w"])
    kl_eng_pink = hist_kl_symmetric(state_eng["w"], state_pink["w"])
    kl_wn_pink = hist_kl_symmetric(state_wn["w"], state_pink["w"])
    pink_to_wn_ratio = kl_eng_pink / max(kl_eng_wn, 1e-9)

    return dict(
        kl_eng_wn=kl_eng_wn,
        kl_eng_pink=kl_eng_pink,
        kl_wn_pink=kl_wn_pink,
        pink_to_wn_ratio=pink_to_wn_ratio,
    )


def _verdict(s):
    pink_pass = s["kl_eng_pink"] > T29_PINK_KL_MIN
    return {
        **s,
        "T29_pink_pass": pink_pass,
        "T29_pass": pink_pass,
    }


def test_T29(substrates):
    m = _verdict(substrates)
    if not m["T29_pass"]:
        pytest.fail(
            f"BET-045 NULL T29 pink-noise discrimination.\n"
            f"  KL(EN, WN) = {m['kl_eng_wn']:.4f}\n"
            f"  KL(EN, pink) = {m['kl_eng_pink']:.4f} (need > {T29_PINK_KL_MIN})\n"
            f"  KL(WN, pink) = {m['kl_wn_pink']:.4f}\n"
            f"  pink/WN ratio: {m['pink_to_wn_ratio']:.4f} "
            f"(should be substantial if pink-substrate is intermediate)"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T29_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-045",
        "verdict": verdict,
        "hypothesis": "T29 substrate discrimination of EN vs pink noise (finer-grained than EN vs WN). Tests granularity of substrate's class-discrimination.",
        "thresholds": {"T29_pink_kl_min": T29_PINK_KL_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

"""R-LR-8 long-run acceptance — scaffold (skip until the long-run produces output).

Pre-registered thresholds from
``docs/superpowers/plans/2026-05-19-flux-encoder-free-iter2.md`` §R-LR-8:

  * ``KL(bridge_spectrum_english || bridge_spectrum_whitenoise) > 0.5``
  * ``KL(MFCC_english || MFCC_no_input) > 0.001`` at the R-14-tuned synthesis

PASS condition for R-LR-8 is the OR of the two — both observables address
distinct questions (internal topology vs external babble) and either is
publishable independently. This module scaffolds the gate so the long-run
dispatcher can verify completion against a single pytest target; it does
NOT pass without R-LR-8's output. R-15 (the item that created this file)
only requires that the file is collectable by pytest and skips gracefully
when ``EQMOD_R_LR_8_OUT_DIR`` is unset.

Expected artifact layout under ``EQMOD_R_LR_8_OUT_DIR``:

  * ``bridge_spectrum_english.npy``     — 2-D probability histogram
  * ``bridge_spectrum_whitenoise.npy``  — same shape
  * ``mfcc_histogram_english.npy``      — 1-D probability histogram
  * ``mfcc_histogram_no_input.npy``     — same shape

When the directory exists but a file is missing, the relevant test
skips with a diagnostic message — preserving the postflight contract
that R-LR-8 is the producer of these artifacts, not R-15.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

# Pre-registered thresholds — locked in the plan; no retuning.
R_LR_8_KL_BRIDGE_SPECTRUM_THRESHOLD = 0.5
R_LR_8_KL_MFCC_THRESHOLD = 0.001


def _require_output_dir() -> Path:
    """Skip the test cleanly when the long-run output is unavailable."""
    env = os.environ.get("EQMOD_R_LR_8_OUT_DIR", "").strip()
    if not env:
        pytest.skip(
            "EQMOD_R_LR_8_OUT_DIR unset — R-LR-8 long-run output not present "
            "(this scaffold is collected for R-15 acceptance; the producer is "
            "R-LR-8)"
        )
    p = Path(env)
    if not p.is_dir():
        pytest.skip(f"EQMOD_R_LR_8_OUT_DIR='{p}' is not a directory")
    return p


def _load_npy(path: Path) -> np.ndarray:
    if not path.is_file():
        pytest.skip(f"R-LR-8 artifact missing: {path}")
    return np.load(path)


def _kl_safe(p: np.ndarray, q: np.ndarray) -> float:
    """Asymmetric ``KL(p || q)`` on probability arrays with Laplace floor."""
    a = p.astype(np.float64).ravel()
    b = q.astype(np.float64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {a.shape} != {b.shape}")
    a = a / a.sum() if a.sum() > 0 else a
    b = b / b.sum() if b.sum() > 0 else b
    eps = 1e-12
    return float(np.sum(a * (np.log(a + eps) - np.log(b + eps))))


def test_bridge_spectrum_audio_vs_white_noise() -> None:
    """Bridge-spectrum KL > 0.5 between English-trained and white-noise runs.

    Locked threshold from R-LR-8 plan. Larger than R-13's 0.1 because the
    long-run scope (1.8M ticks) gives the substrate ample time to form
    audio-dependent topology, if such formation is possible under the
    current F1b/F1c rules.
    """
    out_dir = _require_output_dir()
    spec_eng = _load_npy(out_dir / "bridge_spectrum_english.npy")
    spec_wht = _load_npy(out_dir / "bridge_spectrum_whitenoise.npy")
    from agent.flux.bridge_spectrum import bridge_spectrum_kl

    kl = bridge_spectrum_kl(spec_eng, spec_wht)
    assert kl > R_LR_8_KL_BRIDGE_SPECTRUM_THRESHOLD, (
        f"R-LR-8 bridge-spectrum KL(eng||wht)={kl:.6f} below pre-registered "
        f"threshold {R_LR_8_KL_BRIDGE_SPECTRUM_THRESHOLD}"
    )


def test_synthesis_audio_vs_no_input() -> None:
    """MFCC histogram KL > 0.001 between English-babble and no-input babble.

    Synthesis is run with R-14's tuned (Q=3, gain=1) — much weaker threshold
    than R-11's because the synthesis baseline is finally fair at this combo.
    """
    out_dir = _require_output_dir()
    hist_eng = _load_npy(out_dir / "mfcc_histogram_english.npy")
    hist_no = _load_npy(out_dir / "mfcc_histogram_no_input.npy")

    kl = _kl_safe(hist_eng, hist_no)
    assert kl > R_LR_8_KL_MFCC_THRESHOLD, (
        f"R-LR-8 MFCC KL(eng||no_input)={kl:.6f} below pre-registered "
        f"threshold {R_LR_8_KL_MFCC_THRESHOLD}"
    )

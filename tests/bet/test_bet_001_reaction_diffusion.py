"""BET-001 — pre-registered acceptance under the 2026-05-22 bet programme.

Three locked tests (T1, T2, negative-control). T3-T5 deferred to a later
BET-001 iteration if T1+T2 pass. Per LOGBOOK 2026-05-22 bet pre-registration:
5/5 simultaneously is the WIN bar; any NULL on a single tick is a NULL
iteration, which is the expected mode for >95 % of iterations.

Thresholds locked pre-data in ~/.eqmod/bet/queue.yaml::BET-001 description.
No retuning. NULL with substantive measurements goes into the per-iteration
LOGBOOK so the next hypothesis can build on what was actually observed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pytest

from world.flux.reaction_diffusion import RDConfig, run

# ---------- Pre-registered fixtures (locked) ----------
N_TICKS = 10_000
SAMPLES_PER_TICK = 16
SEED_A = 4242
SEED_B = 7777
WN_SEED = 9999
TARGET_RMS = 0.25
N_BINS = 32

OUT_DIR = Path.home() / ".eqmod/bet/BET-001"


def _make_white_noise(n_samples: int, target_rms: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    s = s / np.sqrt(np.mean(s * s)) * target_rms
    return s.astype(np.float64)


def _make_synthetic_english_like(n_samples: int, target_rms: float, seed: int) -> np.ndarray:
    """Synthetic stand-in for the R-7 English Stage-1 corpus. Real corpus is
    16 kHz mono speech; we approximate with a power-law-pinkish noise that
    has a similar fraction-near-zero distribution (silent phoneme stretches)
    and matched RMS. Distinguishable from white noise by spectrum *and*
    amplitude-distribution. Locked pre-data."""
    rng = np.random.default_rng(seed)
    # Pink-ish noise via random-walk-style integration of white noise
    w = rng.standard_normal(n_samples)
    # Light low-pass to imitate phoneme envelope
    pink = np.cumsum(w)
    # Re-baseline + remove DC
    pink -= np.mean(pink)
    # Add intermittent silence: zero out random spans
    n_silence = max(1, n_samples // 50)
    silence_starts = rng.integers(0, n_samples - 50, size=n_silence)
    for s0 in silence_starts:
        pink[s0:s0 + rng.integers(20, 80)] = 0.0
    # Normalise to target RMS
    rms_now = np.sqrt(np.mean(pink * pink))
    if rms_now > 0:
        pink = pink / rms_now * target_rms
    return pink.astype(np.float64)


def _hist_kl(a: np.ndarray, b: np.ndarray, n_bins: int = N_BINS) -> float:
    """Symmetric KL between flattened-array histograms, Laplace-smoothed.

    Pools the range across a and b so the binning is shared.
    """
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
    kl_ab = float(np.sum(pa * np.log(pa / pb)))
    kl_ba = float(np.sum(pb * np.log(pb / pa)))
    return 0.5 * (kl_ab + kl_ba)


def _write_result_json(verdict: str, measurements: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-001",
        "verdict": verdict,
        "measurements": measurements,
        "hypothesis": "Reaction-diffusion as learning substrate (Turing 1952 + Murray + Cross & Hohenberg + Kondo & Miura)",
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))


# ---------- Fixtures ----------
@pytest.fixture(scope="module")
def substrates():
    """Run the three substrate trajectories once and reuse across tests.

    Returns dict with keys: u_eng, v_eng, u_wn, v_wn, u_neg, v_neg, u_init, v_init.
    Each is a final-state field after N_TICKS.
    """
    cfg = RDConfig()
    n_audio = N_TICKS * SAMPLES_PER_TICK

    eng = _make_synthetic_english_like(n_audio, TARGET_RMS, SEED_A)
    wn = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)

    u_init, v_init = run(cfg, n_ticks=0, audio_samples=None, seed=SEED_A)
    u_eng, v_eng = run(cfg, n_ticks=N_TICKS, audio_samples=eng, samples_per_tick=SAMPLES_PER_TICK, seed=SEED_A)
    u_wn, v_wn = run(cfg, n_ticks=N_TICKS, audio_samples=wn, samples_per_tick=SAMPLES_PER_TICK, seed=SEED_A)
    u_neg, v_neg = run(cfg, n_ticks=N_TICKS, audio_samples=None, seed=SEED_A)

    return dict(
        u_init=u_init, v_init=v_init,
        u_eng=u_eng, v_eng=v_eng,
        u_wn=u_wn, v_wn=v_wn,
        u_neg=u_neg, v_neg=v_neg,
    )


# ---------- Tests (T1, T2, negative control) ----------
def test_T1_persistent_topology_change_under_audio_input(substrates):
    """T1 (bet pre-registration): substrate topology after N_TICKS diverges
    from initial state by symmetric KL > 0.1. Measured on the u-field
    histogram (the activator concentration is the primary substrate state)."""
    kl = _hist_kl(substrates["u_init"], substrates["u_eng"])
    measurements = {"T1_kl_u_init_vs_u_eng": kl}
    if kl > 0.1:
        verdict_partial = "T1_PASS"
    else:
        verdict_partial = "T1_NULL"
    # Bet-aware verdict accumulation happens in the wrapper test below;
    # this assertion is per-test for pytest reporting.
    assert kl > 0.1, f"T1 KL={kl:.6f} ≤ 0.1 threshold (verdict {verdict_partial})"


def test_T2_content_discrimination_english_vs_whitenoise(substrates):
    """T2 (bet pre-registration): substrate trained on English diverges
    from substrate trained on matched-RMS white noise by symmetric KL > 0.1."""
    kl = _hist_kl(substrates["u_eng"], substrates["u_wn"])
    assert kl > 0.1, f"T2 KL={kl:.6f} ≤ 0.1 threshold"


def test_negative_control_no_audio_no_pattern(substrates):
    """The substrate with no audio input must produce a state distinguishable
    from the substrate with English input — otherwise the audio is a no-op
    and any T1/T2 PASS would not be attributable to the audio channel."""
    kl = _hist_kl(substrates["u_neg"], substrates["u_eng"])
    assert kl > 0.05, f"negative control KL={kl:.6f} ≤ 0.05 threshold (audio is no-op)"


# ---------- Bet-aware result.json writer (runs at session teardown) ----------
@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    """After all tests in this module complete, write result.json with the
    full measurement record. This is what the bet dispatcher reads."""
    yield  # let tests run
    # Re-compute the measurements for the result.json (tests already asserted)
    kl_t1 = _hist_kl(substrates["u_init"], substrates["u_eng"])
    kl_t2 = _hist_kl(substrates["u_eng"], substrates["u_wn"])
    kl_neg = _hist_kl(substrates["u_neg"], substrates["u_eng"])
    measurements = {
        "T1_kl_u_init_vs_u_eng": kl_t1,
        "T2_kl_u_eng_vs_u_wn": kl_t2,
        "neg_control_kl_u_neg_vs_u_eng": kl_neg,
        "T1_threshold": 0.1,
        "T2_threshold": 0.1,
        "neg_control_threshold": 0.05,
    }
    # Per bet pre-registration, a single-test FAIL is NULL not failed.
    # All five tests required for PASS, but this iteration only ran T1+T2+neg.
    t1_pass = kl_t1 > 0.1
    t2_pass = kl_t2 > 0.1
    neg_pass = kl_neg > 0.05
    if t1_pass and t2_pass and neg_pass:
        # Two of five bet tests passed (T1, T2). T3-T5 not run this iteration.
        # Bet WIN requires 5/5; this is a partial — verdict is NULL with
        # substantive measurements documented.
        verdict = "null"
        measurements["note"] = "T1+T2 PASS; T3/T4/T5 not measured this iteration; bet 5/5 bar requires all five — null is correct verdict"
    else:
        verdict = "null"
        measurements["note"] = "at least one of T1/T2/neg-control failed; iteration informs next hypothesis design"
    _write_result_json(verdict, measurements)

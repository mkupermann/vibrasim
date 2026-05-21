"""R-21 verification — G25 content-driven position injection at 10k ticks.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-21`` rows 5-7 and
``docs/amendments/G25-content-driven-injection.md`` §3.

Three tests:

* Test 5 — position histogram KL > 0.1 between English-audio and
  matched-RMS white-noise substrates. Threshold 0.1 is locked
  pre-data; 10× stronger than R-20's energy-KL threshold because
  position is a higher-bandwidth content channel than amplitude.

* Test 6 — position histogram KL < 0.005 between same English audio
  fed to two substrates with different RNG seeds. Negative control:
  if this fails, the apparent content-coupling in test 5 is a seed
  artefact, not actual content reactivity.

* Test 7 — bridge-weight spectrum KL > 0.01 between the test-5
  substrates. Downstream confirmation that position-channel content
  reaches the bridge layer (not averaged away by binding/plasticity).

All three substrate runs use ``EQMOD_USE_CONTENT_DRIVEN_POSITION=1``
via a session-scoped env-var fixture so they exercise the G25 path.

Locked-by-protocol; no retuning of 0.1 / 0.005 / 0.01 thresholds.
NULL is a valid verdict.
"""
from __future__ import annotations

import os

import numpy as np
import pytest

from agent.flux.bridge_spectrum import (
    bridge_spectrum_kl,
    bridge_weight_spectrum,
    load_english_stage1_segment,
    make_white_noise,
    run_short_encoder_free_substrate,
)


# ---- Locked parameters (pre-data, no retune) -----------------------
# R-20 lineage for SR, SPT, N_TICKS, TARGET_RMS, SUBSTRATE_SEEDs.
# R-21-specific: 2D position-histogram binning chosen pre-data.
SR = 16_000
SPT = 16
N_TICKS = 10_000
N_SAMPLES = N_TICKS * SPT
TARGET_RMS = 0.25
SUBSTRATE_SEED_A = 4242
SUBSTRATE_SEED_B = 7777
WHITE_NOISE_SEED = 9999
GRID_DIMS: tuple[int, int, int] = (30, 15, 8)

# Position-histogram binning. The hot-floor xy extent is
# Lx*voxel_size × Ly*voxel_size = 30 × 15 (voxel_size=1.0). An 8×4 grid
# gives 32 cells with bin width ~3.75 in each dimension — matched in
# total count to R-20's 32-bin energy histogram so cross-diagnostic
# KL comparisons stay on the same scale.
POS_HIST_N_X = 8
POS_HIST_N_Y = 4
POS_HIST_RANGE_X = (0.0, float(GRID_DIMS[0]))
POS_HIST_RANGE_Y = (0.0, float(GRID_DIMS[1]))


# ---- Module-scoped env var for G25 path ---------------------------


@pytest.fixture(scope="module", autouse=True)
def _enable_content_driven_position():
    """Force the content-driven path on for every test in this module.

    Module-scoped so the substrate fixtures see ``EQMOD_USE_CONTENT_DRIVEN_POSITION=1``
    at the moment they invoke ``inject_raw_audio_chunk``. The
    function-scoped pytest ``monkeypatch`` fixture cannot drive a
    module-scoped substrate fixture, hence direct ``os.environ``
    manipulation with explicit restoration.
    """
    key = "EQMOD_USE_CONTENT_DRIVEN_POSITION"
    prev = os.environ.get(key)
    os.environ[key] = "1"
    try:
        yield
    finally:
        if prev is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = prev


# ---- Helpers --------------------------------------------------------


def _english_or_skip() -> np.ndarray:
    eng = load_english_stage1_segment(N_SAMPLES, target_rms=TARGET_RMS)
    if eng is None:
        pytest.skip(
            "R-7 English corpus manifest not available on this machine; "
            "R-21 verification requires Stage-1 audio."
        )
    return eng


def _position_histogram(quanta) -> np.ndarray:
    """Return a length-(N_X*N_Y) normalised 2D position histogram.

    Reads ``quanta.pos[quanta.alive, :2]`` and bins into a 2D grid;
    flattens to 1D for the existing 1D KL helper. Empty input → zero
    array (KL helper Laplace-smooths).
    """
    alive = np.asarray(quanta.alive, dtype=bool)
    if not bool(alive.any()):
        return np.zeros(POS_HIST_N_X * POS_HIST_N_Y, dtype=np.float64)
    xy = np.asarray(quanta.pos[alive, :2], dtype=np.float64)
    hist, _, _ = np.histogram2d(
        xy[:, 0], xy[:, 1],
        bins=[POS_HIST_N_X, POS_HIST_N_Y],
        range=[list(POS_HIST_RANGE_X), list(POS_HIST_RANGE_Y)],
    )
    total = float(hist.sum())
    if total <= 0.0:
        return np.zeros(POS_HIST_N_X * POS_HIST_N_Y, dtype=np.float64)
    return (hist.astype(np.float64) / total).ravel()


def _symmetric_kl(spec_a: np.ndarray, spec_b: np.ndarray) -> float:
    """Symmetric KL via bridge_spectrum_kl Laplace smoothing."""
    kl_ab = bridge_spectrum_kl(spec_a, spec_b)
    kl_ba = bridge_spectrum_kl(spec_b, spec_a)
    return 0.5 * (kl_ab + kl_ba)


# ---- Module-scoped substrate fixtures (one 10k-tick run each) ------


@pytest.fixture(scope="module")
def substrate_english_seed_a():
    """English Stage-1 audio + SUBSTRATE_SEED_A; G25 path active."""
    eng = _english_or_skip()
    nodes, bridges, quanta = run_short_encoder_free_substrate(
        waveform=eng,
        n_ticks=N_TICKS,
        sample_rate_hz=SR,
        samples_per_tick=SPT,
        grid_dims=GRID_DIMS,
        seed=SUBSTRATE_SEED_A,
        return_full_state=True,
    )
    return nodes, bridges, quanta


@pytest.fixture(scope="module")
def substrate_whitenoise_seed_a():
    """Matched-RMS white noise + SUBSTRATE_SEED_A; G25 path active."""
    wht = make_white_noise(N_SAMPLES, target_rms=TARGET_RMS,
                            seed=WHITE_NOISE_SEED)
    nodes, bridges, quanta = run_short_encoder_free_substrate(
        waveform=wht,
        n_ticks=N_TICKS,
        sample_rate_hz=SR,
        samples_per_tick=SPT,
        grid_dims=GRID_DIMS,
        seed=SUBSTRATE_SEED_A,
        return_full_state=True,
    )
    return nodes, bridges, quanta


@pytest.fixture(scope="module")
def substrate_english_seed_b():
    """Same English Stage-1 audio + SUBSTRATE_SEED_B; G25 path active.

    Used only by test 6 (negative control).
    """
    eng = _english_or_skip()
    nodes, bridges, quanta = run_short_encoder_free_substrate(
        waveform=eng,
        n_ticks=N_TICKS,
        sample_rate_hz=SR,
        samples_per_tick=SPT,
        grid_dims=GRID_DIMS,
        seed=SUBSTRATE_SEED_B,
        return_full_state=True,
    )
    return nodes, bridges, quanta


# ---- Tests ---------------------------------------------------------


def test_10k_quanta_position_KL_above_0p1_english_vs_whitenoise(
    substrate_english_seed_a, substrate_whitenoise_seed_a,
):
    """Test 5 — KL > 0.1 on position histograms.

    Threshold 0.1 locked pre-data per ``QUEUE.yaml::R-21`` row 5.
    """
    _, _, q_eng = substrate_english_seed_a
    _, _, q_wht = substrate_whitenoise_seed_a
    spec_eng = _position_histogram(q_eng)
    spec_wht = _position_histogram(q_wht)
    kl = _symmetric_kl(spec_eng, spec_wht)
    print(f"\n[R-21 test 5] position KL English vs white noise = {kl:.6f}")
    assert int(np.sum(q_eng.alive)) > 0, (
        "no alive quanta in English substrate at tick 10000"
    )
    assert int(np.sum(q_wht.alive)) > 0, (
        "no alive quanta in white-noise substrate at tick 10000"
    )
    assert kl > 0.1, (
        f"position-KL English-vs-white-noise = {kl:.6f} below locked "
        f"threshold 0.1; G25 position channel does not carry content "
        f"strongly enough"
    )


def test_10k_negative_control_same_audio_different_seed_position_KL_below_0p005(
    substrate_english_seed_a, substrate_english_seed_b,
):
    """Test 6 — same audio, different RNG seed: KL < 0.005.

    Threshold 0.005 locked pre-data per ``QUEUE.yaml::R-21`` row 6.
    """
    _, _, q_a = substrate_english_seed_a
    _, _, q_b = substrate_english_seed_b
    spec_a = _position_histogram(q_a)
    spec_b = _position_histogram(q_b)
    kl = _symmetric_kl(spec_a, spec_b)
    print(f"\n[R-21 test 6] position KL same-audio different-seed = {kl:.6f}")
    assert kl < 0.005, (
        f"position-KL same-audio different-seed = {kl:.6f} above locked "
        f"threshold 0.005; the apparent content-coupling in test 5 may "
        f"be a seed artefact, not actual content reactivity"
    )


def test_10k_bridge_count_differs_under_english_vs_whitenoise(
    substrate_english_seed_a, substrate_whitenoise_seed_a,
):
    """Test 7 — bridge-weight spectrum KL > 0.01.

    Threshold 0.01 locked pre-data per ``QUEUE.yaml::R-21`` row 7.
    """
    n_eng, b_eng, _ = substrate_english_seed_a
    n_wht, b_wht, _ = substrate_whitenoise_seed_a
    spec_eng = bridge_weight_spectrum(n_eng, b_eng)
    spec_wht = bridge_weight_spectrum(n_wht, b_wht)
    kl = 0.5 * (
        bridge_spectrum_kl(spec_eng, spec_wht)
        + bridge_spectrum_kl(spec_wht, spec_eng)
    )
    print(f"\n[R-21 test 7] bridge-spectrum KL English vs white noise = {kl:.6f}")
    assert int(b_eng.alive.sum()) > 0 and int(b_wht.alive.sum()) > 0, (
        f"no alive bridges at tick 10000: "
        f"english={int(b_eng.alive.sum())}, white={int(b_wht.alive.sum())}"
    )
    assert kl > 0.01, (
        f"bridge-spectrum KL English-vs-white-noise = {kl:.6f} below "
        f"locked threshold 0.01; position-channel content does not "
        f"reach the bridge layer"
    )

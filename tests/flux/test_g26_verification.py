"""R-22 verification — G26 density-by-amplitude at 10k ticks.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-22`` rows 5-7 and
``docs/amendments/G26-density-by-amplitude.md`` §3.

Three tests:

* Test 5 — alive-quanta count histogram KL > 0.05 between English-
  audio and matched-RMS white-noise substrates. Threshold 0.05 is
  locked pre-data, halved from R-20's 0.01-energy threshold because
  count is lower-bandwidth than energy (max 4 distinct values per
  sample) but should preserve a much larger fraction of variance
  through substrate mixing (count is conserved at injection).

* Test 6 — alive-quanta count histogram KL < 0.01 between same
  English audio fed to two substrates with different RNG seeds.
  Negative control discriminator: PASS = the test-5 variance is
  content-driven, not seed-driven.

* Test 7 — at tick 10000, EITHER total alive-bridge count differs by
  > 10% between EN and WN substrates, OR symmetric KL of bridge-
  weight spectra > 0.01. OR semantics — density may propagate to
  bridges via the count-channel or via the weight-channel.

All three substrate runs use ``EQMOD_USE_DENSITY_BY_AMPLITUDE=1``
via a session-scoped env-var fixture so they exercise the G26 path.

Locked-by-protocol; no retuning of 0.05 / 0.01 / 0.10-or-0.01
thresholds. NULL is a valid verdict.
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
# R-20 / R-21 lineage: SR, SPT, N_TICKS, TARGET_RMS, SUBSTRATE_SEEDs.
SR = 16_000
SPT = 16
N_TICKS = 10_000
N_SAMPLES = N_TICKS * SPT
TARGET_RMS = 0.25
SUBSTRATE_SEED_A = 4242
SUBSTRATE_SEED_B = 7777
WHITE_NOISE_SEED = 9999
GRID_DIMS: tuple[int, int, int] = (30, 15, 8)

# Per-voxel alive-quanta count histogram. 32 bins on [0, max_count_observed]
# (range computed pooled across the two compared substrates so both
# substrates share the same binning, per amendment §3 row 5).
COUNT_HIST_NBINS = 32


# ---- Module-scoped env var for G26 path ---------------------------


@pytest.fixture(scope="module", autouse=True)
def _enable_density_by_amplitude():
    """Force the density-by-amplitude path on for every test in this module."""
    key = "EQMOD_USE_DENSITY_BY_AMPLITUDE"
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
            "R-22 verification requires Stage-1 audio."
        )
    return eng


def _per_voxel_alive_counts(quanta, grid_dims) -> np.ndarray:
    """Return a 1-D integer array of alive-quanta count per voxel.

    Quanta are positioned in continuous (x, y, z); the floor cells use
    integer voxel indices. We bin by `(int(pos), ...)` clipped to the
    grid extent so quanta outside the box (after subvoxel jitter) still
    fall into a valid cell. The output array has length Lx*Ly*Lz.
    """
    Lx, Ly, Lz = grid_dims
    n_cells = int(Lx * Ly * Lz)
    alive = np.asarray(quanta.alive, dtype=bool)
    if not bool(alive.any()):
        return np.zeros(n_cells, dtype=np.int64)
    pos = np.asarray(quanta.pos[alive], dtype=np.float64)
    # Grid uses voxel_size=1.0 in our fixture, so floor() == int index.
    ix = np.clip(np.floor(pos[:, 0]).astype(np.int64), 0, Lx - 1)
    iy = np.clip(np.floor(pos[:, 1]).astype(np.int64), 0, Ly - 1)
    iz = np.clip(np.floor(pos[:, 2]).astype(np.int64), 0, Lz - 1)
    flat = ix * (Ly * Lz) + iy * Lz + iz
    counts = np.bincount(flat, minlength=n_cells)
    return counts.astype(np.int64)


def _count_histogram_pooled(
    counts_a: np.ndarray, counts_b: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Bin two count arrays into matching 32-bin histograms.

    Range [0, max_count_observed] where ``max_count_observed`` is the
    pooled max across both substrates (amendment §3 row 5 wording
    "[0, max_count_observed]" + "differ by symmetric KL" demands a
    shared support so the KL is well defined).
    """
    max_count = int(max(int(counts_a.max()), int(counts_b.max())))
    if max_count < 1:
        max_count = 1
    edges_top = float(max_count) + 1e-9  # ensure max cell falls in last bin
    hist_a, _ = np.histogram(
        counts_a, bins=COUNT_HIST_NBINS, range=(0.0, edges_top),
    )
    hist_b, _ = np.histogram(
        counts_b, bins=COUNT_HIST_NBINS, range=(0.0, edges_top),
    )
    total_a = float(hist_a.sum())
    total_b = float(hist_b.sum())
    pa = hist_a.astype(np.float64) / total_a if total_a > 0 else np.zeros_like(hist_a, dtype=np.float64)
    pb = hist_b.astype(np.float64) / total_b if total_b > 0 else np.zeros_like(hist_b, dtype=np.float64)
    return pa, pb, max_count


def _symmetric_kl(spec_a: np.ndarray, spec_b: np.ndarray) -> float:
    """Symmetric KL via bridge_spectrum_kl Laplace smoothing."""
    kl_ab = bridge_spectrum_kl(spec_a, spec_b)
    kl_ba = bridge_spectrum_kl(spec_b, spec_a)
    return 0.5 * (kl_ab + kl_ba)


# ---- Module-scoped substrate fixtures ------------------------------


@pytest.fixture(scope="module")
def substrate_english_seed_a():
    """English Stage-1 audio + SUBSTRATE_SEED_A; G26 path active."""
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
    """Matched-RMS white noise + SUBSTRATE_SEED_A; G26 path active."""
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
    """Same English Stage-1 audio + SUBSTRATE_SEED_B; G26 path active.

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


def test_10k_alive_quanta_count_differs_under_english_vs_whitenoise(
    substrate_english_seed_a, substrate_whitenoise_seed_a,
):
    """Test 5 — count histogram KL > 0.05 (English vs white noise)."""
    _, _, q_eng = substrate_english_seed_a
    _, _, q_wht = substrate_whitenoise_seed_a
    counts_eng = _per_voxel_alive_counts(q_eng, GRID_DIMS)
    counts_wht = _per_voxel_alive_counts(q_wht, GRID_DIMS)
    pa, pb, max_count = _count_histogram_pooled(counts_eng, counts_wht)
    kl = _symmetric_kl(pa, pb)
    n_alive_eng = int(q_eng.alive.sum())
    n_alive_wht = int(q_wht.alive.sum())
    mean_ratio = (n_alive_eng / max(n_alive_wht, 1))
    print(
        f"\n[R-22 test 5] count-hist KL English vs white noise = {kl:.6f}; "
        f"n_alive_eng={n_alive_eng} n_alive_wht={n_alive_wht} "
        f"mean_count_ratio(eng/wn)={mean_ratio:.4f} max_count_obs={max_count}"
    )
    assert n_alive_eng > 0 and n_alive_wht > 0, (
        f"no alive quanta at tick {N_TICKS}: "
        f"eng={n_alive_eng}, wn={n_alive_wht}"
    )
    assert kl > 0.05, (
        f"count-hist KL English vs white noise = {kl:.6f} below locked "
        f"threshold 0.05; G26 density channel does not survive substrate "
        f"mixing through to tick {N_TICKS}. n_alive_eng={n_alive_eng} "
        f"n_alive_wht={n_alive_wht} mean_count_ratio={mean_ratio:.4f}"
    )


def test_10k_alive_quanta_count_negative_control_same_audio_diff_seed(
    substrate_english_seed_a, substrate_english_seed_b,
):
    """Test 6 — count histogram KL < 0.01 (same English, different seeds)."""
    _, _, q_a = substrate_english_seed_a
    _, _, q_b = substrate_english_seed_b
    counts_a = _per_voxel_alive_counts(q_a, GRID_DIMS)
    counts_b = _per_voxel_alive_counts(q_b, GRID_DIMS)
    pa, pb, max_count = _count_histogram_pooled(counts_a, counts_b)
    kl = _symmetric_kl(pa, pb)
    n_alive_a = int(q_a.alive.sum())
    n_alive_b = int(q_b.alive.sum())
    print(
        f"\n[R-22 test 6] count-hist KL same-audio diff-seed = {kl:.6f}; "
        f"n_alive_a={n_alive_a} n_alive_b={n_alive_b} "
        f"max_count_obs={max_count}"
    )
    assert kl < 0.01, (
        f"count-hist KL same-audio diff-seed = {kl:.6f} above locked "
        f"threshold 0.01; test-5 variance may be a seed artefact rather "
        f"than content-driven. n_alive_a={n_alive_a} n_alive_b={n_alive_b}"
    )


def test_10k_bridge_count_differs_under_english_vs_whitenoise(
    substrate_english_seed_a, substrate_whitenoise_seed_a,
):
    """Test 7 — total bridge count differs > 10% OR bridge-spectrum KL > 0.01.

    OR semantics per amendment §3 row 7: density may propagate to
    bridges via the count-channel (alive-bridge count) or via the
    weight-channel (bridge-weight spectrum). Either passes the test.
    """
    n_eng, b_eng, _ = substrate_english_seed_a
    n_wht, b_wht, _ = substrate_whitenoise_seed_a
    n_bridges_eng = int(b_eng.alive.sum())
    n_bridges_wht = int(b_wht.alive.sum())
    # Count delta (relative).
    denom = max(n_bridges_eng, n_bridges_wht, 1)
    count_delta = abs(n_bridges_eng - n_bridges_wht) / denom
    # Bridge-weight spectrum KL.
    spec_eng = bridge_weight_spectrum(n_eng, b_eng)
    spec_wht = bridge_weight_spectrum(n_wht, b_wht)
    kl = 0.5 * (
        bridge_spectrum_kl(spec_eng, spec_wht)
        + bridge_spectrum_kl(spec_wht, spec_eng)
    )
    print(
        f"\n[R-22 test 7] bridge-count eng={n_bridges_eng} wht={n_bridges_wht} "
        f"delta={count_delta:.4f}; bridge-spectrum KL = {kl:.6f}"
    )
    # T1-friendly sanity: at least one substrate must have alive bridges,
    # otherwise the spectrum is degenerate and the test is uninformative.
    assert n_bridges_eng > 0 or n_bridges_wht > 0, (
        f"no alive bridges at tick {N_TICKS} in either substrate"
    )
    passes = (count_delta > 0.10) or (kl > 0.01)
    assert passes, (
        f"bridge response below locked thresholds: count-delta "
        f"{count_delta:.4f} <= 0.10 AND bridge-spectrum KL {kl:.6f} "
        f"<= 0.01. eng_bridges={n_bridges_eng} wht_bridges={n_bridges_wht}. "
        f"Density did not propagate to the bridge layer (either via count "
        f"or weight channel)."
    )

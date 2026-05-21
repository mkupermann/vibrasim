"""R-20 — G24 energy-variance diagnostic.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-20`` and motivated
by R-18 (autopilot/R-18 commit b8d6ffe, 2026-05-21T00:36Z) which
returned NULL on the G24 50k-tick verification: symmetric bridge-spectrum
KL = 0.000000 under ``EQMOD_USE_ENERGY_WEIGHTED_FLUX=1`` for English vs
white-noise. The architectural firewall R-13/R-16 identified survived
G24 at the bridge-spectrum readout.

R-20 walks back one step from the bridge-spectrum to ask: does
``quanta.energy`` itself vary across audio inputs at all? If it does
not, the firewall is at injection. If it does, but the per-bridge
``count_energy_flux_through`` array does not vary, the firewall is in
the bridge geometry (averaging variance away). The verdict-mapping in
the LOGBOOK directs the design of the next amendment (G25).

Tests are LOCKED; NULL is a valid verdict per autopilot charter. No
retuning of the 0.01 / 0.005 / 0.01 thresholds.

Tests:

* Test 1 (energy histogram, English vs white noise, KL > 0.01):
  PASS = ``quanta.energy`` varies with audio content at the substrate's
  internal energy field at tick 10_000.

* Test 2 (energy histogram, same English audio, different seeds, KL < 0.005):
  Negative control. PASS = the variance in test 1 comes from audio
  content, not from RNG dispersion of quanta positions/velocities.

* Test 3 (per-bridge energy-flux array, English vs white noise, KL > 0.01):
  PASS = the variance in ``quanta.energy`` survives the
  ``count_energy_flux_through`` bridge-readout step at tick 10_000.

Verdict mapping (encoded in the LOGBOOK postmortem):

* test1 PASS + test3 PASS → ``quanta.energy`` varies AND flux variance
  survives → G25 should focus on the plasticity-rule design (why does
  the variance not reach the bridge-weight spectrum?).
* test1 PASS + test3 FAIL → variance is averaged out by bridge geometry
  → G25 should rethink the bridge-readout step.
* test1 FAIL → ``quanta.energy`` does not vary across audio content
  → upstream injection is the firewall → G25 must redesign
  ``inject_raw_audio_sample``.

Negative control discipline: test 2 must always pass regardless of
tests 1 and 3; if it fails, the diagnostic itself is over-fitting to
seed, not measuring content-coupling.

All locked parameters mirror R-16 / R-18 lineage so the diagnostic
sits cleanly between the R-16 firewall confirmation (count-based,
KL=0) and the R-18 firewall reproduction (energy-weighted, KL=0).
"""
from __future__ import annotations

import numpy as np
import pytest

from agent.flux.bridge_spectrum import (
    bridge_spectrum_kl,
    load_english_stage1_segment,
    make_white_noise,
    run_short_encoder_free_substrate,
)
from world.flux.plasticity import count_energy_flux_through


# ---- Locked parameters (pre-data, no retune) -----------------------
# R-16 / R-18 lineage: SR, SPT, TARGET_RMS, SUBSTRATE_SEED, WHITE_NOISE_SEED.
# Diagnostic-specific: N_TICKS lowered from 50_000 → 10_000 per QUEUE acceptance
# text; SUBSTRATE_SEED_B chosen distinct from SUBSTRATE_SEED to drive the
# negative-control comparison.
SR = 16_000
SPT = 16
N_TICKS = 10_000
N_SAMPLES = N_TICKS * SPT
TARGET_RMS = 0.25
SUBSTRATE_SEED_A = 4242
SUBSTRATE_SEED_B = 7777
WHITE_NOISE_SEED = 9999

# Histogram binning — locked pre-data choices.
# Energy values are ``abs(sample)`` after RMS=0.25 normalisation:
# half-normal mean ≈ 0.2 for Gaussian white noise, sparse speech peaks
# up to ~1.0 occasionally. Range (0.0, 1.5) provides headroom; 32 bins
# is fine resolution at 10k-tick scope where ~10^5 alive quanta are
# expected. Same shape used for test 3 (per-bridge energy_flux array)
# with a wider range bracket since per-bridge values aggregate quanta.
ENERGY_HIST_NBINS = 32
ENERGY_HIST_RANGE: tuple[float, float] = (0.0, 1.5)
FLUX_HIST_NBINS = 32
FLUX_HIST_RANGE: tuple[float, float] = (0.0, 5.0)


def _english_or_skip() -> np.ndarray:
    eng = load_english_stage1_segment(N_SAMPLES, target_rms=TARGET_RMS)
    if eng is None:
        pytest.skip(
            "R-7 English corpus manifest not available on this machine; "
            "R-20 diagnostic requires Stage-1 audio for the energy-variance "
            "measurement."
        )
    return eng


def _normalised_histogram(
    values: np.ndarray,
    n_bins: int,
    value_range: tuple[float, float],
) -> np.ndarray:
    """Return a length-``n_bins`` probability histogram of ``values``.

    Empty input returns a zero array (never NaN); ``bridge_spectrum_kl``
    Laplace-smooths empty cells so the symmetric KL stays finite.
    """
    arr = np.asarray(values, dtype=np.float64).ravel()
    if arr.size == 0:
        return np.zeros(n_bins, dtype=np.float64)
    hist, _ = np.histogram(arr, bins=n_bins, range=value_range)
    total = float(hist.sum())
    if total <= 0.0:
        return np.zeros(n_bins, dtype=np.float64)
    return hist.astype(np.float64) / total


def _symmetric_kl(spec_a: np.ndarray, spec_b: np.ndarray) -> float:
    """Symmetric KL via ``bridge_spectrum_kl`` Laplace-smoothing."""
    kl_ab = bridge_spectrum_kl(spec_a, spec_b)
    kl_ba = bridge_spectrum_kl(spec_b, spec_a)
    return 0.5 * (kl_ab + kl_ba)


# ---- Module-scoped fixtures: each substrate run is ~60s; we share -
# the three substrate states across the three tests rather than re-
# running. The R-20 acceptance reads quanta.energy and bridges/nodes
# at the final tick; sharing fixtures does not affect that.


@pytest.fixture(scope="module")
def substrate_english_seed_a():
    """English Stage-1 audio + SUBSTRATE_SEED_A, energy-weighted path."""
    eng = _english_or_skip()
    nodes, bridges, quanta, plasticity_cfg = run_short_encoder_free_substrate(
        waveform=eng,
        n_ticks=N_TICKS,
        sample_rate_hz=SR,
        samples_per_tick=SPT,
        seed=SUBSTRATE_SEED_A,
        use_energy_weighted=True,
        return_full_state=True,
    )
    return nodes, bridges, quanta, plasticity_cfg


@pytest.fixture(scope="module")
def substrate_whitenoise_seed_a():
    """Matched-RMS white noise + SUBSTRATE_SEED_A, energy-weighted path."""
    wht = make_white_noise(N_SAMPLES, target_rms=TARGET_RMS, seed=WHITE_NOISE_SEED)
    nodes, bridges, quanta, plasticity_cfg = run_short_encoder_free_substrate(
        waveform=wht,
        n_ticks=N_TICKS,
        sample_rate_hz=SR,
        samples_per_tick=SPT,
        seed=SUBSTRATE_SEED_A,
        use_energy_weighted=True,
        return_full_state=True,
    )
    return nodes, bridges, quanta, plasticity_cfg


@pytest.fixture(scope="module")
def substrate_english_seed_b():
    """Same English Stage-1 audio + SUBSTRATE_SEED_B, energy-weighted path.

    Used only by test 2 (negative control): two substrates with same
    audio content but different RNG seeds must produce statistically
    indistinguishable energy histograms.
    """
    eng = _english_or_skip()
    nodes, bridges, quanta, plasticity_cfg = run_short_encoder_free_substrate(
        waveform=eng,
        n_ticks=N_TICKS,
        sample_rate_hz=SR,
        samples_per_tick=SPT,
        seed=SUBSTRATE_SEED_B,
        use_energy_weighted=True,
        return_full_state=True,
    )
    return nodes, bridges, quanta, plasticity_cfg


# ---- Test 1: quanta.energy histogram, English vs white noise -------


def test_quanta_energy_histogram_differs_under_english_vs_whitenoise(
    substrate_english_seed_a, substrate_whitenoise_seed_a,
):
    """KL > 0.01 between energy histograms at tick 10_000.

    Read ``quanta.energy[quanta.alive]`` from each substrate at the
    final tick, build a 1-D 32-bin histogram with range (0.0, 1.5),
    and compute symmetric KL. PASS = the substrate's internal energy
    field carries audio-content information; FAIL (NULL) = the
    architectural firewall is at injection itself, not at the bridge
    readout.
    """
    _, _, quanta_eng, _ = substrate_english_seed_a
    _, _, quanta_wht, _ = substrate_whitenoise_seed_a

    eng_energies = quanta_eng.energy[quanta_eng.alive]
    wht_energies = quanta_wht.energy[quanta_wht.alive]

    hist_eng = _normalised_histogram(
        eng_energies, ENERGY_HIST_NBINS, ENERGY_HIST_RANGE,
    )
    hist_wht = _normalised_histogram(
        wht_energies, ENERGY_HIST_NBINS, ENERGY_HIST_RANGE,
    )

    kl = _symmetric_kl(hist_eng, hist_wht)
    assert kl > 0.01, (
        f"Energy histograms English vs white noise: symmetric KL={kl:.6f} "
        f"(threshold 0.01). n_alive_eng={int(quanta_eng.alive.sum())} "
        f"n_alive_wht={int(quanta_wht.alive.sum())}. "
        "Diagnostic NULL: quanta.energy itself does not vary across audio "
        "content; the architectural firewall is at injection upstream, not "
        "at the bridge-readout step. G25 must redesign "
        "inject_raw_audio_sample (e.g., content-driven xy positioning)."
    )


# ---- Test 2: negative control (same audio, different seeds) --------


def test_quanta_energy_histogram_negative_control_same_audio_different_seed(
    substrate_english_seed_a, substrate_english_seed_b,
):
    """KL < 0.005 between two English-audio substrates with different seeds.

    Confirms the variance test 1 measures comes from audio content, not
    from substrate RNG dispersion. If this gate fails, the diagnostic
    is over-fitting to seed and test 1's PASS would be a state detector,
    not a content-coupling signal. Per CHARTER negative-control rule.
    """
    _, _, quanta_eng_a, _ = substrate_english_seed_a
    _, _, quanta_eng_b, _ = substrate_english_seed_b

    eng_a_energies = quanta_eng_a.energy[quanta_eng_a.alive]
    eng_b_energies = quanta_eng_b.energy[quanta_eng_b.alive]

    hist_eng_a = _normalised_histogram(
        eng_a_energies, ENERGY_HIST_NBINS, ENERGY_HIST_RANGE,
    )
    hist_eng_b = _normalised_histogram(
        eng_b_energies, ENERGY_HIST_NBINS, ENERGY_HIST_RANGE,
    )

    kl = _symmetric_kl(hist_eng_a, hist_eng_b)
    assert kl < 0.005, (
        f"Energy histograms English seed_a vs English seed_b: symmetric "
        f"KL={kl:.6f} (threshold < 0.005). "
        f"n_alive_a={int(quanta_eng_a.alive.sum())} "
        f"n_alive_b={int(quanta_eng_b.alive.sum())}. "
        "Diagnostic NULL: same audio content under different RNG seeds "
        "produces distinguishable energy histograms — variance comes from "
        "seed dispersion rather than content. The diagnostic is "
        "over-fitting and test 1's PASS, if any, is a state detector."
    )


# ---- Test 3: per-bridge energy flux array, English vs white noise --


def test_bridge_energy_flux_array_differs_under_english_vs_whitenoise(
    substrate_english_seed_a, substrate_whitenoise_seed_a,
):
    """KL > 0.01 between per-bridge energy_flux arrays at tick 10_000.

    For each substrate, compute ``count_energy_flux_through`` on its
    final-tick state. Histogram the alive-bridge slots of the resulting
    flux array (shape ``(max_bridges,)``) into a 32-bin distribution
    with range (0.0, 5.0) and compute symmetric KL. PASS = the
    audio-content variance in ``quanta.energy`` survives the bridge
    geometric readout; FAIL (NULL) = bridge geometry averages variance
    away.
    """
    _, bridges_eng, quanta_eng, cfg = substrate_english_seed_a
    nodes_eng = substrate_english_seed_a[0]
    _, bridges_wht, quanta_wht, cfg_wht = substrate_whitenoise_seed_a
    nodes_wht = substrate_whitenoise_seed_a[0]

    flux_eng = count_energy_flux_through(bridges_eng, nodes_eng, quanta_eng, cfg)
    flux_wht = count_energy_flux_through(
        bridges_wht, nodes_wht, quanta_wht, cfg_wht,
    )

    # Restrict to alive bridges in each substrate; comparing the full
    # max_bridges arrays would dump the bulk of the mass into bin-0
    # for slot=dead entries and crush the diagnostic.
    flux_eng_alive = flux_eng[bridges_eng.alive]
    flux_wht_alive = flux_wht[bridges_wht.alive]

    hist_eng = _normalised_histogram(
        flux_eng_alive, FLUX_HIST_NBINS, FLUX_HIST_RANGE,
    )
    hist_wht = _normalised_histogram(
        flux_wht_alive, FLUX_HIST_NBINS, FLUX_HIST_RANGE,
    )

    kl = _symmetric_kl(hist_eng, hist_wht)
    assert kl > 0.01, (
        f"Per-bridge energy_flux arrays English vs white noise: symmetric "
        f"KL={kl:.6f} (threshold 0.01). "
        f"n_alive_bridges_eng={int(bridges_eng.alive.sum())} "
        f"n_alive_bridges_wht={int(bridges_wht.alive.sum())}. "
        "Diagnostic NULL: the per-bridge energy flux readout averages "
        "audio-content variance away — bridge geometry is the firewall. "
        "G25 should rethink the bridge tube/segment readout step."
    )

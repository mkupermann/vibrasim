"""R-18 — G24 energy-weighted-flux 50k-tick verification.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-18`` and
``docs/amendments/G24-energy-weighted-flux.md`` §4. Tests are LOCKED;
NULL is a valid verdict per autopilot charter — no retuning of the
0.01 / 0.1 / 0.005 / 1e-6 thresholds.

The four gates measure whether G24 breaks the architectural firewall
quantitatively confirmed at KL=0.000000 by R-16 (commit de62772):

* Gate 1 (English vs white noise, KL > 0.01):
  R-16's failed gate, now under ``EQMOD_USE_ENERGY_WEIGHTED_FLUX=1``.
  PASS = G24 produces content-coupling at 50k-tick scope.

* Gate 2 (English vs silence, KL > 0.1):
  R-16's second failed gate, energy-weighted path. PASS = the substrate
  also distinguishes the trivial limit (silent input).

* Gate 3 (white_noise vs white_noise with independent seeds, KL < 0.005):
  Negative control. Two same-distribution inputs must NOT produce
  distinguishable bridge spectra. PASS = G24 is not over-fitting to seed.

* Gate 4 (legacy count-based path, KL < 1e-6):
  Reproduces R-16 under the unchanged legacy path. PASS = R-17 did not
  regress the count-based path; the firewall is still total without
  the G24 opt-in env-var route.

All four gates run 50k ticks per substrate using the same encoder-free
runner. ``run_short_encoder_free_substrate(use_energy_weighted=True)``
swaps the per-tick plasticity step to G24's pair
(``count_energy_flux_through`` + ``apply_plasticity_energy_weighted``)
while keeping every other config and the audio injector unchanged, so
gates 1-3 isolate exactly the plasticity-readout change.
"""
from __future__ import annotations

import numpy as np
import pytest

from agent.flux.bridge_spectrum import (
    bridge_spectrum_kl,
    bridge_weight_spectrum,
    load_english_stage1_segment,
    make_white_noise,
    run_short_encoder_free_substrate,
)


# ---- Locked parameters (identical to R-16 / R-13 lineage) ----------
SR = 16_000
SPT = 16
N_TICKS = 50_000
N_SAMPLES = N_TICKS * SPT
TARGET_RMS = 0.25
SUBSTRATE_SEED = 4242
WHITE_NOISE_SEED = 9999
# Gate-3 negative-control seeds: independent of gate-1 substrate seed
# AND of the gate-1 white-noise seed. Both substrate and waveform RNG
# differ between the two gate-3 runs.
NEG_CTRL_SUBSTRATE_SEED_A = SUBSTRATE_SEED        # 4242 (reuse gate-1 run)
NEG_CTRL_NOISE_SEED_A = WHITE_NOISE_SEED          # 9999 (reuse gate-1 run)
NEG_CTRL_SUBSTRATE_SEED_B = 7777
NEG_CTRL_NOISE_SEED_B = 11111


def _english_or_skip() -> np.ndarray:
    eng = load_english_stage1_segment(N_SAMPLES, target_rms=TARGET_RMS)
    if eng is None:
        pytest.skip(
            "R-7 English corpus manifest not available on this machine"
        )
    return eng


def _symmetric_kl(spec_a: np.ndarray, spec_b: np.ndarray) -> tuple[float, float, float]:
    kl_ab = bridge_spectrum_kl(spec_a, spec_b)
    kl_ba = bridge_spectrum_kl(spec_b, spec_a)
    return kl_ab, kl_ba, 0.5 * (kl_ab + kl_ba)


# ---- Module-scope substrate fixtures (each ~4-5 min, cached) -------


@pytest.fixture(scope="module")
def english_substrate_weighted():
    """English-50k under the G24 energy-weighted path. Reused by gates 1+2."""
    english = _english_or_skip()
    return run_short_encoder_free_substrate(
        waveform=english, n_ticks=N_TICKS, seed=SUBSTRATE_SEED,
        use_energy_weighted=True,
    )


@pytest.fixture(scope="module")
def white_substrate_weighted_a():
    """White-noise-50k, seed-A. Used by gates 1 and 3."""
    white = make_white_noise(
        N_SAMPLES, target_rms=TARGET_RMS, seed=NEG_CTRL_NOISE_SEED_A,
    )
    return run_short_encoder_free_substrate(
        waveform=white, n_ticks=N_TICKS, seed=NEG_CTRL_SUBSTRATE_SEED_A,
        use_energy_weighted=True,
    )


# ---- Gate 1 — English vs white noise, weighted path, KL > 0.01 -----


@pytest.mark.slow
def test_50k_english_vs_white_noise_KL_above_0p01_under_weighted_path(
    english_substrate_weighted, white_substrate_weighted_a,
):
    """50k English vs matched-RMS white noise, both energy-weighted: KL > 0.01.

    R-16's threshold (0.01) is preserved. R-16 measured 0.000000 here on the
    count-based path. If G24 breaks the firewall this gate passes; otherwise
    it NULLs and gate 4 must reproduce R-16's KL≈0.0 to confirm we did not
    regress the legacy path.
    """
    nodes_eng, bridges_eng = english_substrate_weighted
    nodes_wht, bridges_wht = white_substrate_weighted_a

    # RMS sanity check on the inputs themselves (fixtures consumed them).
    english_raw = _english_or_skip()
    white_raw = make_white_noise(
        N_SAMPLES, target_rms=TARGET_RMS, seed=NEG_CTRL_NOISE_SEED_A,
    )
    eng_rms = float(np.sqrt(np.mean(english_raw * english_raw)))
    white_rms = float(np.sqrt(np.mean(white_raw * white_raw)))
    assert abs(eng_rms - white_rms) / max(eng_rms, 1e-12) < 0.01, (
        f"RMS mismatch English ({eng_rms:.4f}) vs white ({white_rms:.4f}); "
        f"matched-RMS is the whole point of this comparison"
    )

    n_eng = int(bridges_eng.alive.sum())
    n_wht = int(bridges_wht.alive.sum())
    assert n_eng > 0, "English-trained substrate produced no alive bridges"
    assert n_wht > 0, "White-noise-trained substrate produced no alive bridges"

    spec_eng = bridge_weight_spectrum(nodes_eng, bridges_eng)
    spec_wht = bridge_weight_spectrum(nodes_wht, bridges_wht)
    kl_ab, kl_ba, kl_sym = _symmetric_kl(spec_eng, spec_wht)

    print(
        f"R-18 gate1 english_vs_whitenoise weighted: "
        f"KL(eng||wht)={kl_ab:.6f}  KL(wht||eng)={kl_ba:.6f}  "
        f"sym={kl_sym:.6f}  "
        f"bridges_eng={n_eng}  bridges_wht={n_wht}  "
        f"seeds(substrate={SUBSTRATE_SEED}, white={NEG_CTRL_NOISE_SEED_A})"
    )

    assert kl_sym > 0.01, (
        f"G24 does NOT break the firewall: bridge spectra under the "
        f"energy-weighted path do not distinguish English audio from "
        f"matched-RMS white noise at 50k-tick scope. "
        f"symmetric KL={kl_sym:.6f} (threshold 0.01). "
        f"KL(eng||wht)={kl_ab:.6f} KL(wht||eng)={kl_ba:.6f}. "
        f"bridges_eng={n_eng} bridges_wht={n_wht}. "
        f"Verdict: NULL per autopilot charter — no retuning. "
        f"G24 amendment design needs revision; queue G25 with the lesson."
    )


# ---- Gate 2 — English vs silence, weighted path, KL > 0.1 ---------


@pytest.mark.slow
def test_50k_english_vs_silence_KL_above_0p1_under_weighted_path(
    english_substrate_weighted,
):
    """50k English vs silence, both energy-weighted: KL > 0.1.

    Silence is the maximally different input from any signal. Threshold
    identical to R-16's failed silence gate. Under the energy-weighted
    path silence produces near-zero energy_flux on every tick; bridges
    therefore decay (apply_plasticity_energy_weighted uses flux_min=1.0
    in energy-per-tick units), and the resulting bridge-weight spectrum
    differs from the English-trained one. The Laplace-smoothed KL keeps
    the divergence finite even if the silence substrate has zero alive
    bridges at the end of the run.
    """
    nodes_eng, bridges_eng = english_substrate_weighted

    silence = np.zeros(N_SAMPLES, dtype=np.float64)
    nodes_sil, bridges_sil = run_short_encoder_free_substrate(
        waveform=silence, n_ticks=N_TICKS, seed=SUBSTRATE_SEED,
        use_energy_weighted=True,
    )

    n_eng = int(bridges_eng.alive.sum())
    n_sil = int(bridges_sil.alive.sum())
    assert n_eng > 0, "English-trained substrate produced no alive bridges"

    spec_eng = bridge_weight_spectrum(nodes_eng, bridges_eng)
    spec_sil = bridge_weight_spectrum(nodes_sil, bridges_sil)
    kl_ab, kl_ba, kl_sym = _symmetric_kl(spec_eng, spec_sil)

    print(
        f"R-18 gate2 english_vs_silence weighted: "
        f"KL(eng||sil)={kl_ab:.6f}  KL(sil||eng)={kl_ba:.6f}  "
        f"sym={kl_sym:.6f}  "
        f"bridges_eng={n_eng}  bridges_sil={n_sil}  "
        f"seed(substrate={SUBSTRATE_SEED})"
    )

    assert kl_sym > 0.1, (
        f"G24 does NOT distinguish English from silence at 50k scope: "
        f"symmetric KL={kl_sym:.6f} (threshold 0.1). "
        f"KL(eng||sil)={kl_ab:.6f} KL(sil||eng)={kl_ba:.6f}. "
        f"bridges_eng={n_eng} bridges_sil={n_sil}. "
        f"Verdict: NULL per autopilot charter — no retuning."
    )


# ---- Gate 3 — independent white-noise seeds, KL < 0.005 -----------


@pytest.mark.slow
def test_50k_white_noise_vs_white_noise_independent_seeds_KL_below_0p005_under_weighted_path(
    white_substrate_weighted_a,
):
    """50k white-vs-white with independent substrate+noise seeds: KL < 0.005.

    Negative control. Two same-distribution inputs (Gaussian, target_rms
    matched) under independent RNG seeds for BOTH the substrate state and
    the waveform must NOT produce distinguishable bridge spectra. If this
    gate fails the substrate is over-fitting to seed rather than coupling
    to content, and the gate-1/gate-2 PASS would be a state detector
    (NULL per charter §"PASS without negative control is NULL").

    Seeds: run A = (substrate={NEG_CTRL_SUBSTRATE_SEED_A},
    noise={NEG_CTRL_NOISE_SEED_A}), reused from gate 1.
            run B = (substrate={NEG_CTRL_SUBSTRATE_SEED_B},
    noise={NEG_CTRL_NOISE_SEED_B}), independent of A on both axes.
    """
    nodes_a, bridges_a = white_substrate_weighted_a

    white_b = make_white_noise(
        N_SAMPLES, target_rms=TARGET_RMS, seed=NEG_CTRL_NOISE_SEED_B,
    )
    nodes_b, bridges_b = run_short_encoder_free_substrate(
        waveform=white_b, n_ticks=N_TICKS, seed=NEG_CTRL_SUBSTRATE_SEED_B,
        use_energy_weighted=True,
    )

    n_a = int(bridges_a.alive.sum())
    n_b = int(bridges_b.alive.sum())
    assert n_a > 0, "Run-A white-noise substrate produced no alive bridges"
    assert n_b > 0, "Run-B white-noise substrate produced no alive bridges"

    spec_a = bridge_weight_spectrum(nodes_a, bridges_a)
    spec_b = bridge_weight_spectrum(nodes_b, bridges_b)
    kl_ab, kl_ba, kl_sym = _symmetric_kl(spec_a, spec_b)

    print(
        f"R-18 gate3 whitenoise_vs_whitenoise weighted: "
        f"KL(a||b)={kl_ab:.6f}  KL(b||a)={kl_ba:.6f}  "
        f"sym={kl_sym:.6f}  "
        f"bridges_a={n_a}  bridges_b={n_b}  "
        f"seeds(A: substrate={NEG_CTRL_SUBSTRATE_SEED_A} "
        f"noise={NEG_CTRL_NOISE_SEED_A}; B: substrate="
        f"{NEG_CTRL_SUBSTRATE_SEED_B} noise={NEG_CTRL_NOISE_SEED_B})"
    )

    assert kl_sym < 0.005, (
        f"Negative control failed: two same-distribution white-noise "
        f"inputs produce distinguishable bridge spectra under the "
        f"energy-weighted path. symmetric KL={kl_sym:.6f} "
        f"(threshold 0.005). KL(a||b)={kl_ab:.6f} KL(b||a)={kl_ba:.6f}. "
        f"bridges_a={n_a} bridges_b={n_b}. "
        f"G24 may be over-fitting to RNG seed rather than coupling to "
        f"content; gate-1/gate-2 PASS would be NULL per charter."
    )


# ---- Gate 4 — legacy count-based path reproduces R-16 KL≈0 ---------


@pytest.mark.slow
def test_legacy_count_based_path_still_returns_KL_zero():
    """50k English-vs-white-noise under the legacy count-based path: KL < 1e-6.

    Amendment §5 control: reproduces R-16 (commit de62772, KL=0.000000) to
    confirm R-17's additions to ``world/flux/plasticity.py`` did not
    regress the count-based pathway. If THIS gate fails the legacy path
    has drifted and the gate-1/gate-2 PASS is not interpretable; G24's
    architectural claim depends on the count-based baseline being unmoved.

    This test does NOT share fixtures with the weighted gates; it runs
    its own 50k pair under ``use_energy_weighted=False`` (the default,
    legacy behaviour preserved byte-identically per R-17b).
    """
    english = _english_or_skip()
    white = make_white_noise(N_SAMPLES, target_rms=TARGET_RMS, seed=WHITE_NOISE_SEED)

    nodes_eng, bridges_eng = run_short_encoder_free_substrate(
        waveform=english, n_ticks=N_TICKS, seed=SUBSTRATE_SEED,
        use_energy_weighted=False,
    )
    nodes_wht, bridges_wht = run_short_encoder_free_substrate(
        waveform=white, n_ticks=N_TICKS, seed=SUBSTRATE_SEED,
        use_energy_weighted=False,
    )

    n_eng = int(bridges_eng.alive.sum())
    n_wht = int(bridges_wht.alive.sum())
    assert n_eng > 0, "English-trained substrate produced no alive bridges"
    assert n_wht > 0, "White-noise-trained substrate produced no alive bridges"

    spec_eng = bridge_weight_spectrum(nodes_eng, bridges_eng)
    spec_wht = bridge_weight_spectrum(nodes_wht, bridges_wht)
    kl_ab, kl_ba, kl_sym = _symmetric_kl(spec_eng, spec_wht)

    print(
        f"R-18 gate4 legacy_count_based english_vs_whitenoise: "
        f"KL(eng||wht)={kl_ab:.6f}  KL(wht||eng)={kl_ba:.6f}  "
        f"sym={kl_sym:.6f}  "
        f"bridges_eng={n_eng}  bridges_wht={n_wht}  "
        f"seeds(substrate={SUBSTRATE_SEED}, white={WHITE_NOISE_SEED})"
    )

    assert kl_sym < 1e-6, (
        f"Legacy count-based path regressed: KL between English and "
        f"matched-RMS white noise is no longer ~0.0. "
        f"symmetric KL={kl_sym:.6f} (threshold 1e-6, R-16 had 0.000000). "
        f"R-17's plasticity.py additions may have leaked into the count "
        f"path; G24's architectural claim cannot be evaluated without an "
        f"unchanged legacy baseline."
    )

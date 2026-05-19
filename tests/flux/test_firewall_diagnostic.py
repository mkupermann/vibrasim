"""R-16 architectural-firewall diagnostic — 50k smoke for content-coupling.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-16``:

  ``test_50k_matched_rms_english_vs_white_noise_bridge_spectrum_KL_above_0p01``
  ``test_50k_matched_rms_english_vs_silence_bridge_spectrum_KL_above_0p1``

R-13's forensic finding (commit eca9545) was: under the current F1b/F1c
plasticity + binding rules, audio amplitude entering through
``inject_raw_audio_chunk`` is firewalled in ``nodes.energy`` and never
reaches the density/binding/flux pathway that determines bridge weights.
The R-13 50k KL(English||white-noise) was below the 0.1 threshold.

R-16 sets a much weaker threshold (0.01 instead of 0.1) and adds a
silence-vs-English control. The two outcomes carry distinct meanings:

* KL(English, white-noise) > 0.01 PASS, KL(English, silence) > 0.1 PASS:
  the firewall is partial — there IS content coupling at 50k scope, just
  not at R-13's stronger threshold. The encoder-free architecture is
  alive but quiet; R-LR-8 long-run scope may still get over R-LR-8's
  pre-registered 0.5 nats gate.

* KL(English, white-noise) < 0.01 AND KL(English, silence) > 0.1: the
  substrate couples to gross RMS / energy presence but not to spectral
  content. The firewall lets through the loudness envelope, blocks the
  audio structure. The G24 amendment would target the F1b plasticity
  rule.

* BOTH KLs < their thresholds (silence test fails too): the firewall is
  total — bridge weights are independent of the input waveform entirely
  (only the encoder-free injector seed matters). The G24 amendment would
  target the audio_raw injection path itself, not F1b.

Thresholds are LOCKED. NULL is a valid verdict per autopilot charter.
The session writes the measured KLs into LOGBOOK regardless of pass/fail
so the architectural conclusion is on the record.
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


# Locked parameters, identical to R-13's gate (which R-15 salvaged to main).
# Same SR / SPT / N_TICKS / TARGET_RMS so this is the same 50k-tick run, just
# with a different threshold and an added silence control.
SR = 16_000
SPT = 16
N_TICKS = 50_000
N_SAMPLES = N_TICKS * SPT
TARGET_RMS = 0.25
SUBSTRATE_SEED = 4242
WHITE_NOISE_SEED = 9999


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


@pytest.fixture(scope="module")
def english_substrate():
    """Cached English-trained substrate, reused across both gates.

    Two pre-registered tests in this file each compare against the English
    50k substrate. Re-running it twice would double wallclock with no
    research benefit (both reads are read-only). Module scope means: the
    cost-pay-once happens at the first test that needs it; the second test
    reuses the same (nodes, bridges) objects unchanged.
    """
    english = _english_or_skip()
    return run_short_encoder_free_substrate(
        waveform=english, n_ticks=N_TICKS, seed=SUBSTRATE_SEED,
    )


@pytest.mark.slow
def test_50k_matched_rms_english_vs_white_noise_bridge_spectrum_KL_above_0p01(english_substrate):
    """50k-tick English vs matched-RMS white noise: symmetric KL > 0.01.

    Threshold 0.01 is the pre-registered floor — the smallest non-trivial
    KL value above the floating-point noise floor at this scope. Failure
    here together with PASS on the silence test below means the firewall
    selectively blocks audio structure while letting through gross energy
    presence (motivates a G24 amendment to F1b plasticity).
    """
    nodes_eng, bridges_eng = english_substrate
    white = make_white_noise(N_SAMPLES, target_rms=TARGET_RMS, seed=WHITE_NOISE_SEED)

    # Sanity-check RMS match between the English input (already inside the
    # fixture) and white-noise — both must be ~TARGET_RMS for a fair test.
    english_raw = _english_or_skip()
    eng_rms = float(np.sqrt(np.mean(english_raw * english_raw)))
    white_rms = float(np.sqrt(np.mean(white * white)))
    assert abs(eng_rms - white_rms) / max(eng_rms, 1e-12) < 0.01, (
        f"RMS mismatch English ({eng_rms:.4f}) vs white ({white_rms:.4f}); "
        f"matched-RMS is the whole point of this comparison"
    )

    nodes_wht, bridges_wht = run_short_encoder_free_substrate(
        waveform=white, n_ticks=N_TICKS, seed=SUBSTRATE_SEED,
    )

    n_eng = int(bridges_eng.alive.sum())
    n_wht = int(bridges_wht.alive.sum())
    assert n_eng > 0, "English-trained substrate produced no alive bridges"
    assert n_wht > 0, "White-noise-trained substrate produced no alive bridges"

    spec_eng = bridge_weight_spectrum(nodes_eng, bridges_eng)
    spec_wht = bridge_weight_spectrum(nodes_wht, bridges_wht)
    kl_ab, kl_ba, kl_sym = _symmetric_kl(spec_eng, spec_wht)

    print(
        f"R-16 english_vs_whitenoise: KL(eng||wht)={kl_ab:.6f}  "
        f"KL(wht||eng)={kl_ba:.6f}  sym={kl_sym:.6f}  "
        f"bridges_eng={n_eng}  bridges_wht={n_wht}"
    )

    assert kl_sym > 0.01, (
        f"Architectural firewall: bridge spectra do not distinguish English "
        f"audio from matched-RMS white noise at 50k-tick scope. "
        f"symmetric KL={kl_sym:.6f} (threshold 0.01). "
        f"KL(eng||wht)={kl_ab:.6f} KL(wht||eng)={kl_ba:.6f}. "
        f"bridges_eng={n_eng} bridges_wht={n_wht}. "
        f"Verdict: NULL per autopilot charter — no retuning. "
        f"This confirms R-13's eca9545 forensic finding."
    )


@pytest.mark.slow
def test_50k_matched_rms_english_vs_silence_bridge_spectrum_KL_above_0p1(english_substrate):
    """50k-tick English vs silence: symmetric KL > 0.1.

    The control: silence is the maximally different input from any signal.
    If THIS test nulls too, the firewall is total — bridge weights are
    independent of the input waveform entirely and only depend on injector
    + substrate RNG state. If it passes while the white-noise test fails,
    the substrate couples to gross energy presence but not to spectral
    structure.
    """
    nodes_eng, bridges_eng = english_substrate
    silence = np.zeros(N_SAMPLES, dtype=np.float64)

    nodes_sil, bridges_sil = run_short_encoder_free_substrate(
        waveform=silence, n_ticks=N_TICKS, seed=SUBSTRATE_SEED,
    )

    n_eng = int(bridges_eng.alive.sum())
    n_sil = int(bridges_sil.alive.sum())
    assert n_eng > 0, "English-trained substrate produced no alive bridges"

    spec_eng = bridge_weight_spectrum(nodes_eng, bridges_eng)
    spec_sil = bridge_weight_spectrum(nodes_sil, bridges_sil)
    kl_ab, kl_ba, kl_sym = _symmetric_kl(spec_eng, spec_sil)

    print(
        f"R-16 english_vs_silence: KL(eng||sil)={kl_ab:.6f}  "
        f"KL(sil||eng)={kl_ba:.6f}  sym={kl_sym:.6f}  "
        f"bridges_eng={n_eng}  bridges_sil={n_sil}"
    )

    assert kl_sym > 0.1, (
        f"Total architectural firewall: bridge spectra do not distinguish "
        f"English audio from silence at 50k-tick scope. "
        f"symmetric KL={kl_sym:.6f} (threshold 0.1). "
        f"KL(eng||sil)={kl_ab:.6f} KL(sil||eng)={kl_ba:.6f}. "
        f"bridges_eng={n_eng} bridges_sil={n_sil}. "
        f"Verdict: NULL per autopilot charter — no retuning. "
        f"If white-noise test also failed, the firewall is total and G24 "
        f"must target the audio_raw injection path, not F1b plasticity."
    )

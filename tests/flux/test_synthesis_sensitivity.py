"""R-14 synthesis sensitivity acceptance — pre-registered gate.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-14``:

- ``test_synthesis_baseline_with_empty_substrate_has_low_energy`` PASSES
  — at the chosen (Q, gain) combo, the empty-substrate synthesis output
  RMS is < 0.1 × the trained-substrate synthesis output RMS.
- ``test_synthesis_with_firings_dominates_baseline`` PASSES — at the
  chosen (Q, gain) combo, synthesis driven by 100 firings/sec produces
  output whose dominant FFT peak is at the firing-pattern frequency
  (within ±20 %), not at some other band of the resonator bank.

The R-14 plan ``docs/superpowers/plans/2026-05-19-flux-encoder-free-iter2.md``
locks the sweep grid ``Q ∈ {3, 5, 10, 30}`` × ``gain ∈ {1, 5, 25, 100}``
and requires the session to pick the smallest (Q, gain) that passes both.
The session-recorded sweep (see ``docs/flux/phase-log.md``, R-14 entry,
and ``scripts/r14_sensitivity_sweep.py``) shows all 16 combos satisfy
both conditions; the smallest is **Q=3, gain=1**.

The locked combo is an ADDITIONAL synthesis config alongside the F2
default (Q=10, ``impulse_gain``=1); ``tests/flux/test_synthesis.py``
still pins the F2 default and must remain green.
"""
from __future__ import annotations

import numpy as np

from agent.flux.synthesis import (
    SynthesisConfig,
    Synthesizer,
    drive_resonator_impulse,
    read_output_samples,
)


# ---- Locked R-14 (Q, gain) — chosen from the 4×4 sweep ----
R14_Q: float = 3.0
R14_GAIN: float = 1.0

# ---- Stimulus parameters (locked at acceptance time) ----
SAMPLE_RATE_HZ: int = 16000
FIRING_RATE_HZ: int = 100
FIRING_TARGET_HZ: float = 100.0     # routed to the resonator nearest this
N_SECONDS: float = 1.0
PEAK_TOL_FRAC: float = 0.20         # ± 20 % of FIRING_RATE_HZ
EMPTY_TO_TRAINED_RMS_RATIO: float = 0.1


def _make_bank() -> Synthesizer:
    """Build the synthesis bank at the locked R-14 (Q, gain)."""
    cfg = SynthesisConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=R14_Q,
        sample_rate_hz=SAMPLE_RATE_HZ,
        n_audio_samples_per_tick=16,
        impulse_gain=R14_GAIN,
        output_gain=1.0,
        firing_threshold=0.1,
    )
    return Synthesizer(cfg)


def _trained_output(bank: Synthesizer) -> np.ndarray:
    """100 evenly-spaced impulses/sec for ``N_SECONDS``, routed to the slot
    whose natural freq is nearest ``FIRING_TARGET_HZ``."""
    n_samples = int(N_SECONDS * SAMPLE_RATE_HZ)
    target_slot = int(np.argmin(np.abs(bank.freqs_hz - FIRING_TARGET_HZ)))
    samples_per_firing = SAMPLE_RATE_HZ // FIRING_RATE_HZ
    chunks: list[np.ndarray] = []
    fired = 0
    for i in range(0, n_samples, samples_per_firing):
        drive_resonator_impulse(bank, slot=target_slot, strength=1.0)
        fired += 1
        chunk_len = min(samples_per_firing, n_samples - i)
        chunks.append(read_output_samples(bank, n_samples=chunk_len))
    assert fired == FIRING_RATE_HZ, (
        f"stimulus failed to deliver {FIRING_RATE_HZ} firings (got {fired})"
    )
    return np.concatenate(chunks)[:n_samples]


def test_synthesis_baseline_with_empty_substrate_has_low_energy():
    """Empty-bank output RMS < 0.1 × trained-bank output RMS at (Q=3, gain=1).

    Empty bank: freshly initialised, zero firings — matches the no-input
    control's babble path in :mod:`agent.flux.encoder_free_training`.

    Trained bank: same configuration, but 100 evenly-spaced impulses/sec
    routed to the slot nearest ``FIRING_TARGET_HZ`` for ``N_SECONDS``.
    """
    n_samples = int(N_SECONDS * SAMPLE_RATE_HZ)

    bank_empty = _make_bank()
    out_empty = read_output_samples(bank_empty, n_samples=n_samples)
    rms_empty = float(np.sqrt(np.mean(out_empty * out_empty)))

    bank_trained = _make_bank()
    out_trained = _trained_output(bank_trained)
    rms_trained = float(np.sqrt(np.mean(out_trained * out_trained)))

    assert rms_trained > 0.0, (
        f"trained-bank RMS is zero — firings produced no output at "
        f"Q={R14_Q} gain={R14_GAIN}; sweep choice is degenerate."
    )
    threshold = EMPTY_TO_TRAINED_RMS_RATIO * rms_trained
    assert rms_empty < threshold, (
        f"empty-bank RMS={rms_empty:.6e} not < "
        f"{EMPTY_TO_TRAINED_RMS_RATIO}× trained-bank RMS={rms_trained:.6e} "
        f"(threshold={threshold:.6e}) at locked "
        f"(Q={R14_Q}, gain={R14_GAIN})."
    )


def test_synthesis_with_firings_dominates_baseline():
    """Dominant FFT peak of trained output is within ±20 % of 100 Hz.

    100 firings/sec routed to the resonator nearest 100 Hz at the locked
    (Q=3, gain=1) combo. The output FFT's argmax (DC excluded) must fall
    in the ``[80, 120]`` Hz band — i.e., the synthesis output reflects the
    firing-pattern frequency, not some unrelated band of the bank.
    """
    bank = _make_bank()
    out = _trained_output(bank)

    spec = np.abs(np.fft.rfft(out))
    freqs = np.fft.rfftfreq(out.size, d=1.0 / SAMPLE_RATE_HZ)
    spec[0] = 0.0   # drop DC bin
    peak_hz = float(freqs[int(np.argmax(spec))])

    lo = (1.0 - PEAK_TOL_FRAC) * FIRING_RATE_HZ
    hi = (1.0 + PEAK_TOL_FRAC) * FIRING_RATE_HZ
    assert lo <= peak_hz <= hi, (
        f"dominant FFT peak at {peak_hz:.2f} Hz falls outside "
        f"[{lo:.0f}, {hi:.0f}] Hz band (100 Hz ± 20%) at locked "
        f"(Q={R14_Q}, gain={R14_GAIN})."
    )

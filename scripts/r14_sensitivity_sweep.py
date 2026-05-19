"""R-14 synthesis sensitivity sweep — characterise (Q, gain) grid.

Sweeps Q in {3, 5, 10, 30} and gain in {1, 5, 25, 100} (16 combos) and
records:

  - empty_rms     : output RMS of a freshly-initialised bank that
                    receives 0 firings over 1 s of audio.
  - trained_rms   : output RMS of a bank that receives 100 evenly
                    spaced impulses/sec at a single mid-band slot.
  - peak_hz       : dominant FFT peak of the trained-bank output,
                    measured below resonator natural freq.
  - test1_pass    : empty_rms < 0.1 * trained_rms
  - test2_pass    : 80.0 <= peak_hz <= 120.0  (100 Hz ± 20 %)

The smallest (Q, gain) that satisfies both becomes the locked combo
for R-14. Documented in docs/flux/phase-log.md, then the
test_synthesis_sensitivity.py acceptance tests run against that combo.

Run:  python -m scripts.r14_sensitivity_sweep
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from agent.flux.synthesis import (
    SynthesisConfig,
    Synthesizer,
    drive_resonator_impulse,
    read_output_samples,
)


SAMPLE_RATE_HZ = 16000
FIRING_RATE_HZ = 100
N_SECONDS = 1.0
# Slot whose natural freq is nearest the firing rate. On a 64-resonator
# log-spaced bank covering 50–8000 Hz this is slot 9 (~103.2 Hz).
# Driving the resonator nearest the firing rate is the unambiguous reading
# of "synthesis driven by 100 firings/sec produces output whose dominant
# FFT peak is at the firing-pattern frequency" — the natural mode aligns
# with the firing rate, so coherent buildup amplifies the 100 Hz line.
TARGET_SLOT = 9
PEAK_TOL = 0.20         # ± 20 % of FIRING_RATE_HZ


def _make_bank(Q: float, gain: float) -> Synthesizer:
    cfg = SynthesisConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=float(Q),
        sample_rate_hz=SAMPLE_RATE_HZ,
        n_audio_samples_per_tick=16,
        impulse_gain=float(gain),
        output_gain=1.0,
        firing_threshold=0.1,
    )
    return Synthesizer(cfg)


def measure_empty_rms(Q: float, gain: float) -> float:
    """Output RMS with zero firings injected (matches no-input control)."""
    bank = _make_bank(Q, gain)
    n_samples = int(N_SECONDS * SAMPLE_RATE_HZ)
    out = read_output_samples(bank, n_samples=n_samples)
    return float(np.sqrt(np.mean(out * out)))


def trained_output(Q: float, gain: float) -> np.ndarray:
    """Output waveform with 100 evenly-spaced impulses into the mid slot."""
    bank = _make_bank(Q, gain)
    n_samples = int(N_SECONDS * SAMPLE_RATE_HZ)
    samples_per_firing = SAMPLE_RATE_HZ // FIRING_RATE_HZ   # 160
    out_chunks: list[np.ndarray] = []
    fired = 0
    for i in range(0, n_samples, samples_per_firing):
        drive_resonator_impulse(bank, slot=TARGET_SLOT, strength=1.0)
        fired += 1
        chunk_len = min(samples_per_firing, n_samples - i)
        out_chunks.append(read_output_samples(bank, n_samples=chunk_len))
    out = np.concatenate(out_chunks)[:n_samples]
    assert fired == FIRING_RATE_HZ, f"expected {FIRING_RATE_HZ} firings, got {fired}"
    return out


def measure_trained_metrics(Q: float, gain: float) -> tuple[float, float]:
    """Return (RMS, dominant FFT peak Hz) for the trained-bank output."""
    out = trained_output(Q, gain)
    rms = float(np.sqrt(np.mean(out * out)))
    if rms == 0.0:
        return 0.0, float("nan")
    spec = np.abs(np.fft.rfft(out))
    freqs = np.fft.rfftfreq(out.size, d=1.0 / SAMPLE_RATE_HZ)
    spec[0] = 0.0   # drop DC
    peak_hz = float(freqs[int(np.argmax(spec))])
    return rms, peak_hz


def main() -> None:
    Q_grid = [3, 5, 10, 30]
    gain_grid = [1, 5, 25, 100]
    rows: list[dict] = []
    print(
        f"{'Q':>4} {'gain':>5} {'empty_rms':>11} {'trained_rms':>13} "
        f"{'peak_hz':>10} {'t1':>4} {'t2':>4}"
    )
    print("-" * 60)
    for Q in Q_grid:
        for gain in gain_grid:
            empty = measure_empty_rms(Q, gain)
            trained_rms, peak_hz = measure_trained_metrics(Q, gain)
            test1 = (trained_rms > 0.0) and (empty < 0.1 * trained_rms)
            # Test 2: peak at firing rate (100 Hz) within ±20 %.
            in_band = (
                (1.0 - PEAK_TOL) * FIRING_RATE_HZ
                <= peak_hz
                <= (1.0 + PEAK_TOL) * FIRING_RATE_HZ
            )
            test2 = bool(in_band)
            rows.append({
                "Q": Q, "gain": gain,
                "empty_rms": empty,
                "trained_rms": trained_rms,
                "peak_hz": peak_hz,
                "test1": test1, "test2": test2,
                "passes_both": test1 and test2,
            })
            print(
                f"{Q:>4} {gain:>5} {empty:>11.4e} {trained_rms:>13.4e} "
                f"{peak_hz:>10.2f} {'OK' if test1 else '..':>4} "
                f"{'OK' if test2 else '..':>4}"
            )

    passing = [r for r in rows if r["passes_both"]]
    print("-" * 60)
    print(f"{len(passing)} of {len(rows)} combos pass both tests")
    if passing:
        # Smallest = lowest Q, then lowest gain.
        passing.sort(key=lambda r: (r["Q"], r["gain"]))
        choice = passing[0]
        print(
            f"Locked choice: Q={choice['Q']} gain={choice['gain']} "
            f"(trained_rms={choice['trained_rms']:.4e}, "
            f"peak_hz={choice['peak_hz']:.2f})"
        )
    else:
        print("No combo passes both. Sweep is NULL.")

    out_path = Path("/tmp/r14_sweep.json")
    out_path.write_text(json.dumps(rows, indent=2))
    print(f"Raw rows written to {out_path}")


if __name__ == "__main__":
    main()

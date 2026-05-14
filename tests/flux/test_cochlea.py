"""Tests for cochlea — F2."""
from __future__ import annotations

import numpy as np
import pytest

from agent.flux.cochlea import Resonator, step_resonator


def test_resonator_rings_at_its_tuned_frequency():
    """An impulse into a 1 kHz resonator produces a ringing whose
    zero-crossing rate matches ~1 kHz."""
    sr = 16000
    r = Resonator(freq_hz=1000.0, Q=10.0)
    out = np.zeros(2000, dtype=np.float64)
    out[0] = step_resonator(r, drive=1.0, sr=sr)
    for i in range(1, len(out)):
        out[i] = step_resonator(r, drive=0.0, sr=sr)
    # zero crossings of the tail (after initial transient)
    tail = out[200:1200]
    zc = np.sum(np.diff(np.sign(tail)) != 0)
    # 1000 Hz over 1000 samples @ 16 kHz = 62.5 ms => ~125 zero crossings
    assert 100 < zc < 150, f"zc={zc} not consistent with 1 kHz ringing"


def test_resonator_decays_under_Q():
    """A finite-Q resonator's envelope decays over time."""
    sr = 16000
    r = Resonator(freq_hz=500.0, Q=5.0)
    samples = []
    samples.append(step_resonator(r, drive=1.0, sr=sr))
    for _ in range(1, 4000):
        samples.append(step_resonator(r, drive=0.0, sr=sr))
    early = np.max(np.abs(samples[:500]))
    late = np.max(np.abs(samples[-500:]))
    assert late < 0.2 * early, f"envelope did not decay: early={early}, late={late}"


def test_resonator_selectivity_off_band():
    """Driving a 1 kHz resonator with a 4 kHz sine produces a smaller
    response than driving it with a 1 kHz sine."""
    sr = 16000
    n = 4000

    def drive(freq):
        r = Resonator(freq_hz=1000.0, Q=10.0)
        out = []
        for i in range(n):
            x = np.sin(2 * np.pi * freq * i / sr)
            out.append(step_resonator(r, drive=x, sr=sr))
        return np.max(np.abs(out[-1000:]))

    on_band = drive(1000.0)
    off_band = drive(4000.0)
    assert on_band > 3.0 * off_band, (
        f"resonator not selective: on={on_band}, off={off_band}"
    )


def test_cochlea_bank_log_spaced_frequencies():
    from agent.flux.cochlea import Cochlea, CochleaConfig
    cfg = CochleaConfig(n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0, Q=5.0)
    bank = Cochlea(cfg)
    freqs = bank.freqs_hz
    assert len(freqs) == 64
    assert freqs[0] == pytest.approx(50.0, rel=1e-3)
    assert freqs[-1] == pytest.approx(8000.0, rel=1e-3)
    # log spacing: ratios constant
    ratios = freqs[1:] / freqs[:-1]
    assert np.std(ratios) / np.mean(ratios) < 1e-6


def test_inject_hot_floor_freq_hz_override_pins_log_freq():
    """freq_hz_override puts log(freq_hz) on every injected vibration."""
    from world.flux.quantum import Quanta
    from world.flux.grid import Grid
    from world.flux.boundary import inject_hot_floor
    rng = np.random.default_rng(0)
    q = Quanta(max_quanta=100)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    n = inject_hot_floor(
        q, g, n=10, energy_per=1.0, freq_mean=999.0,
        vel_z_mean=1.0, freq_hz_override=440.0, rng=rng,
    )
    assert n == 10
    freqs = q.freq[q.alive]
    assert np.allclose(freqs, np.log(440.0), atol=1e-12)


def test_cochlea_bank_peaks_at_input_frequency():
    """A 1 kHz tone through the full bank → the resonator nearest
    1 kHz has the largest peak amplitude over the window."""
    from agent.flux.cochlea import Cochlea, CochleaConfig, step_resonators
    cfg = CochleaConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=10.0, sample_rate_hz=16000,
    )
    bank = Cochlea(cfg)
    sr = cfg.sample_rate_hz
    n = 4000
    t = np.arange(n) / sr
    x = np.sin(2 * np.pi * 1000.0 * t)
    peaks = step_resonators(bank, samples=x)
    idx_target = int(np.argmin(np.abs(bank.freqs_hz - 1000.0)))
    idx_actual = int(np.argmax(peaks))
    assert abs(idx_actual - idx_target) <= 1, (
        f"bank peak at idx={idx_actual} (freq={bank.freqs_hz[idx_actual]:.1f}), "
        f"expected near idx={idx_target} (freq={bank.freqs_hz[idx_target]:.1f})"
    )


def test_cochlea_inject_routes_1khz_tone_to_correct_floor_slot():
    """200 ms of 1 kHz sine → cochlea bank → cochlea_inject deposits
    vibrations on the substrate whose freq median is near log(1000 Hz)."""
    from world.flux.quantum import Quanta
    from world.flux.grid import Grid
    from agent.flux.cochlea import (
        Cochlea, CochleaConfig, step_resonators, cochlea_inject,
    )
    rng = np.random.default_rng(0)
    cfg = CochleaConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=10.0, sample_rate_hz=16000, inject_gain=2.0, inject_max_per_tick=8,
    )
    bank = Cochlea(cfg)
    q = Quanta(max_quanta=10_000)
    g = Grid(dims=(30, 30, 60), voxel_size=1.0)
    sr = cfg.sample_rate_hz
    n_samples = 3200  # 200 ms
    t = np.arange(n_samples) / sr
    waveform = np.sin(2 * np.pi * 1000.0 * t)
    for tick_idx in range(200):
        chunk = waveform[tick_idx * 16:(tick_idx + 1) * 16]
        step_resonators(bank, samples=chunk)
        cochlea_inject(q, g, bank, cfg, rng=rng)
    alive_freqs_log = q.freq[q.alive]
    assert alive_freqs_log.size > 0, "no vibrations were injected"
    alive_freqs_hz = np.exp(alive_freqs_log)
    target = 1000.0
    median_hz = float(np.median(alive_freqs_hz))
    assert 0.8 * target < median_hz < 1.2 * target, (
        f"injected freq median {median_hz:.1f} Hz not near 1 kHz target"
    )


def test_read_wav_mono_16k_roundtrip(tmp_path):
    """Write a known sine to wav, read it back, check shape + amplitude."""
    import wave
    from agent.flux.audio_in import read_wav_mono_16k, iter_sample_chunks
    sr = 16000
    n = sr // 2  # 500 ms
    t = np.arange(n) / sr
    x = (0.5 * np.sin(2 * np.pi * 440.0 * t) * 32767.0).astype(np.int16)
    p = tmp_path / "tone.wav"
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(x.tobytes())
    y = read_wav_mono_16k(p)
    assert y.shape == (n,)
    assert 0.45 < np.max(np.abs(y)) < 0.55
    chunks = list(iter_sample_chunks(y, 16))
    assert len(chunks) == n // 16
    assert all(len(c) == 16 for c in chunks)

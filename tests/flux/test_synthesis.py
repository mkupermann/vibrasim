"""Tests for synthesis — F2."""
from __future__ import annotations

import numpy as np
import pytest

from agent.flux.synthesis import (
    Synthesizer, SynthesisConfig,
    drive_resonator_impulse, read_output_samples,
    route_node_firings_explicit,
)


def test_synthesis_impulse_produces_ringing_at_resonator_freq():
    """A single impulse into the 1 kHz resonator produces an output
    waveform whose spectrum peaks near 1 kHz."""
    cfg = SynthesisConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=10.0, sample_rate_hz=16000,
    )
    bank = Synthesizer(cfg)
    idx_1k = int(np.argmin(np.abs(bank.freqs_hz - 1000.0)))
    drive_resonator_impulse(bank, slot=idx_1k, strength=1.0)
    out = read_output_samples(bank, n_samples=2000)
    spec = np.abs(np.fft.rfft(out))
    freqs = np.fft.rfftfreq(len(out), d=1.0 / cfg.sample_rate_hz)
    peak_hz = freqs[int(np.argmax(spec))]
    assert 800.0 < peak_hz < 1200.0, f"peak at {peak_hz} Hz, expected ~1000"


def test_synthesis_routes_node_firings_to_nearest_resonator():
    """A forced node-firing pattern at log(1000) drives the synthesis
    bank to produce an output spectrum peak near 1 kHz."""
    cfg = SynthesisConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=10.0, sample_rate_hz=16000, impulse_gain=1.0,
    )
    bank = Synthesizer(cfg)
    firings = [(float(np.log(1000.0)), 1.0)] * 20
    route_node_firings_explicit(bank, firings)
    out = read_output_samples(bank, n_samples=4000)
    spec = np.abs(np.fft.rfft(out))
    freqs = np.fft.rfftfreq(len(out), d=1.0 / cfg.sample_rate_hz)
    peak_hz = freqs[int(np.argmax(spec))]
    assert 800.0 < peak_hz < 1200.0, f"peak at {peak_hz} Hz, expected ~1000"


def test_F2_1khz_burst_roundtrip_cochlea_only():
    """1 kHz tone burst → cochlea bank → cochlea-shortcut → synthesis bank
    → output. The pre-registered F2 acceptance test (spec §9 F2 row).

    Isolates F2 routing (cochlea peaks → synthesis impulses → ringing) from
    substrate dynamics. Binding is disabled by virtue of running the bank
    shortcut, not the full tick loop.
    """
    from agent.flux.cochlea import Cochlea, CochleaConfig, step_resonators
    sr = 16000
    ccfg = CochleaConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=10.0, sample_rate_hz=sr,
    )
    scfg = SynthesisConfig(
        n_resonators=64, freq_min_hz=50.0, freq_max_hz=8000.0,
        Q=10.0, sample_rate_hz=sr,
    )
    coch = Cochlea(ccfg)
    synth = Synthesizer(scfg)
    n_samples = sr // 2  # 500 ms
    t = np.arange(n_samples) / sr
    x = np.sin(2 * np.pi * 1000.0 * t)
    chunk = 16
    out_total: list[float] = []
    for i in range(0, n_samples, chunk):
        buf = x[i:i + chunk]
        peaks = step_resonators(coch, samples=buf)
        for slot, p in enumerate(peaks):
            if p > 0.01:
                drive_resonator_impulse(synth, slot=slot, strength=float(p))
        out_total.extend(read_output_samples(synth, n_samples=chunk))
    out = np.array(out_total[-(sr // 4):])  # last 250 ms, skip transients
    spec = np.abs(np.fft.rfft(out))
    freqs = np.fft.rfftfreq(len(out), d=1.0 / sr)
    peak_hz = freqs[int(np.argmax(spec))]
    assert 800.0 < peak_hz < 1200.0, (
        f"round-trip peak at {peak_hz} Hz, expected ~1000"
    )


def test_wav_writer_roundtrip(tmp_path):
    """Write a known sine via WavWriter, read back, verify shape + amplitude."""
    from agent.flux.audio_out import WavWriter
    from agent.flux.audio_in import read_wav_mono_16k
    sr = 16000
    n = sr // 4  # 250 ms
    t = np.arange(n) / sr
    x = 0.5 * np.sin(2 * np.pi * 440.0 * t)
    p = tmp_path / "out.wav"
    with WavWriter(p, sample_rate_hz=sr) as w:
        # append in chunks to exercise the buffer
        for i in range(0, n, 16):
            w.append(x[i:i + 16])
    y = read_wav_mono_16k(p)
    assert y.shape == (n,)
    assert 0.45 < np.max(np.abs(y)) < 0.55

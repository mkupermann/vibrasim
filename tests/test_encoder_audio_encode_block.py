"""Tests for STFT-based audio encoding (AC2, AC3)."""
import numpy as np
import pytest
from agent.encoder_audio import encode_block


def test_AC2_pure_tone_round_trips():
    """5-cycle 1000 Hz sine at 16 kHz: encode produces emission near 1000 Hz."""
    sample_rate = 16000
    fft_size = 512
    duration_samples = fft_size
    t = np.arange(duration_samples) / sample_rate
    samples = 0.5 * np.sin(2 * np.pi * 1000 * t).astype(np.float32)
    emissions = encode_block(samples, sample_rate=sample_rate, fft_size=fft_size,
                             amplitude_threshold=0.01)
    # Find emission with frequency closest to 1000 Hz
    freqs = [e[0] for e in emissions]
    assert any(abs(f - 1000.0) < 50.0 for f in freqs), (
        f"AC2: no emission near 1000 Hz; got freqs={freqs}"
    )
    # Amplitude should be above threshold for the 1000 Hz bin
    near_1k = [e for e in emissions if abs(e[0] - 1000.0) < 50.0]
    assert all(e[1] >= 0.01 for e in near_1k)


def test_AC3_silence_produces_no_emissions():
    """All-zero input → empty emissions list (or all below-threshold filtered)."""
    samples = np.zeros(512, dtype=np.float32)
    emissions = encode_block(samples, amplitude_threshold=0.01)
    assert emissions == []


def test_AC3b_below_threshold_filtered():
    """Very quiet signal → no emissions."""
    sample_rate = 16000
    t = np.arange(512) / sample_rate
    samples = (0.0001 * np.sin(2 * np.pi * 1000 * t)).astype(np.float32)
    emissions = encode_block(samples, sample_rate=sample_rate,
                             amplitude_threshold=0.01)
    assert emissions == []


def test_AC3c_freq_range_clipped():
    """Frequencies outside [freq_min, freq_max] are excluded."""
    sample_rate = 16000
    fft_size = 512
    t = np.arange(fft_size) / sample_rate
    # 30 Hz tone — below freq_min=50
    samples = 0.5 * np.sin(2 * np.pi * 30 * t).astype(np.float32)
    emissions = encode_block(samples, sample_rate=sample_rate, fft_size=fft_size,
                             freq_min=50.0, freq_max=8000.0,
                             amplitude_threshold=0.001)
    assert all(e[0] >= 50.0 for e in emissions)

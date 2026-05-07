"""Tests for inverse-STFT decoding (AC4, AC5)."""
import numpy as np
from agent.encoder_audio import encode_block, decode_to_audio


def test_AC4_decode_single_tone_has_peak_at_target():
    """[(1000, 0.5, True)] decodes to audio with spectral peak near 1000 Hz."""
    samples = decode_to_audio(
        [(1000.0, 0.5, True)],
        block_size=256, sample_rate=16000, fft_size=512,
    )
    assert samples.shape == (256,)
    assert samples.dtype == np.float32
    # Spectral peak check
    spectrum = np.fft.rfft(samples, n=512)
    freqs = np.fft.rfftfreq(512, d=1.0 / 16000)
    peak_idx = int(np.argmax(np.abs(spectrum)))
    peak_freq = float(freqs[peak_idx])
    assert abs(peak_freq - 1000.0) < 1000.0 * 0.02, (
        f"AC4: decoded peak at {peak_freq} Hz, expected ~1000 Hz"
    )


def test_AC5_encode_decode_preserves_dominant_frequency():
    """Encode a 1 kHz tone, decode emissions, peak still at 1 kHz ±5%."""
    sample_rate = 16000
    fft_size = 512
    t = np.arange(fft_size) / sample_rate
    samples_in = 0.5 * np.sin(2 * np.pi * 1000 * t).astype(np.float32)
    emissions = encode_block(samples_in, sample_rate=sample_rate, fft_size=fft_size)
    samples_out = decode_to_audio(emissions, block_size=fft_size,
                                   sample_rate=sample_rate, fft_size=fft_size)
    spectrum = np.fft.rfft(samples_out, n=fft_size)
    freqs = np.fft.rfftfreq(fft_size, d=1.0 / sample_rate)
    peak_idx = int(np.argmax(np.abs(spectrum)))
    peak_freq = float(freqs[peak_idx])
    assert abs(peak_freq - 1000.0) < 1000.0 * 0.05

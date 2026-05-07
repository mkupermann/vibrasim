"""Plan C — pure-functional audio encoding/decoding.

Frequency-to-position mapping, STFT and ISTFT helpers. No threads, no state,
no I/O. Easily testable.
"""
import numpy as np


def freq_to_port_position(
    freq: float,
    freq_min: float = 50.0,
    freq_max: float = 8000.0,
    port_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
    rng: np.random.Generator | None = None,
) -> tuple[float, float, float]:
    """Map an audio frequency (Hz) to a 3D position inside the port volume.

    X is deterministic — log-normalised mapping along the port's X axis.
    Y and Z are random within the port box (so different frequencies don't
    always land on the same y/z and bind into the same electron).
    """
    if rng is None:
        rng = np.random.default_rng()
    f_clamped = max(freq_min, min(freq_max, freq))
    log_norm = (np.log(f_clamped) - np.log(freq_min)) / (np.log(freq_max) - np.log(freq_min))
    x = port_origin[0] + log_norm * port_size[0]
    y = port_origin[1] + float(rng.random()) * port_size[1]
    z = port_origin[2] + float(rng.random()) * port_size[2]
    return (float(x), y, z)


def encode_block(
    samples: np.ndarray,
    sample_rate: int = 16000,
    fft_size: int = 512,
    amplitude_threshold: float = 0.01,
    freq_min: float = 50.0,
    freq_max: float = 8000.0,
) -> list[tuple[float, float, bool]]:
    """STFT a block, return (freq, amplitude, polarity) per significant bin.

    Polarity is encoded as the sign of the bin's real part (positive → True,
    negative → False). Amplitude is the magnitude clipped to [0, 1].
    """
    spectrum = np.fft.rfft(samples, n=fft_size)
    freqs = np.fft.rfftfreq(fft_size, d=1.0 / sample_rate)
    out: list[tuple[float, float, bool]] = []
    for i, c in enumerate(spectrum):
        f = float(freqs[i])
        if f < freq_min or f > freq_max:
            continue
        a = float(np.abs(c)) / fft_size
        if a < amplitude_threshold:
            continue
        polarity = bool(c.real >= 0)
        out.append((f, min(a, 1.0), polarity))
    return out


def decode_to_audio(
    emissions: list[tuple[float, float, bool]],
    block_size: int = 256,
    sample_rate: int = 16000,
    fft_size: int = 512,
    freq_min: float = 50.0,
    freq_max: float = 8000.0,
) -> np.ndarray:
    """Inverse-STFT a list of (freq, amplitude, polarity) triples to audio.

    v1: take the first block_size samples of the IFFT'd block. No
    overlap-add windowing — phase artifacts at block boundaries are
    tolerated; acceptance test I2 only requires spectral correlation.
    """
    spectrum = np.zeros(fft_size // 2 + 1, dtype=complex)
    bin_width = sample_rate / fft_size
    for f, a, polarity in emissions:
        if f < freq_min or f > freq_max:
            continue
        bin_idx = int(round(f / bin_width))
        if bin_idx < 0 or bin_idx >= len(spectrum):
            continue
        sign = 1.0 if polarity else -1.0
        spectrum[bin_idx] += a * fft_size * sign
    samples = np.fft.irfft(spectrum, n=fft_size)
    return samples[:block_size].astype(np.float32)

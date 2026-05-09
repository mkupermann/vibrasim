"""Inverse of `agent/encoder_audio.py`.

Converts a stream of atom firings observed in the audio_output port back
into a time-domain waveform. The pipeline is:

    firings (time, freq, polarity)
        -> STFT bins
        -> ISTFT waveform
        -> normalised float32 in [-1, 1]
        -> int16 .wav (optional)

This module is intentionally self-contained: it does not import from
`encoder_audio` even though it mirrors that module's parameters. The
constants (`freq_min=50`, `freq_max=8000`, `fft_size=512`,
`sample_rate=16000`, default port box) match `encoder_audio.py` so the
encode -> decode round-trip is well-defined.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import scipy.io.wavfile
import scipy.signal


# --- frequency / position mapping -------------------------------------------------


def port_position_to_freq(
    pos: tuple[float, float, float],
    port_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
    freq_min: float = 50.0,
    freq_max: float = 8000.0,
) -> float:
    """Inverse of ``encoder_audio.freq_to_port_position``.

    Recovers the encoded frequency from the X coordinate of a 3D port
    position. Y and Z are ignored — the encoder placed them randomly.
    The X axis is a log-linear map between ``freq_min`` and ``freq_max``.
    """
    if port_size[0] <= 0.0:
        raise ValueError("port_size[0] must be positive")
    log_norm = (pos[0] - port_origin[0]) / port_size[0]
    log_norm = float(np.clip(log_norm, 0.0, 1.0))
    log_f = np.log(freq_min) + log_norm * (np.log(freq_max) - np.log(freq_min))
    return float(np.exp(log_f))


# --- firings -> STFT --------------------------------------------------------------


def decode_firings_to_stft(
    firings: list[tuple[float, float, bool]],
    sample_rate: int = 16000,
    fft_size: int = 512,
) -> np.ndarray:
    """Bin atom firings into a complex STFT matrix.

    Parameters
    ----------
    firings
        Sequence of ``(time_seconds, freq_hz, polarity)`` triples. Polarity
        encodes phase: ``True`` -> 0, ``False`` -> pi.
    sample_rate
        Audio sample rate. The STFT hop is fixed at 10 ms (160 samples at
        16 kHz) to match the encoder's frame cadence.
    fft_size
        Length of each STFT frame.

    Returns
    -------
    np.ndarray
        Complex STFT matrix of shape ``(fft_size // 2 + 1, n_frames)``.
        ``n_frames`` is determined by the latest firing time, or 1 if
        the firing list is empty (a single all-zeros frame).
    """
    if fft_size <= 0:
        raise ValueError("fft_size must be positive")

    hop = max(1, sample_rate // 100)  # 10 ms hop
    bin_width = sample_rate / fft_size
    n_freq_bins = fft_size // 2 + 1

    if not firings:
        return np.zeros((n_freq_bins, 1), dtype=np.complex128)

    max_time = max(t for (t, _f, _p) in firings)
    n_frames = max(1, int(np.ceil(max_time * sample_rate / hop)) + 1)

    stft = np.zeros((n_freq_bins, n_frames), dtype=np.complex128)

    for t, f, polarity in firings:
        if f <= 0.0:
            continue
        bin_idx = int(round(f / bin_width))
        if bin_idx < 0 or bin_idx >= n_freq_bins:
            continue
        frame_idx = int(round(t * sample_rate / hop))
        if frame_idx < 0 or frame_idx >= n_frames:
            continue
        # phase = 0 for True, pi for False -> +1 / -1 multiplier
        sign = 1.0 + 0j if polarity else -1.0 + 0j
        # Each firing contributes unit magnitude. Multiple firings on the same
        # (frame, bin) accumulate.
        stft[bin_idx, frame_idx] += sign

    return stft


# --- STFT -> waveform -------------------------------------------------------------


def stft_to_waveform(
    stft: np.ndarray,
    sample_rate: int = 16000,
    fft_size: int = 512,
) -> np.ndarray:
    """Inverse-STFT to a real-valued time-domain waveform.

    Uses ``scipy.signal.istft`` with the same hop (10 ms) used in
    ``decode_firings_to_stft``. Output is float32 clipped to [-1, 1].
    """
    hop = max(1, sample_rate // 100)
    _t, samples = scipy.signal.istft(
        stft,
        fs=sample_rate,
        nperseg=fft_size,
        noverlap=fft_size - hop,
        nfft=fft_size,
        input_onesided=True,
    )
    samples = np.asarray(samples, dtype=np.float32)
    samples = np.clip(samples, -1.0, 1.0)
    return samples


# --- high-level convenience -------------------------------------------------------


def decode_block(
    firings: list[tuple[float, float, bool]],
    duration_seconds: float,
    sample_rate: int = 16000,
) -> np.ndarray:
    """Convert a firings stream to a normalised waveform of fixed duration.

    The waveform is truncated or zero-padded to ``duration_seconds`` and
    rescaled so its peak amplitude is 0.95 (preventing int16 clipping
    in ``write_wav``). Pure silence -> all-zeros waveform.
    """
    if duration_seconds <= 0.0:
        raise ValueError("duration_seconds must be positive")

    n_target = int(round(duration_seconds * sample_rate))
    stft = decode_firings_to_stft(firings, sample_rate=sample_rate)
    waveform = stft_to_waveform(stft, sample_rate=sample_rate)

    if waveform.size < n_target:
        waveform = np.concatenate(
            [waveform, np.zeros(n_target - waveform.size, dtype=np.float32)]
        )
    else:
        waveform = waveform[:n_target]

    peak = float(np.max(np.abs(waveform))) if waveform.size else 0.0
    if peak > 0.0:
        waveform = (waveform / peak) * np.float32(0.95)

    return waveform.astype(np.float32, copy=False)


# --- wav I/O ----------------------------------------------------------------------


def write_wav(
    samples: np.ndarray,
    path: str | Path,
    sample_rate: int = 16000,
) -> None:
    """Write a float32 [-1, 1] sample array as a 16-bit PCM mono .wav file."""
    arr = np.asarray(samples, dtype=np.float32)
    arr = np.clip(arr, -1.0, 1.0)
    pcm16 = (arr * np.float32(32767.0)).astype(np.int16)
    scipy.io.wavfile.write(str(path), sample_rate, pcm16)

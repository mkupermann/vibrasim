"""Audio input glue — read wav, resample to 16 kHz mono, iterate chunks.

Thin layer over `wave` stdlib + numpy. No external dependency. Resampling
is a linear-interp sample-rate converter — adequate for spectral tests
where exact phase is not required.
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

DEFAULT_SR_HZ = 16000


def read_wav_mono_16k(path: str | Path,
                      target_sr_hz: int = DEFAULT_SR_HZ) -> np.ndarray:
    """Read a wav file, downmix to mono, resample to target_sr_hz.

    Returns shape (N,) float64 in [-1.0, 1.0]. Integer PCM formats are
    rescaled by the appropriate width.
    """
    p = Path(path)
    with wave.open(str(p), "rb") as w:
        n_channels = w.getnchannels()
        sample_width = w.getsampwidth()
        framerate = w.getframerate()
        n_frames = w.getnframes()
        raw = w.readframes(n_frames)

    if sample_width == 1:
        # 8-bit PCM is unsigned in WAV; map to [-1, 1).
        arr = np.frombuffer(raw, dtype=np.uint8).astype(np.float64)
        arr = (arr - 128.0) / 128.0
    elif sample_width == 2:
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    elif sample_width == 4:
        arr = np.frombuffer(raw, dtype=np.int32).astype(np.float64) / 2147483648.0
    else:
        raise ValueError(
            f"unsupported sample width {sample_width} bytes (path={p})"
        )

    if n_channels > 1:
        arr = arr.reshape(-1, n_channels).mean(axis=1)

    if framerate != target_sr_hz:
        arr = _resample_linear(arr, framerate, target_sr_hz)
    return arr.astype(np.float64, copy=False)


def _resample_linear(x: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    """Linear-interpolation resample — fast, low-fidelity but adequate for
    spectral tests where exact phase is not the contract."""
    if src_sr == dst_sr:
        return x
    n_dst = int(round(len(x) * dst_sr / src_sr))
    src_idx = np.arange(n_dst, dtype=np.float64) * src_sr / dst_sr
    i0 = np.floor(src_idx).astype(np.int64)
    i0 = np.clip(i0, 0, len(x) - 1)
    i1 = np.clip(i0 + 1, 0, len(x) - 1)
    frac = src_idx - i0
    return (1.0 - frac) * x[i0] + frac * x[i1]


def iter_sample_chunks(samples: np.ndarray, chunk_size: int):
    """Yield non-overlapping chunks of size `chunk_size`. The final chunk
    may be shorter than `chunk_size`."""
    n = len(samples)
    for i in range(0, n, chunk_size):
        yield samples[i:i + chunk_size]

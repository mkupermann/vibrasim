"""Audio output glue — append-and-flush 16 kHz mono wav writer.

Thin layer over `wave` stdlib + numpy. No external dependency. Samples
accumulate in a buffer; flush writes them out as 16-bit PCM. Same sample
rate convention as audio_in (16 kHz mono per spec §5.6 / §5.7).
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

DEFAULT_SR_HZ = 16000


def write_wav_mono_16k(path: str | Path,
                       samples: np.ndarray,
                       sample_rate_hz: int = DEFAULT_SR_HZ,
                       clip: bool = True) -> None:
    """Write float64 samples in [-1, 1] to a 16-bit PCM mono wav file.

    If `clip` is True, samples outside [-1, 1] are clipped before
    quantisation (16-bit signed range). If False, they wrap — useful
    for diagnostic checks but normally you want the clip.
    """
    p = Path(path)
    x = np.asarray(samples, dtype=np.float64)
    if clip:
        x = np.clip(x, -1.0, 1.0)
    x_i16 = (x * 32767.0).astype(np.int16)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(sample_rate_hz))
        w.writeframes(x_i16.tobytes())


class WavWriter:
    """Append-and-flush 16-bit PCM mono wav writer at a fixed sample rate.

    Buffer samples via `append`; when done, call `flush` to commit to disk.
    Re-opening for append is not supported (wave stdlib limitation); call
    `flush` exactly once per file.
    """

    def __init__(self, path: str | Path,
                 sample_rate_hz: int = DEFAULT_SR_HZ):
        self.path = Path(path)
        self.sample_rate_hz = int(sample_rate_hz)
        self._buf: list[np.ndarray] = []
        self._flushed = False

    def append(self, samples: np.ndarray) -> None:
        if self._flushed:
            raise RuntimeError(
                f"WavWriter({self.path}) already flushed — cannot append"
            )
        self._buf.append(np.asarray(samples, dtype=np.float64))

    def flush(self) -> None:
        if self._flushed:
            return
        if not self._buf:
            joined = np.zeros(0, dtype=np.float64)
        else:
            joined = np.concatenate(self._buf)
        write_wav_mono_16k(self.path, joined, self.sample_rate_hz)
        self._flushed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.flush()

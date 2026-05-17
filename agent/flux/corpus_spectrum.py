"""Corpus log-power spectrum quantised to the F2 cochlea log-bins.

Used by `agent.flux.training_metric.corpus_alignment_index` as the
reference distribution against which the substrate's surviving-bridge
endpoint-frequency histogram is compared.

Definition (locked by R-6 plan §"Pre-registered numeric thresholds"):
- Welch periodogram on the corpus waveform at the corpus sample rate.
- Magnitude squared, log-scaled, then quantised to `n_freq_bins`
  log-spaced bins matching the cochlea bank (default
  `freq_band_hz=(50.0, 8000.0)`, `n_freq_bins=64`).
- Normalised to sum to 1.0 so it is a probability distribution.

Pure function, no side effects. Caching to disk is the caller's job.
"""
from __future__ import annotations

import numpy as np


def compute_corpus_log_power_spectrum(
    corpus_waveform: np.ndarray,
    sample_rate_hz: int,
    n_freq_bins: int = 64,
    freq_band_hz: tuple[float, float] = (50.0, 8000.0),
    nperseg: int = 4096,
) -> np.ndarray:
    """Return a length-`n_freq_bins` probability distribution over the
    cochlea log-spaced frequency bins.

    Args:
        corpus_waveform: 1-D float waveform.
        sample_rate_hz: source sample rate (no resampling here; caller
            must hand a waveform already at the cochlea's rate).
        n_freq_bins: number of log-spaced bins (matches cochlea bank).
        freq_band_hz: (f_min, f_max) for the bin edges, log-spaced.
        nperseg: Welch segment length in samples.

    Returns:
        np.ndarray of shape (n_freq_bins,), float64, sums to 1.0.
    """
    x = np.asarray(corpus_waveform, dtype=np.float64).reshape(-1)
    if x.size < 2:
        return np.full(n_freq_bins, 1.0 / n_freq_bins, dtype=np.float64)

    psd = _welch_psd(x, sample_rate_hz=sample_rate_hz, nperseg=nperseg)
    freqs = np.fft.rfftfreq(nperseg, d=1.0 / sample_rate_hz)
    bin_edges = np.logspace(
        np.log10(freq_band_hz[0]),
        np.log10(freq_band_hz[1]),
        n_freq_bins + 1,
    )
    log_power = np.log1p(psd)

    binned = np.zeros(n_freq_bins, dtype=np.float64)
    for k in range(n_freq_bins):
        mask = (freqs >= bin_edges[k]) & (freqs < bin_edges[k + 1])
        if mask.any():
            binned[k] = float(log_power[mask].mean())
    total = float(binned.sum())
    if total <= 0.0:
        return np.full(n_freq_bins, 1.0 / n_freq_bins, dtype=np.float64)
    return binned / total


def _welch_psd(
    x: np.ndarray, sample_rate_hz: int, nperseg: int,
) -> np.ndarray:
    """Minimal Welch PSD: Hann windows, 50% overlap, magnitude-squared
    mean across segments. Avoids scipy as a dependency.
    """
    n = x.size
    if n < nperseg:
        nperseg = max(64, int(2 ** np.floor(np.log2(max(n, 64)))))
    step = nperseg // 2
    window = 0.5 - 0.5 * np.cos(
        2.0 * np.pi * np.arange(nperseg) / nperseg
    )
    win_norm = float((window ** 2).sum())
    if win_norm == 0.0:
        win_norm = 1.0
    segments = []
    for start in range(0, n - nperseg + 1, step):
        seg = x[start:start + nperseg] * window
        spec = np.fft.rfft(seg)
        segments.append((spec.real ** 2 + spec.imag ** 2) / win_norm)
    if not segments:
        return np.zeros(nperseg // 2 + 1, dtype=np.float64)
    psd = np.mean(np.stack(segments, axis=0), axis=0)
    return psd

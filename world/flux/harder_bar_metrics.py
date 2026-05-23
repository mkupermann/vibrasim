"""Helpers for BET-009 harder-bar tests T7-T9.

Pre-registered in LOGBOOK 2026-05-23 ~20:55. Thresholds locked.
"""
from __future__ import annotations

import numpy as np


def hist_kl_symmetric(a: np.ndarray, b: np.ndarray, n_bins: int = 32) -> float:
    """Symmetric histogram KL with Laplace smoothing. Same as BET-002 _hist_kl."""
    a_flat = a.ravel()
    b_flat = b.ravel()
    lo = min(a_flat.min(), b_flat.min())
    hi = max(a_flat.max(), b_flat.max())
    if hi - lo < 1e-12:
        return 0.0
    edges = np.linspace(lo, hi, n_bins + 1)
    ha, _ = np.histogram(a_flat, bins=edges)
    hb, _ = np.histogram(b_flat, bins=edges)
    pa = (ha + 1.0) / (ha.sum() + n_bins)
    pb = (hb + 1.0) / (hb.sum() + n_bins)
    return 0.5 * (float(np.sum(pa * np.log(pa / pb))) + float(np.sum(pb * np.log(pb / pa))))


def shuffle_chunks_in_time(audio: np.ndarray, chunk_size: int, seed: int) -> np.ndarray:
    """Return a permutation of `audio` where contiguous `chunk_size`-sample
    blocks are randomly re-ordered. Preserves the marginal sample distribution
    exactly (each sample appears once) but destroys temporal/sequence order.
    """
    n = audio.size
    n_chunks = n // chunk_size
    if n_chunks <= 1:
        return audio.copy()
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n_chunks)
    out = np.empty_like(audio[:n_chunks * chunk_size])
    for new_pos, old_pos in enumerate(perm):
        out[new_pos * chunk_size:(new_pos + 1) * chunk_size] = (
            audio[old_pos * chunk_size:(old_pos + 1) * chunk_size]
        )
    return out


def spatial_autocorrelation(field_4d: np.ndarray) -> float:
    """Mean Pearson correlation between immediate-neighbour cells in a
    4D field of shape (Lx, Ly, Lz, n_features). Averaged across all three
    axis-pairs and all features. Returns a scalar in [-1, 1].

    A substrate with no spatial structure → ~0. A substrate with topological
    organisation (e.g., SOM with Gaussian neighbourhood update) → > 0.
    """
    Lx, Ly, Lz, F = field_4d.shape
    correlations = []
    for axis in range(3):
        # Build the pair (cell, cell+1 along axis)
        if axis == 0:
            a = field_4d[:-1, :, :, :]
            b = field_4d[1:, :, :, :]
        elif axis == 1:
            a = field_4d[:, :-1, :, :]
            b = field_4d[:, 1:, :, :]
        else:
            a = field_4d[:, :, :-1, :]
            b = field_4d[:, :, 1:, :]
        # Per-feature Pearson r across all neighbour pairs along this axis
        for f in range(F):
            a_f = a[..., f].ravel()
            b_f = b[..., f].ravel()
            if a_f.std() < 1e-12 or b_f.std() < 1e-12:
                continue
            r = float(np.corrcoef(a_f, b_f)[0, 1])
            if not np.isnan(r):
                correlations.append(r)
    if not correlations:
        return 0.0
    return float(np.mean(correlations))

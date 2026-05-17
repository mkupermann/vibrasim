"""R-8 corpus-alignment metric — pure function over substrate state.

Definition (locked by R-6 plan §"Pre-registered numeric thresholds"):

    alignment = 1 - JS(p_bridge || p_corpus) / ln(2)

where:
- `p_bridge` is the distribution of alive-bridge endpoint frequencies,
  binned into `n_freq_bins` log-spaced bins matching the cochlea bank.
  Each alive bridge contributes its two endpoints (src + dst) to the
  histogram (so a bridge with both endpoints in the same bin adds 2.0
  to that bin).
- `p_corpus` is the pre-computed `corpus_log_power_spectrum` over the
  same bin grid.
- JS-divergence uses log base e; the `ln(2)` normaliser bounds JS to
  `[0, ln(2)]`, so `alignment ∈ [0, 1]`.

Returns 0.0 if no alive bridges.
"""
from __future__ import annotations

import numpy as np

from world.flux.bridges import Bridges
from world.flux.structures import Nodes


def corpus_alignment_index(
    bridges: Bridges,
    nodes: Nodes,
    corpus_log_power_spectrum: np.ndarray,
    n_freq_bins: int = 64,
    freq_band_hz: tuple[float, float] = (50.0, 8000.0),
) -> float:
    """Compute `1 - JS(p_bridge || p_corpus) / ln(2)`.

    Args:
        bridges: live Bridges container (SoA).
        nodes: live Nodes container (SoA); `nodes.freq` is in log-Hz.
        corpus_log_power_spectrum: shape (n_freq_bins,), probability
            distribution (sums to 1.0). Output of
            `compute_corpus_log_power_spectrum`.
        n_freq_bins: bin count; must match the corpus distribution.
        freq_band_hz: log-bin edges, must match corpus computation.

    Returns:
        alignment ∈ [0, 1]. 0.0 if no alive bridges.
    """
    alive_mask = bridges.alive
    if not bool(alive_mask.any()):
        return 0.0
    alive_idx = np.where(alive_mask)[0]
    src = bridges.src[alive_idx]
    dst = bridges.dst[alive_idx]
    # nodes.freq is log-Hz; convert to Hz, then binned to log-edges.
    endpoint_log_hz = np.concatenate([nodes.freq[src], nodes.freq[dst]])
    endpoint_hz = np.exp(endpoint_log_hz)

    bin_edges = np.logspace(
        np.log10(freq_band_hz[0]),
        np.log10(freq_band_hz[1]),
        n_freq_bins + 1,
    )
    # np.histogram clamps below first edge / above last edge to bin 0 /
    # last; we want to drop out-of-band endpoints, not pile them in
    # the boundary bins.
    in_band = (
        (endpoint_hz >= bin_edges[0])
        & (endpoint_hz <= bin_edges[-1])
    )
    endpoint_hz_in_band = endpoint_hz[in_band]
    if endpoint_hz_in_band.size == 0:
        return 0.0
    counts, _ = np.histogram(endpoint_hz_in_band, bins=bin_edges)
    total = float(counts.sum())
    if total <= 0.0:
        return 0.0
    p_bridge = counts.astype(np.float64) / total

    p_corpus = np.asarray(corpus_log_power_spectrum, dtype=np.float64)
    if p_corpus.shape != p_bridge.shape:
        raise ValueError(
            f"corpus_log_power_spectrum shape {p_corpus.shape} != "
            f"bridge histogram shape {p_bridge.shape}"
        )
    # Renormalise just in case caller didn't.
    p_corpus_sum = float(p_corpus.sum())
    if p_corpus_sum <= 0.0:
        return 0.0
    p_corpus = p_corpus / p_corpus_sum

    js = _js_divergence(p_bridge, p_corpus)
    alignment = 1.0 - js / float(np.log(2.0))
    # Clip to [0, 1] for floating-point safety.
    return float(np.clip(alignment, 0.0, 1.0))


def _js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Jensen-Shannon divergence (log base e). Bounded by ln(2)."""
    m = 0.5 * (p + q)
    return float(0.5 * _kl(p, m) + 0.5 * _kl(q, m))


def _kl(p: np.ndarray, q: np.ndarray) -> float:
    """KL(p || q) with zero-mass handled by skipping (0 * log 0 := 0)."""
    mask = (p > 0.0) & (q > 0.0)
    if not bool(mask.any()):
        return 0.0
    return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))

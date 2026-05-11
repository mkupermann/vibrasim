"""Binding mechanism — the single rule that replaces 6 engineered levels.

Per spec §3, a bond forms between two or more vibrations within distance
`r` and time window `τ` with probability:

    p_bind = sigmoid(α * pred_coherence + β * (T_crit - T_local))

In F1a this is implemented in its scope-minimal form:
- `pred_coherence` is frequency-equality within `eps` (1.0 or 0.0), not
  the full windowed cross-correlation. T3 uses single-frequency
  injection, so this collapses trivially to 1.0 for all candidate pairs.
  The full cross-correlation version arrives in F2 when the cochlea
  brings multi-frequency input.
- Binding consumes quanta (frees their slots) and creates one Node.
- Binding is exothermic: a fraction `η` of total binding energy is
  exported as heat (added to the auditor).
- F1a binds in groups of exactly 2 per event. F1b will generalise.
"""
from __future__ import annotations
import numpy as np

from world.flux.quantum import Quanta


def pred_coherence(freq_a: float, freq_b: float,
                   eps: float = 1.0) -> float:
    """Simplified F1a coherence: 1.0 iff |freq_a - freq_b| < eps.

    The spec defines pred_coherence as a windowed temporal
    cross-correlation of frequency-amplitude trajectories. F1a's
    single-frequency injection makes all pairs trivially coherent;
    the binary form here matches that regime exactly. Full version
    arrives in F2 with multi-frequency cochlea input.
    """
    return 1.0 if abs(freq_a - freq_b) < eps else 0.0


def find_pairs_within(quanta: Quanta, r: float) -> np.ndarray:
    """Return shape (M, 2) int array of (i, j) pairs with i<j where the
    two alive quanta are within Euclidean distance r of each other.

    Naive O(N^2/2) algorithm — fine at F1a scale (≤ 1000 alive quanta).
    A KD-tree or cell-list optimisation is the F1b/F2 concern.
    """
    alive_idx = np.where(quanta.alive)[0]
    n = alive_idx.size
    if n < 2:
        return np.zeros((0, 2), dtype=np.int64)

    pos = quanta.pos[alive_idx]  # (n, 3)
    # Pairwise squared distances
    diff = pos[:, None, :] - pos[None, :, :]  # (n, n, 3)
    d2 = (diff * diff).sum(axis=-1)  # (n, n)
    r2 = r * r

    # Upper-triangle mask, strictly within r (d2 < r2)
    i_local, j_local = np.where(np.triu(d2 < r2, k=1))
    if i_local.size == 0:
        return np.zeros((0, 2), dtype=np.int64)
    pairs = np.stack([alive_idx[i_local], alive_idx[j_local]], axis=1)
    return pairs.astype(np.int64)

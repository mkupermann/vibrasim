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

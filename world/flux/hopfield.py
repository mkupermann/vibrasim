"""Hopfield Network (Hopfield 1982) — attractor-based pattern completion.

Stores patterns as attractors in a recurrent network via Hebbian
outer-product learning. Given partial cue, network dynamically
converges to nearest stored attractor.

Pre-LLM (1982). No backprop. No learning rate. Just outer-product
accumulation + iterative recall.

For audio: store SOM cell weights (or training-chunk features) as
attractor patterns. Test pattern completion from partial cues.

Mechanism (continuous Hopfield-Tank variant for real-valued patterns):
  Storage:
    W = sum over stored patterns x: x x^T   (Hebbian outer product)
  Recall (given partial cue y with some entries fixed, others = 0):
    y_new = tanh(W @ y / scale)
    iterate until convergence

References:
  - Hopfield JJ, Neural networks and physical systems with emergent
    collective computational abilities, PNAS 1982
  - Hopfield JJ, Neurons with graded response have collective
    computational properties like those of two-state neurons,
    PNAS 1984 (continuous variant)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class HopfieldConfig:
    n_features: int = 10
    n_iterations: int = 20
    scale: float = 1.0
    rng_seed: int = 0


def initialise(cfg: HopfieldConfig) -> dict:
    return {
        "W": np.zeros((cfg.n_features, cfg.n_features), dtype=np.float64),
        "n_stored": 0,
    }


def store(state: dict, pattern: np.ndarray) -> None:
    """Add pattern to attractor via Hebbian outer product."""
    state["W"] += np.outer(pattern, pattern)
    state["n_stored"] += 1


def store_patterns(state: dict, patterns: np.ndarray) -> None:
    """Bulk-add patterns (one per row)."""
    state["W"] += patterns.T @ patterns
    state["n_stored"] += patterns.shape[0]


def recall(state: dict, cue: np.ndarray, known_mask: np.ndarray, cfg: HopfieldConfig) -> np.ndarray:
    """Iterate dynamics from partial cue, return convergent pattern.

    cue: shape (n_features,), with values at known positions and 0 elsewhere.
    known_mask: bool array, True where cue value is given (fixed during iteration).
    """
    y = cue.copy()
    for _ in range(cfg.n_iterations):
        y_new = np.tanh(state["W"] @ y / cfg.scale)
        # Clamp known positions
        y_new[known_mask] = cue[known_mask]
        y = y_new
    return y

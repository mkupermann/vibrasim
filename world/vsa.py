"""EQMOD-2 — Vector-Symbolic / Hyperdimensional algebra on the substrate.

New mathematics built on the substrate's own ±1 vector codes, to get the one
thing memorization (n-gram / least-squares) cannot: COMPOSITIONAL GENERALIZATION.
NOT an LLM, NOT a transformer, no backprop, no pretraining — pure hypervector
algebra + the energy attractor as a clean-up memory.

Operations on ±1 hypervectors (dimension D, large for quasi-orthogonality):
- **bind(a,b) = a ⊙ b** (element-wise product). Stays ±1, is its own inverse
  (bind(bind(a,b),b)=a), and the result is dissimilar to both inputs — it ties a
  ROLE to a FILLER.
- **bundle([v…]) = sign(Σ v)** (superposition). Stays ±1, is SIMILAR to each input
  — it forms a set / a record of role-filler pairs.
- **sim(a,b)** = normalized agreement in [-1,1].
- **CleanupMemory** = the content-addressable energy attractor: map a noisy
  hypervector back to the nearest stored symbol (nearest codebook item).

Composition is ALGEBRAIC and SYSTEMATIC: a fact built by binding+bundling can be
queried by unbinding, and this works for ANY combination of known symbols —
including ones never stored as a whole. That is generalization, not lookup.
"""
from __future__ import annotations

import numpy as np


def rand_hv(D: int, rng) -> np.ndarray:
    return rng.choice([-1.0, 1.0], D)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def unbind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b              # product binding is its own inverse


def bundle(vecs) -> np.ndarray:
    s = np.sum(np.asarray(vecs), axis=0)
    out = np.sign(s)
    out[out == 0] = 1.0
    return out


def bundle_analog(vecs) -> np.ndarray:
    """ANALOG superposition: sum WITHOUT the sign() clamp. Keeps the graded
    magnitude a linear readout needs to unbind a slot and recover each filler's
    value (BET-126). Matches the substrate's tanh-graded activations; ±1 bundle was
    a discretization. Stays substrate-native — just addition, no new machinery."""
    return np.sum(np.asarray(vecs, dtype=np.float64), axis=0)


def sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / len(a))


class CleanupMemory:
    """The substrate's content-addressable attractor as a symbol clean-up."""
    def __init__(self):
        self.names = []
        self.M = None           # (n_items, D)

    def add(self, name: str, hv: np.ndarray):
        self.names.append(name)
        self.M = hv[None, :] if self.M is None else np.vstack([self.M, hv])

    def cleanup(self, x: np.ndarray):
        """Return (name, similarity) of the nearest stored symbol."""
        scores = self.M @ x / x.shape[0]
        i = int(np.argmax(scores))
        return self.names[i], float(scores[i])

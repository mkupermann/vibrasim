"""Hyperdimensional Computing (Kanerva 2009) — algebraic vector substrate.

Qualitatively different paradigm:
  - Each "concept" = fixed bipolar vector in {-1, +1}^D (D=10000 typical)
  - BIND: element-wise multiplication (creates association)
  - SUPERPOSE: element-wise sum (creates compositional bundle)
  - SIMILARITY: cosine
  - Memory: store superposition, retrieve by binding-unbinding

NOT statistical learning. NOT gradient-based. NOT pattern matching.
Algebraic operations in fixed high-dim space.

Pre-LLM (Kanerva 1988 SDM precursor, 2009 modern HDC).

For audio:
  Each feature dim gets a random bipolar BASIS VECTOR.
  Audio chunk encoded as superposition of (basis_i * weighted_by_feature_i)
  Optionally bind to "position" vector for sequence context.
  Store class-prototypes by averaging chunk-vectors.
  Classify via cosine to prototypes.

References:
  - Kanerva P, Hyperdimensional Computing: An Introduction to Computing
    in Distributed Representation with High-Dimensional Random Vectors,
    Cognitive Computation 2009
  - Kanerva P, Sparse Distributed Memory, MIT Press 1988 (precursor)
  - Plate TA, Holographic Reduced Representations, IEEE TNN 1995
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from world.flux.cognitive_map import encode_sensor


@dataclass
class HDCConfig:
    dimensionality: int = 10_000
    n_features: int = 10
    samples_per_tick: int = 16
    fft_bands: int = 8
    rng_seed: int = 0


def initialise(cfg: HDCConfig) -> dict:
    rng = np.random.default_rng(cfg.rng_seed)
    # Generate random bipolar basis vectors for each feature dimension
    basis = rng.choice([-1, 1], size=(cfg.n_features, cfg.dimensionality)).astype(np.int8)
    # Generate random bipolar level vectors for quantizing feature values
    # (encode continuous feature as one of N discrete levels via interpolation)
    n_levels = 10
    levels = np.zeros((cfg.n_features, n_levels, cfg.dimensionality), dtype=np.int8)
    for f in range(cfg.n_features):
        base = rng.choice([-1, 1], cfg.dimensionality)
        levels[f, 0] = base
        # Gradually flip bits to create level continuum
        for k in range(1, n_levels):
            mask = rng.uniform(0, 1, cfg.dimensionality) < (1.0 / n_levels)
            levels[f, k] = levels[f, k-1] * (1 - 2*mask.astype(np.int8))
    return {
        "cfg": cfg,
        "basis": basis, "levels": levels, "n_levels": n_levels,
        "memory": {},   # class → accumulated superposition vector
        "memory_counts": {},  # class → count of chunks
    }


def encode_chunk(state: dict, audio_chunk: np.ndarray, cfg: HDCConfig) -> np.ndarray:
    """Encode an audio chunk as a hyperdimensional vector via bind+superpose."""
    features = encode_sensor(audio_chunk, cfg)
    # For each feature, quantize value to a level, then bind with basis
    result = np.zeros(cfg.dimensionality, dtype=np.float64)
    for f in range(cfg.n_features):
        val = max(0.0, min(1.0, features[f] / 0.5))  # clip to [0,1]
        level_idx = int(val * (state["n_levels"] - 1))
        # Bind basis[f] with level[f, level_idx]
        bound = state["basis"][f] * state["levels"][f, level_idx]
        result += bound
    # Bipolarize: sign + 0-handling
    return np.sign(result).astype(np.int8)


def store(state: dict, audio_chunk: np.ndarray, class_label: int, cfg: HDCConfig) -> None:
    """Add chunk to class prototype via superposition."""
    vec = encode_chunk(state, audio_chunk, cfg).astype(np.float64)
    if class_label not in state["memory"]:
        state["memory"][class_label] = np.zeros(cfg.dimensionality, dtype=np.float64)
        state["memory_counts"][class_label] = 0
    state["memory"][class_label] += vec
    state["memory_counts"][class_label] += 1


def get_prototype(state: dict, class_label: int) -> np.ndarray:
    return np.sign(state["memory"][class_label]).astype(np.int8)


def classify(state: dict, audio_chunk: np.ndarray, cfg: HDCConfig) -> int:
    """Return class with highest cosine similarity to chunk's encoding."""
    vec = encode_chunk(state, audio_chunk, cfg).astype(np.float64)
    best_class, best_sim = -1, -2.0
    for c in state["memory"]:
        proto = get_prototype(state, c).astype(np.float64)
        sim = float(np.dot(vec, proto) / (np.linalg.norm(vec) * np.linalg.norm(proto) + 1e-12))
        if sim > best_sim:
            best_sim, best_class = sim, c
    return best_class

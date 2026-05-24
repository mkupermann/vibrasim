"""Adaptive Resonance Theory (Grossberg 1987) — self-allocating substrate.

Pre-LLM-era online learning system that ALLOCATES NEW CATEGORIES on
demand based on a "vigilance" threshold. The substrate decides when
input is unfamiliar enough to warrant a new category cell, vs when
input fits an existing category.

This is genuine "selbstständig" in a way that fixed-grid SOMs are not:
substrate determines its own capacity based on input diversity, not
externally-fixed grid_dims.

Mechanism (simplified ART2 for continuous inputs):
  For each input x:
    1. Compute match score s_i = ||x|| / ||x - w_i|| (resonance) for each
       existing cell i. (Higher = better match.)
    2. Find best match cell j = argmax s_i.
    3. If s_j >= vigilance: RESONANCE. Update w_j toward x (Hebbian).
       Else: VIGILANCE RESET. Allocate new cell with w = x.

Substrate self-grows: starts with 0 cells, ends with as many as needed.

References:
  - Grossberg S, Competitive learning: from interactive activation to
    adaptive resonance, Cognitive Science 1987
  - Carpenter G & Grossberg S, ART 2: self-organization of stable
    category recognition codes for analog input patterns,
    Applied Optics 1987
  - Carpenter G & Grossberg S, A massively parallel architecture for
    a self-organizing neural pattern recognition machine,
    Computer Vision Graphics and Image Processing 1987
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from world.flux.cognitive_map import encode_sensor


@dataclass
class ARTConfig:
    """All parameters locked pre-data per BET-046."""
    n_features: int = 10
    vigilance: float = 0.85   # similarity threshold for resonance
    learning_rate: float = 0.1
    max_cells: int = 500     # safety cap
    sample_rate_hz: int = 16000
    samples_per_tick: int = 16
    fft_bands: int = 8
    rng_seed: int = 0


def initialise(cfg: ARTConfig) -> dict:
    return {
        "weights": np.zeros((0, cfg.n_features), dtype=np.float64),
        "visit_count": np.zeros(0, dtype=np.int64),
        "n_resonances": 0,
        "n_allocations": 0,
        "tick": 0,
    }


def _cosine_match(weights: np.ndarray, sensor: np.ndarray) -> np.ndarray:
    """Per-cell cosine similarity (used as ART match score)."""
    if weights.shape[0] == 0:
        return np.zeros(0)
    sensor_norm = np.linalg.norm(sensor) + 1e-12
    w_norms = np.linalg.norm(weights, axis=1) + 1e-12
    return weights @ sensor / (w_norms * sensor_norm)


def step(state: dict, audio_chunk: np.ndarray, cfg: ARTConfig) -> None:
    if audio_chunk.size == 0:
        return
    sensor = encode_sensor(audio_chunk, cfg)
    if state["weights"].shape[0] == 0:
        # First input: allocate first cell
        state["weights"] = sensor.reshape(1, -1).copy()
        state["visit_count"] = np.array([1], dtype=np.int64)
        state["n_allocations"] += 1
    else:
        scores = _cosine_match(state["weights"], sensor)
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        if best_score >= cfg.vigilance:
            # Resonance — update existing cell
            state["weights"][best_idx] += cfg.learning_rate * (sensor - state["weights"][best_idx])
            state["visit_count"][best_idx] += 1
            state["n_resonances"] += 1
        elif state["weights"].shape[0] < cfg.max_cells:
            # Allocate new cell
            state["weights"] = np.vstack([state["weights"], sensor.reshape(1, -1)])
            state["visit_count"] = np.concatenate([state["visit_count"], [1]])
            state["n_allocations"] += 1
        # If at cap: hard-update best match anyway (don't drop input)
        else:
            state["weights"][best_idx] += cfg.learning_rate * (sensor - state["weights"][best_idx])
            state["visit_count"][best_idx] += 1
            state["n_resonances"] += 1
    state["tick"] += 1


def run(
    cfg: ARTConfig,
    n_ticks: int,
    audio_samples: np.ndarray | None,
    state: dict | None = None,
) -> dict:
    if state is None:
        state = initialise(cfg)
    if audio_samples is None:
        return state
    for tick in range(n_ticks):
        i0 = tick * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = audio_samples[i0:i1]
        if chunk.size == 0:
            continue
        step(state, chunk, cfg)
    return state


def classify(state: dict, sensor: np.ndarray, cfg: ARTConfig) -> int:
    """Return BMU index (closest cell by cosine match)."""
    if state["weights"].shape[0] == 0:
        return -1
    scores = _cosine_match(state["weights"], sensor)
    return int(np.argmax(scores))

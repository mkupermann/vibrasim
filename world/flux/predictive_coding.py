"""Predictive Coding (Rao & Ballard 1999) — hierarchical prediction-error substrate.

Pre-LLM era brain-inspired learning. Top-down predictions are compared
to bottom-up input; only prediction ERRORS propagate. The substrate
develops internal representations h that EXPLAIN incoming sensors via
a learned decoder D.

Simplified single-layer PC:
  Hidden state: h (n_hidden,)
  Decoder:      D (n_features, n_hidden)
  Prediction:   x_hat = D @ h
  Error:        e = x - x_hat
  h update:     h += eta_h * (D.T @ e - lambda_h * h)   (sparsity prior)
  D update:     D += eta_D * np.outer(e, h)             (Hebbian)

After training, h is the substrate's COMPRESSED INTERPRETATION of x.

References:
  - Rao RPN & Ballard DH, Predictive coding in the visual cortex: a
    functional interpretation of some extra-classical receptive-field
    effects, Nature Neuroscience 1999
  - Olshausen BA & Field DJ, Emergence of simple-cell receptive field
    properties by learning a sparse code for natural images, Nature 1996
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from world.flux.cognitive_map import encode_sensor


@dataclass
class PCConfig:
    n_features: int = 10
    n_hidden: int = 30
    eta_h: float = 0.05         # h-update rate (inference)
    eta_d: float = 0.001        # D-update rate (learning)
    lambda_h: float = 0.05      # sparsity coefficient
    n_inference_iter: int = 10  # h-inference iterations per input
    sample_rate_hz: int = 16000
    samples_per_tick: int = 16
    fft_bands: int = 8
    rng_seed: int = 0


def initialise(cfg: PCConfig) -> dict:
    rng = np.random.default_rng(cfg.rng_seed)
    D = rng.standard_normal((cfg.n_features, cfg.n_hidden)) * 0.1
    return {"D": D, "tick": 0, "h_last": np.zeros(cfg.n_hidden, dtype=np.float64)}


def _infer_h(D: np.ndarray, x: np.ndarray, cfg: PCConfig) -> np.ndarray:
    """Iteratively infer h that minimizes ||x - D h|| + lambda ||h||."""
    h = np.zeros(D.shape[1], dtype=np.float64)
    for _ in range(cfg.n_inference_iter):
        x_hat = D @ h
        e = x - x_hat
        # Gradient step with sparsity
        h += cfg.eta_h * (D.T @ e - cfg.lambda_h * h)
    return h


def step(state: dict, audio_chunk: np.ndarray, cfg: PCConfig) -> None:
    if audio_chunk.size == 0:
        return
    x = encode_sensor(audio_chunk, cfg)
    h = _infer_h(state["D"], x, cfg)
    # Decoder update: Hebbian on prediction-error * h
    x_hat = state["D"] @ h
    e = x - x_hat
    state["D"] += cfg.eta_d * np.outer(e, h)
    state["h_last"] = h
    state["tick"] += 1


def run(
    cfg: PCConfig,
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


def encode_to_h(state: dict, audio_chunk: np.ndarray, cfg: PCConfig) -> np.ndarray:
    """Encode an audio chunk to its h representation under current D."""
    x = encode_sensor(audio_chunk, cfg)
    return _infer_h(state["D"], x, cfg)

"""Echo State Network (Jaeger 2001) — temporal substrate.

Pre-LLM-era reservoir computing. Random sparse recurrent network with
fixed weights. Input drives state evolution; substrate ENCODES TEMPORAL
CONTEXT via the dynamics, not via static cell-routing.

Key difference from SOM/cog_map (BET-001..BET-029):
  Those substrates: each tick independent, BMU/hash routes to one cell.
                    Substrate state = static feature distribution.
  This substrate:   reservoir state u(t) depends on FULL HISTORY u(0..t-1).
                    Each new input perturbs the existing trajectory.
                    Substrate state = encoded temporal trajectory.

This addresses one of the limitations of SOM+replay (per BET-028 honest
AI-researcher review): no temporal structure. ESN has temporal structure
by construction.

Mechanism (Jaeger 2001):
  u(t+1) = (1-alpha) u(t) + alpha tanh(W_in x(t) + W_res u(t))
  - W_res random sparse, scaled to spectral radius < 1 (echo state property)
  - W_in random dense
  - alpha = leak rate (controls how fast state forgets)

No training of W_res, W_in. Only the readout layer (W_out, optional)
would be trained — for our substrate tests, we measure state u(T) directly.

References:
  - Jaeger H, The "echo state" approach to analysing and training
    recurrent neural networks, GMD Report 148, 2001
  - Maass W, Natschlager T, Markram H, Real-time computing without stable
    states: a new framework for neural computation based on perturbations,
    Neural Computation 2002 (Liquid State Machine, related)
  - Lukosevicius M, Jaeger H, Reservoir computing approaches to recurrent
    neural network training, Computer Science Review 2009 (textbook)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from world.flux.cognitive_map import encode_sensor


@dataclass
class ReservoirConfig:
    """All parameters locked pre-data per BET-030."""
    reservoir_size: int = 1000
    n_features: int = 10           # encoder output dim
    spectral_radius: float = 0.9   # echo-state property requires < 1
    density: float = 0.1           # sparse recurrent connectivity
    input_scale: float = 0.5
    leak_rate: float = 0.3
    sample_rate_hz: int = 16000
    samples_per_tick: int = 16
    fft_bands: int = 8
    rng_seed: int = 0


def initialise(cfg: ReservoirConfig) -> dict:
    rng = np.random.default_rng(cfg.rng_seed)
    # Sparse recurrent weight matrix
    W_res = rng.standard_normal((cfg.reservoir_size, cfg.reservoir_size))
    mask = rng.random((cfg.reservoir_size, cfg.reservoir_size)) < cfg.density
    W_res *= mask
    # Scale to target spectral radius
    eigenvalues = np.linalg.eigvals(W_res)
    current_radius = float(np.max(np.abs(eigenvalues)))
    if current_radius > 0:
        W_res *= cfg.spectral_radius / current_radius
    # Input weight matrix
    W_in = rng.standard_normal((cfg.reservoir_size, cfg.n_features)) * cfg.input_scale
    # Initial state
    u = np.zeros(cfg.reservoir_size, dtype=np.float64)
    return {
        "W_res": W_res, "W_in": W_in, "u": u,
        "tick": 0, "state_history_recent": None,
    }


def step(state: dict, audio_chunk: np.ndarray, tick: int, cfg: ReservoirConfig) -> None:
    if audio_chunk.size == 0:
        return
    x = encode_sensor(audio_chunk, cfg)
    u_old = state["u"]
    pre_act = state["W_in"] @ x + state["W_res"] @ u_old
    u_new = (1 - cfg.leak_rate) * u_old + cfg.leak_rate * np.tanh(pre_act)
    state["u"] = u_new
    state["tick"] += 1


def run(
    cfg: ReservoirConfig,
    n_ticks: int,
    audio_samples: np.ndarray | None,
    state: dict | None = None,
    return_state_history: bool = False,
) -> dict:
    if state is None:
        state = initialise(cfg)
    if audio_samples is None:
        return state
    history = None
    if return_state_history:
        history = np.zeros((n_ticks, cfg.reservoir_size), dtype=np.float64)
    for tick in range(n_ticks):
        i0 = tick * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = audio_samples[i0:i1]
        if chunk.size == 0:
            continue
        step(state, chunk, tick, cfg)
        if history is not None:
            history[tick] = state["u"]
    if history is not None:
        state["state_history_recent"] = history
    return state

"""Kuramoto-style coupled oscillator network — phase-based substrate.

Qualitatively different from all prior substrates:
  - Information encoded in PHASE relationships between oscillators
  - Computation via synchronization patterns
  - Audio drives oscillator frequencies (rate-coding through phase)
  - Coupling matrix evolves via Hebbian-like sync-based rule

Brain inspiration:
  - Buzsáki G, Rhythms of the Brain (OUP 2006): cortex computes
    via cross-frequency phase coupling
  - Singer W, Synchronization of cortical activity and its
    putative role in information processing and learning,
    Annu Rev Physiol 1993: binding-by-synchrony hypothesis
  - Strogatz SH, From Kuramoto to Crawford: exploring the onset
    of synchronization, Physica D 2000

Kuramoto model:
  dθ_i/dt = ω_i + (K/N) Σ_j W[i,j] sin(θ_j - θ_i)

Where:
  θ_i: phase of oscillator i
  ω_i: natural frequency (driven by audio in our case)
  W: coupling matrix (Hebbian-updated based on synchrony)
  K: global coupling strength
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class KuramotoConfig:
    n_oscillators: int = 100
    base_frequency_hz: float = 10.0  # baseline natural frequency
    frequency_spread_hz: float = 2.0  # heterogeneity
    coupling_K: float = 1.5
    audio_freq_modulation: float = 50.0  # how much audio shifts ω
    hebbian_rate: float = 0.001
    w_max: float = 1.0
    w_init: float = 0.01
    dt_ms: float = 10.0  # 100 Hz simulation step
    sample_rate_hz: int = 16000
    rng_seed: int = 0


def initialise(cfg: KuramotoConfig) -> dict:
    rng = np.random.default_rng(cfg.rng_seed)
    n = cfg.n_oscillators
    # Natural frequencies (heterogeneous to enable interesting sync patterns)
    omega = cfg.base_frequency_hz + rng.standard_normal(n) * cfg.frequency_spread_hz
    # Initial phases random
    theta = rng.uniform(0, 2 * np.pi, n)
    # Coupling matrix initially weak and uniform
    W = np.full((n, n), cfg.w_init, dtype=np.float64)
    np.fill_diagonal(W, 0)
    return {
        "cfg": cfg,
        "omega": omega,
        "theta": theta,
        "W": W,
        "global_time_ms": 0.0,
        "phase_history": [],  # accumulated phases for analysis
        "order_param_history": [],  # global sync order parameter R(t)
    }


def step(state: dict, audio_sample: float) -> None:
    cfg = state["cfg"]
    n = cfg.n_oscillators
    # Audio modulates frequencies — abs(audio) shifts oscillators by additional rate
    omega_effective = state["omega"] + abs(audio_sample) * cfg.audio_freq_modulation
    # Compute coupling input: K/N Σ W[i,j] sin(θ_j - θ_i)
    theta = state["theta"]
    phase_diff = theta[None, :] - theta[:, None]  # (n, n)
    coupling = (cfg.coupling_K / n) * (state["W"] * np.sin(phase_diff)).sum(axis=1)
    # Phase update (radians per step)
    dtheta_per_ms = 2 * np.pi * omega_effective / 1000.0 + coupling
    theta_new = (theta + dtheta_per_ms * cfg.dt_ms) % (2 * np.pi)
    state["theta"] = theta_new
    # Hebbian update: increase W[i,j] when oscillators i,j are in-phase
    # cosine of phase diff is in-phase indicator
    in_phase = np.cos(phase_diff)
    state["W"] += cfg.hebbian_rate * in_phase * cfg.dt_ms
    state["W"] = np.clip(state["W"], 0, cfg.w_max)
    np.fill_diagonal(state["W"], 0)
    # Global order parameter R = |mean(exp(iθ))|
    R = abs(np.mean(np.exp(1j * theta_new)))
    state["order_param_history"].append(float(R))
    state["global_time_ms"] += cfg.dt_ms


def run_audio(state: dict, audio: np.ndarray) -> dict:
    cfg = state["cfg"]
    decimation = int(cfg.sample_rate_hz * cfg.dt_ms / 1000)
    for i in range(0, audio.size, decimation):
        sample = float(audio[i])
        step(state, sample)
    return state


def measure_phase_distribution(state: dict, n_bins: int = 36) -> np.ndarray:
    """Histogram of current phases — how clustered is the population?"""
    hist, _ = np.histogram(state["theta"], bins=n_bins, range=(0, 2 * np.pi))
    return hist

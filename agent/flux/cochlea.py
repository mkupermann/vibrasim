"""Cochlea — F2 audio input adapter.

A fixed bank of `N_cochlea` second-order damped resonators, log-spaced from
`freq_min_hz` to `freq_max_hz`, that converts a mono audio waveform into
per-resonator instantaneous amplitudes. Each resonator obeys
`amp'' + (ω/Q) amp' + ω² amp = ω² x(t)` (driven harmonic oscillator), with
ω = 2π * freq_hz and dt = 1 / sample_rate_hz.

Discretisation is Crank-Nicolson (trapezoid) on the linear state-space form
[[0, 1], [-ω², -γ]]; unconditionally stable for any ω, dt, Q (γ = ω/Q).
Semi-implicit Euler was tried first per the plan but blows up at f=8 kHz
Q=10 sr=16 kHz where ω·dt ≈ 3.14 exceeds the symplectic-Euler stability
limit (≈ 2). The plan explicitly permits "trapezoid (semi-implicit Euler
also OK)".

Per spec §5.6 the cochlea is FIXED — its centre frequencies, Q, and floor
positions are locked at config time. No learning, no adaptation.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Resonator:
    """One second-order damped resonator. State: (amp, vel)."""

    freq_hz: float
    Q: float
    amp: float = 0.0
    vel: float = 0.0


def step_resonator(r: Resonator, drive: float, sr: int) -> float:
    """Advance one resonator by one audio sample. Returns the new amp.

    Crank-Nicolson on [amp, vel] driven by `drive` held constant over dt.
    """
    omega = 2.0 * np.pi * r.freq_hz
    gamma = omega / r.Q
    dt = 1.0 / sr
    a = 0.5 * dt * omega * omega          # dt/2 · ω²
    b = 0.5 * dt * gamma                  # dt/2 · γ
    half_dt = 0.5 * dt
    D = 1.0 + b + a * half_dt             # det of (I - dt/2·A)

    rhs1 = r.amp + half_dt * r.vel
    rhs2 = (1.0 - b) * r.vel - a * r.amp + 2.0 * a * drive

    amp_new = ((1.0 + b) * rhs1 + half_dt * rhs2) / D
    vel_new = (-a * rhs1 + rhs2) / D

    r.amp = amp_new
    r.vel = vel_new
    return r.amp


@dataclass
class CochleaConfig:
    """Locked cochlea geometry. Spec §5.6: the cochlea is FIXED."""

    n_resonators: int = 64
    freq_min_hz: float = 50.0
    freq_max_hz: float = 8000.0
    Q: float = 5.0
    sample_rate_hz: int = 16000
    n_audio_samples_per_tick: int = 16
    inject_gain: float = 1.0
    inject_max_per_tick: int = 8
    floor_disc_radius: float = 1.0


class Cochlea:
    """Log-spaced bank of resonators advanced by audio samples.

    State (amp, vel) is held in shape-(N,) float arrays so step_resonators
    can advance all N resonators per sample with vectorised numpy ops.

    Attributes:
        cfg: locked configuration.
        freqs_hz: shape (N,) log-spaced centre frequencies.
        amp, vel: shape (N,) state vectors.
        last_peaks: shape (N,) peak abs(amp) from the most recent
            step_resonators call. Used by cochlea_inject.
    """

    def __init__(self, cfg: CochleaConfig):
        self.cfg = cfg
        N = cfg.n_resonators
        self.freqs_hz = np.geomspace(
            cfg.freq_min_hz, cfg.freq_max_hz, num=N, dtype=np.float64
        )
        self.amp = np.zeros(N, dtype=np.float64)
        self.vel = np.zeros(N, dtype=np.float64)
        self.last_peaks = np.zeros(N, dtype=np.float64)
        sr = cfg.sample_rate_hz
        omega = 2.0 * np.pi * self.freqs_hz
        gamma = omega / cfg.Q
        dt = 1.0 / sr
        # Pre-compute Crank-Nicolson coefficients per resonator.
        self._half_dt = 0.5 * dt
        self._a = 0.5 * dt * omega * omega      # dt/2 · ω²
        self._b = 0.5 * dt * gamma              # dt/2 · γ
        self._D = 1.0 + self._b + self._a * self._half_dt
        self._one_plus_b_over_D = (1.0 + self._b) / self._D
        self._half_dt_over_D = self._half_dt / self._D
        self._neg_a_over_D = -self._a / self._D
        self._inv_D = 1.0 / self._D
        self._one_minus_b = 1.0 - self._b
        self._two_a = 2.0 * self._a


def step_resonators(bank: Cochlea, samples: np.ndarray) -> np.ndarray:
    """Advance every resonator in `bank` by the audio `samples` buffer.

    Returns shape (N,) per-resonator peak |amp| over the buffer.
    State (amp, vel) carries over between calls.
    """
    amp = bank.amp
    vel = bank.vel
    a = bank._a
    one_minus_b = bank._one_minus_b
    two_a = bank._two_a
    half_dt = bank._half_dt
    one_plus_b_over_D = bank._one_plus_b_over_D
    half_dt_over_D = bank._half_dt_over_D
    neg_a_over_D = bank._neg_a_over_D
    inv_D = bank._inv_D

    peaks = np.zeros_like(amp)

    for s in samples:
        rhs1 = amp + half_dt * vel
        rhs2 = one_minus_b * vel - a * amp + two_a * s
        amp_new = one_plus_b_over_D * rhs1 + half_dt_over_D * rhs2
        vel_new = neg_a_over_D * rhs1 + rhs2 * inv_D
        amp = amp_new
        vel = vel_new
        np.maximum(peaks, np.abs(amp), out=peaks)

    bank.amp = amp
    bank.vel = vel
    bank.last_peaks = peaks
    return peaks

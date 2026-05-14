"""Cochlea — F2 audio input adapter.

A fixed bank of `N_cochlea` second-order damped resonators, log-spaced from
`freq_min_hz` to `freq_max_hz`, that converts a mono audio waveform into
per-resonator instantaneous amplitudes. Each resonator obeys
`amp'' + (ω/Q) amp' + ω² amp = ω² x(t)` (driven harmonic oscillator), with
ω = 2π * freq_hz and dt = 1 / sample_rate_hz. Discretisation is semi-implicit
Euler: stable for Q≤~50 at 16 kHz.

Per spec §5.6 the cochlea is FIXED — its centre frequencies, Q, and floor
positions are locked at config time. No learning, no adaptation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Resonator:
    """One second-order damped resonator. State: (amp, vel)."""

    freq_hz: float
    Q: float
    amp: float = 0.0
    vel: float = 0.0


def step_resonator(r: Resonator, drive: float, sr: int) -> float:
    """Advance one resonator by one audio sample and return its amp.

    Semi-implicit Euler on the driven harmonic oscillator.
    """
    omega = 2.0 * np.pi * r.freq_hz
    dt = 1.0 / sr
    acc = omega * omega * (drive - r.amp) - (omega / r.Q) * r.vel
    r.vel += acc * dt
    r.amp += r.vel * dt
    return r.amp

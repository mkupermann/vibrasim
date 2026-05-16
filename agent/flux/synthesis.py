"""Synthesis — F2 audio output adapter.

Mirror of the cochlea bank used in reverse. Spec §5.7: the synthesis
bank IS the cochlea bank, just driven from the substrate side instead
of from the audio side.

Per spec §5.6 the resonator bank is FIXED — same log-spaced centre
frequencies, same Q. Plasticity does not touch the synthesis bank;
only bridges between nodes (F1b) are plastic.

Each tick the substrate emits "node firings" — proxied as positive
deltas in bridge flux above `firing_threshold` (spec §5.7). Each
firing routes to the resonator whose log(freq_hz) is closest to the
firing's frequency, driving an impulse on that resonator's velocity.
Output samples come from sample-wise sum of all resonator amps,
scaled by `output_gain`.

The discretisation is the same Crank-Nicolson scheme as the cochlea
(`agent/flux/cochlea.py`) — unconditionally stable, no NaN even at
high Q. See that file for the derivation.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SynthesisConfig:
    """Locked synthesis-bank geometry. Mirrors CochleaConfig by design."""

    n_resonators: int = 64
    freq_min_hz: float = 50.0
    freq_max_hz: float = 8000.0
    Q: float = 5.0
    sample_rate_hz: int = 16000
    n_audio_samples_per_tick: int = 16
    impulse_gain: float = 1.0
    output_gain: float = 1.0
    firing_threshold: float = 0.1


class Synthesizer:
    """Bank of impulse-driven resonators producing an output waveform.

    Same physics as Cochlea — second-order damped oscillator per resonator,
    Crank-Nicolson stepping. State (amp, vel) shared by both modes; only
    the drive source differs:
      cochlea: x(t) drives ω²·x term in the ODE
      synth:   firings inject directly into vel (delta-function in x)

    Attributes:
        cfg:        locked configuration.
        freqs_hz:   shape (N,) log-spaced centre frequencies.
        amp, vel:   shape (N,) state vectors.
    """

    def __init__(self, cfg: SynthesisConfig):
        self.cfg = cfg
        N = cfg.n_resonators
        self.freqs_hz = np.geomspace(
            cfg.freq_min_hz, cfg.freq_max_hz, num=N, dtype=np.float64
        )
        self.amp = np.zeros(N, dtype=np.float64)
        self.vel = np.zeros(N, dtype=np.float64)
        sr = cfg.sample_rate_hz
        omega = 2.0 * np.pi * self.freqs_hz
        gamma = omega / cfg.Q
        dt = 1.0 / sr
        self._half_dt = 0.5 * dt
        self._a = 0.5 * dt * omega * omega
        self._b = 0.5 * dt * gamma
        self._D = 1.0 + self._b + self._a * self._half_dt
        self._one_plus_b_over_D = (1.0 + self._b) / self._D
        self._half_dt_over_D = self._half_dt / self._D
        self._neg_a_over_D = -self._a / self._D
        self._inv_D = 1.0 / self._D
        self._one_minus_b = 1.0 - self._b
        # log(freq_hz) for log-nearest matching during firing routing.
        self._log_freqs = np.log(self.freqs_hz)


def drive_resonator_impulse(bank: Synthesizer, slot: int,
                             strength: float) -> None:
    """Impulse drive on one resonator: vel += strength * impulse_gain.

    A delta-function in x(t) integrated over dt is equivalent to a jump
    in vel proportional to strength (and ω², but we fold ω² into the
    caller's gain choice). Resonator then rings freely from the new vel.
    """
    bank.vel[slot] += strength * bank.cfg.impulse_gain


def read_output_samples(bank: Synthesizer, n_samples: int) -> np.ndarray:
    """Advance bank by n_samples with drive=0; return per-sample sum of amps.

    The output sample at audio index s is `output_gain * sum_i amp_i(s)`.
    State (amp, vel) carries over between calls — impulses injected before
    this call ring out across the n_samples window (and beyond).
    """
    amp = bank.amp
    vel = bank.vel
    a = bank._a
    one_minus_b = bank._one_minus_b
    half_dt = bank._half_dt
    one_plus_b_over_D = bank._one_plus_b_over_D
    half_dt_over_D = bank._half_dt_over_D
    neg_a_over_D = bank._neg_a_over_D
    inv_D = bank._inv_D
    out_gain = bank.cfg.output_gain

    out = np.empty(n_samples, dtype=np.float64)
    for s in range(n_samples):
        rhs1 = amp + half_dt * vel
        rhs2 = one_minus_b * vel - a * amp        # drive=0 → no 2a·x term
        amp_new = one_plus_b_over_D * rhs1 + half_dt_over_D * rhs2
        vel_new = neg_a_over_D * rhs1 + rhs2 * inv_D
        amp = amp_new
        vel = vel_new
        out[s] = out_gain * float(np.sum(amp))
    bank.amp = amp
    bank.vel = vel
    return out


def route_node_firings_explicit(bank: Synthesizer,
                                 firings) -> int:
    """Route an explicit list of (freq_log, strength) pairs into the bank.

    Each firing drives the resonator whose log(freq_hz) is closest to the
    firing's freq_log. Returns the number of firings routed.

    Used in tests and in Task 6 part (a) "cochlea-only" round-trip to
    isolate routing math from substrate dynamics.
    """
    log_freqs = bank._log_freqs
    n = 0
    for freq_log, strength in firings:
        slot = int(np.argmin(np.abs(log_freqs - float(freq_log))))
        drive_resonator_impulse(bank, slot, float(strength))
        n += 1
    return n


def route_node_firings(nodes, bridges,
                        prev_flux: np.ndarray,
                        current_flux: np.ndarray,
                        bank: Synthesizer,
                        cfg: SynthesisConfig) -> int:
    """Dynamics-coupled firing routing — Task 6 part (b) path.

    A "firing" is an alive bridge whose flux delta (current - prev)
    exceeds cfg.firing_threshold. The firing's frequency is the mean of
    its endpoints' node frequencies (log-Hz, matching spec §5.2). Its
    strength is the flux delta. Routes to the nearest log-Hz resonator.

    The cochlea-only round-trip (the pre-registered F2 acceptance test)
    uses route_node_firings_explicit, not this path. This routing is
    kept minimal — Task 6 part (b) explores it but is not the locked
    acceptance.

    Returns the number of firings routed.
    """
    threshold = cfg.firing_threshold
    n_br = bridges.max_bridges
    if prev_flux.shape[0] != n_br or current_flux.shape[0] != n_br:
        raise ValueError(
            "prev_flux/current_flux must be shape (max_bridges,)"
        )
    delta = current_flux.astype(np.float64) - prev_flux.astype(np.float64)
    alive = bridges.alive
    fire = alive & (delta > threshold)
    if not np.any(fire):
        return 0
    slots = np.where(fire)[0]
    n = 0
    for s in slots:
        src = int(bridges.src[s])
        dst = int(bridges.dst[s])
        if not (nodes.alive[src] and nodes.alive[dst]):
            continue
        freq_log = 0.5 * (float(nodes.freq[src]) + float(nodes.freq[dst]))
        strength = float(delta[s])
        slot_idx = int(np.argmin(np.abs(bank._log_freqs - freq_log)))
        drive_resonator_impulse(bank, slot_idx, strength)
        n += 1
    return n

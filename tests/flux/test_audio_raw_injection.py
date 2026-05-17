"""Tests for encoder-free audio injection — R-10.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-10``. Three acceptance
gates plus two ``position_hash`` determinism/coverage unit tests.

See ``docs/superpowers/plans/2026-05-17-flux-encoder-free-audio-detailed.md``
for the locked design decisions (energy = abs(sample), freq =
log(SR/2), one quantum per sample, no per-sample frequency jitter).
"""
from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import pearsonr

from agent.flux.audio_raw import (
    inject_raw_audio_chunk,
    inject_raw_audio_sample,
    position_hash,
)
from world.flux.dynamics import tick
from world.flux.grid import Grid
from world.flux.quantum import Quanta


SR = 16000


# ---------- position_hash unit tests --------------------------------


def test_position_hash_is_deterministic():
    p1 = position_hash(sample_index=12345, Lx=80, Ly=40, voxel_size=1.0)
    p2 = position_hash(sample_index=12345, Lx=80, Ly=40, voxel_size=1.0)
    assert p1 == p2, "position_hash must be deterministic for fixed args"


def test_position_hash_covers_floor_plane():
    """Many sample indices populate both x and y axes near both edges."""
    xs, ys = [], []
    for i in range(1000):
        x, y = position_hash(sample_index=i, Lx=80, Ly=40, voxel_size=1.0)
        xs.append(x)
        ys.append(y)
    xs_arr = np.asarray(xs)
    ys_arr = np.asarray(ys)
    assert xs_arr.min() < 5.0 and xs_arr.max() > 75.0, (
        f"x not covering floor: min={xs_arr.min():.3f} max={xs_arr.max():.3f}"
    )
    assert ys_arr.min() < 5.0 and ys_arr.max() > 35.0, (
        f"y not covering floor: min={ys_arr.min():.3f} max={ys_arr.max():.3f}"
    )


# ---------- R-10 acceptance: one quantum per sample -----------------


def test_raw_injection_one_quantum_per_sample():
    """0.1 s 1 kHz sine @ 16 kHz → exactly 1600 quanta, all freq=log(SR/2),
    energies tracking the rectified waveform."""
    n = SR // 10  # 0.1 s = 1600 samples
    t = np.arange(n) / SR
    waveform = np.sin(2 * np.pi * 1000.0 * t)
    grid = Grid(dims=(80, 40, 10), voxel_size=1.0)
    q = Quanta(max_quanta=10_000)
    rng = np.random.default_rng(0)
    injected = inject_raw_audio_chunk(
        q, grid, waveform, base_sample_index=0, sample_rate_hz=SR, rng=rng,
    )
    assert injected == 1600, (
        f"expected exactly 1600 quanta for 1600 samples, got {injected}"
    )
    alive = q.alive
    assert int(alive.sum()) == 1600
    # All quanta carry freq = log(SR/2) — no scatter.
    expected_freq = float(np.log(SR / 2.0))
    assert np.allclose(q.freq[alive], expected_freq), (
        "encoder-free quanta must all carry freq=log(SR/2) (no scatter)"
    )
    # Energies must equal the rectified waveform in injection order.
    energies = q.energy[alive]
    assert np.allclose(energies, np.abs(waveform), atol=1e-7), (
        "energies did not track the rectified waveform in injection order"
    )


# ---------- R-10 acceptance: silence injects zero energy ------------


def test_raw_injection_silence_injects_zero_energy():
    """0.1 s of silence still injects 1600 quanta; each carries energy ≈ 0.

    The injector does NOT skip silent samples — the one-quantum-per-sample
    invariant is exact. Silent quanta carry zero energy, which keeps the
    pulse-rate analysis in R-11 straightforward.
    """
    n = SR // 10
    silence = np.zeros(n, dtype=np.float64)
    grid = Grid(dims=(80, 40, 10), voxel_size=1.0)
    q = Quanta(max_quanta=10_000)
    rng = np.random.default_rng(0)
    injected = inject_raw_audio_chunk(
        q, grid, silence, base_sample_index=0, sample_rate_hz=SR, rng=rng,
    )
    assert injected == 1600
    alive = q.alive
    assert np.max(np.abs(q.energy[alive])) < 1e-12, (
        "silence must inject quanta with energy ≈ 0 within float epsilon"
    )


# ---------- R-10 acceptance: AM envelope visible in substrate -------


def test_raw_injection_amplitude_modulation_visible_in_substrate():
    """AM tone (1 kHz carrier, 10 Hz envelope) over 1 s → Pearson
    correlation between input envelope and substrate hot-floor energy
    density time-series ≥ 0.70.

    Setup: 16 audio samples per substrate tick (1 kHz tick rate at
    SR=16000); substrate dt=0.5 so the cochlea-style vel_z=1.0 drifts
    each quantum past the z<2 floor band in ~4 ticks, giving the floor
    energy a short integration window that tracks the 100-tick envelope
    cycle without lossy phase shift.
    """
    duration_s = 1.0
    n = int(SR * duration_s)
    t = np.arange(n) / SR
    carrier = np.sin(2 * np.pi * 1000.0 * t)
    envelope = 0.5 * (1.0 + np.cos(2 * np.pi * 10.0 * t))
    waveform = envelope * carrier

    grid = Grid(dims=(80, 40, 10), voxel_size=1.0)
    q = Quanta(max_quanta=500_000)
    rng = np.random.default_rng(0)

    chunk = 16
    dt = 0.5  # substrate tick: clears z<2 in ~4 ticks at vel_z=1
    energy_per_tick = []
    for tick_idx in range(n // chunk):
        s0 = tick_idx * chunk
        buf = waveform[s0:s0 + chunk]
        inject_raw_audio_chunk(
            q, grid, buf, base_sample_index=s0,
            sample_rate_hz=SR, rng=rng,
        )
        tick(q, grid, dt=dt, injector=None, rng=rng)
        floor_mask = q.alive & (q.pos[:, 2] < 2.0)
        energy_per_tick.append(float(q.energy[floor_mask].sum()))
    energy_per_tick = np.asarray(energy_per_tick)

    env_decimated = envelope[::chunk][:len(energy_per_tick)]
    r, _ = pearsonr(env_decimated, energy_per_tick)
    assert r >= 0.70, (
        f"AM envelope not visible in substrate: r={r:.3f}, expected ≥ 0.70"
    )


# ---------- R-10 extra: per-sample API sanity -----------------------


def test_inject_raw_audio_sample_returns_one_on_success_zero_on_full():
    grid = Grid(dims=(80, 40, 10), voxel_size=1.0)
    q = Quanta(max_quanta=2)
    rng = np.random.default_rng(0)
    assert inject_raw_audio_sample(q, grid, 0.5, 0, rng=rng) == 1
    assert inject_raw_audio_sample(q, grid, 0.5, 1, rng=rng) == 1
    # buffer now full
    assert inject_raw_audio_sample(q, grid, 0.5, 2, rng=rng) == 0

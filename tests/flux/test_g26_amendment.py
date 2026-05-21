"""R-22 unit tests for G26 — density-by-amplitude injection.

Acceptance per ``.eqmod/autopilot/QUEUE.yaml::R-22`` rows 1-4 and
``docs/amendments/G26-density-by-amplitude.md`` §3.

Mechanical tests on the density-count formula, energy conservation
across the per-sample burst, legacy path preservation, and env-var
routing. The 10k-tick substrate verification lives in
``test_g26_verification.py``.
"""
from __future__ import annotations

import os

import numpy as np
import pytest

from agent.flux.audio_raw import (
    DENSITY_K,
    DENSITY_N_MAX,
    density_count,
    inject_raw_audio_sample,
    position_hash,
)
from world.flux.grid import Grid
from world.flux.quantum import Quanta


# Locked legacy fixtures: numerical ``position_hash`` output for four
# (sample_index, Lx, Ly, voxel_size, seed) tuples, taken from the R-13
# / R-14 era (same hash function, unchanged since R-10). They pin the
# legacy path so the density-mode sibling cannot regress it.
_LEGACY_FIXTURES = [
    # (sample_index, Lx, Ly, voxel_size, seed, expected_x, expected_y)
    (12345, 30, 15, 1.0, 0,
     3.99239005520939827e+00, 9.95019581168889999e+00),
    (0, 30, 15, 1.0, 0,
     2.64993242430500686e+01, 7.21385271870531142e+00),
    (1, 30, 15, 1.0, 0,
     1.69968472514301538e+01, 8.02788444212637842e+00),
    (999999, 80, 40, 1.0, 0,
     3.56213346868753433e+01, 1.08743475098162889e+01),
]


# ---------- Test 1: density count proportional to amplitude ---------


def test_density_count_proportional_to_amplitude():
    """G26 §3 row 1: with DENSITY_K=4, DENSITY_N_MAX=4 the count formula
    must return n(0.0)=0, n(0.125)=1, n(0.4)=2, n(0.7)=3, n(1.0)=4.

    These five fixtures are LOCKED. The brief's pseudocode shows
    ``np.round`` which is banker's rounding; ``np.round(0.5)`` is 0,
    not 1. The acceptance fixtures use schoolbook rounding (always
    round half away from zero), so density_count uses
    ``floor(x + 0.5)`` to match the locked predictions.
    """
    assert DENSITY_K == 4, f"DENSITY_K must be 4 (locked), got {DENSITY_K}"
    assert DENSITY_N_MAX == 4, (
        f"DENSITY_N_MAX must be 4 (locked), got {DENSITY_N_MAX}"
    )
    cases = [
        (0.0, 0),
        (0.125, 1),
        (0.4, 2),
        (0.7, 3),
        (1.0, 4),
    ]
    for sample_value, expected_n in cases:
        n = density_count(sample_value)
        assert n == expected_n, (
            f"density_count({sample_value}) returned {n}, "
            f"expected {expected_n}"
        )
    # Symmetry: sign should not matter (the formula uses |sample_value|).
    for sample_value, expected_n in cases:
        n_neg = density_count(-sample_value)
        assert n_neg == expected_n, (
            f"density_count({-sample_value}) returned {n_neg}, "
            f"expected {expected_n} (formula uses |sample_value|)"
        )
    # Hard cap: pathological values above 1.0 still capped at N_MAX.
    assert density_count(10.0) == DENSITY_N_MAX
    assert density_count(-10.0) == DENSITY_N_MAX


# ---------- Test 2: energy conservation per sample ------------------


def test_density_preserves_total_energy_per_sample(monkeypatch):
    """G26 §3 row 2: per-sample energy budget unchanged from legacy.

    For ``sample_value=0.6``, ``density_count`` returns 2; density mode
    injects 2 quanta each with energy ``|0.6| / 2 = 0.3``; sum = 0.6
    = ``abs(sample_value)``. Verified across all n >= 1 in the
    amplitude domain.
    """
    monkeypatch.setenv("EQMOD_USE_DENSITY_BY_AMPLITUDE", "1")
    grid = Grid(dims=(30, 15, 8), voxel_size=1.0, T_smoothing=0.1)
    # Test the headline fixture first.
    quanta = Quanta(max_quanta=64)
    rng = np.random.default_rng(0)
    n = inject_raw_audio_sample(
        quanta, grid, sample_value=0.6, sample_index=42, rng=rng,
    )
    assert n == 2, (
        f"sample_value=0.6 should inject 2 quanta in density mode, got {n}"
    )
    energies = quanta.energy[quanta.alive]
    assert energies.shape == (2,), (
        f"expected exactly 2 alive quanta, got {len(energies)}"
    )
    assert np.allclose(energies, 0.3, atol=1e-12), (
        f"each density quantum at sample_value=0.6 should carry energy=0.3, "
        f"got {energies.tolist()}"
    )
    assert float(energies.sum()) == pytest.approx(0.6, abs=1e-12), (
        f"sum of density-burst energies must equal abs(sample_value)=0.6, "
        f"got sum={float(energies.sum())}"
    )

    # Sweep over the amplitude domain — T1 conservation across all n>=1.
    for sample_value in [0.125, 0.2, 0.4, 0.5, 0.7, 0.8, 1.0]:
        q = Quanta(max_quanta=64)
        rng = np.random.default_rng(1)
        n = inject_raw_audio_sample(
            q, grid, sample_value=sample_value, sample_index=7, rng=rng,
        )
        expected_n = density_count(sample_value)
        assert n == expected_n, (
            f"sample_value={sample_value}: injected {n}, "
            f"density_count says {expected_n}"
        )
        if expected_n >= 1:
            total = float(q.energy[q.alive].sum())
            assert total == pytest.approx(abs(sample_value), abs=1e-12), (
                f"sample_value={sample_value}: total density energy "
                f"{total} != abs(sample_value) {abs(sample_value)}"
            )
            per_q = q.energy[q.alive]
            assert np.allclose(per_q, abs(sample_value) / expected_n,
                               atol=1e-12), (
                f"per-quantum energy not uniform at sample_value={sample_value}: "
                f"got {per_q.tolist()}"
            )

    # n=0 case: silent sample injects nothing.
    q0 = Quanta(max_quanta=64)
    n0 = inject_raw_audio_sample(
        q0, grid, sample_value=0.0, sample_index=99,
        rng=np.random.default_rng(0),
    )
    assert n0 == 0 and q0.n_alive() == 0, (
        f"silent sample must inject 0 quanta in density mode, "
        f"got n={n0} n_alive={q0.n_alive()}"
    )


# ---------- Test 3: legacy injection bit-identical ------------------


def test_legacy_injection_unchanged(monkeypatch):
    """G26 §3 row 3: without env var, ``inject_raw_audio_sample`` keeps
    legacy semantics — one quantum at the legacy ``position_hash`` xy
    with ``energy = abs(sample_value)``. Pinned against four R-13/R-14
    -era ``position_hash`` fixtures.
    """
    # Verify env var off path uses legacy position_hash directly.
    monkeypatch.delenv("EQMOD_USE_DENSITY_BY_AMPLITUDE", raising=False)
    for (sample_index, Lx, Ly, voxel_size, seed,
         expected_x, expected_y) in _LEGACY_FIXTURES:
        x, y = position_hash(
            sample_index, Lx, Ly, voxel_size, seed=seed,
        )
        assert x == expected_x and y == expected_y, (
            f"legacy position_hash drift at sample_index={sample_index}, "
            f"Lx={Lx}, Ly={Ly}, voxel_size={voxel_size}, seed={seed}: "
            f"got ({x}, {y}), expected ({expected_x}, {expected_y})"
        )
    # Verify legacy injection path produces 1 quantum with energy =
    # abs(sample_value) at the deterministic xy.
    grid_30_15_8 = Grid(dims=(30, 15, 8), voxel_size=1.0, T_smoothing=0.1)
    quanta = Quanta(max_quanta=8)
    rng = np.random.default_rng(0)
    n = inject_raw_audio_sample(
        quanta, grid_30_15_8, sample_value=0.6, sample_index=12345,
        rng=rng, position_hash_seed=0,
    )
    assert n == 1, (
        f"legacy mode must inject exactly 1 quantum per sample; got {n}"
    )
    alive = quanta.alive
    assert int(alive.sum()) == 1
    assert quanta.energy[alive][0] == pytest.approx(0.6, abs=1e-12), (
        f"legacy energy must equal abs(sample_value)=0.6"
    )
    expected_xy = position_hash(12345, 30, 15, 1.0, seed=0)
    pos_xy = (float(quanta.pos[alive][0, 0]), float(quanta.pos[alive][0, 1]))
    assert pos_xy == expected_xy, (
        f"legacy xy must match position_hash: got {pos_xy}, "
        f"expected {expected_xy}"
    )

    # Confirm env var = "0" still routes legacy.
    monkeypatch.setenv("EQMOD_USE_DENSITY_BY_AMPLITUDE", "0")
    q2 = Quanta(max_quanta=8)
    n2 = inject_raw_audio_sample(
        q2, grid_30_15_8, sample_value=0.6, sample_index=12345,
        rng=np.random.default_rng(0), position_hash_seed=0,
    )
    assert n2 == 1, (
        f"env_var='0' must still take legacy path; got n={n2}"
    )


# ---------- Test 4: env var routes to density path ------------------


def test_env_var_routes_to_density_path(monkeypatch):
    """G26 §3 row 4: with EQMOD_USE_DENSITY_BY_AMPLITUDE=1,
    ``inject_raw_audio_sample`` calls the density helper. Verified via
    monkey-patched spy on the module-level reference.
    """
    import agent.flux.audio_raw as raw_mod

    density_calls = []

    real_density_fn = raw_mod.inject_raw_audio_sample_density

    def density_spy(quanta, grid, sample_value, sample_index, **kwargs):
        density_calls.append((sample_value, sample_index))
        return real_density_fn(
            quanta, grid, sample_value, sample_index, **kwargs,
        )

    monkeypatch.setattr(
        raw_mod, "inject_raw_audio_sample_density", density_spy,
    )

    grid = Grid(dims=(30, 15, 8), voxel_size=1.0, T_smoothing=0.1)
    quanta = Quanta(max_quanta=64)
    rng = np.random.default_rng(0)

    # No env var: density helper NOT called.
    monkeypatch.delenv("EQMOD_USE_DENSITY_BY_AMPLITUDE", raising=False)
    inject_raw_audio_sample(
        quanta, grid, sample_value=0.3, sample_index=42, rng=rng,
    )
    assert len(density_calls) == 0, (
        f"density helper called without env var: {density_calls}"
    )

    # Env var = "0": density helper NOT called.
    monkeypatch.setenv("EQMOD_USE_DENSITY_BY_AMPLITUDE", "0")
    inject_raw_audio_sample(
        quanta, grid, sample_value=0.3, sample_index=43, rng=rng,
    )
    assert len(density_calls) == 0, (
        f"density helper called with env var='0': {density_calls}"
    )

    # Env var = "1": density helper IS called.
    monkeypatch.setenv("EQMOD_USE_DENSITY_BY_AMPLITUDE", "1")
    inject_raw_audio_sample(
        quanta, grid, sample_value=0.3, sample_index=44, rng=rng,
    )
    assert len(density_calls) == 1, (
        f"density helper not called under env var: {density_calls}"
    )
    assert density_calls[0] == (0.3, 44), (
        f"density spy got wrong args: {density_calls[0]}"
    )

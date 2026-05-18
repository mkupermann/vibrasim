"""Pre-registered R-12 acceptance tests — activation field §5.8.

Brief: docs/superpowers/specs/2026-05-17-flux-spec-amendment-activation-field.md
Acceptance locked in .eqmod/autopilot/QUEUE.yaml at R-12. DO NOT retune.

Four tests:
- test_field_decays_exponentially: half-life ≈ 0.69 s within 1% tolerance
- test_field_responds_to_firings: steady-state magnitude tracks N*beta/alpha
- test_coincidence_zero_when_both_endpoints_silent: A=0 → coincidence=0
- test_coincidence_increases_with_paired_activity: monotone in paired A
"""
from __future__ import annotations

import numpy as np
import pytest

from world.flux.activation_field import (
    ActivationField,
    ActivationFieldConfig,
    read_coincidence,
    update_field,
)
from world.flux.grid import Grid
from world.flux.quantum import Quanta


# ----------------------------- helpers -------------------------------

def _make_grid(dims=(4, 4, 4), voxel_size=1.0) -> Grid:
    return Grid(dims=dims, voxel_size=voxel_size)


def _make_quanta_at(grid: Grid, voxel: tuple[int, int, int],
                     n: int, energy_each: float = 1.0) -> Quanta:
    """Spawn `n` alive quanta at the centre of `voxel`."""
    q = Quanta(max_quanta=max(n, 1))
    s = grid.voxel_size
    cx = (voxel[0] + 0.5) * s
    cy = (voxel[1] + 0.5) * s
    cz = (voxel[2] + 0.5) * s
    for _ in range(n):
        q.add(pos=(cx, cy, cz), vel=(0.0, 0.0, 0.0),
              freq=0.0, polarity=1, energy=energy_each)
    return q


def _make_empty_quanta(max_quanta: int = 1) -> Quanta:
    return Quanta(max_quanta=max_quanta)


# -------------------- 1) Exponential-decay test ----------------------

def test_field_decays_exponentially():
    """A single deposit decays to half its initial value at t = ln(2)/alpha.

    Pre-registered tolerance: 1% of initial value.

    Math: A[t+1] = A[t] * (1 - alpha*dt). After N ticks of duration dt,
    A[N] = A[0] * (1 - alpha*dt)^N. With dt small,
    (1 - alpha*dt)^(t/dt) -> exp(-alpha*t). At t = ln(2)/alpha the field
    is at 0.5 * A[0]; the discretisation error at dt=1e-3 s and alpha=1
    is about 0.3% of A[0].
    """
    cfg = ActivationFieldConfig(alpha=1.0, beta=1.0)
    grid = _make_grid()
    field = ActivationField(grid, cfg)

    # Deposit a one-shot value, then advance with no further input.
    voxel = (1, 1, 1)
    field.A[voxel] = 1.0
    A0 = float(field.A[voxel])

    dt = 0.001
    half_life_s = np.log(2.0) / cfg.alpha  # ≈ 0.693 s
    n_ticks = int(round(half_life_s / dt))

    empty_q = _make_empty_quanta()
    for _ in range(n_ticks):
        field.update(empty_q, dt)

    expected_half = 0.5 * A0
    actual = float(field.A[voxel])
    # 1% of initial value as locked tolerance.
    assert abs(actual - expected_half) <= 0.01 * A0, (
        f"after {n_ticks} ticks at dt={dt}s "
        f"(t = {n_ticks * dt:.3f} s ≈ ln(2)/alpha): "
        f"field at {voxel} = {actual:.6f}, expected ~ {expected_half:.6f} "
        f"within {0.01 * A0:.6f} (1% of A0={A0:.3f})."
    )


# -------------------- 2) Firings-track-N test ------------------------

def test_field_responds_to_firings():
    """Feed N alive quanta into a voxel; steady-state A → N*beta/alpha.

    With constant input deposit_rate = N (each quantum has energy 1.0),
    the rate-form update A[t+1] = A[t]*(1 - alpha*dt) + beta*N*dt
    converges to A_ss = beta * N / alpha. Pre-registered: assert the
    steady-state magnitude tracks N * beta / alpha within a numerical
    tolerance.
    """
    cfg = ActivationFieldConfig(alpha=1.0, beta=1.0)
    grid = _make_grid()
    field = ActivationField(grid, cfg)

    N = 7  # arbitrary; coverage of "tracks N" by varying N
    voxel = (2, 2, 2)
    q = _make_quanta_at(grid, voxel, n=N, energy_each=1.0)

    dt = 0.001
    # Drive to steady state: ~10 * (1/alpha) is plenty.
    t_drive_s = 10.0 / cfg.alpha
    n_ticks = int(round(t_drive_s / dt))
    for _ in range(n_ticks):
        field.update(q, dt)

    expected_ss = N * cfg.beta / cfg.alpha
    actual = float(field.A[voxel])
    # Discretisation overshoots/undershoots negligibly at dt=1e-3,
    # alpha=1, t=10 s: closer than 0.1% to N*beta/alpha. Lock at 1%
    # to match the decay-test tolerance class.
    assert abs(actual - expected_ss) <= 0.01 * expected_ss, (
        f"after {n_ticks} ticks of constant N={N} input: "
        f"steady-state A = {actual:.6f}, expected N*beta/alpha = "
        f"{expected_ss:.6f} within 1% ({0.01 * expected_ss:.6f})."
    )


# -------------- 3) Coincidence=0 when both endpoints silent ----------

def test_coincidence_zero_when_both_endpoints_silent():
    """A=0 at both endpoints → coincidence=0 exactly (modulo epsilon)."""
    cfg = ActivationFieldConfig(alpha=1.0, beta=1.0)
    grid = _make_grid()
    field = ActivationField(grid, cfg)

    # Both endpoints in voxels where A is identically zero.
    pos_i = np.array([0.5, 0.5, 0.5])
    pos_j = np.array([3.5, 3.5, 3.5])

    c = field.coincidence(pos_i, pos_j)
    assert c == 0.0, (
        f"coincidence with A=0 at both endpoints must be 0; got {c}"
    )

    # And via the functional read_coincidence helper.
    c_func = read_coincidence(field.A, grid.voxel_size,
                               pos_i, pos_j, A_norm=1.0)
    assert c_func == 0.0, (
        f"functional read_coincidence must also be 0; got {c_func}"
    )


# ----- 4) Coincidence increases with paired activity ----------------

def test_coincidence_increases_with_paired_activity():
    """Gradually raise A at both endpoints → coincidence rises monotonically."""
    cfg = ActivationFieldConfig(alpha=1.0, beta=1.0)
    grid = _make_grid()
    field = ActivationField(grid, cfg)

    # Fix A_norm so we test the numerator's monotonicity, not the rolling
    # normalization's. (A_norm is a slowly-updated constant in the live
    # tick path; for a unit test of coincidence behaviour we hold it
    # constant.)
    field.A_norm = 1.0

    voxel_i = (1, 1, 1)
    voxel_j = (3, 3, 3)
    pos_i = np.array([(voxel_i[0] + 0.5) * grid.voxel_size,
                       (voxel_i[1] + 0.5) * grid.voxel_size,
                       (voxel_i[2] + 0.5) * grid.voxel_size])
    pos_j = np.array([(voxel_j[0] + 0.5) * grid.voxel_size,
                       (voxel_j[1] + 0.5) * grid.voxel_size,
                       (voxel_j[2] + 0.5) * grid.voxel_size])

    levels = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]
    coincidences = []
    for L in levels:
        field.A[voxel_i] = L
        field.A[voxel_j] = L
        coincidences.append(field.coincidence(pos_i, pos_j))

    # Strict monotone increase from L=0 onwards (any pair with one zero
    # gives exactly 0; rising both gives sqrt(L*L)/1 = L).
    for prev, cur, L_prev, L_cur in zip(
        coincidences[:-1], coincidences[1:], levels[:-1], levels[1:]
    ):
        assert cur > prev, (
            f"coincidence not monotonic: at A={L_prev} got {prev}, "
            f"at A={L_cur} got {cur}"
        )

    # Specific value check: at A_i=A_j=L=1.0 and A_norm=1.0,
    # coincidence = sqrt(1*1) / (1 + eps) ≈ 1.0.
    field.A[voxel_i] = 1.0
    field.A[voxel_j] = 1.0
    c1 = field.coincidence(pos_i, pos_j)
    assert c1 == pytest.approx(1.0, abs=1e-6), (
        f"with A=1 at both endpoints and A_norm=1, coincidence "
        f"should be ~1.0; got {c1}"
    )


# -------------------- Bonus: update_field functional API ------------

def test_update_field_functional_api_matches_class():
    """update_field() and ActivationField.update() agree per tick."""
    cfg = ActivationFieldConfig(alpha=1.0, beta=1.0)
    grid = _make_grid()
    field = ActivationField(grid, cfg)

    voxel = (2, 2, 2)
    q = _make_quanta_at(grid, voxel, n=3)

    A_func = np.full(grid.dims, cfg.A_init, dtype=np.float64)
    dt = 0.01
    for _ in range(50):
        field.update(q, dt)
        update_field(A_func, q, grid, cfg, dt)

    assert np.allclose(field.A, A_func, atol=1e-12), (
        "class- and functional-API updates diverged"
    )

"""Registered P2 dynamics and complete accounted-energy ledger."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np
from numpy.typing import NDArray

from vibrasim2.p0.dynamics import periodic_laplacian
from vibrasim2.p0.fixtures import coupling_sites

from .bonds import (
    BondEvent,
    age_and_expire_bonds,
    bond_forces,
    bond_spring_energy,
    capture_positive_work,
    form_eligible_bonds,
)
from .types import P2Arm, P2Config, P2State


@dataclass(frozen=True)
class P2Forces:
    field: NDArray[np.float64]
    matter: NDArray[np.float64]


def initial_state(config: P2Config, source_centre: tuple[int, int]) -> P2State:
    """Create the registered unit-energy field pulse with empty matter state."""
    rows, columns = config.grid_shape
    x0, y0 = source_centre
    if not 0 <= x0 < rows or not 0 <= y0 < columns:
        raise ValueError("source centre must lie inside the grid")
    x_distance = np.abs(np.arange(rows, dtype=np.float64) - x0)
    y_distance = np.abs(np.arange(columns, dtype=np.float64) - y0)
    x_distance = np.minimum(x_distance, rows - x_distance)
    y_distance = np.minimum(y_distance, columns - y_distance)
    squared_distance = np.square(x_distance)[:, None] + np.square(y_distance)[None, :]
    u = np.exp(-squared_distance / (2.0 * config.sigma**2))
    u -= u.mean()
    sites = coupling_sites()
    gradient = 0.5 * config.c**2 * (
        np.square(np.roll(u, -1, axis=0) - u).sum()
        + np.square(np.roll(u, -1, axis=1) - u).sum()
    )
    coupling = 0.5 * config.g * np.square(u[sites[:, 0], sites[:, 1]]).sum()
    energy = float(gradient + coupling)
    if not math.isfinite(energy) or energy <= 0:
        raise ValueError("initial pulse must have positive finite energy")
    u *= math.sqrt(1.0 / energy)
    return P2State(
        u=u,
        p=np.zeros(config.grid_shape),
        q=np.zeros(len(sites)),
        r=np.zeros(len(sites)),
        reservoirs=np.zeros(len(sites)),
        bonds=(),
        formation_sink=0.0,
        bond_time=0.0,
    )


def coupling_matter_force(state: P2State, config: P2Config) -> NDArray[np.float64]:
    sites = coupling_sites()
    return config.g * (state.u[sites[:, 0], sites[:, 1]] - state.q)


def forces(state: P2State, arm: P2Arm, config: P2Config) -> P2Forces:
    """Evaluate field, reciprocal coupling, and live-bond forces."""
    sites = coupling_sites()
    mismatch = state.u[sites[:, 0], sites[:, 1]] - state.q
    field = config.c**2 * periodic_laplacian(state.u)
    np.add.at(field, (sites[:, 0], sites[:, 1]), -config.g * mismatch)
    matter = config.g * mismatch
    bond_field, bond_matter = bond_forces(state, arm, config)
    return P2Forces(field + bond_field, matter + bond_matter)


def _verlet(state: P2State, arm: P2Arm, config: P2Config, dt: float) -> P2State:
    initial_force = forces(state, arm, config)
    half_p = state.p + 0.5 * dt * initial_force.field
    half_r = state.r + 0.5 * dt * initial_force.matter
    positioned = replace(
        state,
        u=state.u + dt * half_p,
        p=half_p,
        q=state.q + dt * half_r,
        r=half_r,
    )
    final_force = forces(positioned, arm, config)
    return replace(
        positioned,
        p=half_p + 0.5 * dt * final_force.field,
        r=half_r + 0.5 * dt * final_force.matter,
    )


def registered_step(
    state: P2State, arm: P2Arm, config: P2Config, *, dt: float
) -> tuple[P2State, tuple[BondEvent, ...]]:
    """Apply the exact frozen P2 operator ordering for one interval."""
    stepped = _verlet(state, arm, config, dt)
    fraction = 0.0 if arm is P2Arm.NO_CAPTURE else config.capture_fraction
    stepped, _ = capture_positive_work(
        stepped,
        coupling_matter_force(stepped, config),
        dt=dt,
        fraction=fraction,
    )
    stepped, expired = age_and_expire_bonds(stepped, config, dt=dt, arm=arm)
    stepped, formed = form_eligible_bonds(stepped, config)
    return stepped, expired + formed


def accounted_energy(state: P2State, arm: P2Arm, config: P2Config) -> float:
    """Return mechanical, stored, and irreversibly consumed formation energy."""
    sites = coupling_sites()
    with np.errstate(over="ignore", invalid="ignore"):
        field = 0.5 * np.square(state.p).sum() + 0.5 * config.c**2 * (
            np.square(np.roll(state.u, -1, axis=0) - state.u).sum()
            + np.square(np.roll(state.u, -1, axis=1) - state.u).sum()
        )
        matter = 0.5 * np.square(state.r).sum()
        mismatch = state.u[sites[:, 0], sites[:, 1]] - state.q
        coupling = 0.5 * config.g * np.square(mismatch).sum()
    live_bonds = sum(bond_spring_energy(state, bond, config, arm) for bond in state.bonds)
    return float(
        field
        + matter
        + coupling
        + live_bonds
        + state.reservoirs.sum()
        + state.formation_sink
    )

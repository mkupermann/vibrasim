"""Hamiltonian forces and velocity-Verlet integration for registered P0 cells."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .fixtures import coupling_sites, edges_for
from .types import ChannelMode, P0Config, P0State, RunCell


def periodic_laplacian(u: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return the nearest-neighbour Laplacian on a periodic square lattice."""

    return (
        np.roll(u, 1, axis=0)
        + np.roll(u, -1, axis=0)
        + np.roll(u, 1, axis=1)
        + np.roll(u, -1, axis=1)
        - 4.0 * u
    )


@dataclass(frozen=True)
class Forces:
    field: NDArray[np.float64]
    matter: NDArray[np.float64]


def forces(state: P0State, cell: RunCell, config: P0Config) -> Forces:
    """Evaluate the exact registered force terms for one P0 arm."""

    sites = coupling_sites()
    if state.u.shape != config.grid_shape or state.p.shape != config.grid_shape:
        raise ValueError("field state shape does not match P0 configuration")
    if state.q.shape != (len(sites),) or state.r.shape != (len(sites),):
        raise ValueError("matter state shape does not match registered coupling sites")

    field = config.c**2 * periodic_laplacian(state.u)
    matter = np.zeros(len(sites), dtype=np.float64)

    if cell.mode is not ChannelMode.NO_BONDS:
        for left, right in edges_for(cell.topology):
            delta = state.q[left] - state.q[right]
            matter[left] -= config.k_b * delta
            matter[right] += config.k_b * delta

    coupling_g = 0.0 if cell.mode is ChannelMode.DECOUPLED else config.g
    mismatch = state.u[sites[:, 0], sites[:, 1]] - state.q
    matter += coupling_g * mismatch
    if cell.mode is not ChannelMode.BROKEN_PAIR:
        np.add.at(field, (sites[:, 0], sites[:, 1]), -coupling_g * mismatch)

    return Forces(field=field, matter=matter)


def velocity_verlet_step(state: P0State, cell: RunCell, config: P0Config) -> P0State:
    """Advance one immutable state by one velocity-Verlet step."""

    initial_force = forces(state, cell, config)
    half_p = state.p + 0.5 * cell.dt * initial_force.field
    half_r = state.r + 0.5 * cell.dt * initial_force.matter
    next_u = state.u + cell.dt * half_p
    next_q = state.q + cell.dt * half_r

    position_state = P0State(next_u, half_p, next_q, half_r)
    final_force = forces(position_state, cell, config)
    next_p = half_p + 0.5 * cell.dt * final_force.field
    next_r = half_r + 0.5 * cell.dt * final_force.matter
    return P0State(next_u, next_p, next_q, next_r)

"""Deterministic registered fixtures and initial conditions for P0."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from .types import ChannelMode, P0Config, P0State, RunCell, RunPurpose, Topology


_COUPLING_SITES = (
    (13, 16),
    (14, 13),
    (18, 13),
    (19, 16),
    (18, 19),
    (14, 19),
)
_EDGES = {
    Topology.CYCLE: ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)),
    Topology.BRANCH: ((0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5)),
}


def _readonly_int_array(values: tuple[tuple[int, int], ...]) -> NDArray[np.int64]:
    result = np.asarray(values, dtype=np.int64)
    result.setflags(write=False)
    return result


def coupling_sites() -> NDArray[np.int64]:
    return _readonly_int_array(_COUPLING_SITES)


def edges_for(topology: Topology) -> NDArray[np.int64]:
    try:
        values = _EDGES[topology]
    except KeyError as exc:
        raise ValueError(f"unsupported P0 topology: {topology!r}") from exc
    return _readonly_int_array(values)


def initial_state(config: P0Config, source_centre: tuple[int, int]) -> P0State:
    nx, ny = config.grid_shape
    x0, y0 = source_centre
    if nx <= 0 or ny <= 0 or not (0 <= x0 < nx and 0 <= y0 < ny):
        raise ValueError("source centre must lie inside a non-empty periodic grid")
    sites = coupling_sites()
    if np.any(sites[:, 0] >= nx) or np.any(sites[:, 1] >= ny):
        raise ValueError("registered coupling sites must lie inside the configured grid")
    if config.sigma <= 0:
        raise ValueError("sigma must be positive")

    x_distance = np.abs(np.arange(nx, dtype=np.float64) - x0)
    y_distance = np.abs(np.arange(ny, dtype=np.float64) - y0)
    x_distance = np.minimum(x_distance, nx - x_distance)
    y_distance = np.minimum(y_distance, ny - y_distance)
    distance_squared = np.square(x_distance)[:, None] + np.square(y_distance)[None, :]
    unscaled = np.exp(-distance_squared / (2.0 * config.sigma**2))
    unscaled -= unscaled.mean()

    gradient_energy = 0.5 * config.c**2 * (
        np.square(np.roll(unscaled, -1, axis=0) - unscaled).sum()
        + np.square(np.roll(unscaled, -1, axis=1) - unscaled).sum()
    )
    coupling_energy = 0.5 * config.g * np.square(unscaled[sites[:, 0], sites[:, 1]]).sum()
    unscaled_total_energy = float(gradient_energy + coupling_energy)
    if not math.isfinite(unscaled_total_energy) or unscaled_total_energy <= 0:
        raise ValueError("initial field must have positive finite total energy")

    u = unscaled * math.sqrt(1.0 / unscaled_total_energy)
    return P0State(
        u=u,
        p=np.zeros(config.grid_shape, dtype=np.float64),
        q=np.zeros(len(_COUPLING_SITES), dtype=np.float64),
        r=np.zeros(len(_COUPLING_SITES), dtype=np.float64),
    )


def registered_stage_a_cells(config: P0Config) -> tuple[RunCell, ...]:
    cells: list[RunCell] = []
    for source in config.source_centres:
        cells.extend(
            (
                RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.PRIMARY, source, config.dt, config.steps),
                RunCell(Topology.BRANCH, ChannelMode.FULL, RunPurpose.PRIMARY, source, config.dt, config.steps),
                RunCell(Topology.CYCLE, ChannelMode.NO_BONDS, RunPurpose.PRIMARY, source, config.dt, config.steps),
                RunCell(Topology.CYCLE, ChannelMode.DECOUPLED, RunPurpose.PRIMARY, source, config.dt, config.steps),
                RunCell(Topology.CYCLE, ChannelMode.BROKEN_PAIR, RunPurpose.SENSITIVITY, source, config.dt, config.steps),
                RunCell(Topology.BRANCH, ChannelMode.BROKEN_PAIR, RunPurpose.SENSITIVITY, source, config.dt, config.steps),
                RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.CONVERGENCE, source, config.dt / 2.0, config.steps * 2),
                RunCell(Topology.BRANCH, ChannelMode.FULL, RunPurpose.CONVERGENCE, source, config.dt / 2.0, config.steps * 2),
            )
        )
    return tuple(cells)


def reproduction_cells(config: P0Config) -> tuple[RunCell, ...]:
    return tuple(
        RunCell(topology, ChannelMode.FULL, RunPurpose.REPRODUCTION, source, config.dt, config.steps)
        for source in config.source_centres
        for topology in (Topology.CYCLE, Topology.BRANCH)
    )


def omega_upper(config: P0Config, topology: Topology) -> float:
    edges = edges_for(topology)
    degrees = np.bincount(edges.ravel(), minlength=len(_COUPLING_SITES))
    maximum_degree = int(degrees.max())
    return math.sqrt(8.0 * config.c**2 + 2.0 * config.g + 2.0 * config.k_b * maximum_degree)

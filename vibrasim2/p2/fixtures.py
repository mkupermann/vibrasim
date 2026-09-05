"""Geometry-derived candidate pairs for V2-P2."""

from __future__ import annotations

import math

from vibrasim2.p0.fixtures import coupling_sites

from .types import P2Arm, P2Cell, P2Config, P2Purpose


def candidate_edges(config: P2Config) -> tuple[tuple[int, int], ...]:
    """Return local pairs from radius alone, in deterministic order."""
    sites = coupling_sites()
    rows, columns = config.grid_shape
    result: list[tuple[int, int]] = []
    for left in range(len(sites)):
        for right in range(left + 1, len(sites)):
            dx = abs(int(sites[left, 0]) - int(sites[right, 0]))
            dy = abs(int(sites[left, 1]) - int(sites[right, 1]))
            dx = min(dx, rows - dx)
            dy = min(dy, columns - dy)
            if math.hypot(dx, dy) <= config.candidate_radius:
                result.append((left, right))
    return tuple(result)


def registered_cells(config: P2Config) -> tuple[P2Cell, ...]:
    """Return the exact frozen 18-cell matrix in execution order."""
    cells: list[P2Cell] = []
    for source in config.source_centres:
        cells.extend(
            (
                P2Cell(P2Arm.FULL, P2Purpose.PRIMARY, source, config.dt, config.steps),
                P2Cell(P2Arm.NO_CAPTURE, P2Purpose.PRIMARY, source, config.dt, config.steps),
                P2Cell(P2Arm.NO_FIELD_FEEDBACK, P2Purpose.PRIMARY, source, config.dt, config.steps),
                P2Cell(P2Arm.FULL, P2Purpose.CONVERGENCE, source, config.dt / 2, config.steps * 2),
                P2Cell(P2Arm.NO_FIELD_FEEDBACK, P2Purpose.CONVERGENCE, source, config.dt / 2, config.steps * 2),
                P2Cell(P2Arm.FULL, P2Purpose.REPRODUCTION, source, config.dt, config.steps),
            )
        )
    return tuple(cells)


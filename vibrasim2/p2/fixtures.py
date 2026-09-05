"""Geometry-derived candidate pairs for V2-P2."""

from __future__ import annotations

import math

from vibrasim2.p0.fixtures import coupling_sites

from .types import P2Config


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


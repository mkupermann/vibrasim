from __future__ import annotations
import numpy as np
from numba import njit


@njit(cache=True)
def periodic_distance_sq(a: np.ndarray, b: np.ndarray, box: np.ndarray) -> float:
    d2 = 0.0
    for i in range(3):
        dx = a[i] - b[i]
        b_i = box[i]
        if dx > b_i * 0.5:
            dx -= b_i
        elif dx < -b_i * 0.5:
            dx += b_i
        d2 += dx * dx
    return d2


@njit(cache=True)
def periodic_midpoint(a: np.ndarray, b: np.ndarray, box: np.ndarray) -> np.ndarray:
    out = np.empty(3, dtype=np.float64)
    for d in range(3):
        delta = b[d] - a[d]
        if delta > box[d] * 0.5:
            delta -= box[d]
        elif delta < -box[d] * 0.5:
            delta += box[d]
        m = a[d] + delta * 0.5
        m = m % box[d]
        out[d] = m
    return out


def build_grid(
    positions: np.ndarray,
    alive: np.ndarray,
    box: np.ndarray,
    cell_size: float,
) -> dict[tuple[int, int, int], list[int]]:
    grid: dict[tuple[int, int, int], list[int]] = {}
    nx = int(np.ceil(box[0] / cell_size))
    ny = int(np.ceil(box[1] / cell_size))
    nz = int(np.ceil(box[2] / cell_size))
    for i in range(positions.shape[0]):
        if not alive[i]:
            continue
        cx = int(positions[i, 0] // cell_size) % nx
        cy = int(positions[i, 1] // cell_size) % ny
        cz = int(positions[i, 2] // cell_size) % nz
        key = (cx, cy, cz)
        if key not in grid:
            grid[key] = []
        grid[key].append(i)
    return grid


def neighbors_of(
    grid: dict[tuple[int, int, int], list[int]],
    pos: np.ndarray,
    box: np.ndarray,
    cell_size: float,
    *,
    exclude_self: bool,
    query_index: int,
) -> list[int]:
    """Iterate the 27-cell (3³) periodic neighbourhood."""
    nx = int(np.ceil(box[0] / cell_size))
    ny = int(np.ceil(box[1] / cell_size))
    nz = int(np.ceil(box[2] / cell_size))
    cx = int(pos[0] // cell_size) % nx
    cy = int(pos[1] // cell_size) % ny
    cz = int(pos[2] // cell_size) % nz
    out: list[int] = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                key = ((cx + dx) % nx, (cy + dy) % ny, (cz + dz) % nz)
                bucket = grid.get(key)
                if bucket is None:
                    continue
                for idx in bucket:
                    if exclude_self and idx == query_index:
                        continue
                    out.append(idx)
    return out

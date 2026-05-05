from __future__ import annotations
import numpy as np
from numba import njit


@njit(cache=True)
def periodic_distance_sq(a: np.ndarray, b: np.ndarray, box: np.ndarray) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    bx = box[0]
    by = box[1]
    if dx > bx * 0.5:
        dx -= bx
    elif dx < -bx * 0.5:
        dx += bx
    if dy > by * 0.5:
        dy -= by
    elif dy < -by * 0.5:
        dy += by
    return dx * dx + dy * dy


@njit(cache=True)
def periodic_midpoint(a: np.ndarray, b: np.ndarray, box: np.ndarray) -> np.ndarray:
    """Midpoint under minimum-image convention. Wraps result into the box."""
    out = np.empty(2, dtype=np.float64)
    for d in range(2):
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
) -> dict[tuple[int, int], list[int]]:
    """Bucket alive points into a grid keyed by (cell_x, cell_y).

    Cell size should equal the maximum query radius.
    """
    grid: dict[tuple[int, int], list[int]] = {}
    nx = int(np.ceil(box[0] / cell_size))
    ny = int(np.ceil(box[1] / cell_size))
    for i in range(positions.shape[0]):
        if not alive[i]:
            continue
        cx = int(positions[i, 0] // cell_size) % nx
        cy = int(positions[i, 1] // cell_size) % ny
        key = (cx, cy)
        if key not in grid:
            grid[key] = []
        grid[key].append(i)
    return grid


def neighbors_of(
    grid: dict[tuple[int, int], list[int]],
    pos: np.ndarray,
    box: np.ndarray,
    cell_size: float,
    *,
    exclude_self: bool,
    query_index: int,
) -> list[int]:
    """Return indices in the 9-cell (3x3) periodic neighborhood of `pos`."""
    nx = int(np.ceil(box[0] / cell_size))
    ny = int(np.ceil(box[1] / cell_size))
    cx = int(pos[0] // cell_size) % nx
    cy = int(pos[1] // cell_size) % ny
    out: list[int] = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            key = ((cx + dx) % nx, (cy + dy) % ny)
            bucket = grid.get(key)
            if bucket is None:
                continue
            for idx in bucket:
                if exclude_self and idx == query_index:
                    continue
                out.append(idx)
    return out

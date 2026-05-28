from __future__ import annotations
import numpy as np

try:
    from numba import njit
except ImportError:
    def njit(*args, **kwargs):
        def wrapper(f): return f
        return wrapper if not args or not callable(args[0]) else args[0]


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


# ============================================================
# Fast spatial grid — Numba JIT with flat arrays
# ============================================================

@njit(cache=True)
def _build_grid_jit(positions, alive, box, cell_size, n):
    """Build cell-list grid as flat arrays.

    Returns (cell_starts, cell_counts, sorted_indices, nx, ny, nz).
    cell_starts[c] = offset into sorted_indices where cell c begins.
    cell_counts[c] = number of particles in cell c.
    """
    nx = max(1, int(np.ceil(box[0] / cell_size)))
    ny = max(1, int(np.ceil(box[1] / cell_size)))
    nz = max(1, int(np.ceil(box[2] / cell_size)))
    n_cells = nx * ny * nz

    # Count particles per cell
    cell_counts = np.zeros(n_cells, dtype=np.int32)
    cell_ids = np.empty(n, dtype=np.int32)
    for i in range(n):
        if not alive[i]:
            cell_ids[i] = -1
            continue
        cx = int(positions[i, 0] // cell_size) % nx
        cy = int(positions[i, 1] // cell_size) % ny
        cz = int(positions[i, 2] // cell_size) % nz
        c = cx * ny * nz + cy * nz + cz
        cell_ids[i] = c
        cell_counts[c] += 1

    # Prefix sum for cell starts
    cell_starts = np.zeros(n_cells + 1, dtype=np.int32)
    for c in range(n_cells):
        cell_starts[c + 1] = cell_starts[c] + cell_counts[c]

    # Fill sorted indices
    total = cell_starts[n_cells]
    sorted_indices = np.empty(total, dtype=np.int32)
    fill = np.zeros(n_cells, dtype=np.int32)
    for i in range(n):
        c = cell_ids[i]
        if c < 0:
            continue
        offset = cell_starts[c] + fill[c]
        sorted_indices[offset] = i
        fill[c] += 1

    return cell_starts, cell_counts, sorted_indices, nx, ny, nz


@njit(cache=True)
def _find_pairs_jit(positions, alive, freq, pol, level, box, cell_size,
                    cell_starts, cell_counts, sorted_indices, nx, ny, nz,
                    r_sq, fmin_ratio, fmax_ratio,
                    upgrade_arr, fusion_arr, fusion_enabled,
                    max_pairs):
    """Find all binding-eligible node pairs. Returns (out_i, out_j, out_target, n_found)."""
    out_i = np.empty(max_pairs, dtype=np.int32)
    out_j = np.empty(max_pairs, dtype=np.int32)
    out_target = np.empty(max_pairs, dtype=np.int8)
    n_found = 0
    n = positions.shape[0]
    n_cells = nx * ny * nz
    locked = np.zeros(n, dtype=np.bool_)

    for ci in range(n_cells):
        start_i = cell_starts[ci]
        count_i = cell_counts[ci]
        if count_i == 0:
            continue

        # Decode cell coordinates
        cxi = ci // (ny * nz)
        cyi = (ci // nz) % ny
        czi = ci % nz

        # 27 neighbors
        for dxx in range(-1, 2):
            for dyy in range(-1, 2):
                for dzz in range(-1, 2):
                    ncx = (cxi + dxx) % nx
                    ncy = (cyi + dyy) % ny
                    ncz = (czi + dzz) % nz
                    cj = ncx * ny * nz + ncy * nz + ncz
                    start_j = cell_starts[cj]
                    count_j = cell_counts[cj]
                    if count_j == 0:
                        continue

                    for ii in range(count_i):
                        i = sorted_indices[start_i + ii]
                        if not alive[i] or locked[i]:
                            continue
                        for jj in range(count_j):
                            j = sorted_indices[start_j + jj]
                            if j <= i:
                                continue
                            if not alive[j] or locked[j]:
                                continue
                            # Polarity check
                            if pol[i] == pol[j]:
                                continue
                            # Level / upgrade check
                            li = level[i]
                            lj = level[j]
                            tgt = int(upgrade_arr[li, lj])
                            if tgt < 0 and fusion_enabled:
                                tgt = int(fusion_arr[li, lj])
                            if tgt < 0:
                                continue
                            # Distance check
                            d2 = 0.0
                            for d in range(3):
                                dx = positions[i, d] - positions[j, d]
                                b = box[d]
                                if dx > b * 0.5:
                                    dx -= b
                                elif dx < -b * 0.5:
                                    dx += b
                                d2 += dx * dx
                            if d2 >= r_sq:
                                continue
                            # Frequency checks only for sub-atom (both < 4)
                            li = level[i]
                            lj = level[j]
                            if li < 4 or lj < 4:
                                fi = freq[i]
                                fj = freq[j]
                                dec_i = 0
                                tmp = fi
                                while tmp >= 10.0:
                                    tmp /= 10.0
                                    dec_i += 1
                                dec_j = 0
                                tmp = fj
                                while tmp >= 10.0:
                                    tmp /= 10.0
                                    dec_j += 1
                                if dec_i != dec_j:
                                    continue
                                fmin = fi if fi < fj else fj
                                fmax = fi if fi > fj else fj
                                ratio = (fmax - fmin) / fmin
                                if ratio < fmin_ratio or ratio > fmax_ratio:
                                    continue
                            # Match!
                            if n_found < max_pairs:
                                out_i[n_found] = i
                                out_j[n_found] = j
                                out_target[n_found] = tgt
                                n_found += 1
                                locked[i] = True
                                locked[j] = True
                                break  # next i
                        if locked[i]:
                            break  # next neighbor cell for this i

    return out_i[:n_found], out_j[:n_found], out_target[:n_found], n_found


@njit(cache=True)
def _apply_resonance_jit(positions, alive, freq, level, box, cell_size,
                         cell_starts, cell_counts, sorted_indices, nx, ny, nz,
                         r_sq, coupling, dt, n):
    """Kuramoto resonance: pull frequencies of nearby nodes toward each other."""
    delta_freq = np.zeros(n, dtype=np.float64)
    n_cells = nx * ny * nz

    for ci in range(n_cells):
        start_i = cell_starts[ci]
        count_i = cell_counts[ci]
        if count_i == 0:
            continue
        cxi = ci // (ny * nz)
        cyi = (ci // nz) % ny
        czi = ci % nz

        for dxx in range(-1, 2):
            for dyy in range(-1, 2):
                for dzz in range(-1, 2):
                    ncx = (cxi + dxx) % nx
                    ncy = (cyi + dyy) % ny
                    ncz = (czi + dzz) % nz
                    cj = ncx * ny * nz + ncy * nz + ncz
                    start_j = cell_starts[cj]
                    count_j = cell_counts[cj]
                    if count_j == 0:
                        continue

                    for ii in range(count_i):
                        i = sorted_indices[start_i + ii]
                        if not alive[i]:
                            continue
                        inertia_i = float(level[i])
                        fi = freq[i]
                        for jj in range(count_j):
                            j = sorted_indices[start_j + jj]
                            if j == i or not alive[j]:
                                continue
                            # Distance check
                            d2 = 0.0
                            for d in range(3):
                                dx = positions[i, d] - positions[j, d]
                                b = box[d]
                                if dx > b * 0.5:
                                    dx -= b
                                elif dx < -b * 0.5:
                                    dx += b
                                d2 += dx * dx
                            if d2 >= r_sq:
                                continue
                            fj = freq[j]
                            fmax = fi if fi > fj else fj
                            if fmax < 1e-6:
                                continue
                            delta_freq[i] += coupling / inertia_i * (fj - fi) / fmax * dt

    # Apply
    for i in range(n):
        if alive[i] and delta_freq[i] != 0.0:
            new_f = freq[i] + delta_freq[i]
            if new_f < 1.0:
                new_f = 1.0
            freq[i] = new_f


# ============================================================
# Python-facing wrappers (backward compatible)
# ============================================================

def build_grid(positions, alive, box, cell_size):
    """Build grid as Python dict (legacy interface)."""
    n = positions.shape[0]
    grid: dict[tuple[int, int, int], list[int]] = {}
    nx = max(1, int(np.ceil(box[0] / cell_size)))
    ny = max(1, int(np.ceil(box[1] / cell_size)))
    nz = max(1, int(np.ceil(box[2] / cell_size)))
    for i in range(n):
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


def neighbors_of(grid, pos, box, cell_size, *, exclude_self, query_index):
    """Iterate the 27-cell periodic neighbourhood (legacy interface)."""
    nx = max(1, int(np.ceil(box[0] / cell_size)))
    ny = max(1, int(np.ceil(box[1] / cell_size)))
    nz = max(1, int(np.ceil(box[2] / cell_size)))
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

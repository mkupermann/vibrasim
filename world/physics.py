from __future__ import annotations
import math
import numpy as np
from numba import njit
from world.spatial import build_grid, neighbors_of, periodic_distance_sq, periodic_midpoint


@njit(cache=True)
def move_vibrations(
    s_pos: np.ndarray,
    s_vel: np.ndarray,
    s_alive: np.ndarray,
    box: np.ndarray,
    dt: float,
) -> None:
    """In-place: advance alive vibrations by dt with periodic-wrap into the box."""
    n = s_pos.shape[0]
    for i in range(n):
        if not s_alive[i]:
            continue
        s_pos[i, 0] = (s_pos[i, 0] + s_vel[i, 0] * dt) % box[0]
        s_pos[i, 1] = (s_pos[i, 1] + s_vel[i, 1] * dt) % box[1]


def bind_vibrations_to_electrons(world) -> int:
    """Scan alive vibrations for binding pairs. Forms electrons. Returns count formed.

    Not @njit: builds a dict-based grid and calls into the typed allocate_node.
    The inner pairwise check (distance, polarity, frequency) is still tight.
    """
    cfg = world.config
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r1 = cfg.r_1
    r1_sq = r1 * r1
    fr = cfg.freq_ratio
    ftol = cfg.freq_tolerance
    fmin_ratio = fr - ftol
    fmax_ratio = fr + ftol

    world.reset_tick_locks()
    grid = build_grid(world.s_pos, world.s_alive, box, r1)
    formed = 0

    for i in range(world.s_pos.shape[0]):
        if not world.s_alive[i] or world.s_locked_this_tick[i]:
            continue
        nbrs = neighbors_of(grid, world.s_pos[i], box, r1, exclude_self=True, query_index=i)
        for j in nbrs:
            if j <= i:
                continue
            if not world.s_alive[j] or world.s_locked_this_tick[j]:
                continue
            if world.s_pol[i] == world.s_pol[j]:
                continue
            d2 = periodic_distance_sq(world.s_pos[i], world.s_pos[j], box)
            if d2 >= r1_sq:
                continue
            f1 = world.s_freq[i]
            f2 = world.s_freq[j]
            ratio = abs(f1 - f2) / min(f1, f2)
            if ratio < fmin_ratio or ratio > fmax_ratio:
                continue
            mid = periodic_midpoint(world.s_pos[i], world.s_pos[j], box)
            new_freq = f1 + f2
            new_pol = bool(world.rng.random() < 0.5)
            constituents = np.array([i, j], dtype=np.int32)
            world.allocate_node(mid, new_freq, new_pol, level=1,
                                constituents=constituents, comp_kind=0)
            world.s_alive[i] = False
            world.s_alive[j] = False
            world.s_locked_this_tick[i] = True
            world.s_locked_this_tick[j] = True
            world.n_alive -= 2
            formed += 1
            break

    return formed


# Pair = level 1+1 → 2; triad = level 2+1 → 3; atom = level 3+1 → 4.
_UPGRADE_TARGET = {
    (1, 1): 2,
    (1, 2): 3, (2, 1): 3,
    (1, 3): 4, (3, 1): 4,
}


def _decade(freq: float) -> int:
    return int(math.floor(math.log10(freq)))


def bind_nodes_upward(world) -> int:
    """Scan alive nodes for upgrade pairs. Returns count of upgrades formed."""
    cfg = world.config
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r2 = cfg.r_2
    r2_sq = r2 * r2
    fr = cfg.freq_ratio
    ftol = cfg.freq_tolerance
    fmin_ratio = fr - ftol
    fmax_ratio = fr + ftol

    world.k_locked_this_tick[:world.k_count] = False
    formed = 0

    grid = build_grid(world.k_pos[:world.k_count], world.k_alive[:world.k_count], box, r2)

    for i in range(world.k_count):
        if not world.k_alive[i] or world.k_locked_this_tick[i]:
            continue
        nbrs = neighbors_of(grid, world.k_pos[i], box, r2, exclude_self=True, query_index=i)
        for j in nbrs:
            if j <= i:
                continue
            if not world.k_alive[j] or world.k_locked_this_tick[j]:
                continue
            li = int(world.k_level[i])
            lj = int(world.k_level[j])
            target = _UPGRADE_TARGET.get((li, lj))
            if target is None:
                continue
            if world.k_pol[i] == world.k_pol[j]:
                continue
            d2 = periodic_distance_sq(world.k_pos[i], world.k_pos[j], box)
            if d2 >= r2_sq:
                continue
            f1 = world.k_freq[i]
            f2 = world.k_freq[j]
            if _decade(f1) != _decade(f2):
                continue
            ratio = abs(f1 - f2) / min(f1, f2)
            if ratio < fmin_ratio or ratio > fmax_ratio:
                continue
            mid = periodic_midpoint(world.k_pos[i], world.k_pos[j], box)
            new_freq = f1 + f2
            new_pol = bool(world.rng.random() < 0.5)
            constituents = np.array([i, j], dtype=np.int32)
            world.allocate_node(mid, new_freq, new_pol, level=target,
                                constituents=constituents, comp_kind=1)
            world.k_alive[i] = False
            world.k_alive[j] = False
            world.k_locked_this_tick[i] = True
            world.k_locked_this_tick[j] = True
            formed += 1
            break

    return formed

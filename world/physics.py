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
    """3D motion with periodic-wrap on all three axes."""
    n = s_pos.shape[0]
    for i in range(n):
        if not s_alive[i]:
            continue
        for d in range(3):
            s_pos[i, d] = (s_pos[i, d] + s_vel[i, d] * dt) % box[d]


def bind_vibrations_to_electrons(world) -> int:
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


_UPGRADE_TARGET = {
    (1, 1): 2,
    (1, 2): 3, (2, 1): 3,
    (1, 3): 4, (3, 1): 4,
}


def _decade(freq: float) -> int:
    return int(math.floor(math.log10(freq)))


def bind_nodes_upward(world) -> int:
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


def decay_unstable_nodes(world, dt: float) -> int:
    """Probabilistic exponential decay of pairs (level 2) and triads (level 3).

    Atoms (level 4) are permanent. Electrons (level 1) are handled by the
    ambient_regeneration channel, not here.
    """
    cfg = world.config
    decay_time = {2: cfg.pair_decay_time, 3: cfg.triad_decay_time}
    rng = world.rng
    decayed = 0
    for i in range(world.k_count):
        if not world.k_alive[i]:
            continue
        level = int(world.k_level[i])
        if level not in (2, 3):
            continue
        tau = decay_time[level]
        p = dt / tau
        if rng.random() < p:
            world.k_alive[i] = False
            start = world.k_comp_offset[i]
            end = world.k_comp_offset[i + 1]
            for j in range(start, end):
                idx = int(world.k_comp_indices[j])
                world.k_alive[idx] = True
            decayed += 1
    return decayed


def ambient_regeneration(world, dt: float) -> tuple[int, int]:
    """Generate new free vibrations and decay unstable nodes back to vibrations.

    Returns (n_generated, n_decayed).
    """
    cfg = world.config
    rng = world.rng
    box = np.asarray(cfg.box_size, dtype=np.float64)
    volume = box[0] * box[1] * box[2]

    # Generation: Poisson(lambda_gen * volume * dt)
    expected = cfg.lambda_gen * volume * dt
    n_new = rng.poisson(expected)
    n_max = world.s_pos.shape[0]
    n_alive_now = int(world.s_alive.sum())
    capacity = n_max - n_alive_now
    n_new = min(n_new, capacity)
    if n_new > 0:
        # Find slot indices that are dead
        dead_idx = np.where(~world.s_alive)[0][:n_new]
        # Sample new vibrations
        for d in range(3):
            world.s_pos[dead_idx, d] = rng.uniform(0.0, box[d], size=n_new)
        if cfg.freq_distribution == "log":
            world.s_freq[dead_idx] = np.exp(rng.uniform(np.log(cfg.freq_min),
                                                        np.log(cfg.freq_max), size=n_new))
        else:
            world.s_freq[dead_idx] = rng.uniform(cfg.freq_min, cfg.freq_max, size=n_new)
        world.s_pol[dead_idx] = rng.random(n_new) < cfg.polarity_split
        # Isotropic 3D velocities
        speeds = rng.uniform(cfg.speed_min, cfg.speed_max, size=n_new)
        z = rng.uniform(-1.0, 1.0, size=n_new)
        phi = rng.uniform(0.0, 2 * np.pi, size=n_new)
        sqz = np.sqrt(1 - z * z)
        world.s_vel[dead_idx, 0] = speeds * sqz * np.cos(phi)
        world.s_vel[dead_idx, 1] = speeds * sqz * np.sin(phi)
        world.s_vel[dead_idx, 2] = speeds * z
        world.s_alive[dead_idx] = True
        world.n_alive += n_new

    # Decay: each alive node level 1/2/3 has Bernoulli(lambda_dec * dt) of decaying
    n_decayed = 0
    if cfg.lambda_dec > 0:
        p = cfg.lambda_dec * dt
        for i in range(world.k_count):
            if not world.k_alive[i]:
                continue
            level = int(world.k_level[i])
            if level not in (1, 2, 3):
                continue  # atoms (level 4) immune
            if rng.random() < p:
                # Cascade decay: revive constituents
                world.k_alive[i] = False
                start = world.k_comp_offset[i]
                end = world.k_comp_offset[i + 1]
                kind = int(world.k_comp_kind[i])
                if kind == 0:
                    # constituents are vibrations; bring them back to life
                    for jj in range(start, end):
                        idx = int(world.k_comp_indices[jj])
                        if not world.s_alive[idx]:
                            world.s_alive[idx] = True
                            world.s_pos[idx] = world.k_pos[i]
                            # Random thermal velocity
                            speed = rng.uniform(cfg.speed_min, cfg.speed_max)
                            z_val = rng.uniform(-1.0, 1.0)
                            phi_val = rng.uniform(0.0, 2 * np.pi)
                            sqz_val = math.sqrt(1 - z_val * z_val)
                            world.s_vel[idx, 0] = speed * sqz_val * math.cos(phi_val)
                            world.s_vel[idx, 1] = speed * sqz_val * math.sin(phi_val)
                            world.s_vel[idx, 2] = speed * z_val
                            world.n_alive += 1
                else:
                    # constituents are nodes; revive them
                    for jj in range(start, end):
                        idx = int(world.k_comp_indices[jj])
                        world.k_alive[idx] = True
                n_decayed += 1

    return n_new, n_decayed

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
    # Phase 1: vibrations → electrons → pairs → triads → atoms
    (1, 1): 2,
    (1, 2): 3, (2, 1): 3,
    (1, 3): 4, (3, 1): 4,
    # Phase 2: atoms binding into molecules. Each upgrade adds one atom; the
    # upgrade table only allows level-4 (atom) on at least one side, so
    # molecules cannot bind to each other.
    (4, 4): 5,
    (4, 5): 6, (5, 4): 6,
    (4, 6): 7, (6, 4): 7,
    (4, 7): 8, (7, 4): 8,
    (4, 8): 9, (8, 4): 9,
    (4, 9): 10, (9, 4): 10,
    (4, 10): 11, (10, 4): 11,
    # Cap at level 11 (deca-atomic). Phase 3+ may revisit.
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


def apply_scale_repulsion(world, dt: float) -> None:
    """Accumulate repulsive force into k_vel for nodes whose freq_ratio exceeds threshold."""
    cfg = world.config
    if cfg.repulsion_k == 0.0 or world.k_count == 0:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)
    cell = cfg.repulsion_cell_size
    threshold = cfg.repulsion_threshold_ratio
    grid = build_grid(world.k_pos[:world.k_count], world.k_alive[:world.k_count], box, cell)

    for i in range(world.k_count):
        if not world.k_alive[i]:
            continue
        f_i = world.k_freq[i]
        nbrs = neighbors_of(grid, world.k_pos[i], box, cell, exclude_self=True, query_index=i)
        for j in nbrs:
            if not world.k_alive[j]:
                continue
            f_j = world.k_freq[j]
            ratio = max(f_i, f_j) / min(f_i, f_j)
            if ratio <= threshold:
                continue
            # Direction vector from j to i (minimum-image periodic)
            dx = world.k_pos[i, 0] - world.k_pos[j, 0]
            dy = world.k_pos[i, 1] - world.k_pos[j, 1]
            dz = world.k_pos[i, 2] - world.k_pos[j, 2]
            # Apply periodic minimum-image wrap
            if dx > box[0] * 0.5:
                dx -= box[0]
            elif dx < -box[0] * 0.5:
                dx += box[0]
            if dy > box[1] * 0.5:
                dy -= box[1]
            elif dy < -box[1] * 0.5:
                dy += box[1]
            if dz > box[2] * 0.5:
                dz -= box[2]
            elif dz < -box[2] * 0.5:
                dz += box[2]
            r2 = dx * dx + dy * dy + dz * dz
            if r2 < 1e-9:
                continue
            r = math.sqrt(r2)
            # F_magnitude = k * (ratio - threshold) / r²
            F_mag = cfg.repulsion_k * (ratio - threshold) / r2
            # Mass proportional to k_level (heavier nodes accelerate less)
            mass_i = float(world.k_level[i])
            ax = F_mag * dx / r / mass_i
            ay = F_mag * dy / r / mass_i
            az = F_mag * dz / r / mass_i
            world.k_vel[i, 0] += ax * dt
            world.k_vel[i, 1] += ay * dt
            world.k_vel[i, 2] += az * dt


def move_nodes(world, dt: float) -> None:
    """Apply k_vel to k_pos with periodic wrap. Atoms move slowly because of mass."""
    box = np.asarray(world.config.box_size, dtype=np.float64)
    for i in range(world.k_count):
        if not world.k_alive[i]:
            continue
        for d in range(3):
            world.k_pos[i, d] = (world.k_pos[i, d] + world.k_vel[i, d] * dt) % box[d]


def neuron_dynamics(world, dt: float) -> None:
    """PHASE4-R1/R2/R3: per-atom integrate-and-fire with refractory.

    Each level-4 (or higher) atom is treated as a leaky integrator. Free
    vibrations within `r_integrate` of the atom contribute to its charge.
    The charge decays exponentially with time constant `tau_membrane`. When
    the charge crosses `theta_fire` and the atom is not in its refractory
    window, the atom emits `n_emit` vibrations isotropically at its position
    and locks for `t_refractory` seconds.

    No-op when `neuron_dynamics_enabled` is False.
    """
    cfg = world.config
    if not cfg.neuron_dynamics_enabled:
        return

    K = world.k_count
    if K == 0:
        return

    # 1. Decay all atom charges
    decay_factor = float(np.exp(-dt / max(cfg.tau_membrane, 1e-9)))
    atom_mask = (world.k_level[:K] >= 4) & world.k_alive[:K]
    if not atom_mask.any():
        return
    atom_indices = np.where(atom_mask)[0]
    world.k_charge[atom_indices] *= decay_factor

    # 2. For each atom not in refractory: count nearby vibrations + add to charge
    r2 = cfg.r_integrate ** 2
    box = np.asarray(cfg.box_size, dtype=np.float64)
    n_alive_v = world.n_alive
    if n_alive_v > 0:
        v_pos = world.s_pos[:n_alive_v]
        v_alive = world.s_alive[:n_alive_v]
    for ai in atom_indices:
        if world.t < world.k_refractory_until[ai]:
            continue
        if n_alive_v == 0:
            continue
        ap = world.k_pos[ai]
        # Periodic-image squared distance
        d = v_pos - ap
        # wrap to [-box/2, box/2]
        d -= box * np.round(d / box)
        d2 = (d * d).sum(axis=1)
        n_in = int(((d2 <= r2) & v_alive).sum())
        if n_in > 0:
            world.k_charge[ai] += float(n_in)

    # 3. Fire: any atom with charge ≥ theta_fire and not refractory emits.
    can_fire = (world.k_charge[atom_indices] >= cfg.theta_fire) & (
        world.t >= world.k_refractory_until[atom_indices]
    )
    firing_atoms = atom_indices[can_fire]
    for ai in firing_atoms:
        _emit_vibrations(world, ai)
        world.k_charge[ai] = 0.0
        world.k_refractory_until[ai] = world.t + cfg.t_refractory
        world.firing_events.append((float(world.t), int(ai)))


def _emit_vibrations(world, atom_idx: int) -> None:
    """Emit n_emit vibrations isotropically around the firing atom's position."""
    cfg = world.config
    n = cfg.n_emit
    # Find n free vibration slots (alive=False)
    free_mask = ~world.s_alive
    free_idx = np.where(free_mask)[0][:n]
    if len(free_idx) == 0:
        return
    if len(free_idx) < n:
        n = len(free_idx)
        free_idx = free_idx[:n]
    box = np.asarray(cfg.box_size, dtype=np.float64)
    pos = world.k_pos[atom_idx]
    # Isotropic unit vectors via Marsaglia
    z = world.rng.uniform(-1.0, 1.0, size=n)
    phi = world.rng.uniform(0.0, 2 * np.pi, size=n)
    sqrt_omz2 = np.sqrt(1 - z * z)
    vx = sqrt_omz2 * np.cos(phi) * cfg.emit_speed
    vy = sqrt_omz2 * np.sin(phi) * cfg.emit_speed
    vz = z * cfg.emit_speed
    for k, fi in enumerate(free_idx):
        world.s_pos[fi] = pos % box  # spawn at firing position
        world.s_vel[fi, 0] = vx[k]
        world.s_vel[fi, 1] = vy[k]
        world.s_vel[fi, 2] = vz[k]
        world.s_freq[fi] = cfg.emit_freq
        world.s_pol[fi] = bool(world.rng.random() < cfg.polarity_split)
        world.s_alive[fi] = True
    # Update n_alive (high-water mark) so the new vibrations are scanned next tick.
    high = int(free_idx.max()) + 1
    if high > world.n_alive:
        world.n_alive = high


def tick(world, dt: float) -> None:
    """One simulation step. See CONCEPT.md v2 §4 + §7.1 for the canonical order."""
    box = np.asarray(world.config.box_size, dtype=np.float64)
    move_vibrations(world.s_pos, world.s_vel, world.s_alive, box, dt)
    apply_scale_repulsion(world, dt)
    move_nodes(world, dt)
    bind_vibrations_to_electrons(world)
    bind_nodes_upward(world)
    decay_unstable_nodes(world, dt)
    ambient_regeneration(world, dt)
    neuron_dynamics(world, dt)
    world.t += dt

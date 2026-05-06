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

# PHASE3-R1: additional molecule+molecule entries, gated by cfg.mol_fusion_enabled.
# These are appended to the lookup at runtime so legacy behaviour is preserved
# when the flag is off.
_UPGRADE_TARGET_FUSION = {
    (5, 5): 6,
    (5, 6): 7, (6, 5): 7,
    (5, 7): 8, (7, 5): 8,
    (6, 6): 7,
    (6, 7): 8, (7, 6): 8,
    (7, 7): 8,
    (5, 8): 9, (8, 5): 9,
    (6, 8): 9, (8, 6): 9,
    (7, 8): 9, (8, 7): 9,
    (8, 8): 9,
}

# Plan A.5 — numpy-array versions for Numba JIT lookup. Numba can't
# index Python dicts efficiently; small dense arrays are the canonical
# pattern. Built once at module import. Cells without an upgrade hold -1.
# The dict versions above are kept for the Python (non-JIT) path.
_MAX_LEVEL = 12
_UPGRADE_TARGET_ARRAY = np.full((_MAX_LEVEL, _MAX_LEVEL), -1, dtype=np.int8)
for (li, lj), target in _UPGRADE_TARGET.items():
    _UPGRADE_TARGET_ARRAY[li, lj] = target

_UPGRADE_TARGET_FUSION_ARRAY = np.full((_MAX_LEVEL, _MAX_LEVEL), -1, dtype=np.int8)
for (li, lj), target in _UPGRADE_TARGET_FUSION.items():
    _UPGRADE_TARGET_FUSION_ARRAY[li, lj] = target


def _decade(freq: float) -> int:
    return int(math.floor(math.log10(freq)))


def _kill_node(world, i: int) -> None:
    """Mark node i dead, decrement ref counts of its constituents, and
    push newly-recyclable slots onto the free list.

    Single source of truth for slot bookkeeping. Every code path that
    deactivates a node must funnel through this helper, otherwise ref
    counts go stale and slots are recycled prematurely.

    A slot is recyclable iff k_alive[i] == False AND k_ref_count[i] == 0.

    When `cfg.slot_recycling_enabled` is False, falls back to the legacy
    "just deactivate, no bookkeeping" behaviour — preserved for regression
    diagnosis.
    """
    cfg = world.config
    if not cfg.slot_recycling_enabled:
        # Legacy path: just deactivate
        world.k_alive[i] = False
        return

    if not world.k_alive[i]:
        return  # already dead — no-op

    world.k_alive[i] = False

    # Decrement ref counts of constituents — only when this slot's composition
    # references node indices (comp_kind != 0), not vibration indices.
    if world.k_comp_kind[i] != 0:
        start = int(world.k_comp_offset[i])
        end = int(world.k_comp_offset[i + 1])
        for j in range(start, end):
            c = int(world.k_comp_indices[j])
            if 0 <= c < world.k_count:
                world.k_ref_count[c] -= 1
                if world.k_ref_count[c] <= 0 and not world.k_alive[c]:
                    if c not in world._free_slots_set:
                        world._free_slots.append(c)
                        world._free_slots_set.add(c)

    # Maybe i itself is now recyclable
    if world.k_ref_count[i] == 0:
        if i not in world._free_slots_set:
            world._free_slots.append(i)
            world._free_slots_set.add(i)


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
            if target is None and cfg.mol_fusion_enabled:
                target = _UPGRADE_TARGET_FUSION.get((li, lj))
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
            _kill_node(world, i)
            _kill_node(world, j)
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
            start = world.k_comp_offset[i]
            end = world.k_comp_offset[i + 1]
            _kill_node(world, i)
            for j in range(start, end):
                idx = int(world.k_comp_indices[j])
                # Revive the constituent; if _kill_node pushed it onto the
                # free list (ref count dropped to 0), remove it first so the
                # slot isn't recycled out from under the revived node.
                if idx in world._free_slots_set:
                    world._free_slots_set.discard(idx)
                    try:
                        world._free_slots.remove(idx)
                    except ValueError:
                        pass
                world.k_alive[idx] = True
            decayed += 1
    return decayed


def decay_high_level_nodes(world, dt: float) -> int:
    """R2: strength-modulated decay for level-5+ molecules.

    Per-tick decay probability for each level-5+ alive node:
        p = lambda_dec_mol * dt / max(strength, 1.0)

    When a molecule decays, it disappears (k_alive=False). Constituent
    atoms (level 4) inside its composition span are not destroyed — they
    live in their own slots and stay alive=True there.

    Returns the count of nodes that decayed this tick.
    """
    cfg = world.config
    if cfg.lambda_dec_mol <= 0.0:
        return 0
    K = world.k_count
    if K == 0:
        return 0
    mask = world.k_alive[:K] & (world.k_level[:K] >= 5)
    if not mask.any():
        return 0
    indices = np.where(mask)[0]
    strengths = np.maximum(world.k_strength[indices], 1.0)
    p_decay = cfg.lambda_dec_mol * dt / strengths
    rolls = world.rng.random(len(indices))
    decayed_mask = rolls < p_decay
    n_decayed = int(decayed_mask.sum())
    for i in indices[decayed_mask]:
        _kill_node(world, i)
    return n_decayed


def ambient_regeneration(world, dt: float) -> tuple[int, int]:
    """Generate new free vibrations and decay unstable nodes back to vibrations.

    R1 recycling rule: when the buffer is full, displace a far-field vibration
    instead of silently no-op'ing.  Active regions (within 2*r_2 of any
    level-4+ node) are protected from displacement.

    Returns (n_displaced_or_allocated, n_decayed).
    """
    cfg = world.config
    rng = world.rng
    box = np.asarray(cfg.box_size, dtype=np.float64)
    box_volume = box[0] * box[1] * box[2]

    # Target steady-state count from equilibrium density
    if cfg.lambda_dec <= 0:
        target_density = 0.0
    else:
        target_density = cfg.lambda_gen / cfg.lambda_dec
    target_count = int(target_density * box_volume)
    current_count = int(world.s_alive.sum())
    deficit = max(0, target_count - current_count)
    if deficit == 0:
        return (0, 0)

    # Active-region positions: alive nodes at level 4+
    if world.k_count > 0:
        active_mask = world.k_alive[:world.k_count] & (world.k_level[:world.k_count] >= 4)
        active_pos = world.k_pos[:world.k_count][active_mask]
    else:
        active_pos = np.empty((0, 3), dtype=np.float64)
    safe_radius_sq = (2.0 * cfg.r_2) ** 2

    n_displaced = 0
    n_allocated = 0

    # --- Pass 1: displace far-field alive vibrations ---
    alive_idx = np.where(world.s_alive)[0]
    rng.shuffle(alive_idx)
    for i in alive_idx:
        if deficit <= 0:
            break
        if len(active_pos):
            d = world.s_pos[i] - active_pos
            d -= box * np.round(d / box)  # periodic minimum-image
            d2 = (d * d).sum(axis=1)
            if (d2 < safe_radius_sq).any():
                continue  # inside an active region; skip
        # Displace: re-randomise position, velocity, frequency, polarity
        world.s_pos[i] = rng.uniform(low=np.zeros(3), high=box)
        world.s_vel[i] = world._sample_velocities_3d(1)[0]
        world.s_freq[i] = world._sample_frequencies(1)[0]
        world.s_pol[i] = bool(rng.random() < cfg.polarity_split)
        n_displaced += 1
        deficit -= 1

    # --- Pass 2: fallback — allocate from unused buffer slots if any remain ---
    if deficit > 0:
        free_idx = np.where(~world.s_alive)[0]
        for i in free_idx[:deficit]:
            world.s_pos[i] = rng.uniform(low=np.zeros(3), high=box)
            world.s_vel[i] = world._sample_velocities_3d(1)[0]
            world.s_freq[i] = world._sample_frequencies(1)[0]
            world.s_pol[i] = bool(rng.random() < cfg.polarity_split)
            world.s_alive[i] = True
            n_allocated += 1
            deficit -= 1
        if n_allocated > 0:
            # Single high-water-mark update; robust to any iteration order
            # (uses the max actually-allocated index, not the loop's last `i`).
            world.n_alive = max(world.n_alive, int(free_idx[:n_allocated].max()) + 1)

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
                start = world.k_comp_offset[i]
                end = world.k_comp_offset[i + 1]
                kind = int(world.k_comp_kind[i])
                _kill_node(world, i)
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
                    # constituents are nodes; revive them (remove from free list
                    # if _kill_node pushed them there when ref count hit 0).
                    for jj in range(start, end):
                        idx = int(world.k_comp_indices[jj])
                        if idx in world._free_slots_set:
                            world._free_slots_set.discard(idx)
                            try:
                                world._free_slots.remove(idx)
                            except ValueError:
                                pass
                        world.k_alive[idx] = True
                n_decayed += 1

    return n_displaced + n_allocated, n_decayed


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

    # R2 strengthening: every level-5+ molecule within r_strengthen of any
    # firing atom on this tick gets strength += dt.
    if len(firing_atoms) > 0:
        K = world.k_count
        molecule_mask = world.k_alive[:K] & (world.k_level[:K] >= 5)
        if molecule_mask.any():
            molecule_indices = np.where(molecule_mask)[0]
            molecule_pos = world.k_pos[molecule_indices]
            r2 = cfg.r_strengthen ** 2
            box = np.asarray(cfg.box_size, dtype=np.float64)
            for ai in firing_atoms:
                ap = world.k_pos[ai]
                d = molecule_pos - ap
                d -= box * np.round(d / box)  # periodic minimum image
                d2 = (d * d).sum(axis=1)
                near_mask = d2 <= r2
                world.k_strength[molecule_indices[near_mask]] += dt


def _emit_vibrations(world, atom_idx: int) -> None:
    """Emit n_emit vibrations isotropically around the firing atom's position.

    Frequencies are drawn uniformly across the configured emission band
    ratios (e.g. [freq_ratio, 1.0, 1/freq_ratio]) so emitted vibrations can
    climb the binding hierarchy via the existing freq_ratio rule.
    """
    cfg = world.config
    n = cfg.n_emit
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
    # Frequency band fan: assign each emission to one of the band ratios.
    band_ratios = np.asarray(cfg.emit_band_ratios, dtype=np.float64)
    band_assignments = world.rng.integers(0, len(band_ratios), size=n)
    # Small per-emission jitter (±5%) so within-band binding is possible
    jitter = world.rng.uniform(0.95, 1.05, size=n)
    base_freqs = band_ratios[band_assignments] * cfg.emit_freq * jitter
    for k, fi in enumerate(free_idx):
        world.s_pos[fi] = pos % box
        world.s_vel[fi, 0] = vx[k]
        world.s_vel[fi, 1] = vy[k]
        world.s_vel[fi, 2] = vz[k]
        world.s_freq[fi] = base_freqs[k]
        world.s_pol[fi] = bool(world.rng.random() < cfg.polarity_split)
        world.s_alive[fi] = True
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
    decay_high_level_nodes(world, dt)   # NEW (R2)
    ambient_regeneration(world, dt)
    neuron_dynamics(world, dt)
    world.t += dt

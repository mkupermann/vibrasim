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


@njit(cache=True)
def _bind_vibrations_check_pairs_njit(
    candidate_i: np.ndarray, candidate_j: np.ndarray, n_candidates: int,
    s_pos: np.ndarray, s_alive: np.ndarray, s_locked_this_tick: np.ndarray,
    s_freq: np.ndarray, s_pol: np.ndarray,
    box: np.ndarray, r1_sq: float,
    fmin_ratio: float, fmax_ratio: float,
) -> tuple:
    """JIT core for bind_vibrations_to_electrons.

    Mirrors `_bind_check_pairs_njit` (which serves bind_nodes_upward) but for
    vibration-level binding. Filters candidate pairs by alive, locked,
    polarity-difference, periodic-distance, and the 8 % frequency rule.

    Returns parallel arrays (out_i, out_j, out_freq, out_mid, n_out) preserving
    input order. The new electron's frequency is f_i + f_j; mid is the periodic
    midpoint. The Python wrapper enforces break-per-i semantics by re-checking
    the lock array after each allocation.
    """
    out_i = np.zeros(n_candidates, dtype=np.int32)
    out_j = np.zeros(n_candidates, dtype=np.int32)
    out_freq = np.zeros(n_candidates, dtype=np.float64)
    out_mid = np.zeros((n_candidates, 3), dtype=np.float64)
    n_out = 0
    for k in range(n_candidates):
        i = candidate_i[k]
        j = candidate_j[k]
        if not s_alive[i] or not s_alive[j]:
            continue
        if s_locked_this_tick[i] or s_locked_this_tick[j]:
            continue
        if s_pol[i] == s_pol[j]:
            continue
        # Periodic distance (3D)
        dx = s_pos[i, 0] - s_pos[j, 0]
        dy = s_pos[i, 1] - s_pos[j, 1]
        dz = s_pos[i, 2] - s_pos[j, 2]
        dx -= box[0] * round(dx / box[0])
        dy -= box[1] * round(dy / box[1])
        dz -= box[2] * round(dz / box[2])
        d2 = dx * dx + dy * dy + dz * dz
        if d2 >= r1_sq:
            continue
        # 8 % frequency rule
        f1 = s_freq[i]
        f2 = s_freq[j]
        if f1 < f2:
            ratio = (f2 - f1) / f1
        else:
            ratio = (f1 - f2) / f2
        if ratio < fmin_ratio or ratio > fmax_ratio:
            continue
        # Periodic midpoint, per-axis (matches periodic_midpoint() semantics)
        for d in range(3):
            delta = s_pos[j, d] - s_pos[i, d]
            if delta > box[d] * 0.5:
                delta -= box[d]
            elif delta < -box[d] * 0.5:
                delta += box[d]
            m = s_pos[i, d] + delta * 0.5
            m = m % box[d]
            out_mid[n_out, d] = m
        out_i[n_out] = i
        out_j[n_out] = j
        out_freq[n_out] = f1 + f2
        n_out += 1
    return out_i, out_j, out_freq, out_mid, n_out


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

    if cfg.numba_jit_enabled:
        # G1: JIT path. Build candidate pairs in Python (spatial-hash query
        # is already JITted internally) preserving the legacy iteration order
        # so break-per-i semantics carry. JIT filters by predicates; Python
        # applies allocations in order.
        cand_i_list: list[int] = []
        cand_j_list: list[int] = []
        for i in range(world.s_pos.shape[0]):
            if not world.s_alive[i]:
                continue
            nbrs = neighbors_of(grid, world.s_pos[i], box, r1,
                                 exclude_self=True, query_index=i)
            for j in nbrs:
                if j <= i:
                    continue
                cand_i_list.append(i)
                cand_j_list.append(j)

        n_candidates = len(cand_i_list)
        if n_candidates == 0:
            return 0

        candidate_i = np.array(cand_i_list, dtype=np.int32)
        candidate_j = np.array(cand_j_list, dtype=np.int32)

        out_i, out_j, out_freq, out_mid, n_out = _bind_vibrations_check_pairs_njit(
            candidate_i, candidate_j, n_candidates,
            world.s_pos, world.s_alive, world.s_locked_this_tick,
            world.s_freq, world.s_pol,
            box, r1_sq, fmin_ratio, fmax_ratio,
        )

        formed = 0
        for k in range(n_out):
            i = int(out_i[k])
            j = int(out_j[k])
            # Re-check after earlier iterations may have consumed these slots
            if not world.s_alive[i] or world.s_locked_this_tick[i]:
                continue
            if not world.s_alive[j] or world.s_locked_this_tick[j]:
                continue
            new_pol = bool(world.rng.random() < 0.5)
            constituents = np.array([i, j], dtype=np.int32)
            new_node = world.allocate_node(
                out_mid[k], float(out_freq[k]), new_pol, level=1,
                constituents=constituents, comp_kind=0,
            )
            if new_node < 0:
                # Capacity exhausted (graceful_capacity mode); stop binding
                # for this tick. Vibrations stay alive.
                break
            world.s_alive[i] = False
            world.s_alive[j] = False
            world.s_locked_this_tick[i] = True
            world.s_locked_this_tick[j] = True
            world.n_alive -= 2
            formed += 1
        return formed

    # Legacy Python path — preserved verbatim for regression diagnosis
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
            new_node = world.allocate_node(
                mid, new_freq, new_pol, level=1,
                constituents=constituents, comp_kind=0,
            )
            if new_node < 0:
                return formed
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


def molecules_in_tube(world, A: np.ndarray, B: np.ndarray, r_bridge: float) -> np.ndarray:
    """Return indices of alive level-5+ molecules whose perpendicular distance
    to the segment A→B is ≤ r_bridge AND whose projection along the segment
    falls within [0, |B-A|].

    Periodic minimum-image is applied to the (M - A) and (B - A) vectors.
    """
    A = np.asarray(A, dtype=np.float64)
    B = np.asarray(B, dtype=np.float64)
    box = np.asarray(world.config.box_size, dtype=np.float64)
    K = world.k_count
    if K == 0:
        return np.empty(0, dtype=np.int64)
    mol_mask = world.k_alive[:K] & (world.k_level[:K] >= 5)
    if not mol_mask.any():
        return np.empty(0, dtype=np.int64)
    indices = np.where(mol_mask)[0]
    M_pos = world.k_pos[indices]

    # Periodic minimum-image on (M - A) and (B - A)
    rM = M_pos - A
    rM -= box * np.round(rM / box)
    v = B - A
    v -= box * np.round(v / box)
    v_len_sq = float((v * v).sum())
    if v_len_sq < 1e-12:
        return np.empty(0, dtype=np.int64)

    # Projection scalar t per molecule
    t = (rM * v).sum(axis=1) / v_len_sq
    in_segment_mask = (t >= 0.0) & (t <= 1.0)
    proj = t[:, None] * v
    perp = rM - proj
    perp_dist_sq = (perp * perp).sum(axis=1)
    in_tube_mask = perp_dist_sq <= r_bridge ** 2
    return indices[in_segment_mask & in_tube_mask]


def apply_stdp(world) -> int:
    """Plan B: spike-timing-dependent plasticity post-tick scan.

    Scans world.firing_events for ordered pairs (t_i, atom_i) → (t_j, atom_j)
    with 0 < (t_j - t_i) ≤ τ_LTP. For each such pair, finds the bridge tube
    (level-5+ molecules between the two atoms) and applies per-molecule
    LTP or LTD based on alignment of the molecule's existing orientation
    with the firing pair's A→B unit vector:

    - No orientation yet (|o| < 1e-6) or alignment ≥ 0 → LTP:
      strengthen + update orientation toward u.
    - Alignment < 0 → LTD: weaken only; orientation unchanged.
      Floor at strength=1.0 so a bridge cannot disappear from LTD alone.

    δ_LTD < δ_LTP by default so a balanced sequence of opposing pairs
    nets to small positive (biological STDP asymmetry).

    Returns the count of (pair, molecule) reinforcement events.
    """
    cfg = world.config
    if not cfg.stdp_enabled:
        return 0
    events = world.firing_events
    if len(events) < 2:
        return 0

    n_reinforcements = 0
    box = np.asarray(cfg.box_size, dtype=np.float64)

    # Pair scan — for each ordered pair within tau_LTP
    for i, (t_i, atom_i) in enumerate(events):
        for j in range(i + 1, len(events)):
            t_j, atom_j = events[j]
            dt_pair = t_j - t_i
            if dt_pair <= 0 or dt_pair > cfg.tau_LTP:
                continue
            if atom_i == atom_j:
                continue
            if atom_i >= world.k_count or atom_j >= world.k_count:
                continue
            A = world.k_pos[atom_i]
            B = world.k_pos[atom_j]
            bridge_indices = molecules_in_tube(world, A, B, cfg.r_bridge)
            if len(bridge_indices) == 0:
                continue
            # Periodic-corrected unit vector A→B
            v_AB = B - A
            v_AB -= box * np.round(v_AB / box)
            v_len = float(np.linalg.norm(v_AB))
            if v_len < 1e-9:
                continue
            u = v_AB / v_len
            # Plan E asymmetric reward physics — swap LTP/LTD when atom_j has
            # k_reward_polarity == -1 (fire_negative origin). Atoms with polarity
            # 0 (ambient default) take the existing alignment-based path unchanged.
            swap_ltp_ltd = (world.k_reward_polarity[atom_j] == -1)

            # G9: lock threshold for bridges that have already committed
            # to a pattern. Locked bridges are skipped entirely.
            lock_threshold = float(cfg.bridge_lock_threshold)
            # Per-molecule LTP/LTD decision based on orientation alignment
            for m in bridge_indices:
                strength_old = float(world.k_strength[m])
                # G9: skip locked bridges so previously-committed memory
                # patterns survive subsequent training.
                if lock_threshold > 0.0 and strength_old >= lock_threshold:
                    continue
                o = world.k_orientation[m]
                o_norm = float(np.linalg.norm(o))
                alignment = float(np.dot(o, u))
                # G8.2: alignment threshold tightens "aligned" so bridges
                # committed to a different pattern (alignment between 0 and
                # the threshold) get LTD instead of LTP. Default 0.0 keeps
                # legacy behaviour.
                strict_threshold = float(cfg.stdp_alignment_strict_threshold)
                # Determine LTP vs LTD based on alignment AND swap flag
                if o_norm < 1e-6:
                    # No prior orientation → LTP normally; LTD if swap
                    do_ltp = not swap_ltp_ltd
                elif alignment >= strict_threshold:
                    # Sufficiently aligned → LTP normally; LTD if swap
                    do_ltp = not swap_ltp_ltd
                else:
                    # Insufficiently aligned (or anti-aligned) → LTD normally
                    do_ltp = swap_ltp_ltd
                if do_ltp:
                    # LTP: strengthen and update orientation toward u
                    weight = cfg.delta_LTP * float(np.exp(-dt_pair / cfg.tau_LTP))
                    world.k_strength[m] = min(strength_old + weight, 1000.0)
                    strength_new = float(world.k_strength[m])
                    # G10: when a bridge crosses lock threshold AND both
                    # constituents (pre-atom and post-atom) share the
                    # same non-zero pattern_id, commit the bridge to that
                    # cell. This prevents cross-pattern bridges (e.g.
                    # visual1's atom firing with audio2's atom by
                    # coincidence during pair1 training) from being
                    # tagged with pattern_id=1.
                    if (lock_threshold > 0.0 and strength_new >= lock_threshold
                            and int(world.k_pattern_id[m]) == 0):
                        pid_i = int(world.k_pattern_id[atom_i])
                        pid_j = int(world.k_pattern_id[atom_j])
                        if pid_i != 0 and pid_i == pid_j:
                            world.k_pattern_id[m] = pid_i
                    if strength_new > 0:
                        o_new = (o * strength_old + u * weight) / strength_new
                        new_norm = float(np.linalg.norm(o_new))
                        if new_norm > 1e-9:
                            o_new = o_new / new_norm
                        world.k_orientation[m] = o_new
                    # G8: lateral inhibition — competing bridges nearby get
                    # LTD so different patterns settle on disjoint bridge
                    # subsets. Only applied on LTP events, not LTD events,
                    # because LTD already weakens the focal bridge.
                    if cfg.lateral_inhibition_enabled:
                        K = world.k_count
                        all_mol_mask = (world.k_alive[:K]
                                        & (world.k_level[:K] >= 5))
                        if all_mol_mask.any():
                            r_inh_sq = cfg.lateral_inhibition_radius ** 2
                            d_inh = world.k_pos[:K] - world.k_pos[m]
                            d_inh -= box * np.round(d_inh / box)
                            d_inh_sq = (d_inh * d_inh).sum(axis=1)
                            inhibit_mask = (
                                all_mol_mask
                                & (d_inh_sq <= r_inh_sq)
                                & (d_inh_sq > 0.0)
                            )
                            inhibit_mask[m] = False  # never inhibit self
                            # Only inhibit molecules NOT in the current
                            # tube (the tube was the "winning" set this
                            # tick).
                            for bidx in bridge_indices:
                                inhibit_mask[bidx] = False
                            inhib_idx = np.where(inhibit_mask)[0]
                            if len(inhib_idx) > 0:
                                inhib_weight = (cfg.delta_LTD
                                                * cfg.lateral_inhibition_strength
                                                * float(np.exp(-dt_pair
                                                               / cfg.tau_LTD)))
                                for ii in inhib_idx:
                                    s_ii = float(world.k_strength[int(ii)])
                                    # G9: locked bridges exempt from
                                    # lateral inhibition LTD too —
                                    # otherwise old patterns get bleed-
                                    # weakened by every new training pair.
                                    if (lock_threshold > 0.0
                                            and s_ii >= lock_threshold):
                                        continue
                                    world.k_strength[int(ii)] = max(
                                        s_ii - inhib_weight, 1.0)
                else:
                    # LTD: weaken only; orientation unchanged
                    weight = cfg.delta_LTD * float(np.exp(-dt_pair / cfg.tau_LTD))
                    world.k_strength[m] = max(strength_old - weight, 1.0)
                n_reinforcements += 1
    # Plan B.5 follow-up (deferred from mid-flight discovery): prune
    # firing_events older than tau_LTP. Without this the list grows
    # unboundedly across ticks, the O(N²) pair scan above goes quadratic
    # in run length, and double-counting amplifies LTP/LTD ~2× per pair.
    # All STDP behaviour is preserved because events older than tau_LTP
    # contribute no qualifying pairs anyway (dt_pair > tau_LTP would be
    # filtered by the inner continue).
    cutoff = world.t - cfg.tau_LTP
    if events and events[0][0] < cutoff:
        world.firing_events = [e for e in events if e[0] >= cutoff]
    return n_reinforcements


def synaptic_transmission(world, dt: float) -> int:
    """Plan B: strong oriented bridges deposit charge into post-synaptic atoms.

    For each level-5+ molecule with k_strength ≥ synaptic_transmission_threshold
    AND |k_orientation| > 0.5 (i.e. it has a stable, well-defined direction):
        Find alive vibrations within r_bridge of the molecule.
        For each: compute alignment = dot(v_unit, orientation_unit).
        If alignment > 0: deposit alignment * w_synaptic * dt charge into every
        level-4 atom within r_bridge of (M_pos + r_bridge * orientation).

    Returns the count of (vibration, post-atom) charge-deposit events.
    """
    cfg = world.config
    if not cfg.stdp_enabled:
        return 0
    K = world.k_count
    if K == 0:
        return 0

    threshold = cfg.synaptic_transmission_threshold
    bridge_mask = (
        world.k_alive[:K]
        & (world.k_level[:K] >= 5)
        & (world.k_strength[:K] >= threshold)
    )
    if not bridge_mask.any():
        return 0
    bridge_indices = np.where(bridge_mask)[0]

    box = np.asarray(cfg.box_size, dtype=np.float64)
    r_bridge = cfg.r_bridge
    r_bridge_sq = r_bridge ** 2
    w_synaptic = cfg.synaptic_transmission_strength
    n_events = 0

    n_alive_v = world.n_alive
    if n_alive_v == 0:
        return 0
    s_pos = world.s_pos[:n_alive_v]
    s_vel = world.s_vel[:n_alive_v]
    s_alive = world.s_alive[:n_alive_v]

    # Pre-build atom-position matrix for post-synaptic search
    atom_mask = world.k_alive[:K] & (world.k_level[:K] == 4)
    if not atom_mask.any():
        return 0
    atom_indices = np.where(atom_mask)[0]
    atom_pos = world.k_pos[atom_indices]

    for m in bridge_indices:
        M = world.k_pos[m]
        o = world.k_orientation[m]
        o_norm = float(np.linalg.norm(o))
        if o_norm <= 0.5:
            continue
        o_unit = o / o_norm

        # Vibrations within r_bridge of M (periodic min-image)
        d_vM = s_pos - M
        d_vM -= box * np.round(d_vM / box)
        d_vM_sq = (d_vM * d_vM).sum(axis=1)
        in_range = (d_vM_sq <= r_bridge_sq) & s_alive
        if not in_range.any():
            continue
        v_in_range_indices = np.where(in_range)[0]

        # G3: post-synaptic search at one or more samples along o_unit.
        # Sample k (k=0..N-1) is at distance (k+1) * r_bridge from M.
        # n_samples=1 (default) ↔ legacy behaviour (single sample at r_bridge).
        # Higher values extend reach so bridges placed mid-segment can still
        # find post-atoms at the destination port end of the orientation ray.
        n_samples = max(1, int(cfg.synaptic_post_search_samples))
        post_mask = np.zeros(atom_pos.shape[0], dtype=np.bool_)
        for k in range(n_samples):
            distance = (k + 1) * r_bridge
            post_centre = M + distance * o_unit
            d_aP = atom_pos - post_centre
            d_aP -= box * np.round(d_aP / box)
            d_aP_sq = (d_aP * d_aP).sum(axis=1)
            post_mask |= d_aP_sq <= r_bridge_sq
        if not post_mask.any():
            continue
        post_atom_indices = atom_indices[post_mask]

        for v_idx in v_in_range_indices:
            v_vel = s_vel[v_idx]
            v_speed = float(np.linalg.norm(v_vel))
            if v_speed < 1e-9:
                continue
            alignment = float(np.dot(v_vel / v_speed, o_unit))
            if alignment <= 0:
                continue
            charge_increment = alignment * w_synaptic * dt
            for a_idx in post_atom_indices:
                world.k_charge[a_idx] += charge_increment
                n_events += 1
    return n_events


def apply_bridge_atom_propagation(world, dt: float) -> int:
    """G6: when a level-4 atom A fires this tick AND there is a strong
    oriented bridge molecule near A pointing toward another atom B, deposit
    charge directly into B without requiring vibrations to travel from A
    through the bridge to B.

    This decouples synaptic transmission from vibration-travel time and
    closes the M4 chain at small sim-time scopes. Models the propagation
    step of biological chemical synapses, where action-potential transit
    between presynaptic and postsynaptic neurons is fast relative to
    individual neurotransmitter molecules diffusing across the cleft.

    Default off via `cfg.bridge_atom_propagation_enabled = False`.

    Returns the count of (pre-atom, bridge, post-atom) propagation events
    triggered this tick.
    """
    cfg = world.config
    if not cfg.bridge_atom_propagation_enabled:
        return 0
    K = world.k_count
    if K == 0:
        return 0

    threshold = cfg.synaptic_transmission_threshold
    bridge_mask = (
        world.k_alive[:K]
        & (world.k_level[:K] >= 5)
        & (world.k_strength[:K] >= threshold)
    )
    if not bridge_mask.any():
        return 0
    bridge_indices = np.where(bridge_mask)[0]

    box = np.asarray(cfg.box_size, dtype=np.float64)
    r_bridge = cfg.r_bridge
    r_bridge_sq = r_bridge ** 2
    n_samples = max(1, int(cfg.synaptic_post_search_samples))
    propagation_strength = cfg.bridge_atom_propagation_strength

    atom_mask = world.k_alive[:K] & (world.k_level[:K] == 4)
    if not atom_mask.any():
        return 0
    atom_indices = np.where(atom_mask)[0]
    atom_pos = world.k_pos[atom_indices]

    # Restrict to firings appended this tick (t_fire == world.t).
    t_now = world.t
    n_events = 0
    for t_fire, atom_idx in world.firing_events:
        if t_fire != t_now:
            continue
        if atom_idx >= K or not world.k_alive[atom_idx]:
            continue
        if int(world.k_level[atom_idx]) != 4:
            continue
        A_pos = world.k_pos[atom_idx]

        # G10: pattern-cell gating. If the firing atom has a non-zero
        # pattern_id (i.e. was committed to a specific pattern during
        # training), restrict bridge candidates to ones that share that
        # pattern_id OR are unassigned (pattern_id=0, ambient).
        firing_pattern = int(world.k_pattern_id[atom_idx])

        # Find strong oriented bridges within r_bridge of the firing atom.
        d_AM = world.k_pos[bridge_indices] - A_pos
        d_AM -= box * np.round(d_AM / box)
        d_AM_sq = (d_AM * d_AM).sum(axis=1)
        nearby_mask = d_AM_sq <= r_bridge_sq

        # G10: strict pattern-cell routing. When the firing atom has a
        # non-zero pattern_id, only fire bridges with the EXACT same
        # pattern_id. Ambient bridges (pattern_id=0) are excluded so
        # they can't cross-talk between patterns. Requires the caller
        # to pre-tag bridges (e.g. by position) for the chain to stay
        # active in test scenarios where ambient bridges previously
        # carried the signal.
        if firing_pattern != 0:
            bridge_pids = world.k_pattern_id[bridge_indices]
            pattern_mask = (bridge_pids == firing_pattern)
            nearby_mask = nearby_mask & pattern_mask
        if not nearby_mask.any():
            continue
        nearby_bridge_indices = bridge_indices[nearby_mask]

        # G9.5: winner-take-all — fire only the single strongest oriented
        # bridge near this firing atom. Without this, every bridge in
        # radius fires, so different patterns' bridges all activate
        # together when their video atoms are adjacent in the port. WTA
        # forces selectivity: each firing atom picks its committed bridge
        # by max strength and fires only that one.
        if cfg.bridge_atom_propagation_winner_take_all:
            best_m = -1
            best_score = -1.0
            for m in nearby_bridge_indices:
                o = world.k_orientation[m]
                o_norm = float(np.linalg.norm(o))
                if o_norm <= 0.5:
                    continue
                score = float(world.k_strength[m]) * o_norm
                if score > best_score:
                    best_score = score
                    best_m = int(m)
            if best_m < 0:
                continue
            nearby_bridge_indices = np.array([best_m], dtype=np.int64)

        for m in nearby_bridge_indices:
            o = world.k_orientation[m]
            o_norm = float(np.linalg.norm(o))
            if o_norm <= 0.5:
                continue
            o_unit = o / o_norm
            M = world.k_pos[m]

            # Sign convention: orientation points from pre to post. We want
            # post-atom B that is "ahead" of M in direction o_unit. Sample at
            # d = r_bridge, 2 * r_bridge, ..., n_samples * r_bridge.
            post_mask = np.zeros(atom_pos.shape[0], dtype=np.bool_)
            for k in range(n_samples):
                distance = (k + 1) * r_bridge
                post_centre = M + distance * o_unit
                d_aP = atom_pos - post_centre
                d_aP -= box * np.round(d_aP / box)
                d_aP_sq = (d_aP * d_aP).sum(axis=1)
                post_mask |= d_aP_sq <= r_bridge_sq

            # Don't propagate back to the firing atom itself
            if atom_idx in atom_indices:
                self_local_idx = int(np.where(atom_indices == atom_idx)[0][0])
                post_mask[self_local_idx] = False

            if not post_mask.any():
                continue
            post_atom_indices = atom_indices[post_mask]
            for a_idx in post_atom_indices:
                world.k_charge[int(a_idx)] += propagation_strength
                n_events += 1
    return n_events


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
        end = int(world.k_comp_end[i])
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


@njit(cache=True)
def _bind_check_pairs_njit(
    candidate_i: np.ndarray, candidate_j: np.ndarray, n_candidates: int,
    k_pos: np.ndarray, k_alive: np.ndarray, k_locked_this_tick: np.ndarray,
    k_freq: np.ndarray, k_pol: np.ndarray, k_level: np.ndarray,
    box: np.ndarray, r2_sq: float,
    fmin_ratio: float, fmax_ratio: float,
    upgrade_table: np.ndarray, fusion_table: np.ndarray, mol_fusion_enabled: bool,
) -> tuple:
    """JIT core for bind_nodes_upward.

    For each candidate pair (i, j) in order, check all binding gates:
    alive, locked, level-table lookup, polarity, distance, decade, freq-ratio.
    Returns parallel arrays (out_i, out_j, out_target, n_out) of pairs that
    pass all gates, preserving input order so the Python wrapper can apply
    break-semantics correctly.

    Note: k_alive and k_locked_this_tick are snapshots at call time; the
    Python wrapper enforces the break / single-bind-per-i rule by checking
    the lock array after each allocation.
    """
    out_i = np.zeros(n_candidates, dtype=np.int32)
    out_j = np.zeros(n_candidates, dtype=np.int32)
    out_target = np.zeros(n_candidates, dtype=np.int8)
    n_out = 0
    for k in range(n_candidates):
        i = candidate_i[k]
        j = candidate_j[k]
        if not k_alive[i] or not k_alive[j]:
            continue
        if k_locked_this_tick[i] or k_locked_this_tick[j]:
            continue
        # Level-table lookup
        li = int(k_level[i])
        lj = int(k_level[j])
        target = upgrade_table[li, lj]
        if target == -1 and mol_fusion_enabled:
            target = fusion_table[li, lj]
        if target == -1:
            continue
        # Polarity gate
        if k_pol[i] == k_pol[j]:
            continue
        # Periodic distance squared
        dx = k_pos[i, 0] - k_pos[j, 0]
        dy = k_pos[i, 1] - k_pos[j, 1]
        dz = k_pos[i, 2] - k_pos[j, 2]
        dx -= box[0] * round(dx / box[0])
        dy -= box[1] * round(dy / box[1])
        dz -= box[2] * round(dz / box[2])
        d2 = dx*dx + dy*dy + dz*dz
        if d2 >= r2_sq:
            continue
        # Decade gate — inline log10 floor
        f1 = k_freq[i]
        f2 = k_freq[j]
        if f1 <= 0.0 or f2 <= 0.0:
            continue
        d1 = int(np.floor(np.log10(f1)))
        d2_dec = int(np.floor(np.log10(f2)))
        if d1 != d2_dec:
            continue
        # Freq ratio gate
        if f1 < f2:
            ratio = (f2 - f1) / f1
        else:
            ratio = (f1 - f2) / f2
        if ratio < fmin_ratio or ratio > fmax_ratio:
            continue
        # Pair passes all gates
        out_i[n_out] = i
        out_j[n_out] = j
        out_target[n_out] = target
        n_out += 1
    return out_i, out_j, out_target, n_out


def _gather_leaf_vibration_indices(world, node_idx: int) -> np.ndarray:
    """Walk the composition tree from a node down to its leaf vibrations.

    Returns an int64 array of vibration indices (level-1 electrons store
    vibration indices in their composition span — k_comp_kind == 0).
    Internal nodes (k_comp_kind != 0) store node indices; they are traversed
    recursively via an explicit stack.
    """
    out: list[int] = []
    stack = [int(node_idx)]
    while stack:
        i = stack.pop()
        start = int(world.k_comp_offset[i])
        end = int(world.k_comp_end[i])
        if int(world.k_comp_kind[i]) == 0:
            # Leaf node — composition span is vibration indices
            for k in range(start, end):
                out.append(int(world.k_comp_indices[k]))
        else:
            # Internal node — composition span is node indices
            for k in range(start, end):
                stack.append(int(world.k_comp_indices[k]))
    return np.array(out, dtype=np.int64)


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
    K = world.k_count
    grid = build_grid(world.k_pos[:K], world.k_alive[:K], box, r2)

    if cfg.numba_jit_enabled:
        # Build the full candidate list in Python (spatial-hash query stays
        # in Python; it is already JIT'd internally).  Preserve the same
        # iteration order as the legacy path so break-semantics are respected.
        cand_i_list: list[int] = []
        cand_j_list: list[int] = []
        for i in range(K):
            if not world.k_alive[i] or world.k_locked_this_tick[i]:
                continue
            nbrs = neighbors_of(grid, world.k_pos[i], box, r2,
                                 exclude_self=True, query_index=i)
            for j in nbrs:
                if j <= i:
                    continue
                cand_i_list.append(i)
                cand_j_list.append(j)

        n_candidates = len(cand_i_list)
        if n_candidates == 0:
            return 0

        candidate_i = np.array(cand_i_list, dtype=np.int32)
        candidate_j = np.array(cand_j_list, dtype=np.int32)

        out_i, out_j, out_target, n_out = _bind_check_pairs_njit(
            candidate_i, candidate_j, n_candidates,
            world.k_pos[:K], world.k_alive[:K], world.k_locked_this_tick[:K],
            world.k_freq[:K], world.k_pol[:K], world.k_level[:K],
            box, r2_sq, fmin_ratio, fmax_ratio,
            _UPGRADE_TARGET_ARRAY, _UPGRADE_TARGET_FUSION_ARRAY,
            bool(cfg.mol_fusion_enabled),
        )

        # Process JIT-returned pairs in order, enforcing break-per-i semantics:
        # after a successful bind, both i and j are locked so subsequent pairs
        # involving either are skipped — exactly matching the legacy `break`.
        for k in range(n_out):
            i = int(out_i[k])
            j = int(out_j[k])
            target = int(out_target[k])
            # Re-check liveness and lock after earlier iterations may have
            # consumed these slots.
            if not world.k_alive[i] or world.k_locked_this_tick[i]:
                continue
            if not world.k_alive[j] or world.k_locked_this_tick[j]:
                continue
            mid = periodic_midpoint(world.k_pos[i], world.k_pos[j], box)
            f1 = world.k_freq[i]
            f2 = world.k_freq[j]
            new_freq = f1 + f2
            new_pol = bool(world.rng.random() < 0.5)
            constituents = np.array([i, j], dtype=np.int32)
            new_node = world.allocate_node(mid, new_freq, new_pol, level=target,
                                           constituents=constituents, comp_kind=1)
            if new_node < 0:
                # Capacity exhausted (graceful_capacity mode); stop.
                break
            # Plan E: propagate reward polarity into newly formed atoms (level 4)
            if target == 4:
                vib_indices = _gather_leaf_vibration_indices(world, new_node)
                if len(vib_indices) > 0:
                    polarities = world.s_reward_polarity[vib_indices]
                    if (polarities != 0).all() and (polarities == polarities[0]).all():
                        world.k_reward_polarity[new_node] = int(polarities[0])
                    # else: stays at default 0 (mixed or conflicting)
            _kill_node(world, i)
            _kill_node(world, j)
            world.k_locked_this_tick[i] = True
            world.k_locked_this_tick[j] = True
            formed += 1
        return formed
    else:
        # Legacy Python path — preserved verbatim for regression diagnosis.
        for i in range(K):
            if not world.k_alive[i] or world.k_locked_this_tick[i]:
                continue
            nbrs = neighbors_of(grid, world.k_pos[i], box, r2,
                                 exclude_self=True, query_index=i)
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
                new_node = world.allocate_node(mid, new_freq, new_pol, level=target,
                                               constituents=constituents, comp_kind=1)
                if new_node < 0:
                    return formed
                # Plan E: propagate reward polarity into newly formed atoms (level 4)
                if target == 4:
                    vib_indices = _gather_leaf_vibration_indices(world, new_node)
                    if len(vib_indices) > 0:
                        polarities = world.s_reward_polarity[vib_indices]
                        if (polarities != 0).all() and (polarities == polarities[0]).all():
                            world.k_reward_polarity[new_node] = int(polarities[0])
                        # else: stays at default 0 (mixed or conflicting)
                _kill_node(world, i)
                _kill_node(world, j)
                world.k_locked_this_tick[i] = True
                world.k_locked_this_tick[j] = True
                formed += 1
                break

        return formed


@njit(cache=True)
def _decay_unstable_njit(k_alive: np.ndarray, k_level: np.ndarray,
                         k_birth: np.ndarray, rolls: np.ndarray,
                         t: float, pair_decay_time: float,
                         triad_decay_time: float, K: int,
                         dt: float) -> np.ndarray:
    """JIT core for decay_unstable_nodes.

    Returns a boolean array of length K marking which slots must be killed.
    The Python wrapper handles RNG generation and free-list bookkeeping.
    Decay formula: p = dt / tau  (linear per-tick probability, matching the
    legacy Python path exactly).
    """
    decayed = np.zeros(K, dtype=np.bool_)
    for i in range(K):
        if not k_alive[i]:
            continue
        level = k_level[i]
        if level == 2:
            tau = pair_decay_time
        elif level == 3:
            tau = triad_decay_time
        else:
            continue
        # Match the existing Python decay formula exactly: p = dt / tau.
        if rolls[i] < dt / tau:
            decayed[i] = True
    return decayed


def decay_unstable_nodes(world, dt: float) -> int:
    """Probabilistic exponential decay of pairs (level 2) and triads (level 3).

    Atoms (level 4) are permanent. Electrons (level 1) are handled by the
    ambient_regeneration channel, not here.

    When cfg.numba_jit_enabled is True, the inner decision loop runs in a
    @njit core. RNG rolls are pre-generated in Python so the RNG stream is
    identical to the legacy path. Free-list bookkeeping and constituent
    revival always run in Python.
    """
    cfg = world.config
    K = world.k_count
    if K == 0:
        return 0

    if cfg.numba_jit_enabled:
        # Pre-generate RNG rolls for qualifying slots only — one roll per alive
        # level-2/3 slot, in ascending slot order — so the RNG stream is
        # identical to the legacy Python path given the same seed.
        k_alive_slice = world.k_alive[:K]
        k_level_slice = world.k_level[:K]
        qualifying = np.where(
            k_alive_slice & ((k_level_slice == 2) | (k_level_slice == 3))
        )[0]
        n_qualifying = len(qualifying)
        if n_qualifying == 0:
            return 0
        batch_rolls = world.rng.random(n_qualifying)
        # Build a per-slot roll array (size K) so the JIT core can index by
        # slot without needing a ragged mapping.  Non-qualifying slots get 1.0
        # (guaranteed not to decay).
        raw_rolls = np.ones(K, dtype=np.float64)
        raw_rolls[qualifying] = batch_rolls
        decayed_mask = _decay_unstable_njit(
            k_alive_slice, k_level_slice, world.k_birth[:K],
            raw_rolls, world.t, cfg.pair_decay_time, cfg.triad_decay_time,
            K, dt,
        )
        n_decayed = 0
        for i in range(K):
            if decayed_mask[i]:
                start = int(world.k_comp_offset[i])
                end = int(world.k_comp_end[i])
                _kill_node(world, i)
                for j in range(start, end):
                    idx = int(world.k_comp_indices[j])
                    # Revive the constituent; if _kill_node pushed it onto the
                    # free list (ref count dropped to 0), remove it first so
                    # the slot isn't recycled out from under the revived node.
                    if idx in world._free_slots_set:
                        world._free_slots_set.discard(idx)
                        try:
                            world._free_slots.remove(idx)
                        except ValueError:
                            pass
                    world.k_alive[idx] = True
                n_decayed += 1
        return n_decayed
    else:
        # Legacy Python path — preserved for regression diagnosis.
        decay_time = {2: cfg.pair_decay_time, 3: cfg.triad_decay_time}
        rng = world.rng
        decayed = 0
        for i in range(K):
            if not world.k_alive[i]:
                continue
            level = int(world.k_level[i])
            if level not in (2, 3):
                continue
            tau = decay_time[level]
            p = dt / tau
            if rng.random() < p:
                start = world.k_comp_offset[i]
                end = world.k_comp_end[i]
                _kill_node(world, i)
                for j in range(start, end):
                    idx = int(world.k_comp_indices[j])
                    # Revive the constituent; if _kill_node pushed it onto the
                    # free list (ref count dropped to 0), remove it first so
                    # the slot isn't recycled out from under the revived node.
                    if idx in world._free_slots_set:
                        world._free_slots_set.discard(idx)
                        try:
                            world._free_slots.remove(idx)
                        except ValueError:
                            pass
                    world.k_alive[idx] = True
                decayed += 1
        return decayed


@njit(cache=True)
def _decay_high_level_njit(k_alive: np.ndarray, k_level: np.ndarray,
                            k_strength: np.ndarray, rolls: np.ndarray,
                            lambda_dec_mol: float, dt: float,
                            K: int) -> np.ndarray:
    """JIT core for decay_high_level_nodes.

    Returns a boolean array of length K marking which slots must be killed.
    rolls has length == number of qualifying (alive, level >= 5) slots.
    Slots are visited in ascending index order; the k-th qualifying slot
    consumes rolls[k]. Non-qualifying slots are never killed.
    Decay formula: p = lambda_dec_mol * dt / max(strength, 1.0)
    """
    decayed = np.zeros(K, dtype=np.bool_)
    roll_idx = 0
    for i in range(K):
        if not k_alive[i]:
            continue
        if k_level[i] < 5:
            continue
        strength = k_strength[i]
        if strength < 1.0:
            strength = 1.0
        p = lambda_dec_mol * dt / strength
        if rolls[roll_idx] < p:
            decayed[i] = True
        roll_idx += 1
    return decayed


def decay_high_level_nodes(world, dt: float) -> int:
    """R2: strength-modulated decay for level-5+ molecules.

    Per-tick decay probability for each level-5+ alive node:
        p = lambda_dec_mol * dt / max(strength, 1.0)

    When a molecule decays, it disappears (k_alive=False). Constituent
    atoms (level 4) inside its composition span are not destroyed — they
    live in their own slots and stay alive=True there.

    Returns the count of nodes that decayed this tick.

    Plan A.5 Task 10: JIT-compiled inner loop. RNG rolls are pre-generated
    in Python and passed to the @njit core so the RNG stream is identical
    to the legacy Python path. The Python wrapper handles _kill_node
    bookkeeping (free-list management). Gated behind cfg.numba_jit_enabled.
    """
    cfg = world.config
    if cfg.lambda_dec_mol <= 0.0:
        return 0
    K = world.k_count
    if K == 0:
        return 0

    if cfg.numba_jit_enabled:
        # Identify qualifying slots (alive, level >= 5) in Python; consume
        # exactly that many rolls. Order matches legacy path.
        n_qualifying = 0
        for i in range(K):
            if world.k_alive[i] and world.k_level[i] >= 5:
                n_qualifying += 1
        if n_qualifying == 0:
            return 0
        rolls = world.rng.random(n_qualifying)
        decayed = _decay_high_level_njit(
            world.k_alive[:K], world.k_level[:K], world.k_strength[:K],
            rolls, cfg.lambda_dec_mol, dt, K,
        )
        n_decayed = 0
        for i in range(K):
            if decayed[i]:
                _kill_node(world, i)
                n_decayed += 1
        return n_decayed
    else:
        # Legacy Python path — preserved for regression diagnosis.
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
                end = world.k_comp_end[i]
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


@njit(cache=True)
def _apply_scale_repulsion_njit(
    k_pos: np.ndarray,
    k_vel: np.ndarray,
    k_alive: np.ndarray,
    k_freq: np.ndarray,
    k_level: np.ndarray,
    box: np.ndarray,
    repulsion_k: float,
    repulsion_threshold_ratio: float,
    dt: float,
    K: int,
) -> None:
    """JIT core for apply_scale_repulsion. Modifies k_vel in place.

    Plan A.5 Task 12: O(k²) double-loop over all alive node pairs. Implements
    §4.6 scale-separation repulsion with periodic minimum-image distance.
    Equivalent to the Python path when repulsion_cell_size >= box_size (all
    pairs are neighbours), which is the typical production configuration.
    """
    for i in range(K):
        if not k_alive[i]:
            continue
        f_i = k_freq[i]
        mass_i = float(k_level[i])
        for j in range(K):
            if i == j:
                continue
            if not k_alive[j]:
                continue
            f_j = k_freq[j]
            if f_i > f_j:
                ratio = f_i / f_j
            else:
                ratio = f_j / f_i
            if ratio <= repulsion_threshold_ratio:
                continue
            # Direction vector from j to i (minimum-image periodic)
            dx = k_pos[i, 0] - k_pos[j, 0]
            dy = k_pos[i, 1] - k_pos[j, 1]
            dz = k_pos[i, 2] - k_pos[j, 2]
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
            r = (r2) ** 0.5
            # F_magnitude = k * (ratio - threshold) / r²
            F_mag = repulsion_k * (ratio - repulsion_threshold_ratio) / r2
            ax = F_mag * dx / r / mass_i
            ay = F_mag * dy / r / mass_i
            az = F_mag * dz / r / mass_i
            k_vel[i, 0] += ax * dt
            k_vel[i, 1] += ay * dt
            k_vel[i, 2] += az * dt


def apply_scale_repulsion(world, dt: float) -> None:
    """§4.6 scale-separation repulsion.

    Plan A.5 Task 12: JIT-compiled inner loop. No RNG; pure deterministic
    numerical. Gated behind cfg.numba_jit_enabled.
    """
    cfg = world.config
    if cfg.repulsion_k == 0.0 or world.k_count == 0:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)
    K = world.k_count
    if cfg.numba_jit_enabled:
        _apply_scale_repulsion_njit(
            world.k_pos[:K], world.k_vel[:K], world.k_alive[:K], world.k_freq[:K],
            world.k_level[:K],
            box, cfg.repulsion_k, cfg.repulsion_threshold_ratio,
            dt, K,
        )
    else:
        # Legacy Python path — preserved for regression diagnosis.
        cell = cfg.repulsion_cell_size
        threshold = cfg.repulsion_threshold_ratio
        grid = build_grid(world.k_pos[:K], world.k_alive[:K], box, cell)

        for i in range(K):
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


@njit(cache=True)
def _move_nodes_njit(k_pos: np.ndarray, k_vel: np.ndarray, k_alive: np.ndarray,
                     box: np.ndarray, dt: float, K: int) -> None:
    """JIT core for move_nodes. Modifies k_pos in place with periodic wrap."""
    for i in range(K):
        if not k_alive[i]:
            continue
        for d in range(3):
            k_pos[i, d] = (k_pos[i, d] + k_vel[i, d] * dt) % box[d]


def move_nodes(world, dt: float) -> None:
    """Apply k_vel to k_pos with periodic wrap. Atoms move slowly because of mass.

    Plan A.5 Task 11: JIT-compiled inner loop. No RNG; deterministic numerical.
    Gated behind cfg.numba_jit_enabled.
    """
    cfg = world.config
    K = world.k_count
    if K == 0:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)
    if cfg.numba_jit_enabled:
        _move_nodes_njit(world.k_pos, world.k_vel, world.k_alive, box, dt, K)
    else:
        # Legacy Python path — preserved for regression diagnosis.
        for i in range(K):
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

    # Plan B: oriented bridges transmit aligned vibrations as charge before
    # the threshold check, so a strong bridge can drive this-tick firing.
    synaptic_transmission(world, dt)

    # 3. Fire: any atom with charge ≥ theta_fire and not refractory emits.
    can_fire = (world.k_charge[atom_indices] >= cfg.theta_fire) & (
        world.t >= world.k_refractory_until[atom_indices]
    )
    # G12: firing-eligibility gating during training. When a pattern is
    # active, atoms with a mismatched non-zero pattern_id are prevented
    # from firing — even if charged. This stops cross-pattern STDP
    # causal pairs from forming entirely at the firing-event source,
    # not just downstream during bridge propagation.
    if cfg.firing_eligibility_gate and int(world.active_pattern_id) != 0:
        active = int(world.active_pattern_id)
        atom_pids = world.k_pattern_id[atom_indices]
        # Allow ambient (0) and matching-pattern atoms; suppress others.
        eligibility = (atom_pids == 0) | (atom_pids == active)
        can_fire = can_fire & eligibility
    firing_atoms = atom_indices[can_fire]

    # G11: sparse-firing winner-take-all per port. When enabled, only the
    # top-K atoms per port (by charge) fire each tick. This forces sparse
    # pattern-specific activation: different stimuli charge different
    # specific atoms, so different bridges fire downstream and the chain
    # output is selective by pattern, not broadband.
    if cfg.sparse_firing_enabled and len(firing_atoms) > 0:
        top_k = max(1, int(cfg.sparse_firing_top_k))
        # Group firing atoms by which port they're in. Atoms outside any
        # named port fall in the "other" group.
        ports = []
        if cfg.audio_io_enabled:
            ports.append(("audio_in", cfg.audio_input_port_origin,
                           cfg.audio_input_port_size))
            ports.append(("audio_out", cfg.audio_output_port_origin,
                           cfg.audio_output_port_size))
        if cfg.video_io_enabled:
            ports.append(("video_in", cfg.video_input_port_origin,
                           cfg.video_input_port_size))
        if ports:
            keep = []
            assigned = np.zeros(len(firing_atoms), dtype=np.bool_)
            for _name, port_o, port_s in ports:
                in_port = np.zeros(len(firing_atoms), dtype=np.bool_)
                for k_i, ai in enumerate(firing_atoms):
                    if assigned[k_i]:
                        continue
                    p = world.k_pos[ai]
                    if (port_o[0] <= p[0] <= port_o[0] + port_s[0]
                            and port_o[1] <= p[1] <= port_o[1] + port_s[1]
                            and port_o[2] <= p[2] <= port_o[2] + port_s[2]):
                        in_port[k_i] = True
                        assigned[k_i] = True
                if in_port.any():
                    port_indices = np.where(in_port)[0]
                    port_charges = world.k_charge[firing_atoms[port_indices]]
                    # Pick top-K by charge
                    n_keep = min(top_k, len(port_indices))
                    top = np.argpartition(-port_charges, n_keep - 1)[:n_keep]
                    keep.extend(port_indices[top].tolist())
            # Atoms outside any port: keep all (they're rare and not
            # subject to discrimination).
            for k_i in range(len(firing_atoms)):
                if not assigned[k_i]:
                    keep.append(k_i)
            firing_atoms = firing_atoms[np.array(sorted(keep), dtype=np.int64)]
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


def apply_speech_loop(world, dt: float) -> int:
    """Plan F: port-to-port firing coupling.

    When an atom inside the audio input port fires THIS TICK, deposit
    `speech_loop_burst_size` vibrations at random positions inside the audio
    output port, all at the firing atom's frequency (with small Gaussian
    jitter `speech_loop_jitter_hz`). Models biological auditory feedback —
    the vocaliser hearing their own utterances closes the auditory-motor
    loop that lets STDP bind input perceptions to output productions.

    Default off via `cfg.speech_loop_strength=0.0`. When > 0, the rule fires
    on each input-port atom-firing event from the current tick.

    Returns count of ghost-burst events triggered this tick.
    """
    cfg = world.config
    if cfg.speech_loop_strength <= 0.0:
        return 0

    burst_size = cfg.speech_loop_burst_size
    if burst_size <= 0:
        return 0

    ai_origin = np.asarray(cfg.audio_input_port_origin, dtype=np.float64)
    ai_size = np.asarray(cfg.audio_input_port_size, dtype=np.float64)
    ao_origin = np.asarray(cfg.audio_output_port_origin, dtype=np.float64)
    ao_size = np.asarray(cfg.audio_output_port_size, dtype=np.float64)

    # Only firings appended this tick (their timestamp == world.t since
    # neuron_dynamics ran during this tick before apply_speech_loop).
    t_now = world.t
    events = world.firing_events
    n_events = 0
    rng = world.rng

    for t_fire, atom_idx in events:
        # Heuristic: events appended this tick have t_fire close to t_now.
        # neuron_dynamics uses world.t at append time; tick advances world.t
        # AFTER apply_speech_loop. So all "this tick" events have t_fire == t_now.
        if t_fire != t_now:
            continue
        if atom_idx >= world.k_count or not world.k_alive[atom_idx]:
            continue
        pos = world.k_pos[atom_idx]
        # Inside audio input port?
        if not (ai_origin[0] <= pos[0] <= ai_origin[0] + ai_size[0] and
                ai_origin[1] <= pos[1] <= ai_origin[1] + ai_size[1] and
                ai_origin[2] <= pos[2] <= ai_origin[2] + ai_size[2]):
            continue
        f_atom = float(world.k_freq[atom_idx])
        pol_atom = bool(world.k_pol[atom_idx])

        # G8.1: Deposit ghosts at the freq-mapped POSITION inside the
        # audio output port (inverse log-mapping of f_atom), not at random
        # positions. read_from_substrate decodes audio_out atom firings via
        # position → freq, so depositing at f_atom's position concentrates
        # the chain's effect on the audio_out atom at that exact freq, not
        # any audio_out atom that happens to be near a random ghost. This
        # is the load-bearing change that lets pattern discrimination work:
        # the input freq is conserved through the speech-loop.
        log_norm = ((np.log(max(f_atom, cfg.audio_freq_min))
                     - np.log(cfg.audio_freq_min))
                    / (np.log(cfg.audio_freq_max) - np.log(cfg.audio_freq_min)))
        log_norm = max(0.0, min(1.0, log_norm))
        target_x = ao_origin[0] + log_norm * ao_size[0]

        # Allocate burst_size vibrations at the freq-mapped X with random
        # Y/Z inside the audio output port. Gracefully no-op if buffer is
        # full.
        free_idx = np.where(~world.s_alive)[0]
        n_to_inject = min(burst_size, len(free_idx))
        if n_to_inject == 0:
            continue
        for k in range(n_to_inject):
            i = int(free_idx[k])
            # Small jitter on x (within ±0.5 unit) so multiple ghosts
            # don't collide at the exact same position
            x_jitter = float(rng.normal(0.0, 0.5))
            world.s_pos[i] = (
                max(ao_origin[0],
                    min(ao_origin[0] + ao_size[0], target_x + x_jitter)),
                ao_origin[1] + float(rng.random()) * ao_size[1],
                ao_origin[2] + float(rng.random()) * ao_size[2],
            )
            world.s_vel[i] = 0.0
            world.s_freq[i] = f_atom + float(rng.normal(0.0, cfg.speech_loop_jitter_hz))
            world.s_pol[i] = pol_atom
            world.s_alive[i] = True
        if n_to_inject > 0:
            world.n_alive = max(world.n_alive, int(free_idx[:n_to_inject].max()) + 1)
        n_events += 1
    return n_events


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
    apply_bridge_atom_propagation(world, dt)  # NEW (G6) — direct atom→atom charge through strong bridges
    apply_stdp(world)              # NEW (Plan B)
    apply_speech_loop(world, dt)   # NEW (Plan F)
    world.t += dt

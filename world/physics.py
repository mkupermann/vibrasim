from __future__ import annotations
import math
import numpy as np
from numba import njit
from world.spatial import build_grid, neighbors_of, periodic_distance_sq, periodic_midpoint


def move_vibrations(
    s_pos: np.ndarray,
    s_vel: np.ndarray,
    s_alive: np.ndarray,
    box: np.ndarray,
    dt: float,
) -> None:
    """3D motion with periodic-wrap on all three axes. Pure numpy."""
    mask = s_alive
    s_pos[mask] = (s_pos[mask] + s_vel[mask] * dt) % box


def _bind_vibrations_check_pairs_numpy(
    candidate_i, candidate_j, s_pos, s_alive, s_locked,
    s_freq, s_pol, box, r1_sq, fmin_ratio, fmax_ratio,
):
    """Vectorized numpy pair filter for vibration binding. No Numba."""
    ci = candidate_i
    cj = candidate_j
    if len(ci) == 0:
        return np.empty(0, np.int32), np.empty(0, np.int32), np.empty(0), np.empty((0, 3))
    # Masks
    alive_ok = s_alive[ci] & s_alive[cj]
    lock_ok = ~s_locked[ci] & ~s_locked[cj]
    pol_ok = s_pol[ci] != s_pol[cj]
    mask = alive_ok & lock_ok & pol_ok
    ci, cj = ci[mask], cj[mask]
    if len(ci) == 0:
        return np.empty(0, np.int32), np.empty(0, np.int32), np.empty(0), np.empty((0, 3))
    # Periodic distance
    d = s_pos[ci] - s_pos[cj]
    d -= box * np.round(d / box)
    d2 = (d * d).sum(axis=1)
    dist_ok = d2 < r1_sq
    ci, cj, d = ci[dist_ok], cj[dist_ok], d[dist_ok]
    if len(ci) == 0:
        return np.empty(0, np.int32), np.empty(0, np.int32), np.empty(0), np.empty((0, 3))
    # Frequency ratio
    f1, f2 = s_freq[ci], s_freq[cj]
    fmin = np.minimum(f1, f2)
    ratio = np.abs(f1 - f2) / np.maximum(fmin, 1e-12)
    freq_ok = (ratio >= fmin_ratio) & (ratio <= fmax_ratio)
    ci, cj = ci[freq_ok], cj[freq_ok]
    if len(ci) == 0:
        return np.empty(0, np.int32), np.empty(0, np.int32), np.empty(0), np.empty((0, 3))
    # Midpoint
    delta = s_pos[cj] - s_pos[ci]
    over = delta > box * 0.5
    under = delta < -box * 0.5
    delta = delta - box * over + box * under
    mid = (s_pos[ci] + delta * 0.5) % box
    out_freq = s_freq[ci] + s_freq[cj]
    return ci.astype(np.int32), cj.astype(np.int32), out_freq, mid


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

    if True:  # numpy vectorized path — no Numba, no grid overhead
        # All-pairs for alive vibrations (fast for <500 vibs)
        alive_idx = np.where(world.s_alive)[0].astype(np.int32)
        n_alive = len(alive_idx)
        if n_alive < 2:
            return 0
        # Upper-triangle pairs
        ii, jj = np.triu_indices(n_alive, k=1)
        candidate_i = alive_idx[ii]
        candidate_j = alive_idx[jj]

        out_i, out_j, out_freq, out_mid = _bind_vibrations_check_pairs_numpy(
            candidate_i, candidate_j,
            world.s_pos, world.s_alive, world.s_locked_this_tick,
            world.s_freq, world.s_pol,
            box, r1_sq, fmin_ratio, fmax_ratio,
        )
        n_out = len(out_i)

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

# PHASE3-R1: molecule+molecule fusion, gated by cfg.mol_fusion_enabled.
# Generalized rule: any two nodes both >= level 4 produce max(a,b)+1,
# capped at _MAX_LEVEL-1. This enables unbounded chain growth.
_UPGRADE_TARGET_FUSION = {}
for _a in range(4, 33):
    for _b in range(_a, 33):
        _target = max(_a, _b) + 1
        if _target < 33:
            _UPGRADE_TARGET_FUSION[(_a, _b)] = _target
            if _a != _b:
                _UPGRADE_TARGET_FUSION[(_b, _a)] = _target

# Plan A.5 — numpy-array versions for Numba JIT lookup. Numba can't
# index Python dicts efficiently; small dense arrays are the canonical
# pattern. Built once at module import. Cells without an upgrade hold -1.
# The dict versions above are kept for the Python (non-JIT) path.
_MAX_LEVEL = 33
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


def prune_firing_log(world) -> None:
    """Trim world.firing_events to whatever the active mechanisms need.

    Runs every tick regardless of stdp_enabled. Without it, BTSP /
    dream / self-aware retain unbounded firing logs across cycles
    even when STDP is off, and the substrate's wall time per tick
    grows linearly with simulation time.
    """
    cfg = world.config
    events = world.firing_events
    if not events:
        return
    retention = float(cfg.tau_LTP)
    if getattr(cfg, "self_aware_enabled", False):
        retention = max(retention, float(cfg.self_model_window))
    if getattr(cfg, "dream_blend_enabled", False):
        retention = max(retention,
                         float(cfg.dream_blend_co_activation_window))
    if getattr(cfg, "btsp_enabled", False):
        retention = max(retention, float(cfg.btsp_tau_eligibility))
    cutoff = world.t - retention
    if events[0][0] < cutoff:
        world.firing_events = [e for e in events if e[0] >= cutoff]


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
    #
    # G18 amendment: BTSP (G14), self-aware (G16), and dream (G15) all
    # need the firing log retained over a SECONDS-scale window, not a
    # 25-ms one. Use the maximum of tau_LTP and the longest downstream
    # window so STDP still gets its tight pruning while dream/self-aware
    # can see co-active patterns within their 0.5-2 sec windows.
    retention = float(cfg.tau_LTP)
    if getattr(cfg, "self_aware_enabled", False):
        retention = max(retention, float(cfg.self_model_window))
    if getattr(cfg, "dream_blend_enabled", False):
        retention = max(retention, float(cfg.dream_blend_co_activation_window))
    if getattr(cfg, "btsp_enabled", False):
        retention = max(retention, float(cfg.btsp_tau_eligibility))
    cutoff = world.t - retention
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


def apply_btsp(world, dt: float) -> int:
    """G14 — Behavioral Time Scale Plasticity.

    Bidirectional, eligibility-trace-based, plateau-gated plasticity at
    the seconds time-scale. The biologically-grounded successor to tight-
    millisecond Hebbian STDP (Magee 2026 Nat Neurosci review; Wu et al
    2024 Nat Commun).

    Mechanism:
      1. Every alive level-4 atom maintains an eligibility trace `E`
         that decays exponentially with `tau_eligibility` (default 6 s).
      2. When an atom fires, its eligibility is bumped by 1.0.
      3. If an atom's accumulated charge crosses `btsp_plateau_charge_
         threshold`, it counts as a plateau event — a "salience signal"
         in biology.
      4. On a plateau event, the substrate finds all level-5+ molecules
         within `btsp_radius` of the plateau atom, and for each pair of
         eligible atoms (eligibility > 0) connected through such a
         molecule, applies BTSP potentiation: strength += btsp_potentiation
         × E_pre × E_post. Bidirectional and one-shot.
      5. Optional excitability bias: atoms with higher eligibility get a
         lower effective theta_fire next tick (Josselyn-style allocation
         by intrinsic excitability).

    What this gives the substrate that millisecond-Hebbian doesn't:
      - One-shot learning across seconds (single trial, no need to repeat)
      - Cross-modal binding without tight temporal coincidence (visual
        and audio can fire 5 sec apart and still bind via BTSP if a
        plateau happens within the eligibility window)
      - Pattern-specific engrams emerge from per-pattern excitability
        biases — different patterns recruit different atom subsets

    Returns count of (plateau_atom, partner_atom) BTSP events.
    """
    cfg = world.config
    if not cfg.btsp_enabled:
        return 0
    K = world.k_count
    if K == 0:
        return 0

    # 1. Decay all atoms' eligibility traces.
    if cfg.btsp_tau_eligibility > 0:
        decay_factor = float(np.exp(-dt / cfg.btsp_tau_eligibility))
        world.k_eligibility[:K] *= decay_factor

    # 2. Bump eligibility for atoms that fired this tick.
    t_now = world.t
    for t_fire, atom_idx in world.firing_events:
        if t_fire != t_now:
            continue
        if atom_idx < K and world.k_alive[atom_idx]:
            world.k_eligibility[int(atom_idx)] += 1.0

    # 3. Find plateau atoms — alive level-4 atoms whose ACCUMULATED
    # eligibility crossed the plateau threshold this tick.
    atom_mask = world.k_alive[:K] & (world.k_level[:K] == 4)
    if not atom_mask.any():
        return 0
    plateau_threshold = float(cfg.btsp_plateau_charge_threshold)
    plateau_mask = atom_mask & (world.k_eligibility[:K] >= plateau_threshold)
    if not plateau_mask.any():
        return 0
    plateau_indices = np.where(plateau_mask)[0]

    # 4. Find all level-5+ molecules; we'll use them as the bridge mesh.
    molecule_mask = world.k_alive[:K] & (world.k_level[:K] >= 5)
    if not molecule_mask.any():
        return 0
    molecule_indices = np.where(molecule_mask)[0]
    molecule_pos = world.k_pos[molecule_indices]

    # 5. For each plateau atom, find nearby molecules + nearby eligible
    # atoms, then commit BTSP between plateau and eligible-partner via
    # the found molecules.
    box = np.asarray(cfg.box_size, dtype=np.float64)
    btsp_r2 = float(cfg.btsp_radius) ** 2
    pot = float(cfg.btsp_potentiation)
    n_events = 0
    eligible_atom_indices = np.where(
        atom_mask & (world.k_eligibility[:K] > 0.05)
    )[0]
    if len(eligible_atom_indices) == 0:
        return 0
    eligible_pos = world.k_pos[eligible_atom_indices]

    for pi in plateau_indices:
        plateau_pos = world.k_pos[pi]

        # Eligible partners within btsp_radius (excluding self)
        d_e = eligible_pos - plateau_pos
        d_e -= box * np.round(d_e / box)
        d_e_sq = (d_e * d_e).sum(axis=1)
        partner_local = np.where((d_e_sq <= btsp_r2)
                                  & (d_e_sq > 0.0))[0]
        if len(partner_local) == 0:
            continue
        partner_atom_indices = eligible_atom_indices[partner_local]

        # Molecules within btsp_radius of plateau (these are the
        # candidate bridges to potentiate)
        d_m = molecule_pos - plateau_pos
        d_m -= box * np.round(d_m / box)
        d_m_sq = (d_m * d_m).sum(axis=1)
        nearby_molecules_local = np.where(d_m_sq <= btsp_r2)[0]
        if len(nearby_molecules_local) == 0:
            continue
        nearby_molecules = molecule_indices[nearby_molecules_local]

        for partner_idx in partner_atom_indices:
            partner_pos = world.k_pos[partner_idx]
            E_partner = float(world.k_eligibility[partner_idx])
            E_plateau = float(world.k_eligibility[pi])
            # For each nearby molecule, check if the partner is also
            # nearby (i.e. molecule lies between plateau and partner)
            for m in nearby_molecules:
                d_mp = world.k_pos[m] - partner_pos
                d_mp -= box * np.round(d_mp / box)
                if (d_mp * d_mp).sum() > btsp_r2:
                    continue
                # BTSP weight update: bidirectional, eligibility-product gated
                delta = pot * E_partner * E_plateau / (
                    plateau_threshold ** 2 + 1.0
                )
                world.k_strength[int(m)] = min(
                    float(world.k_strength[int(m)]) + delta, 1000.0
                )
                # Bridge orientation: midpoint-pointing toward partner
                if int(world.k_pattern_id[m]) == 0:
                    pid_p = int(world.k_pattern_id[pi])
                    pid_o = int(world.k_pattern_id[partner_idx])
                    if pid_p != 0 and pid_p == pid_o:
                        world.k_pattern_id[m] = pid_p
                # Update orientation to point plateau → partner
                seg = partner_pos - world.k_pos[m]
                seg -= box * np.round(seg / box)
                seg_norm = float(np.linalg.norm(seg))
                if seg_norm > 1e-9:
                    world.k_orientation[m] = seg / seg_norm
                n_events += 1

        # Reset plateau atom's eligibility to prevent re-triggering until
        # accumulated again.
        world.k_eligibility[pi] = 0.0

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
            # G13 bidirectional: also sample at -distance so a firing atom
            # at either end of the bridge propagates to atoms at the other
            # end. This is the cross-modal generative recall mechanism —
            # audio→video routing reuses the visual→audio bridges formed
            # during training.
            post_mask = np.zeros(atom_pos.shape[0], dtype=np.bool_)
            sign_signs = (1.0, -1.0) if cfg.bidirectional_bridges else (1.0,)
            for k in range(n_samples):
                for sign in sign_signs:
                    distance = sign * (k + 1) * r_bridge
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


def _bind_check_pairs_njit(
    candidate_i: np.ndarray, candidate_j: np.ndarray, n_candidates: int,
    k_pos: np.ndarray, k_alive: np.ndarray, k_locked_this_tick: np.ndarray,
    k_freq: np.ndarray, k_pol: np.ndarray, k_level: np.ndarray,
    box: np.ndarray, r2_sq: float,
    fmin_ratio: float, fmax_ratio: float,
    upgrade_table: np.ndarray, fusion_table: np.ndarray, mol_fusion_enabled: bool,
    out_i: np.ndarray, out_j: np.ndarray, out_target: np.ndarray,
) -> int:
    """JIT core for bind_nodes_upward. Pre-allocated output arrays.
    Returns parallel arrays (out_i, out_j, out_target, n_out) of pairs that
    pass all gates, preserving input order so the Python wrapper can apply
    break-semantics correctly.

    Note: k_alive and k_locked_this_tick are snapshots at call time; the
    Python wrapper enforces the break / single-bind-per-i rule by checking
    the lock array after each allocation.
    """
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
        # Frequency checks only for sub-atom levels (both < 4).
        # Atoms (level 4+) bind by proximity + polarity alone.
        f1 = k_freq[i]
        f2 = k_freq[j]
        if li < 4 or lj < 4:
            if f1 <= 0.0 or f2 <= 0.0:
                continue
            d1 = int(np.floor(np.log10(f1)))
            d2_dec = int(np.floor(np.log10(f2)))
            if d1 != d2_dec:
                continue
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
    return n_out


def _gather_leaf_vibration_indices(world, node_idx: int) -> np.ndarray:
    """Walk the composition tree from a node down to its leaf vibrations.

    Returns an int64 array of vibration indices (level-1 electrons store
    vibration indices in their composition span — k_comp_kind == 0).
    Internal nodes (k_comp_kind != 0) store node indices; they are traversed
    recursively via an explicit stack.
    """
    out: list[int] = []
    stack = [int(node_idx)]
    visited: set[int] = set()
    max_depth = 1000
    while stack and max_depth > 0:
        max_depth -= 1
        i = stack.pop()
        if i in visited:
            continue  # prevent infinite loops from corrupt composition
        visited.add(i)
        start = int(world.k_comp_offset[i])
        end = int(world.k_comp_end[i])
        if int(world.k_comp_kind[i]) == 0:
            for k in range(start, end):
                out.append(int(world.k_comp_indices[k]))
        else:
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
    if True:  # numpy all-pairs path (no grid, no Numba)
        alive_idx = np.where(world.k_alive[:K])[0].astype(np.int32)
        n_alive = len(alive_idx)
        if n_alive < 2:
            return 0
        ii, jj = np.triu_indices(n_alive, k=1)
        candidate_i = alive_idx[ii]
        candidate_j = alive_idx[jj]
        n_candidates = len(candidate_i)
        out_i = np.zeros(n_candidates, dtype=np.int32)
        out_j = np.zeros(n_candidates, dtype=np.int32)
        out_target = np.zeros(n_candidates, dtype=np.int8)
        # Numpy vectorized pair check (no Python loops)
        ci, cj = candidate_i, candidate_j
        k_alive = world.k_alive[:K]
        k_locked = world.k_locked_this_tick[:K]
        k_pos = world.k_pos[:K]
        k_freq = world.k_freq[:K]
        k_pol = world.k_pol[:K]
        k_level = world.k_level[:K]

        # Basic masks
        alive_ok = k_alive[ci] & k_alive[cj] & ~k_locked[ci] & ~k_locked[cj]
        pol_ok = k_pol[ci] != k_pol[cj]
        mask = alive_ok & pol_ok
        ci, cj = ci[mask], cj[mask]

        if len(ci) > 0:
            # Level lookup
            li = k_level[ci]
            lj = k_level[cj]
            targets = _UPGRADE_TARGET_ARRAY[li, lj]
            if cfg.mol_fusion_enabled:
                need_fusion = targets == -1
                targets[need_fusion] = _UPGRADE_TARGET_FUSION_ARRAY[li[need_fusion], lj[need_fusion]]
            valid = targets >= 0
            ci, cj, targets = ci[valid], cj[valid], targets[valid]

        if len(ci) > 0:
            # Distance check
            d = k_pos[ci] - k_pos[cj]
            d -= box * np.round(d / box)
            d2 = (d * d).sum(axis=1)
            close = d2 < r2_sq
            ci, cj, targets = ci[close], cj[close], targets[close]

        # Frequency selectivity happens once, at vibration→electron binding.
        # Node→node binding is structural (proximity + polarity). When
        # node_freq_binding is False, the 8% rule is skipped for node pairs,
        # unsticking the triad→atom step where summed frequencies diverge.
        if len(ci) > 0 and getattr(cfg, 'node_freq_binding', True):
            # Freq check (only sub-atom)
            li = k_level[ci]
            lj = k_level[cj]
            sub_atom = (li < 4) | (lj < 4)
            if sub_atom.any():
                f1 = k_freq[ci]
                f2 = k_freq[cj]
                fmin = np.minimum(f1, f2)
                ratio = np.abs(f1 - f2) / np.maximum(fmin, 1e-12)
                decade_ok = (np.floor(np.log10(np.maximum(f1, 1.0))).astype(int) ==
                             np.floor(np.log10(np.maximum(f2, 1.0))).astype(int))
                freq_ok = decade_ok & (ratio >= fmin_ratio) & (ratio <= fmax_ratio)
                # Atom-level pairs skip freq check
                pass_freq = ~sub_atom | freq_ok
                ci, cj, targets = ci[pass_freq], cj[pass_freq], targets[pass_freq]

        # BET-091 valence commitment: an atom already bonded into a structure
        # (k_bond_count >= fusion_bond_block) has spent its valence on external
        # bridges and resists internal fusion. Skip any candidate pair where a
        # level-4 atom meets the bond threshold. Unbonded atoms fuse as before,
        # so the cascade up to atom formation is untouched. 0 = off.
        block = getattr(cfg, 'fusion_bond_block', 0)
        if block > 0 and len(ci) > 0:
            bc = world.k_bond_count[:K]
            committed = (((k_level[ci] == 4) & (bc[ci] >= block)) |
                         ((k_level[cj] == 4) & (bc[cj] >= block)))
            keep = ~committed
            ci, cj, targets = ci[keep], cj[keep], targets[keep]

        n_out = len(ci)
        if n_out > 0:
            out_i[:n_out] = ci
            out_j[:n_out] = cj
            out_target[:n_out] = targets

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
            # Bond count: only tracked for bridges (form_bridges), not fusion.
            # Fusion is internal construction; bridges are external connections.
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
                # Frequency checks only for sub-atom levels.
                # Atoms (level 4+) bind by proximity + polarity alone —
                # frequency matching is a vibration-level phenomenon.
                if li < 4 or lj < 4:
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

    # How many vibrations to inject this tick?
    if cfg.lambda_gen <= 0:
        return (0, 0)
    if cfg.lambda_dec > 0:
        # Equilibrium: target_count = lambda_gen/lambda_dec * volume
        target_count = int((cfg.lambda_gen / cfg.lambda_dec) * box_volume)
        current_count = int(world.s_alive.sum())
        deficit = max(0, target_count - current_count)
    else:
        # No decay: inject lambda_gen * volume * dt new vibrations per tick
        deficit = max(1, int(cfg.lambda_gen * box_volume * dt))
    if deficit == 0:
        return (0, 0)

    n_displaced = 0
    n_allocated = 0

    # Fast path: allocate from free slots first (no displacement needed)
    free_idx = np.where(~world.s_alive[:cfg.n_vibrations_max])[0]
    n_free = len(free_idx)
    n_alloc = min(deficit, n_free)
    if n_alloc > 0:
        slots = free_idx[:n_alloc]
        world.s_pos[slots] = rng.uniform(low=np.zeros(3), high=box, size=(n_alloc, 3))
        world.s_vel[slots] = world._sample_velocities_3d(n_alloc)
        world.s_freq[slots] = world._sample_frequencies(n_alloc)
        world.s_pol[slots] = rng.random(n_alloc) < cfg.polarity_split
        world.s_alive[slots] = True
        n_allocated = n_alloc
        deficit -= n_alloc
        if n_alloc > 0:
            world.n_alive = max(world.n_alive, int(slots.max()) + 1)

    # Slow path: if no free slots, displace far-field vibrations
    if deficit > 0:
        active_mask = world.k_alive[:world.k_count] & (world.k_level[:world.k_count] >= 4) if world.k_count > 0 else np.zeros(0, dtype=bool)
        active_pos = world.k_pos[:world.k_count][active_mask] if active_mask.any() else np.empty((0, 3))
        safe_r2 = (2.0 * cfg.r_2) ** 2
        alive_idx = np.where(world.s_alive[:cfg.n_vibrations_max])[0]
        rng.shuffle(alive_idx)
        for i in alive_idx:
            if deficit <= 0:
                break
            if len(active_pos):
                d = world.s_pos[i] - active_pos
                d -= box * np.round(d / box)
                if ((d * d).sum(axis=1) < safe_r2).any():
                    continue
            world.s_pos[i] = rng.uniform(low=np.zeros(3), high=box)
            world.s_vel[i] = world._sample_velocities_3d(1)[0]
            world.s_freq[i] = world._sample_frequencies(1)[0]
            world.s_pol[i] = bool(rng.random() < cfg.polarity_split)
            n_displaced += 1
            deficit -= 1

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


def _largest_bridged_component(world):
    """Indices of atoms in the largest connected bridged component (BFS over alive bridges)."""
    from collections import defaultdict, deque
    adj = defaultdict(set)
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            adj[i].add(j); adj[j].add(i)
    best, seen = [], set()
    for s in adj:
        if s in seen:
            continue
        comp, q = [], deque([s]); seen.add(s)
        while q:
            n = q.popleft(); comp.append(n)
            for nb in adj[n]:
                if nb not in seen:
                    seen.add(nb); q.append(nb)
        if len(comp) > len(best):
            best = comp
    return best


def _fit_sphere(points):
    """Least-squares sphere fit. Returns (centre, radius). Mirrors tools/detect_membranes.fit_sphere."""
    p = np.asarray(points, dtype=np.float64)
    A = np.hstack([2.0 * p, np.ones((p.shape[0], 1))])
    f = (p * p).sum(axis=1)
    c, *_ = np.linalg.lstsq(A, f, rcond=None)
    centre = c[:3]
    radius = math.sqrt(max(c[3] + centre.dot(centre), 0.0))
    return centre, radius


def _membrane_channel_atom(world, dt, centre, f_mem, atom_idx, box):
    """G32: atom-proximity reflector. Reflect an inbound, frequency-incompatible free
    vibration when it comes within r_2 of any CURRENT membrane-atom position. Tracks the
    real, breathing, irregular shell instead of a smooth fitted sphere."""
    cfg = world.config
    alive = world.s_alive
    if not alive.any():
        return
    A = world.k_pos[atom_idx]                      # current atom positions (breathing)
    P = world.s_pos[alive]
    vel = world.s_vel[alive]
    freq = world.s_freq[alive]

    # Nearest membrane-atom distance per free vibration (min-image).
    diff = P[:, None, :] - A[None, :, :]
    diff -= box * np.round(diff / box)
    d2 = (diff * diff).sum(axis=2)
    near = d2.min(axis=1) < (cfg.r_2 * cfg.r_2)

    # Outward radial normal from the shell centre; inbound = moving toward the centre.
    rad = P - centre
    rad -= box * np.round(rad / box)
    r = np.linalg.norm(rad, axis=1)
    n_hat = rad / (r[:, None] + 1e-9)
    inbound = (vel * n_hat).sum(axis=1) < 0.0

    # Frequency-incompatible under the substrate's own binding band.
    fmin = np.minimum(freq, f_mem)
    ratio = np.abs(freq - f_mem) / np.maximum(fmin, 1e-12)
    incompatible = ~((ratio >= cfg.freq_ratio - cfg.freq_tolerance)
                     & (ratio <= cfg.freq_ratio + cfg.freq_tolerance))

    reflect = near & inbound & incompatible
    if cfg.membrane_channel_uptake:
        # G49: also reflect COMPATIBLE OUTBOUND vibrations back inside (trap nutrient) ->
        # the interior accumulates compatible species = active uptake, not just exclusion.
        reflect = reflect | (near & (~inbound) & (~incompatible))
    if not reflect.any():
        return
    alive_idx = np.where(alive)[0]
    sel = alive_idx[reflect]
    v_sel = world.s_vel[sel]
    nh = n_hat[reflect]
    vr = (v_sel * nh).sum(axis=1)
    world.s_vel[sel] = v_sel - 2.0 * vr[:, None] * nh
    world.s_pos[sel] = (world.s_pos[sel] - v_sel * dt) % box


def apply_membrane_channel(world, dt: float) -> None:
    """G31: selective permeability. A frequency-gated reflection barrier at the emergent
    shell surface. No-op when cfg.membrane_channel_k == 0.

    Every cfg.membrane_channel_recompute ticks, derive the membrane from the actual
    structure (largest bridged atom component → sphere fit → centre C, radius R; f_mem =
    mean frequency of those atoms). Each tick, a free vibration that crossed the shell
    surface inward this step is reflected UNLESS it is frequency-compatible with the
    membrane under the substrate's OWN binding band. Compatible passes; incompatible is
    contained outside.
    """
    cfg = world.config
    if cfg.membrane_channel_k == 0.0 or world.k_count == 0:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)

    # (Re)derive membrane on a cadence; cache atom indices + centre + f_mem on the world.
    counter = getattr(world, "_membrane_channel_counter", 0)
    geom = getattr(world, "_membrane_channel_geom", None)
    if geom is None or counter % max(1, cfg.membrane_channel_recompute) == 0:
        comp = _largest_bridged_component(world)
        if len(comp) >= 8:
            idx = np.array(comp)
            centre, radius = _fit_sphere(world.k_pos[idx])
            f_mem = float(world.k_freq[idx].mean())
            geom = (centre, radius, f_mem, idx) if radius > 1e-6 else None
        else:
            geom = None
        world._membrane_channel_geom = geom
    world._membrane_channel_counter = counter + 1
    if geom is None:
        return
    centre, radius, f_mem, atom_idx = geom

    if cfg.membrane_channel_mode == "atom":
        _membrane_channel_atom(world, dt, centre, f_mem, atom_idx, box)
        return

    alive = world.s_alive
    if not alive.any():
        return
    pos = world.s_pos
    vel = world.s_vel
    freq = world.s_freq

    # Radial distance (minimum-image) to the shell centre, this step and previous step.
    d = pos[alive] - centre
    d -= box * np.round(d / box)
    r = np.linalg.norm(d, axis=1)
    prev = (pos[alive] - vel[alive] * dt) - centre
    prev -= box * np.round(prev / box)
    r_prev = np.linalg.norm(prev, axis=1)

    width = cfg.membrane_channel_width
    crossed_in = (r_prev > radius) & (r <= radius) & (np.abs(r - radius) < width + 1e-9)
    if not crossed_in.any():
        return

    # Substrate's own compatibility band relative to f_mem.
    fmin = np.minimum(freq[alive], f_mem)
    ratio = np.abs(freq[alive] - f_mem) / np.maximum(fmin, 1e-12)
    fmin_ratio = cfg.freq_ratio - cfg.freq_tolerance
    fmax_ratio = cfg.freq_ratio + cfg.freq_tolerance
    compatible = (ratio >= fmin_ratio) & (ratio <= fmax_ratio)

    reflect = crossed_in & ~compatible
    if not reflect.any():
        return

    alive_idx = np.where(alive)[0]
    sel = alive_idx[reflect]
    d_sel = d[reflect]
    r_sel = r[reflect]
    n_hat = d_sel / (r_sel[:, None] + 1e-9)
    v_sel = vel[sel]
    vr = (v_sel * n_hat).sum(axis=1)
    vel[sel] = v_sel - 2.0 * vr[:, None] * n_hat
    # Revert position to just outside the shell along the inbound path.
    pos[sel] = (pos[sel] - v_sel * dt) % box


def apply_bond_turnover(world, dt: float) -> None:
    """G53: fluid-membrane primitive. Each alive bridge spontaneously breaks with probability
    bond_turnover_rate*dt, freeing both atoms' valence so form_bridges can re-bond them as atoms
    drift. Bonds break + reform → the network REMODELS (atoms can flow into a wound). No-op when
    bond_turnover_rate == 0. Too high a rate dissolves the membrane (fluidity/stability trade-off)."""
    cfg = world.config
    rate = getattr(cfg, 'bond_turnover_rate', 0.0)
    B = world.b_count
    if rate <= 0.0 or B == 0:
        return
    alive = world.b_alive[:B]
    idx = np.where(alive)[0]
    if len(idx) == 0:
        return
    p = rate * dt
    breaking = idx[world.rng.random(len(idx)) < p]
    for b in breaking:
        i = int(world.b_atom_i[b]); j = int(world.b_atom_j[b])
        world.b_alive[b] = False
        if i < world.k_count:
            world.k_bond_count[i] = max(0, world.k_bond_count[i] - 1)
        if j < world.k_count:
            world.k_bond_count[j] = max(0, world.k_bond_count[j] - 1)


def _reflect_at_sphere(world, dt, centre, R, mode, box):
    """Reflect free vibrations at one engineered sphere (centre, R).

    Default modes (clamp/soft/mirror) are ONE-WAY: reflect only OUTBOUND vibrations
    (keep a region's own emissions in). 'seal' is TWO-WAY: also reflect INBOUND
    vibrations approaching from OUTSIDE, so foreign emissions cannot enter — required to
    isolate multiple compartments (G41)."""
    if R <= 0.0:
        return
    alive = world.s_alive
    if not alive.any():
        return
    d = world.s_pos[alive] - centre
    d -= box * np.round(d / box)
    r = np.linalg.norm(d, axis=1)
    n_hat = d / (r[:, None] + 1e-9)
    v = world.s_vel[alive]
    vdotn = (v * n_hat).sum(axis=1)
    if mode == "seal":
        # Two-way: inside moving out (keep in) OR outside moving in within a band (keep out).
        band = 2.0
        reflect = ((r < R) & (vdotn > 0.0)) | ((r >= R) & (r < R + band) & (vdotn < 0.0))
    else:
        outbound = vdotn > 0.0
        reflect = (r >= R) & outbound
    if not reflect.any():
        return
    alive_idx = np.where(alive)[0]
    sel = alive_idx[reflect]
    nh = n_hat[reflect]
    r_sel = r[reflect]
    v_sel = world.s_vel[sel]
    vr = (v_sel * nh).sum(axis=1)
    world.s_vel[sel] = v_sel - 2.0 * vr[:, None] * nh          # flip radial component inward
    if mode == "seal":
        # Two-way seal: keep inside vibrations just inside, push entering vibrations just
        # outside — so foreign emissions bounce off and own emissions stay in (G41).
        inside = r_sel < R
        r_new = np.where(inside, R * 0.999, R * 1.001)
        world.s_pos[sel] = (centre + nh * r_new[:, None]) % box
    elif mode == "soft":
        # Revert this step's overshoot only — no dense boundary layer (G35).
        world.s_pos[sel] = (world.s_pos[sel] - v_sel * dt) % box
    elif mode == "mirror":
        # Specular reflection: mirror the radial overshoot about R (r -> 2R-r). Contains
        # fully without pinning — reflected vibrations stay distributed through the interior
        # (G37; docs/patterns/engineered_port_wall.md).
        r_new = np.clip(2.0 * R - r_sel, 0.0, R * 0.999)
        world.s_pos[sel] = (centre + nh * r_new[:, None]) % box
    else:
        # Clamp position just inside the wall along the inward normal (G33 default).
        world.s_pos[sel] = (centre + nh * (R * 0.999)) % box


def apply_engineered_compartment(world, dt: float) -> None:
    """G33/G40: engineered compartment wall(s) (CONCEPT §4.8 port topology). Reflect every
    alive free vibration at/beyond an engineered sphere moving OUTWARD, keeping each region's
    emissions local. No-op when cfg.compartment_k == 0. Touches only free vibrations, never
    bound atoms. Supports MULTIPLE compartments via cfg.compartments (each (cx,cy,cz,R));
    falls back to the single cfg.compartment_centre / compartment_radius."""
    cfg = world.config
    if cfg.compartment_k == 0.0:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)
    if cfg.compartments:
        spheres = [(np.asarray(c[:3], dtype=np.float64), float(c[3])) for c in cfg.compartments]
    else:
        spheres = [(np.asarray(cfg.compartment_centre, dtype=np.float64), cfg.compartment_radius)]
    for centre, R in spheres:
        _reflect_at_sphere(world, dt, centre, R, cfg.compartment_mode, box)


def apply_midplane_wall(world, dt: float) -> None:
    """PRIM1-D2: free vibrations confined to half-boxes (midplane + no x-wrap).

    No-op when midplane_wall_enabled is False. Bound nodes untouched.
    Uses world._s_pos_pre_x from tick (pre-move x) to detect crosses and wraps.
    """
    cfg = world.config
    if not getattr(cfg, "midplane_wall_enabled", False):
        return
    alive = world.s_alive
    if not np.any(alive):
        return
    xw = float(getattr(cfg, "midplane_wall_x", 40.0))
    box = np.asarray(cfg.box_size, dtype=np.float64)
    L = float(box[0])
    eps = 1e-6
    dt = float(dt) if dt != 0 else 1e-9
    x = world.s_pos[:, 0]
    vx = world.s_vel[:, 0]
    pre = getattr(world, "_s_pos_pre_x", None)
    if pre is None:
        pre = x - vx * dt
    pre = np.asarray(pre, dtype=np.float64)

    # Undo periodic wrap on x (teleport left↔right)
    wrapped = alive & (np.abs(x - pre) > 0.5 * L)
    if np.any(wrapped):
        from_left = wrapped & (pre < xw)
        from_right = wrapped & (pre >= xw)
        if np.any(from_left):
            world.s_pos[from_left, 0] = eps
            world.s_vel[from_left, 0] = np.abs(world.s_vel[from_left, 0])
        if np.any(from_right):
            world.s_pos[from_right, 0] = L - eps
            world.s_vel[from_right, 0] = -np.abs(world.s_vel[from_right, 0])
        x = world.s_pos[:, 0]

    crossed_lr = alive & (pre < xw) & (x >= xw)
    crossed_rl = alive & (pre >= xw) & (x < xw)
    if np.any(crossed_lr):
        world.s_pos[crossed_lr, 0] = xw - eps
        world.s_vel[crossed_lr, 0] = -np.abs(world.s_vel[crossed_lr, 0])
    if np.any(crossed_rl):
        world.s_pos[crossed_rl, 0] = xw + eps
        world.s_vel[crossed_rl, 0] = np.abs(world.s_vel[crossed_rl, 0])

    x = world.s_pos[:, 0]
    hit_lo = alive & (x <= 0.0)
    hit_hi = alive & (x >= L)
    if np.any(hit_lo):
        world.s_pos[hit_lo, 0] = eps
        world.s_vel[hit_lo, 0] = np.abs(world.s_vel[hit_lo, 0])
    if np.any(hit_hi):
        world.s_pos[hit_hi, 0] = L - eps
        world.s_vel[hit_hi, 0] = -np.abs(world.s_vel[hit_hi, 0])

    # PRIM7: spectral purification — absorb free vibs in the wrong half-band.
    if getattr(cfg, "midplane_sideband_cull_enabled", False):
        gate = float(getattr(cfg, "midplane_gate_f_mid", 1581.14))
        alive2 = world.s_alive
        x2 = world.s_pos[:, 0]
        f = world.s_freq
        wrong_left = alive2 & (x2 < xw) & (f >= gate)
        wrong_right = alive2 & (x2 >= xw) & (f < gate)
        if np.any(wrong_left):
            world.s_alive[wrong_left] = False
        if np.any(wrong_right):
            world.s_alive[wrong_right] = False
        world.n_alive = int(world.s_alive.sum())


def apply_charge_latch_decay(world, dt: float) -> None:
    """PRIM6: optional slow decay of k_latch. No-op if latch off or tau<=0 (hold)."""
    cfg = world.config
    if not getattr(cfg, "charge_latch_enabled", False):
        return
    if not hasattr(world, "k_latch"):
        return
    tau = float(getattr(cfg, "charge_latch_tau", 0.0) or 0.0)
    if tau <= 0.0 or dt <= 0.0:
        return  # permanent hold when enabled and tau<=0
    factor = float(np.exp(-float(dt) / tau))
    K = world.k_count
    world.k_latch[:K] *= factor


def apply_fire_zero_latch(world) -> None:
    """PRIM11: after prop, emitters that fired this tick zero nearby k_latch.

    Runs *after* bridge charge prop so XOR-style clear beats same-tick deposits.
    """
    cfg = world.config
    r_zl = float(getattr(cfg, "fire_zero_latch_radius", 0.0) or 0.0)
    if r_zl <= 0.0 or not hasattr(world, "k_latch"):
        return
    K = world.k_count
    t_now = world.t
    emitters = []
    for tf, ai in world.firing_events:
        if tf != t_now:
            continue
        ai = int(ai)
        if ai < 0 or ai >= K:
            continue
        if hasattr(world, "k_zero_latch_emitter") and int(world.k_zero_latch_emitter[ai]) == 0:
            continue
        emitters.append(ai)
    if not emitters:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r2z = r_zl * r_zl
    emit_set = set(emitters)
    for ai in emitters:
        ap = world.k_pos[ai]
        for j in range(K):
            if j in emit_set or not world.k_alive[j] or int(world.k_level[j]) < 4:
                continue
            d = world.k_pos[j] - ap
            d -= box * np.round(d / box)
            if float(np.dot(d, d)) <= r2z:
                world.k_latch[j] = 0.0


def apply_fire_kill_bridges(world) -> None:
    """PRIM12: emitters that fired this tick kill bridges near them."""
    cfg = world.config
    r_kb = float(getattr(cfg, "fire_kill_bridge_radius", 0.0) or 0.0)
    if r_kb <= 0.0 or world.b_count == 0:
        return
    K = world.k_count
    t_now = world.t
    emitters = []
    for tf, ai in world.firing_events:
        if tf != t_now:
            continue
        ai = int(ai)
        if ai < 0 or ai >= K:
            continue
        if hasattr(world, "k_kill_bridge_emitter") and int(world.k_kill_bridge_emitter[ai]) == 0:
            continue
        emitters.append(ai)
    if not emitters:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r2k = r_kb * r_kb
    for ai in emitters:
        ap = world.k_pos[ai]
        for b in range(world.b_count):
            if not world.b_alive[b]:
                continue
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            for node in (i, j):
                if node < 0 or node >= K or not world.k_alive[node]:
                    continue
                d = world.k_pos[node] - ap
                d -= box * np.round(d / box)
                if float(np.dot(d, d)) <= r2k:
                    world.b_alive[b] = False
                    break


def apply_fire_weaken_bridges(world) -> None:
    """PRIM13: emitters scale down strength of nearby alive bridges (reversible)."""
    cfg = world.config
    r_wb = float(getattr(cfg, "fire_weaken_bridge_radius", 0.0) or 0.0)
    frac = float(getattr(cfg, "fire_weaken_bridge_frac", 1.0) or 0.0)
    if r_wb <= 0.0 or frac <= 0.0 or world.b_count == 0:
        return
    K = world.k_count
    t_now = world.t
    emitters = []
    for tf, ai in world.firing_events:
        if tf != t_now:
            continue
        ai = int(ai)
        if ai < 0 or ai >= K:
            continue
        if hasattr(world, "k_weaken_bridge_emitter") and int(world.k_weaken_bridge_emitter[ai]) == 0:
            continue
        emitters.append(ai)
    if not emitters:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r2w = r_wb * r_wb
    scale = max(0.0, 1.0 - frac)
    for ai in emitters:
        ap = world.k_pos[ai]
        for b in range(world.b_count):
            if not world.b_alive[b]:
                continue
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            for node in (i, j):
                if node < 0 or node >= K or not world.k_alive[node]:
                    continue
                d = world.k_pos[node] - ap
                d -= box * np.round(d / box)
                if float(np.dot(d, d)) <= r2w:
                    world.b_strength[b] = float(world.b_strength[b]) * scale
                    break


def apply_ilw_strength_decay(world, dt: float) -> int:
    """PRIM3: leak level≥4 k_strength toward 1.0 when ilw_strength_decay_tau > 0.

    Does not kill atoms (L4 identity permanence). Returns number of nodes touched.
    No-op when tau <= 0.
    """
    cfg = world.config
    tau = float(getattr(cfg, "ilw_strength_decay_tau", 0.0) or 0.0)
    if tau <= 0.0 or dt <= 0.0:
        return 0
    factor = float(np.exp(-float(dt) / tau))
    K = world.k_count
    n = 0
    for i in range(K):
        if not world.k_alive[i]:
            continue
        if int(world.k_level[i]) < 4:
            continue
        s = float(world.k_strength[i])
        if s <= 1.0:
            continue
        world.k_strength[i] = 1.0 + (s - 1.0) * factor
        n += 1
    return n


def apply_ilw_port_event(world, port_pos, rng=None, seed_freq: float = 3000.0) -> dict:
    """PRIM2: internal local write at *port_pos* — no free-vibration injection.

    Returns stats dict: {mode, atom_idx, mol_idx, delta_strength}.
    Engineered write; named as such. No-op if ilw_enabled is False.
    *seed_freq* used when allocating a new level-4 atom (C5 dual-port bands).

    PRIM4 (ilw_multislot_enabled): if no level≥4 in radius has relative freq
    distance ≤ ilw_multislot_rel_freq to seed_freq, allocate a new L4 instead of
    collapsing onto a mismatched band (multi-item port buffer).
    """
    cfg = world.config
    out = {"mode": "none", "atom_idx": -1, "mol_idx": -1, "delta_strength": 0.0}
    if not getattr(cfg, "ilw_enabled", False):
        return out
    port = np.asarray(port_pos, dtype=np.float64)
    R = float(getattr(cfg, "ilw_radius", 8.0))
    dS = float(getattr(cfg, "ilw_delta_strength", 0.5))
    box = np.asarray(cfg.box_size, dtype=np.float64)
    seed = float(seed_freq)
    multislot = bool(getattr(cfg, "ilw_multislot_enabled", False))
    rel_thr = float(getattr(cfg, "ilw_multislot_rel_freq", 0.35))
    K = world.k_count
    best_m, best_d2 = -1, R * R
    best_a, best_ad2 = -1, R * R
    # PRIM4: best same-band targets (may differ from nearest spatial)
    best_m_band, best_m_band_d2 = -1, R * R
    best_a_band, best_a_band_d2 = -1, R * R
    for i in range(K):
        if not world.k_alive[i]:
            continue
        d = world.k_pos[i] - port
        d -= box * np.round(d / box)
        d2 = float(np.dot(d, d))
        if d2 > R * R:
            continue
        lvl = int(world.k_level[i])
        f = float(world.k_freq[i])
        rel = abs(f - seed) / max(abs(seed), abs(f), 1.0)
        if lvl >= 5:
            if d2 <= best_d2:
                best_d2 = d2
                best_m = i
            if rel <= rel_thr and d2 <= best_m_band_d2:
                best_m_band_d2 = d2
                best_m_band = i
        if lvl == 4:
            if d2 <= best_ad2:
                best_ad2 = d2
                best_a = i
            if rel <= rel_thr and d2 <= best_a_band_d2:
                best_a_band_d2 = d2
                best_a_band = i
    if multislot:
        # Prefer same-band mol, then same-band atom; else seed new slot.
        if best_m_band >= 0:
            world.k_strength[best_m_band] = float(world.k_strength[best_m_band]) + dS
            world.k_freq[best_m_band] = 0.9 * float(world.k_freq[best_m_band]) + 0.1 * seed
            out.update(mode="strengthen_mol", mol_idx=best_m_band, delta_strength=dS)
            return out
        if best_a_band >= 0:
            world.k_strength[best_a_band] = float(world.k_strength[best_a_band]) + dS
            world.k_freq[best_a_band] = 0.85 * float(world.k_freq[best_a_band]) + 0.15 * seed
            out.update(mode="strengthen_atom", atom_idx=best_a_band, delta_strength=dS)
            return out
        # new slot even if other bands present
        idx = world.allocate_node(
            pos=port.copy(),
            freq=seed,
            pol=True,
            level=4,
            constituents=np.zeros(0, dtype=np.int32),
            comp_kind=1,
        )
        if idx >= 0:
            world.k_strength[idx] = 1.0 + dS
            out.update(mode="seed_atom_slot", atom_idx=idx, delta_strength=dS)
        return out
    # --- legacy single-slot path (PRIM2) ---
    if best_m >= 0:
        world.k_strength[best_m] = float(world.k_strength[best_m]) + dS
        world.k_freq[best_m] = 0.9 * float(world.k_freq[best_m]) + 0.1 * seed
        out.update(mode="strengthen_mol", mol_idx=best_m, delta_strength=dS)
        return out
    if best_a >= 0:
        world.k_strength[best_a] = float(world.k_strength[best_a]) + dS
        world.k_freq[best_a] = 0.85 * float(world.k_freq[best_a]) + 0.15 * seed
        out.update(mode="strengthen_atom", atom_idx=best_a, delta_strength=dS)
        return out
    idx = world.allocate_node(
        pos=port.copy(),
        freq=seed,
        pol=True,
        level=4,
        constituents=np.zeros(0, dtype=np.int32),
        comp_kind=1,
    )
    if idx >= 0:
        world.k_strength[idx] = 1.0 + dS
        out.update(mode="seed_atom", atom_idx=idx, delta_strength=dS)
    return out


def _ensure_bridge(world, i: int, j: int, delta: float = 1.0) -> int:
    """Create or strengthen bridge between atoms i,j. Returns bridge index or -1."""
    if i < 0 or j < 0 or i == j:
        return -1
    a, b = (i, j) if i < j else (j, i)
    for bi in range(world.b_count):
        if not world.b_alive[bi]:
            continue
        x, y = int(world.b_atom_i[bi]), int(world.b_atom_j[bi])
        if (min(x, y), max(x, y)) == (a, b):
            world.b_strength[bi] = float(world.b_strength[bi]) + float(delta)
            return bi
    bi = world.b_count
    if bi >= world.b_alive.shape[0]:
        return -1
    world.b_alive[bi] = True
    world.b_atom_i[bi] = i
    world.b_atom_j[bi] = j
    world.b_strength[bi] = float(delta)
    world.b_count += 1
    if hasattr(world, "k_bond_count"):
        world.k_bond_count[i] = int(world.k_bond_count[i]) + 1
        world.k_bond_count[j] = int(world.k_bond_count[j]) + 1
    return bi


def _kill_other_bridges_from(world, atom: int, keep_partner: int) -> int:
    """PRIM8: kill alive bridges incident on *atom* except the one to keep_partner."""
    n = 0
    for bi in range(world.b_count):
        if not world.b_alive[bi]:
            continue
        x, y = int(world.b_atom_i[bi]), int(world.b_atom_j[bi])
        if atom not in (x, y):
            continue
        other = y if x == atom else x
        if other == keep_partner:
            continue
        world.b_alive[bi] = False
        if hasattr(world, "k_bond_count"):
            if world.k_alive[x]:
                world.k_bond_count[x] = max(0, int(world.k_bond_count[x]) - 1)
            if world.k_alive[y]:
                world.k_bond_count[y] = max(0, int(world.k_bond_count[y]) - 1)
        n += 1
    return n


def apply_ilw_pair_write(world, port_L, port_R, seed_L: float, seed_R: float, rng=None) -> dict:
    """PRIM5: dual ILW on L and R; optionally exclusive bridge between written slots.

    PRIM8: if ilw_pair_replace_enabled, drop other bridges from each endpoint.
    Returns {L, R, bridge, mode_L, mode_R}. No-op pieces if ilw disabled.
    """
    cfg = world.config
    out_L = apply_ilw_port_event(world, port_L, rng, seed_freq=float(seed_L))
    out_R = apply_ilw_port_event(world, port_R, rng, seed_freq=float(seed_R))
    i = int(out_L.get("atom_idx", -1))
    if i < 0:
        i = int(out_L.get("mol_idx", -1))
    j = int(out_R.get("atom_idx", -1))
    if j < 0:
        j = int(out_R.get("mol_idx", -1))
    b = -1
    killed = 0
    if getattr(cfg, "ilw_pair_link_enabled", False) and i >= 0 and j >= 0:
        d = float(getattr(cfg, "ilw_pair_link_delta", 1.0))
        b = _ensure_bridge(world, i, j, delta=d)
        if getattr(cfg, "ilw_pair_replace_enabled", False) and b >= 0:
            killed += _kill_other_bridges_from(world, i, j)
            killed += _kill_other_bridges_from(world, j, i)
    return {
        "L": out_L,
        "R": out_R,
        "atom_L": i,
        "atom_R": j,
        "bridge": b,
        "killed_bridges": killed,
    }


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
    # BET-103: engineered compartment wall on the x-plane (0 = off). Atoms only
    # integrate charge from vibrations on their own side, so firing cannot be
    # driven across the boundary (contains activity percolation).
    bx = getattr(cfg, 'compartment_boundary', 0.0)
    vx = v_pos[:, 0] if (bx > 0 and n_alive_v > 0) else None
    for ai in atom_indices:
        if world.t < world.k_refractory_until[ai]:
            continue
        if n_alive_v <= 0:   # guard: n_alive can underflow to <0; v_pos undefined then
            continue
        ap = world.k_pos[ai]
        # Periodic-image squared distance
        d = v_pos - ap
        # wrap to [-box/2, box/2]
        d -= box * np.round(d / box)
        d2 = (d * d).sum(axis=1)
        in_range = (d2 <= r2) & v_alive
        if bx > 0:
            in_range = in_range & ((vx < bx) == (ap[0] < bx))  # same compartment only
        n_in = int(in_range.sum())
        if n_in > 0:
            world.k_charge[ai] += float(n_in)

    # Plan B: oriented bridges transmit aligned vibrations as charge before
    # the threshold check, so a strong bridge can drive this-tick firing.
    synaptic_transmission(world, dt)

    # 3. Fire: any atom with charge ≥ theta and not refractory emits.
    # PRIM9: k_theta_fire[i] > 0 overrides cfg.theta_fire for that node.
    thr = np.full(len(atom_indices), float(cfg.theta_fire), dtype=np.float64)
    if hasattr(world, "k_theta_fire"):
        custom = world.k_theta_fire[atom_indices]
        use = custom > 0
        thr[use] = custom[use]
    can_fire = (world.k_charge[atom_indices] >= thr) & (
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

    # G65: global k-winner-take-all lateral inhibition. Only the top-K most-charged atoms fire
    # each tick; weakly-driven atoms are suppressed. A directionally self-limiting write: only
    # strongly-driven (e.g. stimulated) atoms fire and co-fire, so the write cannot spread to
    # weakly-driven regions. No-op when global_wta_k == 0.
    gk = getattr(cfg, 'global_wta_k', 0)
    if gk > 0 and len(firing_atoms) > gk:
        ch = world.k_charge[firing_atoms]
        top = np.argpartition(-ch, gk - 1)[:gk]
        firing_atoms = firing_atoms[top]

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

    # PRIM10: lateral charge inhibition around firers (soft competition).
    r_inh = float(getattr(cfg, "fire_inhibit_radius", 0.0) or 0.0)
    frac_inh = float(getattr(cfg, "fire_inhibit_frac", 0.5) or 0.0)
    if r_inh > 0.0 and frac_inh > 0.0 and len(firing_atoms) > 0:
        box = np.asarray(cfg.box_size, dtype=np.float64)
        r2i = r_inh * r_inh
        scale = max(0.0, 1.0 - frac_inh)
        fire_set = set(int(x) for x in firing_atoms)
        K = world.k_count
        for ai in firing_atoms:
            ap = world.k_pos[int(ai)]
            for j in range(K):
                if j in fire_set or not world.k_alive[j] or int(world.k_level[j]) < 4:
                    continue
                d = world.k_pos[j] - ap
                d -= box * np.round(d / box)
                if float(np.dot(d, d)) <= r2i:
                    world.k_charge[j] *= scale

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


def cull_excess_vibrations(world) -> int:
    """Cap the number of alive vibrations at world.config.vibration_soft_cap.

    Default behaviour (cap = 0) is a no-op so existing simulations are
    byte-identical. When the cap is positive and alive count exceeds it,
    the *oldest* alive vibrations (lowest indices — FIFO-allocated by the
    feeder) are killed until alive count equals the cap.

    Why: under sustained high-entropy audio injection (predictive-babble
    pipeline), most vibrations don't bind because their frequency ratios
    miss the golden-ratio binding window and their polarities don't
    pair up. Without a cap, alive count climbs to n_vibrations_max and
    every physics tick processes all of them — cycle wall-time grows
    super-linearly. The cull bounds tick cost.

    Returns the number of vibrations killed this tick.
    """
    cap = int(world.config.vibration_soft_cap)
    if cap <= 0:
        return 0
    alive_idx = np.where(world.s_alive)[0]
    n_alive = int(alive_idx.size)
    if n_alive <= cap:
        return 0
    n_to_kill = n_alive - cap
    to_kill = alive_idx[:n_to_kill]
    world.s_alive[to_kill] = False
    world.n_alive = int(max(0, world.n_alive - n_to_kill))
    return int(n_to_kill)


def apply_node_resonance(world, dt: float) -> None:
    """Kuramoto-style frequency synchronization between nearby nodes.

    Nodes within r_2 of each other pull their frequencies toward each
    other proportionally to coupling strength and inversely to frequency
    difference. This is the physical mechanism that makes the 8% binding
    rule achievable: nearby nodes that initially differ by >8% slowly
    synchronize until they enter the binding window.

    df_i/dt = coupling * sum_j(sin(2*pi*(f_j - f_i) / f_i))

    Simplified to linear pull for small differences:
    df_i/dt = coupling * sum_j((f_j - f_i) / max(f_i, f_j))

    Only active when cfg.resonance_coupling > 0.
    """
    cfg = world.config
    coupling = getattr(cfg, 'resonance_coupling', 0.0)
    if coupling <= 0:
        return
    K = world.k_count
    if K < 2:
        return
    r2 = cfg.r_2
    box = np.asarray(cfg.box_size, dtype=np.float64)
    # Numpy vectorized all-pairs resonance (no grid, no Python loops)
    alive_idx = np.where(world.k_alive[:K])[0]
    n = len(alive_idx)
    if n < 2:
        return
    pos = world.k_pos[alive_idx]
    freq = world.k_freq[alive_idx]
    level = world.k_level[alive_idx].astype(np.float64)
    r2_sq = r2 * r2

    # All-pairs distance (periodic)
    # diff[i,j,d] = pos[i,d] - pos[j,d]
    diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]  # (n, n, 3)
    diff -= box * np.round(diff / box)
    d2 = (diff * diff).sum(axis=2)  # (n, n)

    # Mask: within r2, not self
    mask = (d2 < r2_sq) & (np.eye(n, dtype=bool) == False)

    # Frequency pull: coupling/level_i * (f_j - f_i) / max(f_i, f_j)
    fi = freq[:, np.newaxis]  # (n, 1)
    fj = freq[np.newaxis, :]  # (1, n)
    fmax = np.maximum(fi, fj)
    fmax = np.maximum(fmax, 1e-6)
    inertia = level[:, np.newaxis]  # (n, 1)

    pull = coupling / inertia * (fj - fi) / fmax * dt  # (n, n)
    pull[~mask] = 0.0
    delta = pull.sum(axis=1)  # (n,)

    world.k_freq[alive_idx] = np.maximum(1.0, freq + delta)


def tick(world, dt: float) -> None:
    """One simulation step. See CONCEPT.md v2 §4 + §7.1 for the canonical order."""
    box = np.asarray(world.config.box_size, dtype=np.float64)
    # G19: cull at the START of tick so move_vibrations + bind work on a
    # bounded set. Without this, neuron_dynamics's firing emissions
    # (~n_emit per fire × ~hundreds of fires) flood the buffer at the
    # END of the previous tick and the NEXT tick's move_vibrations
    # processes all of them. Default cap = 0 → no-op for legacy worlds.
    cull_excess_vibrations(world)
    # PRIM1-D2 needs pre-move x to detect midplane cross and periodic wrap.
    if getattr(world.config, "midplane_wall_enabled", False) and world.n_alive > 0:
        world._s_pos_pre_x = world.s_pos[:, 0].copy()
    else:
        world._s_pos_pre_x = None
    move_vibrations(world.s_pos, world.s_vel, world.s_alive, box, dt)
    apply_midplane_wall(world, dt)  # PRIM1-D2 — free-vib midplane reflect (no-op unless enabled)
    apply_membrane_channel(world, dt)  # G31 — selective-permeability barrier (no-op when membrane_channel_k=0)
    apply_engineered_compartment(world, dt)  # G33 — engineered port wall (no-op when compartment_k=0)
    apply_scale_repulsion(world, dt)
    move_nodes(world, dt)
    # Resonance every 10 ticks (expensive O(n^2) neighbor query)
    if not hasattr(world, '_resonance_counter'):
        world._resonance_counter = 0
    world._resonance_counter += 1
    if world._resonance_counter % 10 == 0:
        apply_node_resonance(world, dt * 10)  # accumulated dt
    bind_vibrations_to_electrons(world)
    bind_nodes_upward(world)
    # Persistent bridges between atoms (valence-constrained)
    from world.bridges import (form_bridges, decay_bridges,
                                apply_bridge_tension, apply_atom_repulsion,
                                apply_edge_closure)
    form_bridges(world)
    apply_bridge_tension(world, dt)
    apply_atom_repulsion(world, dt)
    from world.bridges import (apply_spontaneous_curvature,
                                apply_flux_plasticity, apply_bistable_plasticity,
                                apply_structural_anchoring)
    apply_spontaneous_curvature(world, dt)
    apply_flux_plasticity(world, dt)
    apply_bistable_plasticity(world, dt)
    apply_structural_anchoring(world, dt)  # BET-090: freeze mature sites (no-op when anchor_damping=0)
    decay_bridges(world, dt)
    apply_bond_turnover(world, dt)      # G53 — spontaneous bond break (fluid membrane); no-op when bond_turnover_rate=0
    decay_unstable_nodes(world, dt)
    decay_high_level_nodes(world, dt)   # NEW (R2)
    apply_ilw_strength_decay(world, dt)  # PRIM3 — L4 strength leak (no-op unless tau>0)
    ambient_regeneration(world, dt)
    # G15: dream-state replay seeding. Must run BEFORE neuron_dynamics so
    # injected charge triggers firings within the same tick. No-op when
    # cfg.dream_mode_enabled is False.
    from world.dream import apply_dream
    apply_dream(world, dt)
    neuron_dynamics(world, dt)
    apply_bridge_atom_propagation(world, dt)  # NEW (G6) — direct atom→atom charge through strong bridges
    apply_stdp(world)              # NEW (Plan B)
    from world.bridges import apply_correlation_plasticity, apply_bridge_charge_propagation
    apply_correlation_plasticity(world, dt)  # BET-099 — firing-coincidence bridge plasticity (no-op when rate=0)
    apply_bridge_charge_propagation(world, dt)  # BET-105 — non-broadcast write along bridges (no-op when rate=0)
    apply_fire_zero_latch(world)  # PRIM11 — clear latch after prop (XOR inhibit)
    apply_fire_kill_bridges(world)  # PRIM12 — structural cut after fire
    apply_fire_weaken_bridges(world)  # PRIM13 — soft reversible bridge weaken
    apply_charge_latch_decay(world, dt)  # PRIM6 — latched prop mark (no-op unless latch on)
    apply_btsp(world, dt)          # NEW (G14) — second-scale eligibility-trace plasticity
    # G16: self-aware substrate — must run after apply_btsp so
    # eligibility traces and firings reflect this tick's reality.
    from world.self_aware import apply_self_aware
    apply_self_aware(world, dt)
    apply_speech_loop(world, dt)   # NEW (Plan F)
    # G18.3: prune the firing log every tick regardless of
    # stdp_enabled. apply_stdp does this internally only when STDP
    # is on; with STDP disabled (autonomous loop default) the log
    # would grow unboundedly otherwise.
    prune_firing_log(world)
    world.t += dt

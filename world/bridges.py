"""Bridge formation — persistent connections between atoms.

Unlike fusion (2 nodes → 1 product), bridges connect atoms without
consuming them. Each atom stays alive with its own position and
properties. The bridge is a separate entity that links two atoms.

This enables chain topology: an atom with valence=2 can be part of
exactly 2 bridges, forming a linear chain. Valence=3 gives branching.

Bridge state is stored as parallel arrays in World:
  b_alive[B]     — is bridge alive
  b_atom_i[B]    — index of first connected atom
  b_atom_j[B]    — index of second connected atom
  b_strength[B]  — connection strength (grows with co-activation)
"""
from __future__ import annotations

import numpy as np
from world.spatial import periodic_distance_sq


def form_bridges(world) -> int:
    """Check all atom pairs within r_2: form bridges where valence allows.

    Returns number of new bridges formed this tick.
    """
    cfg = world.config
    valence = getattr(cfg, 'atom_valence', 0)
    if valence <= 0:
        return 0

    K = world.k_count
    if K < 2:
        return 0

    box = np.asarray(cfg.box_size, dtype=np.float64)
    r2 = cfg.r_2
    r2_sq = r2 * r2

    # Find all alive atoms (level 4)
    atom_mask = world.k_alive[:K] & (world.k_level[:K] == 4)
    atom_idx = np.where(atom_mask)[0]
    n_atoms = len(atom_idx)
    if n_atoms < 2:
        return 0

    # All-pairs distance check
    pos = world.k_pos[atom_idx]
    ii, jj = np.triu_indices(n_atoms, k=1)
    d = pos[ii] - pos[jj]
    d -= box * np.round(d / box)
    d2 = (d * d).sum(axis=1)
    close = d2 < r2_sq

    if not close.any():
        return 0

    ci = atom_idx[ii[close]]
    cj = atom_idx[jj[close]]

    # G86: engineered modularity at the BRIDGE level — no bridge may form across the
    # compartment boundary plane (x = compartment_boundary). Disconnects stim from control
    # so charge cannot percolate along the lattice graph. 0 = off.
    bx = getattr(cfg, 'compartment_boundary', 0.0)
    if bx > 0 and len(ci) > 0:
        same_side = (world.k_pos[ci][:, 0] < bx) == (world.k_pos[cj][:, 0] < bx)
        ci = ci[same_side]
        cj = cj[same_side]

    # Check valence: both atoms must have room
    bonds_i = world.k_bond_count[ci]
    bonds_j = world.k_bond_count[cj]
    can_bind = (bonds_i < valence) & (bonds_j < valence)
    ci = ci[can_bind]
    cj = cj[can_bind]

    if len(ci) == 0:
        return 0

    # Check: no duplicate bridges (same pair already connected)
    B = world.b_count
    existing = set()
    for b in range(B):
        if world.b_alive[b]:
            a, bb = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            existing.add((min(a, bb), max(a, bb)))

    formed = 0
    for k in range(len(ci)):
        i, j = int(ci[k]), int(cj[k])
        key = (min(i, j), max(i, j))
        if key in existing:
            continue
        # Check valence again (may have changed from earlier iterations)
        if world.k_bond_count[i] >= valence or world.k_bond_count[j] >= valence:
            continue

        # Bridge cooldown: atoms that recently bridged can't bridge again
        # immediately. This prevents instant triangle closure and lets
        # chains grow longer before closing.
        cooldown = getattr(cfg, 'bridge_cooldown', 0.0)
        if cooldown > 0:
            age_i = world.t - world.k_birth[i]
            age_j = world.t - world.k_birth[j]
            # Use last_bridge_time stored in k_strength temporarily
            last_i = getattr(world, '_last_bridge_time', {}).get(i, -1e6)
            last_j = getattr(world, '_last_bridge_time', {}).get(j, -1e6)
            if world.t - last_i < cooldown or world.t - last_j < cooldown:
                continue

        # Form bridge
        b = world.b_count
        if b >= world.b_alive.shape[0]:
            break

        world.b_alive[b] = True
        world.b_atom_i[b] = i
        world.b_atom_j[b] = j
        world.b_strength[b] = 1.0
        world.b_count += 1

        world.k_bond_count[i] += 1
        world.k_bond_count[j] += 1
        existing.add(key)
        formed += 1

        # Record bridge time for cooldown
        if cooldown > 0:
            if not hasattr(world, '_last_bridge_time'):
                world._last_bridge_time = {}
            world._last_bridge_time[i] = world.t
            world._last_bridge_time[j] = world.t

    return formed


def apply_bridge_tension(world, dt: float) -> None:
    """Pull bridged atoms toward equilibrium distance.

    Each bridge acts like a spring: atoms closer than r_eq are pushed
    apart, atoms farther are pulled together. This straightens chains
    and prevents bridge-connected atoms from clumping.
    """
    cfg = world.config
    r_eq = cfg.r_2 * 0.5  # equilibrium = 50% of binding radius
    tension_k = 0.5  # spring constant (gentle)
    box = np.asarray(cfg.box_size, dtype=np.float64)

    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        i = int(world.b_atom_i[b])
        j = int(world.b_atom_j[b])
        if not world.k_alive[i] or not world.k_alive[j]:
            continue

        # Periodic displacement
        d = world.k_pos[j] - world.k_pos[i]
        d -= box * np.round(d / box)
        dist = np.sqrt((d * d).sum())
        if dist < 1e-6:
            continue

        # Spring force: F = k * (dist - r_eq) toward/away
        direction = d / dist
        force = tension_k * (dist - r_eq) * dt

        # Apply force (gentle, with velocity damping)
        level_i = max(1.0, float(world.k_level[i]))
        level_j = max(1.0, float(world.k_level[j]))
        world.k_vel[i] += direction * force / level_i
        world.k_vel[j] -= direction * force / level_j
        # Damping: bridged atoms slow down (viscous medium)
        world.k_vel[i] *= 0.95
        world.k_vel[j] *= 0.95


def apply_atom_repulsion(world, dt: float) -> None:
    """Non-bonded atoms repel each other. Combined with bridge tension
    (bonded atoms attract), this produces minimal surfaces — rings flatten
    into membranes, the way soap films and lipid bilayers minimize energy.

    Only acts between atoms that are NOT directly bridged. Bridged pairs
    are governed by bridge tension (attraction toward equilibrium).
    """
    cfg = world.config
    rep_k = getattr(cfg, 'atom_repulsion_k', 0.0)
    if rep_k <= 0:
        return
    K = world.k_count
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r_rep = cfg.r_2 * 0.5  # short-range: only spread close atoms, don't block binding

    atom_mask = world.k_alive[:K] & (world.k_level[:K] == 4)
    atom_idx = np.where(atom_mask)[0]
    n = len(atom_idx)
    if n < 2:
        return

    # Bonded pairs to exclude
    bonded = set()
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            bonded.add((min(i, j), max(i, j)))

    pos = world.k_pos[atom_idx]
    # All-pairs displacement
    diff = pos[:, None, :] - pos[None, :, :]  # (n, n, 3)
    diff -= box * np.round(diff / box)
    dist = np.sqrt((diff * diff).sum(axis=2))  # (n, n)

    for a in range(n):
        force = np.zeros(3)
        for b in range(n):
            if a == b:
                continue
            d = dist[a, b]
            if d >= r_rep or d < 1e-6:
                continue
            ia, ib = int(atom_idx[a]), int(atom_idx[b])
            if (min(ia, ib), max(ia, ib)) in bonded:
                continue  # bonded → bridge tension handles it
            # Inverse repulsion: stronger when closer
            mag = rep_k * (1.0 - d / r_rep) * dt
            force += (diff[a, b] / d) * mag
        world.k_vel[atom_idx[a]] += force


def apply_spontaneous_curvature(world, dt: float) -> None:
    """Push each bridged atom away from its bridge-neighbour centroid.

    For an interior atom with symmetric neighbours the centroid sits on
    the atom — no net force. For an edge atom the neighbours are on one
    side, so the atom is pushed outward, curling the boundary up out of
    the plane. Accumulated, a flat sheet domes into a shell (Helfrich
    spontaneous curvature).
    """
    cfg = world.config
    curv_k = getattr(cfg, 'curvature_k', 0.0)
    if curv_k <= 0:
        return
    K = world.k_count
    box = np.asarray(cfg.box_size, dtype=np.float64)

    # Build adjacency
    nbrs = {}
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            if i < K and j < K and world.k_alive[i] and world.k_alive[j]:
                nbrs.setdefault(i, []).append(j)
                nbrs.setdefault(j, []).append(i)

    for i, ns in nbrs.items():
        if len(ns) < 2:
            continue
        # Vector from neighbour centroid to atom (periodic)
        acc = np.zeros(3)
        for j in ns:
            d = world.k_pos[i] - world.k_pos[j]
            d -= box * np.round(d / box)
            acc += d
        # acc points from centroid toward atom; push further that way
        norm = np.sqrt((acc * acc).sum())
        if norm < 1e-6:
            continue
        world.k_vel[i] += (acc / norm) * curv_k * dt


def apply_edge_closure(world, dt: float) -> None:
    """Edge atoms (free valence) attract other edge atoms, curling the
    sheet toward closure. Models the higher energy of exposed membrane
    edges that drives vesicle closure in lipid systems.
    """
    cfg = world.config
    close_k = getattr(cfg, 'edge_closure_k', 0.0)
    valence = getattr(cfg, 'atom_valence', 0)
    if close_k <= 0 or valence <= 0:
        return
    K = world.k_count
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r_close = cfg.r_2 * 2.0  # edges feel each other at longer range

    atom_mask = world.k_alive[:K] & (world.k_level[:K] == 4)
    atom_idx = np.where(atom_mask)[0]
    # Edge atoms: have at least one free valence slot
    edges = [int(a) for a in atom_idx if world.k_bond_count[a] < valence
             and world.k_bond_count[a] > 0]  # bonded but not saturated
    if len(edges) < 2:
        return

    bonded = set()
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            bonded.add((min(i, j), max(i, j)))

    for a in range(len(edges)):
        ia = edges[a]
        force = np.zeros(3)
        for b in range(a + 1, len(edges)):
            ib = edges[b]
            if (min(ia, ib), max(ia, ib)) in bonded:
                continue
            d = world.k_pos[ib] - world.k_pos[ia]
            d -= box * np.round(d / box)
            dist = np.sqrt((d * d).sum())
            if dist < 1e-6 or dist > r_close:
                continue
            # Attraction toward other edge (pulls boundary together)
            mag = close_k * (dist / r_close) * dt
            force += (d / dist) * mag
        world.k_vel[ia] += force


def apply_flux_plasticity(world, dt: float) -> None:
    """Bridge strength follows vibration flux through it.

    A bridge whose endpoint atoms both sit in high-vibration-density
    regions carries more flux and strengthens. Low-flux bridges weaken.
    This is structural plasticity from physics — not an STDP rule, not
    spike-timing, not supervised. Strength tracks the energy flowing
    through the channel, the way a riverbed deepens under flow.
    """
    cfg = world.config
    rate = getattr(cfg, 'flux_plasticity_rate', 0.0)
    if rate <= 0:
        return
    K = world.k_count
    if world.b_count == 0:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r_sense = cfg.r_2  # radius around an atom to count vibration flux
    r_sense_sq = r_sense * r_sense
    threshold = getattr(cfg, 'flux_threshold', 2.0)
    decay = getattr(cfg, 'flux_decay', 0.05)
    max_s = getattr(cfg, 'flux_max_strength', 10.0)

    # Count vibrations near each atom that has a bridge
    atoms_with_bridges = set()
    for b in range(world.b_count):
        if world.b_alive[b]:
            atoms_with_bridges.add(int(world.b_atom_i[b]))
            atoms_with_bridges.add(int(world.b_atom_j[b]))

    vib_pos = world.s_pos
    vib_alive = world.s_alive
    density = {}
    for a in atoms_with_bridges:
        if a >= K or not world.k_alive[a]:
            density[a] = 0
            continue
        ap = world.k_pos[a]
        d = vib_pos - ap
        d -= box * np.round(d / box)
        d2 = (d * d).sum(axis=1)
        density[a] = int(np.sum(vib_alive & (d2 < r_sense_sq)))

    # Relative plasticity: compute flux per bridge, then potentiate
    # bridges above the mean and depress below. Auto-adapts to background
    # density — detects relative hotspots, not absolute level. Parameter-
    # free competition between channels for the vibration flux.
    fluxes = []
    bridge_ids = []
    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        fluxes.append(density.get(i, 0) * density.get(j, 0))
        bridge_ids.append(b)
    if not fluxes:
        return
    fluxes = np.array(fluxes, dtype=np.float64)
    nb = len(bridge_ids)
    total_flux = fluxes.sum()
    if total_flux < 1e-6:
        return
    # Conserved redistribution: a fixed total bond-energy budget is shared
    # among bridges in proportion to the flux they carry. High-flux bridges
    # gain at the expense of low-flux ones. The system cannot globally
    # saturate — strengthening one channel weakens others. Finite binding
    # energy redistributed by flux. This is competition, not amplification.
    budget = nb * 1.0  # mean strength stays ~1.0
    target = budget * (fluxes / total_flux)  # proportional share
    for k, b in enumerate(bridge_ids):
        cur = world.b_strength[b]
        # Relax toward flux-proportional target
        world.b_strength[b] = float(np.clip(
            cur + rate * dt * (target[k] - cur), 0.0, max_s))


def apply_bistable_plasticity(world, dt: float) -> None:
    """Bistable bridge strength — the mechanism BET-087/088 found missing.

    Each bridge sits in a double-well potential: stable WEAK and STRONG
    states with an unstable barrier between. Vibration flux pushes
    strength up. If flux pushes it past the barrier, it falls into the
    STRONG well and LATCHES there — staying strong after the flux stops.
    That hysteresis is memory: a record of past flux, not a mirror of
    present flux. This is how a synapse holds LTP.

    ds/dt = -k*(s-low)*(s-mid)*(s-high)  +  flux_drive
    """
    cfg = world.config
    rate = getattr(cfg, 'bistable_rate', 0.0)
    if rate <= 0:
        return
    K = world.k_count
    if world.b_count == 0:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r_sense_sq = cfg.r_2 * cfg.r_2
    low = getattr(cfg, 'bistable_low', 1.0)
    mid = getattr(cfg, 'bistable_mid', 3.0)
    high = getattr(cfg, 'bistable_high', 6.0)
    well_k = getattr(cfg, 'bistable_well_k', 0.02)
    flux_gain = getattr(cfg, 'bistable_flux_gain', 0.02)
    flux_ref = getattr(cfg, 'bistable_flux_ref', 30.0)

    # Local vibration density per bridged atom
    atoms = set()
    for b in range(world.b_count):
        if world.b_alive[b]:
            atoms.add(int(world.b_atom_i[b])); atoms.add(int(world.b_atom_j[b]))
    vib_pos = world.s_pos
    vib_alive = world.s_alive
    density = {}
    for a in atoms:
        if a >= K or not world.k_alive[a]:
            density[a] = 0.0
            continue
        d = vib_pos - world.k_pos[a]
        d -= box * np.round(d / box)
        density[a] = float(np.sum(vib_alive & ((d * d).sum(axis=1) < r_sense_sq)))

    # Flux per bridge, then drive RELATIVE to the mean. Only above-average-
    # flux bridges are pushed up; below-average pushed down. Combined with
    # the double well, above-average bridges latch strong and STAY strong
    # even after their flux returns to average (hysteresis = memory).
    fluxes = []
    ids = []
    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        fluxes.append(density.get(i, 0.0) * density.get(j, 0.0))
        ids.append(b)
    if not ids:
        return
    fluxes = np.array(fluxes, dtype=np.float64)
    mean_flux = max(fluxes.mean(), 1e-6)
    # BET-092: drive mode. 'relative' (default, BET-089 v2) drives strength up
    # only for above-MEAN-flux bridges — but on a populated lattice the mean
    # rides up with the stimulus and the ratio stays near 1, so nothing latches.
    # 'absolute' drives up bridges above a FIXED reference (bistable_flux_ref):
    # stim-region flux clears the reference and latches; resting flux does not.
    mode = getattr(cfg, 'bistable_drive_mode', 'relative')
    ref = flux_ref if mode == 'absolute' else mean_flux
    # BET-097: rectified drive. The two-sided drive is negative whenever flux <
    # ref, so when the field is removed (flux→0) it actively pushes latched
    # bridges DOWN and erases the memory. Rectifying (max(0, ·)) makes flux a
    # one-sided WRITE signal: it only pushes strength UP, and the bistable well
    # alone decides hold-vs-decay. "No input" then means "hold", as a latch must.
    rectified = getattr(cfg, 'bistable_drive_rectified', False)
    for k, b in enumerate(ids):
        s = world.b_strength[b]
        well = -well_k * (s - low) * (s - mid) * (s - high)
        drive = flux_gain * (fluxes[k] / ref - 1.0)
        if rectified and drive < 0.0:
            drive = 0.0
        s_new = s + rate * dt * (well + drive)
        world.b_strength[b] = float(np.clip(s_new, 0.0, high + 1.0))


def apply_correlation_plasticity(world, dt: float) -> None:
    """BET-099: Hebbian firing-coincidence plasticity on bridges.

    The flux-driven bistable latch (BET-089→098) wrote selectively but its
    memory eroded — per-bridge flux state is fragile against bridge turnover.
    Here the SAME bistable double-well (which holds well, BET-097) is driven by
    a turnover-robust WRITE signal: when two BRIDGED atoms FIRE within tau_LTP
    of each other (neuron_dynamics → firing_events), the bridge between them is
    pushed over the barrier into the STRONG well. Bridges with no recent
    co-firing get zero drive and relax to whichever well they are in — so the
    well alone decides hold-vs-decay and "no input" means "hold".

    Reuses substrate primitives only: firing_events (spike log), bridges
    (b_atom_i/j, b_strength), and the bistable well params. No molecules, no LLM.
    Gated by cfg.corr_plasticity_rate (0 = off).
    """
    cfg = world.config
    rate = getattr(cfg, 'corr_plasticity_rate', 0.0)
    if rate <= 0 or world.b_count == 0:
        return
    low = getattr(cfg, 'bistable_low', 1.0)
    mid = getattr(cfg, 'bistable_mid', 3.0)
    high = getattr(cfg, 'bistable_high', 6.0)
    well_k = getattr(cfg, 'bistable_well_k', 0.04)
    pot = getattr(cfg, 'corr_potentiation', 1.0)
    tau = getattr(cfg, 'tau_LTP', 0.02)

    # Bridge lookup by (sorted) atom pair.
    bridge_of = {}
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            bridge_of[(i, j) if i < j else (j, i)] = b

    # BET-103: engineered compartment — co-firing potentiation cannot cross the
    # x-plane wall (0 = off).
    bx = getattr(cfg, 'compartment_boundary', 0.0)

    # Bridges whose two atoms co-fired within tau_LTP this retention window.
    cofired = set()
    ev = world.firing_events
    for x in range(len(ev)):
        t_i, ai = ev[x]
        for y in range(x + 1, len(ev)):
            t_j, aj = ev[y]
            if abs(t_j - t_i) > tau or ai == aj:
                continue
            if bx > 0 and ai < world.k_count and aj < world.k_count:
                if (world.k_pos[ai][0] < bx) != (world.k_pos[aj][0] < bx):
                    continue  # pair straddles the compartment wall — no cross-write
            key = (ai, aj) if ai < aj else (aj, ai)
            b = bridge_of.get(key)
            if b is not None:
                cofired.add(b)

    # BET-108: consolidation. Once a bridge latches past consol_threshold it is
    # locked at the strong well — immune to subsequent decay/turnover — so a
    # written memory cannot drift back below mid in POST (the recall metastability
    # that capped BET-106 at 0.32). 0 = off. Control bridges never reach the
    # threshold, so they are never locked.
    consol = getattr(cfg, 'bridge_consolidate_threshold', 0.0)
    if consol > 0 and not hasattr(world, '_consolidated'):
        world._consolidated = set()

    # G69: LEAKY write. A continuous downward pull toward `low`, so a bridge stays high ONLY while
    # CONTINUOUSLY reinforced (drive must beat leak). This breaks the bistable well's "no input =
    # hold" — which latched any control bridge that transiently crossed mid. With a leak, the
    # stim engram (continuous co-firing) holds and consolidates, while control's INTERMITTENT
    # co-firing decays back to low between bumps and never consolidates -> selective by the
    # temporal structure of the drive. 0 = off (original hold-forever well).
    leak = getattr(cfg, 'bridge_leak_rate', 0.0)

    # Bistable well + rectified one-sided co-firing drive.
    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        if consol > 0 and b in world._consolidated:
            world.b_strength[b] = high        # locked (consolidated memory)
            continue
        s = world.b_strength[b]
        well = -well_k * (s - low) * (s - mid) * (s - high)
        drive = pot if b in cofired else 0.0
        s_new = s + rate * dt * (well + drive) - leak * dt * (s - low)
        s_new = float(np.clip(s_new, 0.0, high + 1.0))
        world.b_strength[b] = s_new
        if consol > 0 and s_new >= consol:
            world._consolidated.add(b)
            world.b_strength[b] = high


def apply_bridge_charge_propagation(world, dt: float) -> None:
    """BET-105: non-broadcast write along the BRIDGE GRAPH.

    The omnidirectional emission write (BET-104) floods or percolates — it is
    the bottleneck. Here a firing atom deposits charge DIRECTLY into its bridged
    neighbours (no emitted vibrations), scaled by bridge strength. Co-activation
    then travels only along connectivity, so it does not flood; and the
    compartment wall (cutting cross-boundary bridges) contains it WITHOUT
    starving within-compartment propagation. Strength feeds back: a strong
    bridge propagates harder, so a written memory self-sustains its own recall.

    Reuses only firing_events, bridges, k_charge, and the bistable strength.
    Gated by cfg.bridge_charge_prop_rate (0 = off). Pairs with n_emit≈0.
    """
    cfg = world.config
    gain = getattr(cfg, 'bridge_charge_prop_rate', 0.0)
    if gain <= 0 or world.b_count == 0:
        return
    K = world.k_count
    t_now = world.t
    firing = {int(ai) for (tf, ai) in world.firing_events if tf == t_now and ai < K}
    if not firing:
        return
    bx = getattr(cfg, 'compartment_boundary', 0.0)
    # BET-107: graded propagation — only already-LATCHED bridges (strength >=
    # prop_min) carry the recall signal. A written stim bridge self-sustains its
    # memory; a blank control bridge (strength ~low) cannot carry any charge, so
    # control is silent by construction. The initial WRITE still comes from the
    # stimulus vibrations + correlation potentiation; propagation only sustains
    # what has already been written. 0 = ungated (BET-105/106 behaviour).
    prop_min = getattr(cfg, 'bridge_prop_min_strength', 0.0)
    latch_on = bool(getattr(cfg, "charge_latch_enabled", False))
    coin = bool(getattr(cfg, "coincidence_and_enabled", False))
    coin_sources = {}
    coin_deps = {}

    def _gated(tgt: int) -> bool:
        if not coin or not hasattr(world, "k_coincidence_gate"):
            return False
        return int(world.k_coincidence_gate[tgt]) != 0

    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        s = world.b_strength[b]
        if s < prop_min:
            continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        if i >= K or j >= K:
            continue
        if bx > 0 and ((world.k_pos[i][0] < bx) != (world.k_pos[j][0] < bx)):
            continue  # cross-compartment bridge is cut — no propagation across
        if i in firing and world.k_alive[j]:
            dep = gain * s
            if _gated(j):
                coin_sources.setdefault(j, set()).add(i)
                coin_deps[j] = coin_deps.get(j, 0.0) + dep
            else:
                world.k_charge[j] += dep
                if latch_on and hasattr(world, "k_latch"):
                    world.k_latch[j] = float(world.k_latch[j]) + dep
        if j in firing and world.k_alive[i]:
            dep = gain * s
            if _gated(i):
                coin_sources.setdefault(i, set()).add(j)
                coin_deps[i] = coin_deps.get(i, 0.0) + dep
            else:
                world.k_charge[i] += dep
                if latch_on and hasattr(world, "k_latch"):
                    world.k_latch[i] = float(world.k_latch[i]) + dep
    # PRIM9: coincidence-gated targets need ≥2 distinct firers same tick
    for tgt, srcs in coin_sources.items():
        if len(srcs) < 2:
            continue
        dep = float(coin_deps.get(tgt, 0.0))
        world.k_charge[tgt] += dep
        if latch_on and hasattr(world, "k_latch"):
            world.k_latch[tgt] = float(world.k_latch[tgt]) + dep


def apply_structural_anchoring(world, dt: float) -> None:
    """Mature, fully-bonded atoms stiffen the lattice — they stop drifting.

    An atom that has held a high bond count for a sustained period is an
    interior lattice site whose neighbours have locked in. Real membranes
    and crystals rigidify this way: once the local coordination saturates,
    the bonds stop rearranging and the site is fixed. We model that by
    damping the velocity of mature atoms hard, freezing the scaffold.

    This is NOT hand-placing atoms — the atoms emerged from the cascade.
    It only freezes what already self-assembled, so the bridges riding on
    them keep stable identities. Without it the handful of mobile bridges
    drift between regions and no place-specific read-out is possible
    (the confound that blocked BET-089's selective memory).
    """
    cfg = world.config
    damping = getattr(cfg, 'anchor_damping', 0.0)
    if damping <= 0:
        return
    bond_min = getattr(cfg, 'anchor_bond_min', 2)
    age_req = getattr(cfg, 'anchor_age', 50.0)
    K = world.k_count

    if not hasattr(world, '_bond_mature_since'):
        world._bond_mature_since = {}
    mature = world._bond_mature_since

    for a in range(K):
        if not world.k_alive[a] or world.k_level[a] != 4:
            mature.pop(a, None)
            continue
        if world.k_bond_count[a] >= bond_min:
            if a not in mature:
                mature[a] = world.t
            # Freeze once it has been mature long enough
            if world.t - mature[a] >= age_req:
                world.k_vel[a] *= damping
        else:
            mature.pop(a, None)


def decay_bridges(world, dt: float) -> int:
    """Remove bridges whose atoms are dead."""
    removed = 0
    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        i = int(world.b_atom_i[b])
        j = int(world.b_atom_j[b])
        if i >= world.k_count or j >= world.k_count:
            world.b_alive[b] = False
            removed += 1
            continue
        if not world.k_alive[i] or not world.k_alive[j]:
            world.b_alive[b] = False
            # Restore valence slots
            if i < world.k_count:
                world.k_bond_count[i] = max(0, world.k_bond_count[i] - 1)
            if j < world.k_count:
                world.k_bond_count[j] = max(0, world.k_bond_count[j] - 1)
            removed += 1
    return removed


def get_bridge_stats(world) -> dict:
    """Return bridge statistics for HUD display."""
    B = world.b_count
    if B == 0:
        return {'n_bridges': 0, 'n_chains': 0, 'max_chain': 0}

    alive_bridges = world.b_alive[:B]
    n_alive = int(alive_bridges.sum())

    if n_alive == 0:
        return {'n_bridges': 0, 'n_chains': 0, 'max_chain': 0}

    # Build adjacency from bridges → find connected components
    from collections import defaultdict, deque
    adj = defaultdict(set)
    for b in range(B):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            adj[i].add(j)
            adj[j].add(i)

    # Connected components via BFS
    visited = set()
    components = []
    for start in adj:
        if start in visited:
            continue
        comp = set()
        queue = deque([start])
        while queue:
            node = queue.popleft()
            if node in comp:
                continue
            comp.add(node)
            for nb in adj[node]:
                if nb not in comp:
                    queue.append(nb)
        visited |= comp
        components.append(comp)

    max_chain = max(len(c) for c in components) if components else 0

    return {
        'n_bridges': n_alive,
        'n_chains': len(components),
        'max_chain': max_chain,
    }

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

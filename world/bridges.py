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

        # Form bridge
        b = world.b_count
        if b >= world.b_alive.shape[0]:
            break  # bridge buffer full

        world.b_alive[b] = True
        world.b_atom_i[b] = i
        world.b_atom_j[b] = j
        world.b_strength[b] = 1.0
        world.b_count += 1

        world.k_bond_count[i] += 1
        world.k_bond_count[j] += 1
        existing.add(key)
        formed += 1

    return formed


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

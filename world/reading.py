"""Reading substrate — learn written English from substrate physics.

Architecture:
  - Retina: grid of atoms at fixed positions (input layer)
  - Letter rendering: each letter activates a subset of retina atoms
  - Hebbian bridges: bridges between co-activated atoms strengthen
  - Pattern completion: partial activation propagates through strong bridges

No Brian2. No STDP equations. Bridge strength grows from substrate
physics: atoms that vibrate together, bridge together.
"""
from __future__ import annotations

import numpy as np
from pathlib import Path


# 5x7 bitmap font for uppercase letters (standard LCD font)
FONT_5x7 = {
    'A': [
        "01110",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001",
    ],
    'B': [
        "11110",
        "10001",
        "10001",
        "11110",
        "10001",
        "10001",
        "11110",
    ],
    'C': [
        "01110",
        "10001",
        "10000",
        "10000",
        "10000",
        "10001",
        "01110",
    ],
    'D': [
        "11100",
        "10010",
        "10001",
        "10001",
        "10001",
        "10010",
        "11100",
    ],
    'E': [
        "11111",
        "10000",
        "10000",
        "11110",
        "10000",
        "10000",
        "11111",
    ],
    'H': [
        "10001",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001",
    ],
    'I': [
        "11111",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "11111",
    ],
    'L': [
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "11111",
    ],
    'O': [
        "01110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110",
    ],
    'T': [
        "11111",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
    ],
    'W': [
        "10001",
        "10001",
        "10001",
        "10101",
        "10101",
        "11011",
        "10001",
    ],
}


def letter_to_pixels(letter: str) -> np.ndarray:
    """Convert a letter to a 7x5 boolean array."""
    rows = FONT_5x7.get(letter.upper())
    if rows is None:
        return np.zeros((7, 5), dtype=bool)
    return np.array([[c == '1' for c in row] for row in rows], dtype=bool)


def create_retina(world, grid_w: int = 5, grid_h: int = 7,
                  spacing: float = 2.0, origin: np.ndarray = None) -> np.ndarray:
    """Create a grid of atoms as retina (input layer).

    Returns array of atom node indices (grid_h, grid_w).
    """
    if origin is None:
        box = np.asarray(world.config.box_size)
        origin = box * 0.3  # offset from corner

    retina = np.zeros((grid_h, grid_w), dtype=np.int32)
    for r in range(grid_h):
        for c in range(grid_w):
            pos = origin + np.array([c * spacing, r * spacing, 0.0])
            pos = pos % np.asarray(world.config.box_size)
            node = world.allocate_node(
                pos, freq=5000.0, pol=bool((r + c) % 2),
                level=4, constituents=np.array([], dtype=np.int32),
                comp_kind=1)
            retina[r, c] = node
    return retina


def activate_letter(world, retina: np.ndarray, letter: str,
                    charge: float = 10.0) -> int:
    """Activate retina atoms corresponding to a letter's pixels.

    Returns number of activated atoms.
    """
    pixels = letter_to_pixels(letter)
    activated = 0
    for r in range(min(pixels.shape[0], retina.shape[0])):
        for c in range(min(pixels.shape[1], retina.shape[1])):
            if pixels[r, c]:
                node = retina[r, c]
                if node < world.k_count and world.k_alive[node]:
                    world.k_charge[node] += charge
                    activated += 1
    return activated


def hebbian_bridge_update(world, retina: np.ndarray,
                          learning_rate: float = 0.1,
                          threshold: float = 5.0) -> int:
    """Strengthen bridges between co-activated retina atoms.

    Atoms with charge > threshold are "active". Bridges between
    two active atoms get their strength increased. Bridges between
    active and inactive atoms get weakened.

    Also forms NEW bridges between co-active atoms that don't have one yet.

    Returns number of bridges modified.
    """
    # Find active atoms
    flat = retina.flatten()
    active = set()
    for node in flat:
        if node < world.k_count and world.k_alive[node]:
            if world.k_charge[node] > threshold:
                active.add(int(node))

    if len(active) < 2:
        return 0

    modified = 0
    active_list = sorted(active)

    # Update existing bridges
    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        if i in active and j in active:
            # Both active: strengthen (Hebbian potentiation)
            world.b_strength[b] = min(10.0, world.b_strength[b] + learning_rate)
            modified += 1
        elif i in active or j in active:
            # One active: weaken (heterosynaptic depression)
            world.b_strength[b] = max(0.01, world.b_strength[b] - learning_rate * 0.3)
            modified += 1

    # Form new bridges between co-active atoms that lack one
    existing = set()
    for b in range(world.b_count):
        if world.b_alive[b]:
            a, bb = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            existing.add((min(a, bb), max(a, bb)))

    for a_idx in range(len(active_list)):
        for b_idx in range(a_idx + 1, len(active_list)):
            i, j = active_list[a_idx], active_list[b_idx]
            key = (min(i, j), max(i, j))
            if key in existing:
                continue
            # Check distance
            box = np.asarray(world.config.box_size, dtype=np.float64)
            d = world.k_pos[i] - world.k_pos[j]
            d -= box * np.round(d / box)
            dist = np.sqrt((d * d).sum())
            if dist > world.config.r_2 * 2:  # wider radius for retina bridges
                continue
            # Form bridge
            b = world.b_count
            if b >= world.b_alive.shape[0]:
                break
            world.b_alive[b] = True
            world.b_atom_i[b] = i
            world.b_atom_j[b] = j
            world.b_strength[b] = learning_rate
            world.b_count += 1
            existing.add(key)
            modified += 1

    return modified


def propagate_activation(world, retina: np.ndarray,
                         strength_threshold: float = 0.5,
                         propagation_charge: float = 3.0) -> int:
    """Propagate activation through strong bridges.

    Active atoms push charge through bridges with strength > threshold
    to their connected atoms. This completes partial patterns.

    Returns number of propagation events.
    """
    events = 0
    flat = set(int(n) for n in retina.flatten())

    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        if world.b_strength[b] < strength_threshold:
            continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        if i not in flat or j not in flat:
            continue

        ci = world.k_charge[i] if i < world.k_count else 0
        cj = world.k_charge[j] if j < world.k_count else 0

        # Propagate from active to inactive
        if ci > 5.0 and cj < 2.0:
            world.k_charge[j] += propagation_charge * world.b_strength[b]
            events += 1
        elif cj > 5.0 and ci < 2.0:
            world.k_charge[i] += propagation_charge * world.b_strength[b]
            events += 1

    return events


def read_retina(world, retina: np.ndarray, threshold: float = 3.0) -> np.ndarray:
    """Read which retina atoms are active. Returns boolean grid."""
    result = np.zeros(retina.shape, dtype=bool)
    for r in range(retina.shape[0]):
        for c in range(retina.shape[1]):
            node = retina[r, c]
            if node < world.k_count and world.k_alive[node]:
                result[r, c] = world.k_charge[node] > threshold
    return result


def print_pattern(pattern: np.ndarray) -> str:
    """Pretty-print a boolean grid as text."""
    lines = []
    for r in range(pattern.shape[0]):
        lines.append(''.join('#' if pattern[r, c] else '.' for c in range(pattern.shape[1])))
    return '\n'.join(lines)

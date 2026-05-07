"""Tests for tools/classify_molecules.py — molecule-species fingerprinting."""
import math
from pathlib import Path
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot

from tools.classify_molecules import classify, species_fingerprint


def _world_with_atoms(box=200.0, n_max=64):
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(box, box, box),
        n_vibrations_max=64,
        n_nodes_max=n_max,
        rng_seed=42,
        repulsion_cell_size=float(box),
    )
    return World(cfg)


def _add_atom(w: World, idx: int, freq: float, pol: bool = True):
    w.k_pos[idx] = [10.0, 10.0, 10.0]
    w.k_freq[idx] = freq
    w.k_pol[idx] = pol
    w.k_level[idx] = 4
    w.k_alive[idx] = False  # we don't care about atom-level "alive" for fingerprint
    w.k_birth[idx] = w.t
    w.k_comp_kind[idx] = 1
    if idx >= w.k_count:
        w.k_count = idx + 1
        w.k_comp_offset[idx + 1] = w.k_comp_offset[idx]
        w.k_comp_end[idx] = w.k_comp_offset[idx]


def _add_molecule(w: World, idx: int, level: int, constituent_node_indices: list[int]):
    """Hand-place a molecule at slot idx referencing existing atoms / molecules."""
    w.k_pos[idx] = [10.0, 10.0, 10.0]
    w.k_freq[idx] = sum(float(w.k_freq[c]) for c in constituent_node_indices)
    w.k_pol[idx] = True
    w.k_level[idx] = level
    w.k_alive[idx] = True
    w.k_birth[idx] = w.t
    w.k_comp_kind[idx] = 1
    start = w.k_comp_used
    n = len(constituent_node_indices)
    for j, cidx in enumerate(constituent_node_indices):
        w.k_comp_indices[start + j] = cidx
    w.k_comp_offset[idx] = start
    w.k_comp_offset[idx + 1] = start + n
    w.k_comp_end[idx] = start + n
    w.k_comp_used = start + n
    if idx >= w.k_count:
        w.k_count = idx + 1


def test_species_fingerprint_sorted():
    assert species_fingerprint([4, 3, 3]) == "A334"
    assert species_fingerprint([3, 4]) == "A34"
    assert species_fingerprint([3]) == "A3"
    assert species_fingerprint([]) == "A?"


def test_classify_empty_world(tmp_path):
    w = _world_with_atoms()
    save_snapshot(w, tmp_path / "empty.npz")
    counts = classify(tmp_path / "empty.npz")
    assert counts == {}


def test_classify_single_diatomic_a33(tmp_path):
    """One level-5 molecule made of two atoms at decade 3 → A33: 1."""
    w = _world_with_atoms()
    _add_atom(w, 0, freq=2000.0)   # decade 3
    _add_atom(w, 1, freq=2160.0)   # decade 3
    _add_molecule(w, 2, level=5, constituent_node_indices=[0, 1])
    save_snapshot(w, tmp_path / "single.npz")
    counts = classify(tmp_path / "single.npz")
    assert counts == {"A33": 1}


def test_classify_mixed_decades(tmp_path):
    """Three molecules: (3,3), (3,4), (4,4) → three species, one each."""
    w = _world_with_atoms(n_max=128)
    # Atoms at decade 3
    _add_atom(w, 0, 2000.0)
    _add_atom(w, 1, 2160.0)
    # Atoms at decade 3 and 4 (mixed)
    _add_atom(w, 2, 2400.0)
    _add_atom(w, 3, 16000.0)
    # Atoms at decade 4
    _add_atom(w, 4, 18000.0)
    _add_atom(w, 5, 19440.0)
    # Three molecules
    _add_molecule(w, 6, level=5, constituent_node_indices=[0, 1])
    _add_molecule(w, 7, level=5, constituent_node_indices=[2, 3])
    _add_molecule(w, 8, level=5, constituent_node_indices=[4, 5])
    save_snapshot(w, tmp_path / "mixed.npz")
    counts = classify(tmp_path / "mixed.npz")
    assert counts == {"A33": 1, "A34": 1, "A44": 1}


def test_classify_higher_orders(tmp_path):
    """A tri-atomic at decades (3, 3, 4) → A334: 1."""
    w = _world_with_atoms(n_max=64)
    _add_atom(w, 0, 2000.0)
    _add_atom(w, 1, 2160.0)
    _add_atom(w, 2, 16000.0)
    # Build a level-5 first, then a level-6 from level-5 + atom-2
    _add_molecule(w, 3, level=5, constituent_node_indices=[0, 1])
    _add_molecule(w, 4, level=6, constituent_node_indices=[3, 2])
    # Mark the L5 dead so only the L6 is alive
    w.k_alive[3] = False
    save_snapshot(w, tmp_path / "trio.npz")
    counts = classify(tmp_path / "trio.npz")
    assert counts == {"A334": 1}

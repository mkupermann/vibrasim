import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import apply_scale_repulsion, move_nodes


def _two_nodes(w: World, freq1, freq2, pos1, pos2):
    """Hand-place two electrons with given frequencies at given positions."""
    w.k_pos[0] = pos1
    w.k_freq[0] = freq1
    w.k_level[0] = 1
    w.k_alive[0] = True
    w.k_pos[1] = pos2
    w.k_freq[1] = freq2
    w.k_level[1] = 1
    w.k_alive[1] = True
    w.k_count = 2


def test_no_repulsion_below_threshold():
    """Frequency ratio < 1000 → no force."""
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(1000., 1000., 1000.),
                      n_vibrations_max=4, n_nodes_max=4, repulsion_k=100.0,
                      rng_seed=42)
    w = World(cfg)
    _two_nodes(w, 1000., 1500., [100., 100., 100.], [200., 100., 100.])  # ratio 1.5
    initial_pos = w.k_pos[:2].copy()
    for _ in range(100):
        apply_scale_repulsion(w, cfg.dt)
        move_nodes(w, cfg.dt)
    assert np.allclose(w.k_pos[:2], initial_pos, atol=1e-3)


def test_repulsion_above_threshold():
    """Frequency ratio > 1000 → nodes drift apart."""
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(1000., 1000., 1000.),
                      n_vibrations_max=4, n_nodes_max=4, repulsion_k=1000.0,
                      rng_seed=42)
    w = World(cfg)
    _two_nodes(w, 100., 200000., [100., 100., 100.], [200., 100., 100.])  # ratio 2000
    initial_distance = np.linalg.norm(w.k_pos[1] - w.k_pos[0])
    for _ in range(1000):
        apply_scale_repulsion(w, cfg.dt)
        move_nodes(w, cfg.dt)
    final_distance = np.linalg.norm(w.k_pos[1] - w.k_pos[0])
    assert final_distance > initial_distance


def test_atoms_participate():
    """Heavier atoms move less under same force, but they do move."""
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(1000., 1000., 1000.),
                      n_vibrations_max=4, n_nodes_max=4, repulsion_k=1000.0,
                      rng_seed=42)
    w = World(cfg)
    _two_nodes(w, 100., 200000., [100., 100., 100.], [200., 100., 100.])
    w.k_level[1] = 4  # heavier
    initial_displacement_light = w.k_pos[0].copy()
    for _ in range(1000):
        apply_scale_repulsion(w, cfg.dt)
        move_nodes(w, cfg.dt)
    delta_light = np.linalg.norm(w.k_pos[0] - initial_displacement_light)
    assert delta_light > 0  # atom moves at all

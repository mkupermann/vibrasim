import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World


def test_world_constructs_with_correct_3d_capacity(default_config):
    w = World(default_config)
    N = default_config.n_vibrations_max
    K = default_config.n_nodes_max
    assert w.s_pos.shape == (N, 3)
    assert w.s_vel.shape == (N, 3)
    assert w.k_pos.shape == (K, 3)
    assert w.k_vel.shape == (K, 3)


def test_seeded_vibrations_in_3d_box(default_config):
    w = World(default_config)
    alive = w.s_alive
    bx, by, bz = default_config.box_size
    assert np.all(w.s_pos[alive, 0] >= 0)
    assert np.all(w.s_pos[alive, 0] < bx)
    assert np.all(w.s_pos[alive, 1] >= 0)
    assert np.all(w.s_pos[alive, 1] < by)
    assert np.all(w.s_pos[alive, 2] >= 0)
    assert np.all(w.s_pos[alive, 2] < bz)


def test_seeded_velocities_isotropic_in_3d(default_config):
    """Seeded velocities should not be confined to a 2D plane."""
    w = World(default_config)
    alive = w.s_alive
    # In a uniform 3D distribution of velocities, each component has nonzero variance.
    for d in range(3):
        assert np.std(w.s_vel[alive, d]) > 1.0


def test_seeded_speeds_in_range(default_config):
    w = World(default_config)
    alive = w.s_alive
    speeds = np.linalg.norm(w.s_vel[alive], axis=1)
    assert np.all(speeds >= default_config.speed_min - 1e-6)
    assert np.all(speeds <= default_config.speed_max + 1e-6)


def test_total_vibrations_count():
    """Bookkeeping: total_vibrations counts free + bound."""
    cfg = WorldConfig(n_initial_vibrations=10, box_size=(100.0, 100.0, 100.0),
                      n_vibrations_max=16, n_nodes_max=8, rng_seed=42)
    w = World(cfg)
    assert w.total_vibrations() == 10  # 10 free, no bound


def test_world_seeds_initial_vibrations(default_config):
    w = World(default_config)
    assert w.n_alive == default_config.n_initial_vibrations
    alive_idx = np.where(w.s_alive)[0]
    assert len(alive_idx) == default_config.n_initial_vibrations


def test_seeded_frequencies_in_range(default_config):
    w = World(default_config)
    alive = w.s_alive
    assert np.all(w.s_freq[alive] >= default_config.freq_min)
    assert np.all(w.s_freq[alive] <= default_config.freq_max)


def test_seeded_polarities_split_roughly_half(default_config):
    w = World(default_config)
    alive = w.s_alive
    even_share = np.mean(w.s_pol[alive])
    assert 0.4 < even_share < 0.6


def test_log_frequency_distribution_skews_low(default_config):
    """Log-distributed frequencies should have median below the arithmetic midpoint."""
    w = World(default_config)
    alive = w.s_alive
    median = float(np.median(w.s_freq[alive]))
    mid = (default_config.freq_min + default_config.freq_max) / 2
    assert median < mid


def test_initial_node_count_is_zero(default_config):
    w = World(default_config)
    assert w.k_count == 0
    assert not np.any(w.k_alive)


def test_reproducible_seeding(default_config):
    w1 = World(default_config)
    w2 = World(default_config)
    np.testing.assert_array_equal(w1.s_pos, w2.s_pos)
    np.testing.assert_array_equal(w1.s_vel, w2.s_vel)
    np.testing.assert_array_equal(w1.s_freq, w2.s_freq)
    np.testing.assert_array_equal(w1.s_pol, w2.s_pol)


def test_k_strength_field_initialised_to_one():
    """k_strength must default to 1.0 for every node slot — birth strength."""
    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=16)
    w = World(cfg)
    assert w.k_strength.shape == (16,)
    assert w.k_strength.dtype == np.float64
    # Every slot starts with strength 1.0
    assert (w.k_strength == 1.0).all()


def test_AP_k_ref_count_initialised_zero():
    """Plan A.5: per-slot reference count is zero at world init."""
    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=16)
    w = World(cfg)
    assert w.k_ref_count.shape == (16,)
    assert w.k_ref_count.dtype == np.int32
    assert (w.k_ref_count == 0).all()
    assert w._free_slots == []
    assert w._free_slots_set == set()


def test_k_orientation_field_initialised_to_zero():
    """k_orientation is a per-node 3-vector; default zero (no orientation inferred yet)."""
    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=16)
    w = World(cfg)
    assert w.k_orientation.shape == (16, 3)
    assert w.k_orientation.dtype == np.float64
    assert (w.k_orientation == 0.0).all()

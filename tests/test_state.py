import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World


def test_world_constructs_with_correct_capacity(default_config):
    w = World(default_config)
    assert w.s_pos.shape == (default_config.n_vibrations_max, 2)
    assert w.s_vel.shape == (default_config.n_vibrations_max, 2)
    assert w.s_freq.shape == (default_config.n_vibrations_max,)
    assert w.s_pol.shape == (default_config.n_vibrations_max,)
    assert w.s_alive.shape == (default_config.n_vibrations_max,)
    assert w.k_pos.shape == (default_config.n_nodes_max, 2)
    assert w.k_freq.shape == (default_config.n_nodes_max,)
    assert w.k_pol.shape == (default_config.n_nodes_max,)
    assert w.k_level.shape == (default_config.n_nodes_max,)
    assert w.k_alive.shape == (default_config.n_nodes_max,)


def test_world_seeds_initial_vibrations(default_config):
    w = World(default_config)
    assert w.n_alive == default_config.n_initial_vibrations
    alive_idx = np.where(w.s_alive)[0]
    assert len(alive_idx) == default_config.n_initial_vibrations


def test_seeded_vibrations_within_box(default_config):
    w = World(default_config)
    alive = w.s_alive
    assert np.all(w.s_pos[alive, 0] >= 0)
    assert np.all(w.s_pos[alive, 0] < default_config.box_size[0])
    assert np.all(w.s_pos[alive, 1] >= 0)
    assert np.all(w.s_pos[alive, 1] < default_config.box_size[1])


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


def test_seeded_speeds_in_range(default_config):
    w = World(default_config)
    alive = w.s_alive
    speeds = np.linalg.norm(w.s_vel[alive], axis=1)
    assert np.all(speeds >= default_config.speed_min - 1e-9)
    assert np.all(speeds <= default_config.speed_max + 1e-9)


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

"""Tests for boundary injection + absorption."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.boundary import inject_hot_floor


def test_inject_hot_floor_adds_correct_count():
    q = Quanta(max_quanta=100)
    g = Grid(dims=(10, 10, 10))
    injected = inject_hot_floor(
        q, g, n=5, energy_per=1.0,
        freq_mean=200.0, vel_z_mean=1.0,
        rng=np.random.default_rng(0),
    )
    assert injected == 5
    assert q.n_alive() == 5


def test_inject_hot_floor_places_at_z_near_zero():
    q = Quanta(max_quanta=100)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    inject_hot_floor(q, g, n=20, energy_per=1.0,
                     freq_mean=200.0, vel_z_mean=1.0,
                     rng=np.random.default_rng(0))
    alive_z = q.pos[q.alive, 2]
    # All injected vibrations should start in the lowest voxel layer
    assert alive_z.min() >= 0.0
    assert alive_z.max() < 1.0  # voxel_size


def test_inject_hot_floor_gives_upward_velocity():
    q = Quanta(max_quanta=100)
    g = Grid(dims=(10, 10, 10))
    inject_hot_floor(q, g, n=20, energy_per=1.0,
                     freq_mean=200.0, vel_z_mean=2.0,
                     rng=np.random.default_rng(0))
    alive_vz = q.vel[q.alive, 2]
    # All upward (positive z velocity)
    assert (alive_vz > 0).all()
    # Mean roughly matches vel_z_mean (with sampling noise tolerance)
    assert abs(alive_vz.mean() - 2.0) < 1.0


def test_inject_hot_floor_assigns_constant_energy():
    q = Quanta(max_quanta=100)
    g = Grid(dims=(10, 10, 10))
    inject_hot_floor(q, g, n=10, energy_per=1.5,
                     freq_mean=200.0, vel_z_mean=1.0,
                     rng=np.random.default_rng(0))
    assert q.total_energy() == 15.0


def test_inject_hot_floor_returns_actual_count_when_buffer_full():
    q = Quanta(max_quanta=3)
    g = Grid(dims=(10, 10, 10))
    injected = inject_hot_floor(q, g, n=10, energy_per=1.0,
                                freq_mean=200.0, vel_z_mean=1.0,
                                rng=np.random.default_rng(0))
    assert injected == 3
    assert q.n_alive() == 3

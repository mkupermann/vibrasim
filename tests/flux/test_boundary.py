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


from world.flux.boundary import absorb_cold_faces


def test_absorb_cold_faces_returns_zero_when_no_quanta_at_boundary():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    # Quantum well inside the cube
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0),
          freq=100.0, polarity=1, energy=1.0)
    exported = absorb_cold_faces(q, g, delta=0.5)
    assert exported == 0.0
    assert q.n_alive() == 1


def test_absorb_cold_faces_removes_quanta_at_ceiling():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    # Quanta at the ceiling face (z > Lz - delta)
    q.add(pos=(5.0, 5.0, 9.8), vel=(0, 0, 1), freq=100.0, polarity=1,
          energy=1.0)
    q.add(pos=(3.0, 3.0, 5.0), vel=(0, 0, 1), freq=100.0, polarity=1,
          energy=1.0)  # interior — not absorbed
    exported = absorb_cold_faces(q, g, delta=0.5)
    assert exported == 1.0
    assert q.n_alive() == 1


def test_absorb_cold_faces_removes_quanta_at_side_walls():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    # x near 0
    q.add(pos=(0.1, 5.0, 5.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=2.0)
    # x near Lx
    q.add(pos=(9.9, 5.0, 5.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=2.0)
    # y near 0
    q.add(pos=(5.0, 0.05, 5.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=2.0)
    # y near Ly
    q.add(pos=(5.0, 9.95, 5.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=2.0)
    # interior
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=2.0)
    exported = absorb_cold_faces(q, g, delta=0.5)
    assert exported == 8.0  # 4 absorbed × 2.0
    assert q.n_alive() == 1


from world.flux.boundary import inject_cold_ceiling


def test_inject_cold_ceiling_places_at_z_near_ceiling():
    q = Quanta(max_quanta=100)
    Lz = 10
    g = Grid(dims=(10, 10, Lz), voxel_size=1.0)
    inject_cold_ceiling(q, g, n=20, energy_per=1.0,
                        freq_mean=200.0, vel_z_sigma=0.5,
                        rng=np.random.default_rng(0))
    alive_z = q.pos[q.alive, 2]
    assert alive_z.min() >= (Lz - 1) * 1.0
    assert alive_z.max() < Lz * 1.0


def test_inject_cold_ceiling_gives_downward_velocity():
    q = Quanta(max_quanta=100)
    g = Grid(dims=(10, 10, 10))
    inject_cold_ceiling(q, g, n=50, energy_per=1.0,
                        freq_mean=200.0, vel_z_sigma=0.5,
                        rng=np.random.default_rng(0))
    alive_vz = q.vel[q.alive, 2]
    # Strictly non-positive — `vel_z = -|N(0, sigma)|` is downward by
    # construction; any positive value indicates a sign-bug.
    assert (alive_vz <= 0.0).all()
    # Mean is statistically downward (below zero), magnitude ~sigma/sqrt(pi/2)
    # for a half-normal distribution.
    assert alive_vz.mean() < 0.0


def test_inject_cold_ceiling_returns_actual_count_when_buffer_full():
    q = Quanta(max_quanta=3)
    g = Grid(dims=(10, 10, 10))
    injected = inject_cold_ceiling(q, g, n=10, energy_per=1.0,
                                    freq_mean=200.0, vel_z_sigma=0.5,
                                    rng=np.random.default_rng(0))
    assert injected == 3
    assert q.n_alive() == 3


def test_inject_cold_ceiling_records_polarity_minus_one():
    """Cosmetic distinction: ceiling-injected quanta carry polarity=-1."""
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10))
    inject_cold_ceiling(q, g, n=5, energy_per=1.0,
                        freq_mean=200.0, vel_z_sigma=0.5,
                        rng=np.random.default_rng(0))
    alive_pol = q.polarity[q.alive]
    assert (alive_pol == -1).all()


def test_absorb_cold_faces_does_not_absorb_at_hot_floor():
    """Hot floor (z near 0) must NOT be a cold face."""
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    q.add(pos=(5.0, 5.0, 0.05), vel=(0, 0, 1), freq=100, polarity=1,
          energy=1.0)
    exported = absorb_cold_faces(q, g, delta=0.5)
    assert exported == 0.0
    assert q.n_alive() == 1

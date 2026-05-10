"""Tests for Grid — voxelisation + temperature field."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.grid import Grid


def test_grid_creates_zeroed_temperature_field():
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    assert g.dims == (10, 10, 10)
    assert g.voxel_size == 1.0
    assert g.T.shape == (10, 10, 10)
    assert g.T.dtype == np.float64
    np.testing.assert_array_equal(g.T, np.zeros((10, 10, 10)))


def test_position_to_voxel_within_bounds():
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    assert g.pos_to_voxel((0.0, 0.0, 0.0)) == (0, 0, 0)
    assert g.pos_to_voxel((5.5, 7.2, 3.1)) == (5, 7, 3)
    assert g.pos_to_voxel((9.99, 9.99, 9.99)) == (9, 9, 9)


def test_position_to_voxel_clips_at_boundaries():
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    # Out-of-bounds should clip to valid voxel
    assert g.pos_to_voxel((10.5, 5.0, 5.0)) == (9, 5, 5)
    assert g.pos_to_voxel((-0.5, 5.0, 5.0)) == (0, 5, 5)


def test_position_to_voxel_respects_voxel_size():
    g = Grid(dims=(5, 5, 5), voxel_size=2.0)
    assert g.pos_to_voxel((0.0, 0.0, 0.0)) == (0, 0, 0)
    assert g.pos_to_voxel((2.0, 2.0, 2.0)) == (1, 1, 1)
    assert g.pos_to_voxel((3.9, 5.5, 9.99)) == (1, 2, 4)


def test_update_temperature_from_density():
    g = Grid(dims=(4, 4, 4), voxel_size=1.0, T_smoothing=1.0)
    # Density field of size dims: voxel (2,2,2) has 5 quanta, rest zero
    density = np.zeros((4, 4, 4), dtype=np.float64)
    density[2, 2, 2] = 5.0
    g.update_temperature(density)
    assert g.T[2, 2, 2] == 5.0
    assert g.T[0, 0, 0] == 0.0


def test_temperature_smoothing_is_exponential():
    g = Grid(dims=(2, 2, 2), voxel_size=1.0, T_smoothing=0.5)
    density = np.full((2, 2, 2), 10.0)
    g.update_temperature(density)
    # First update: 0.5 * 10 + 0.5 * 0 = 5
    np.testing.assert_allclose(g.T, np.full((2, 2, 2), 5.0))
    g.update_temperature(density)
    # Second update: 0.5 * 10 + 0.5 * 5 = 7.5
    np.testing.assert_allclose(g.T, np.full((2, 2, 2), 7.5))

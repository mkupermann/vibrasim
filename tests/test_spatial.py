import numpy as np
import pytest
from world.spatial import build_grid, neighbors_of, periodic_distance_sq, periodic_midpoint


def test_periodic_distance_no_wrap_3d():
    box = np.array([100.0, 100.0, 100.0])
    a = np.array([10.0, 10.0, 10.0])
    b = np.array([13.0, 14.0, 22.0])
    d2 = periodic_distance_sq(a, b, box)
    assert d2 == pytest.approx(9 + 16 + 144)  # 169


def test_periodic_distance_with_wrap_3d():
    box = np.array([100.0, 100.0, 100.0])
    a = np.array([1.0, 1.0, 1.0])
    b = np.array([99.0, 99.0, 99.0])
    d2 = periodic_distance_sq(a, b, box)
    # Each axis wraps; delta = 2 in each dim → d2 = 12
    assert d2 == pytest.approx(12.0)


def test_3d_neighbors_within_27_cells():
    """A 3D grid query visits 27 neighbour cells."""
    positions = np.array([[5.0, 5.0, 5.0], [15.0, 5.0, 5.0]])  # adjacent x-cells
    alive = np.array([True, True])
    box = np.array([100.0, 100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    nbrs = neighbors_of(grid, positions[0], box, cell_size, exclude_self=True, query_index=0)
    assert 1 in nbrs


def test_3d_neighbors_periodic_wrap():
    positions = np.array([[1.0, 50.0, 50.0], [99.0, 50.0, 50.0]])  # opposite x-faces
    alive = np.array([True, True])
    box = np.array([100.0, 100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    nbrs = neighbors_of(grid, positions[0], box, cell_size, exclude_self=True, query_index=0)
    assert 1 in nbrs


def test_periodic_midpoint_3d():
    box = np.array([100.0, 100.0, 100.0])
    a = np.array([10.0, 20.0, 30.0])
    b = np.array([14.0, 24.0, 38.0])
    m = periodic_midpoint(a, b, box)
    assert np.allclose(m, [12.0, 22.0, 34.0])


def test_periodic_midpoint_3d_wrap():
    box = np.array([100.0, 100.0, 100.0])
    a = np.array([99.0, 50.0, 50.0])
    b = np.array([1.0, 50.0, 50.0])
    m = periodic_midpoint(a, b, box)
    # Wrap midpoint is at 0 (or 100), not at 50.
    assert m[0] < 1.0 or m[0] > 99.0
    assert m[1] == pytest.approx(50.0)
    assert m[2] == pytest.approx(50.0)


def test_dead_points_excluded_3d():
    positions = np.array([[5.0, 5.0, 5.0], [6.0, 6.0, 6.0]])
    alive = np.array([True, False])
    box = np.array([100.0, 100.0, 100.0])
    grid = build_grid(positions, alive, box, 10.0)
    nbrs = neighbors_of(grid, positions[0], box, 10.0, exclude_self=True, query_index=0)
    assert 1 not in nbrs

import numpy as np
import pytest
from world.spatial import build_grid, neighbors_of, periodic_distance_sq


def test_periodic_distance_no_wrap():
    box = np.array([100.0, 100.0])
    a = np.array([10.0, 10.0])
    b = np.array([13.0, 14.0])
    d2 = periodic_distance_sq(a, b, box)
    assert d2 == pytest.approx(25.0)


def test_periodic_distance_with_wrap():
    box = np.array([100.0, 100.0])
    a = np.array([1.0, 1.0])
    b = np.array([99.0, 99.0])
    d2 = periodic_distance_sq(a, b, box)
    assert d2 == pytest.approx(8.0)


def test_grid_buckets_points_correctly():
    positions = np.array([
        [5.0, 5.0],
        [12.0, 5.0],
        [5.0, 12.0],
        [95.0, 95.0],
    ])
    alive = np.array([True, True, True, True])
    box = np.array([100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    assert 0 in neighbors_of(grid, np.array([5.0, 5.0]), box, cell_size, exclude_self=False, query_index=-1)


def test_neighbors_within_cell_and_adjacent():
    positions = np.array([[5.0, 5.0], [15.0, 5.0]])
    alive = np.array([True, True])
    box = np.array([100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    nbrs = neighbors_of(grid, positions[0], box, cell_size, exclude_self=True, query_index=0)
    assert 1 in nbrs


def test_neighbors_across_periodic_boundary():
    positions = np.array([[1.0, 50.0], [99.0, 50.0]])
    alive = np.array([True, True])
    box = np.array([100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    nbrs = neighbors_of(grid, positions[0], box, cell_size, exclude_self=True, query_index=0)
    assert 1 in nbrs


def test_dead_points_excluded():
    positions = np.array([[5.0, 5.0], [6.0, 6.0]])
    alive = np.array([True, False])
    box = np.array([100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    nbrs = neighbors_of(grid, positions[0], box, cell_size, exclude_self=True, query_index=0)
    assert 1 not in nbrs

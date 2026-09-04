from dataclasses import dataclass
from types import ModuleType, SimpleNamespace
import sys

import numpy as np

from vibrasim2.observation import EdgeKind, ObservationStatus
from vibrasim2.p0.observation import (
    ObservationMetadata,
    ObservationProjectionConfig,
    ProjectionTopology,
    project_p0_observation,
)


@dataclass(frozen=True)
class State:
    u: np.ndarray
    p: np.ndarray
    q: np.ndarray
    r: np.ndarray


@dataclass(frozen=True)
class Snapshot:
    tick: int
    simulation_time: float
    state: State


def three_by_three_snapshot_and_topology():
    u = np.arange(1, 10, dtype=np.float64).reshape(3, 3)
    state = State(
        u,
        np.zeros((3, 3), dtype=np.float64),
        np.array((0.25, 0.2501), dtype=np.float64),
        np.zeros(2, dtype=np.float64),
    )
    snapshot = Snapshot(10, 0.5, state)
    topology = ProjectionTopology(
        grid_shape=(3, 3),
        coupling_sites=np.array(((0, 0), (0, 1)), dtype=np.int64),
        matter_edges=np.array(((0, 1),), dtype=np.int64),
        vertical_coupling_kind=EdgeKind.RECIPROCAL_COUPLING,
    )
    return snapshot, topology


def metadata(sequence: int = 1) -> ObservationMetadata:
    return ObservationMetadata(
        run_id="r1", stage="A", arm="cycle", source_centre=(0, 0),
        sequence=sequence, emitted_monotonic_ns=2_000_000_000,
        status=ObservationStatus.RUNNING,
    )


def expected_declared_edges():
    return {(9, 10), (0, 9), (1, 10)}


def test_projection_uses_only_declared_coordinates_and_scale():
    snapshot, topology = three_by_three_snapshot_and_topology()
    envelope = project_p0_observation(
        snapshot, topology, metadata(), ObservationProjectionConfig(display_scale=4.0)
    )
    np.testing.assert_array_equal(
        envelope.frame.positions[:9],
        np.array(
            [(x, y, 4.0 * snapshot.state.u[x, y]) for x in range(3) for y in range(3)],
            dtype=np.float64,
        ),
    )
    np.testing.assert_array_equal(envelope.frame.positions[9:, 2], np.array((1.0, 1.0004)))
    assert set(map(tuple, envelope.frame.edges)) == expected_declared_edges()
    assert envelope.frame.edge_kinds == (
        EdgeKind.MATTER,
        EdgeKind.RECIPROCAL_COUPLING,
        EdgeKind.RECIPROCAL_COUPLING,
    )
    before = snapshot.state.u.copy()
    project_p0_observation(
        snapshot, topology, metadata(sequence=2), ObservationProjectionConfig(display_scale=8.0)
    )
    np.testing.assert_array_equal(snapshot.state.u, before)


def test_spatial_proximity_never_creates_an_edge():
    snapshot, topology = three_by_three_snapshot_and_topology()
    frame = project_p0_observation(
        snapshot, topology, metadata(), ObservationProjectionConfig(display_scale=4.0)
    ).frame
    assert set(map(tuple, frame.edges)) == expected_declared_edges()


def test_field_lines_are_exact_declared_periodic_neighbours():
    snapshot, topology = three_by_three_snapshot_and_topology()
    frame = project_p0_observation(
        snapshot, topology, metadata(), ObservationProjectionConfig(4.0)
    ).frame
    actual = {
        (tuple(line[0, :2].astype(int)), tuple(line[1, :2].astype(int)))
        for line in frame.field_lines
    }
    expected = {
        ((x, y), neighbour)
        for x in range(3)
        for y in range(3)
        for neighbour in (((x + 1) % 3, y), (x, (y + 1) % 3))
    }
    assert actual == expected


def test_registered_modes_expose_only_their_declared_terms(monkeypatch):
    fixtures = ModuleType("vibrasim2.p0.fixtures")
    fixtures.coupling_sites = lambda: np.array(
        ((0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 0)), dtype=np.int64
    )
    fixtures.edges_for = lambda topology: np.array(
        ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)), dtype=np.int64
    )
    monkeypatch.setitem(sys.modules, "vibrasim2.p0.fixtures", fixtures)
    config = SimpleNamespace(grid_shape=(3, 3), assert_registered=lambda: None)
    topology = SimpleNamespace(value="cycle")
    expected = {
        "full": (6, EdgeKind.RECIPROCAL_COUPLING),
        "no_bonds": (0, EdgeKind.RECIPROCAL_COUPLING),
        "decoupled": (6, None),
        "broken_pair": (6, EdgeKind.MATERIAL_ONLY_CONTROL),
    }
    for mode, (matter_count, vertical_kind) in expected.items():
        projected = ProjectionTopology.from_registered(
            config, SimpleNamespace(mode=SimpleNamespace(value=mode), topology=topology)
        )
        assert len(projected.matter_edges) == matter_count
        assert projected.vertical_coupling_kind is vertical_kind

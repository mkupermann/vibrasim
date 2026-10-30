"""Deterministic projection of persisted P0 state into observation geometry."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from vibrasim2.observation import (
    EdgeKind,
    EdgeState,
    ObservationEnvelope,
    ObservationStatus,
    WireframeFrame,
)


@dataclass(frozen=True)
class ObservationMetadata:
    run_id: str
    stage: str
    arm: str
    source_centre: tuple[int, int]
    sequence: int
    emitted_monotonic_ns: int
    status: ObservationStatus


@dataclass(frozen=True)
class ObservationProjectionConfig:
    display_scale: float = 4.0
    schema_version: int = 1

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("schema_version must be 1")
        if not np.isfinite(self.display_scale) or self.display_scale <= 0:
            raise ValueError("display_scale must be positive and finite")


def _readonly_int_array(value: Any, shape_tail: tuple[int, ...], name: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.int64)
    if array.ndim != 2 or array.shape[1:] != shape_tail:
        raise ValueError(f"{name} must have shape (n, {shape_tail[0]})")
    array = array.copy()
    array.setflags(write=False)
    return array


@dataclass(frozen=True)
class ProjectionTopology:
    grid_shape: tuple[int, int]
    coupling_sites: np.ndarray
    matter_edges: np.ndarray
    vertical_coupling_kind: EdgeKind | None = None

    def __post_init__(self) -> None:
        if len(self.grid_shape) != 2 or any(not isinstance(v, int) or v <= 0 for v in self.grid_shape):
            raise ValueError("grid_shape must contain two positive integers")
        sites = _readonly_int_array(self.coupling_sites, (2,), "coupling_sites")
        edges = _readonly_int_array(self.matter_edges, (2,), "matter_edges")
        rows, columns = self.grid_shape
        if sites.size and ((sites[:, 0] < 0).any() or (sites[:, 0] >= rows).any()
                           or (sites[:, 1] < 0).any() or (sites[:, 1] >= columns).any()):
            raise ValueError("coupling site is outside the grid")
        if edges.size and ((edges < 0).any() or (edges >= len(sites)).any()):
            raise ValueError("matter edge endpoint is outside the coupling sites")
        if edges.size and (edges[:, 0] == edges[:, 1]).any():
            raise ValueError("matter edges cannot be self-edges")
        kind = self.vertical_coupling_kind
        if kind is not None:
            try:
                kind = EdgeKind(kind)
            except ValueError as exc:
                raise ValueError("vertical coupling kind is invalid") from exc
            if kind is EdgeKind.MATTER:
                raise ValueError("vertical coupling kind must describe a coupling or control")
        object.__setattr__(self, "grid_shape", tuple(self.grid_shape))
        object.__setattr__(self, "coupling_sites", sites)
        object.__setattr__(self, "matter_edges", edges)
        object.__setattr__(self, "vertical_coupling_kind", kind)

    @classmethod
    def from_registered(cls, config: Any, cell: Any) -> "ProjectionTopology":
        """Build the visible terms for one registered P0 cell.

        Imports are deliberately local: the projection contract can be tested
        with tiny declared fixtures and does not make the observer depend on
        the simulator at import time.
        """
        config.assert_registered()
        from vibrasim2.p0.fixtures import coupling_sites, edges_for

        sites = coupling_sites()
        if len(sites) != 6:
            raise ValueError("registered P0 requires exactly six coupling sites")
        mode = getattr(cell.mode, "value", cell.mode)
        if mode == "no_bonds":
            matter_edges = np.empty((0, 2), dtype=np.int64)
        else:
            matter_edges = edges_for(cell.topology)
        if mode in {"full", "no_bonds"}:
            vertical_kind = EdgeKind.RECIPROCAL_COUPLING
        elif mode == "decoupled":
            vertical_kind = None
        elif mode == "broken_pair":
            vertical_kind = EdgeKind.MATERIAL_ONLY_CONTROL
        else:
            raise ValueError(f"unsupported registered channel mode: {mode}")
        return cls(config.grid_shape, sites, matter_edges, vertical_kind)


def _snapshot_values(snapshot: Any) -> tuple[np.ndarray, np.ndarray, int, float]:
    state = snapshot.state
    u = np.asarray(state.u, dtype=np.float64)
    q = np.asarray(state.q, dtype=np.float64)
    return u, q, int(snapshot.tick), float(snapshot.simulation_time)


def project_p0_observation(
    snapshot: Any,
    topology: ProjectionTopology,
    metadata: ObservationMetadata,
    config: ObservationProjectionConfig,
) -> ObservationEnvelope:
    """Project a persisted snapshot without inferring or mutating simulation state."""
    u, q, tick, simulation_time = _snapshot_values(snapshot)
    if u.shape != topology.grid_shape:
        raise ValueError("snapshot field shape does not match grid_shape")
    if q.shape != (len(topology.coupling_sites),):
        raise ValueError("snapshot matter shape does not match coupling_sites")
    if not np.isfinite(u).all() or not np.isfinite(q).all():
        raise ValueError("snapshot values must be finite for observation")

    rows, columns = topology.grid_shape
    grid_size = rows * columns
    field_positions = np.array(
        [(x, y, config.display_scale * u[x, y])
         for x in range(rows) for y in range(columns)],
        dtype=np.float64,
    )
    matter_positions = np.array(
        [(int(x), int(y), config.display_scale * q[index])
         for index, (x, y) in enumerate(topology.coupling_sites)],
        dtype=np.float64,
    )
    positions = np.concatenate((field_positions, matter_positions), axis=0)

    edges: list[tuple[int, int]] = []
    kinds: list[EdgeKind] = []
    matter_offset = grid_size
    for first, second in topology.matter_edges:
        edges.append((matter_offset + int(first), matter_offset + int(second)))
        kinds.append(EdgeKind.MATTER)
    if topology.vertical_coupling_kind is not None:
        for index, (x, y) in enumerate(topology.coupling_sites):
            field_index = int(x) * columns + int(y)
            edges.append((field_index, matter_offset + index))
            kinds.append(topology.vertical_coupling_kind)

    field_lines = []
    for x in range(rows):
        for y in range(columns):
            source = field_positions[x * columns + y]
            for neighbour_x, neighbour_y in (((x + 1) % rows, y), (x, (y + 1) % columns)):
                field_lines.append(np.array(
                    (source, field_positions[neighbour_x * columns + neighbour_y]),
                    dtype=np.float64,
                ))

    frame = WireframeFrame(
        positions=positions,
        edges=np.asarray(edges, dtype=np.int32).reshape((-1, 2)),
        edge_states=(EdgeState.SUPPLIED,) * len(edges),
        edge_kinds=tuple(kinds),
        field_lines=tuple(field_lines),
    )
    return ObservationEnvelope(
        schema_version=config.schema_version,
        run_id=metadata.run_id,
        stage=metadata.stage,
        arm=metadata.arm,
        source_centre=metadata.source_centre,
        tick=tick,
        simulation_time=simulation_time,
        sequence=metadata.sequence,
        emitted_monotonic_ns=metadata.emitted_monotonic_ns,
        status=metadata.status,
        display_scale=config.display_scale,
        frame=frame,
    )

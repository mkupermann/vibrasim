"""Process-safe, value-neutral contracts for observing simulator state."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class EdgeState(str, Enum):
    """The observation reports supplied edges, not a lifecycle transition."""

    SUPPLIED = "supplied"
    AVAILABLE = "available"
    LIVE = "live"


class EdgeKind(str, Enum):
    MATTER = "matter"
    RECIPROCAL_COUPLING = "reciprocal_coupling"
    MATERIAL_ONLY_CONTROL = "material_only_control"


class ObservationStatus(str, Enum):
    RUNNING = "running"
    COMPLETE = "complete"


def _frozen_array(value: object, *, dtype: np.dtype, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=dtype).copy()
    array.setflags(write=False)
    return array


@dataclass(frozen=True)
class WireframeFrame:
    positions: np.ndarray
    edges: np.ndarray
    edge_states: tuple[EdgeState, ...]
    edge_kinds: tuple[EdgeKind, ...]
    field_lines: tuple[np.ndarray, ...] = ()
    particle_values: np.ndarray | None = None

    def __post_init__(self) -> None:
        positions = np.asarray(self.positions, dtype=np.float64)
        edges = np.asarray(self.edges, dtype=np.int32)
        if positions.ndim != 2 or positions.shape[1:] != (3,):
            raise ValueError("positions must have shape (n, 3)")
        if not np.isfinite(positions).all():
            raise ValueError("positions must be finite")
        if edges.size == 0:
            edges = np.empty((0, 2), dtype=np.int32)
        if edges.ndim != 2 or edges.shape[1:] != (2,):
            raise ValueError("edges must have shape (m, 2)")
        if len(self.edge_states) != len(edges):
            raise ValueError("one edge state is required for each edge")
        if len(self.edge_kinds) != len(edges):
            raise ValueError("one edge kind is required for each edge")
        if edges.size and (int(edges.min()) < 0 or int(edges.max()) >= len(positions)):
            raise ValueError("edge endpoint is outside the particle array")
        try:
            edge_states = tuple(EdgeState(state) for state in self.edge_states)
            edge_kinds = tuple(EdgeKind(kind) for kind in self.edge_kinds)
        except ValueError as exc:
            raise ValueError("edge state or edge kind is invalid") from exc
        field_lines = tuple(np.asarray(line, dtype=np.float64) for line in self.field_lines)
        if any(line.ndim != 2 or line.shape[1:] != (3,) or len(line) < 2
               or not np.isfinite(line).all() for line in field_lines):
            raise ValueError("field lines must each be finite with shape (n>=2, 3)")
        if self.particle_values is None:
            particle_values = np.empty(0, dtype=np.float64)
        else:
            particle_values = np.asarray(self.particle_values, dtype=np.float64)
            if particle_values.shape != (len(positions),) or not np.isfinite(particle_values).all():
                raise ValueError("particle_values must be finite with shape (n,)")
        object.__setattr__(self, "positions", _frozen_array(positions, dtype=np.float64, name="positions"))
        object.__setattr__(self, "edges", _frozen_array(edges, dtype=np.int32, name="edges"))
        object.__setattr__(self, "edge_states", edge_states)
        object.__setattr__(self, "edge_kinds", edge_kinds)
        object.__setattr__(
            self,
            "field_lines",
            tuple(_frozen_array(line, dtype=np.float64, name="field line") for line in field_lines),
        )
        object.__setattr__(
            self,
            "particle_values",
            _frozen_array(particle_values, dtype=np.float64, name="particle_values"),
        )


@dataclass(frozen=True)
class ObservationEnvelope:
    schema_version: int
    run_id: str
    stage: str
    arm: str
    source_centre: tuple[int, int]
    tick: int
    simulation_time: float
    sequence: int
    emitted_monotonic_ns: int
    status: ObservationStatus
    display_scale: float
    frame: WireframeFrame

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("schema_version must be 1")
        for name, value in (("run_id", self.run_id), ("stage", self.stage), ("arm", self.arm)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if len(self.source_centre) != 2 or not all(isinstance(value, int) for value in self.source_centre):
            raise ValueError("source_centre must contain two integers")
        if not isinstance(self.tick, int) or self.tick < 0:
            raise ValueError("tick must be non-negative")
        if not np.isfinite(self.simulation_time) or self.simulation_time < 0:
            raise ValueError("simulation_time must be non-negative and finite")
        if not isinstance(self.sequence, int) or self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if not isinstance(self.emitted_monotonic_ns, int) or self.emitted_monotonic_ns < 0:
            raise ValueError("emitted_monotonic_ns must be non-negative")
        try:
            status = ObservationStatus(self.status)
        except ValueError as exc:
            raise ValueError("status is invalid") from exc
        if not np.isfinite(self.display_scale) or self.display_scale <= 0:
            raise ValueError("display_scale must be positive and finite")
        if not isinstance(self.frame, WireframeFrame):
            raise ValueError("frame must be a WireframeFrame")
        object.__setattr__(self, "source_centre", tuple(self.source_centre))
        object.__setattr__(self, "status", status)

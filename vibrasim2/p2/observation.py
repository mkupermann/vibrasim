"""Read-only P2 projection into the shared 3D wireframe contract."""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from vibrasim2.observation import EdgeKind, EdgeState, WireframeFrame
from vibrasim2.p0.fixtures import coupling_sites
from vibrasim2.p0.observation import (
    ObservationMetadata,
    ObservationProjectionConfig,
    ProjectionTopology,
    project_p0_observation,
)

from .fixtures import candidate_edges
from .trajectory import P2Snapshot
from .types import P2Cell, P2Config


def project_p2_observation(
    snapshot: P2Snapshot,
    cell: P2Cell,
    config: P2Config,
    metadata: ObservationMetadata,
    projection_config: ObservationProjectionConfig,
):
    """Show only copied P2 state, including real candidates and live bonds."""
    candidates = candidate_edges(config)
    topology = ProjectionTopology(
        config.grid_shape,
        coupling_sites(),
        np.asarray(candidates, dtype=np.int64),
        EdgeKind.RECIPROCAL_COUPLING,
    )
    envelope = project_p0_observation(snapshot, topology, metadata, projection_config)
    live = {(bond.left, bond.right) for bond in snapshot.state.bonds}
    candidate_states = tuple(
        EdgeState.LIVE if edge in live else EdgeState.AVAILABLE
        for edge in candidates
    )
    remaining_states = (EdgeState.SUPPLIED,) * (len(envelope.frame.edges) - len(candidates))
    values = np.zeros(len(envelope.frame.positions), dtype=np.float64)
    half_cost = config.formation_cost / 2.0
    if half_cost > 0:
        values[-len(snapshot.state.reservoirs):] = np.clip(
            snapshot.state.reservoirs / half_cost, 0.0, 1.0
        )
    frame = WireframeFrame(
        positions=envelope.frame.positions,
        edges=envelope.frame.edges,
        edge_states=candidate_states + remaining_states,
        edge_kinds=envelope.frame.edge_kinds,
        field_lines=envelope.frame.field_lines,
        particle_values=values,
    )
    return replace(envelope, frame=frame, arm=cell.arm.value, stage="P2")


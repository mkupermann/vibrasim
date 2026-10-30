from dataclasses import replace

import numpy as np

from vibrasim2.observation import EdgeState, ObservationStatus
from vibrasim2.p0.observation import ObservationMetadata, ObservationProjectionConfig
from vibrasim2.p2.dynamics import initial_state
from vibrasim2.p2.observation import project_p2_observation
from vibrasim2.p2.trajectory import P2Snapshot
from vibrasim2.p2.types import Bond, P2Arm, P2Cell, P2Config, P2Purpose


def test_p2_projection_shows_candidates_live_bonds_and_reservoirs_without_aliasing():
    config = P2Config.registered()
    state = replace(
        initial_state(config, (4, 16)),
        reservoirs=np.array([0.01, 0.02, 0, 0, 0, 0]),
        bonds=(Bond(0, 1, 1.0, 0.0, 0.0),),
    )
    snapshot = P2Snapshot(10, 0.25, state)
    metadata = ObservationMetadata(
        run_id="v2-p2-test", stage="P2", arm="full",
        source_centre=(4, 16), sequence=1, emitted_monotonic_ns=100,
        status=ObservationStatus.RUNNING,
    )

    envelope = project_p2_observation(
        snapshot,
        P2Cell(P2Arm.FULL, P2Purpose.PRIMARY, (4, 16), 0.025, 4000),
        config,
        metadata,
        ObservationProjectionConfig(),
    )

    assert envelope.tick == 10
    assert envelope.frame.positions.shape == (1030, 3)
    assert envelope.frame.edge_states[:6].count(EdgeState.LIVE) == 1
    assert envelope.frame.edge_states[:6].count(EdgeState.AVAILABLE) == 5
    np.testing.assert_allclose(envelope.frame.particle_values[-6:], [1.0, 1.0, 0, 0, 0, 0])
    state.reservoirs.flags.writeable = True
    state.reservoirs[0] = 0.0
    assert envelope.frame.particle_values[-6] == 1.0


def test_no_field_feedback_projection_marks_vertical_control_edges():
    config = P2Config.registered()
    state = initial_state(config, (4, 16))
    envelope = project_p2_observation(
        P2Snapshot(0, 0.0, state),
        P2Cell(P2Arm.NO_FIELD_FEEDBACK, P2Purpose.PRIMARY, (4, 16), 0.025, 4000),
        config,
        ObservationMetadata(
            "v2-p2-test", "P2", "no_field_feedback", (4, 16), 1, 100,
            ObservationStatus.RUNNING,
        ),
        ObservationProjectionConfig(),
    )

    assert envelope.arm == "no_field_feedback"
    assert len(envelope.frame.edges) == 12


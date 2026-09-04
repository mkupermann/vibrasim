import pytest
import numpy as np

from vibrasim2.observation import EdgeKind, ObservationStatus
from vibrasim2.p0.observation import (
    ObservationMetadata,
    ObservationProjectionConfig,
    ProjectionTopology,
    project_p0_observation,
)
from vibrasim2.p0.types import P0State, P0StateSnapshot
from vibrasim2.viewer_process import ViewerController, iter_replay_envelopes
from vibrasim2.wireframe import build_geometry

pytestmark = [pytest.mark.gui, pytest.mark.external]


def test_gui_geometry_uses_supplied_edges_field_lines_and_freeze():
    """Exercise the renderer contract without starting a desktop window."""
    topology = ProjectionTopology(
        (2, 2),
        np.array(((0, 0), (1, 1))),
        np.array(((0, 1),)),
        EdgeKind.RECIPROCAL_COUPLING,
    )
    snapshot = P0StateSnapshot(
        10,
        0.5,
        P0State(np.zeros((2, 2)), np.zeros((2, 2)), np.zeros(2), np.zeros(2)),
    )
    envelope = project_p0_observation(
        snapshot,
        topology,
        ObservationMetadata("r1", "A", "cycle", (0, 0), 1, 1, ObservationStatus.RUNNING),
        ObservationProjectionConfig(),
    )
    geometry = build_geometry(envelope.frame)
    assert geometry.edge_segments.shape == (3, 2, 3)
    assert len(geometry.field_lines) == 8
    assert EdgeKind.RECIPROCAL_COUPLING in geometry.edge_kinds

    controller = ViewerController()
    controller.accept(envelope)
    assert controller.next_drawable() == envelope
    controller.set_frozen(True)
    controller.accept(envelope)
    assert controller.next_drawable() is None


def test_gui_replay_contract_is_two_frame_and_read_only(tmp_path):
    """Replay consumes the journal and does not call a runner or dynamics."""
    from tests.test_vibrasim2_spawn_transport import _replay_tree

    _replay_tree(tmp_path)
    envelopes = tuple(iter_replay_envelopes(tmp_path))
    assert [item.tick for item in envelopes] == [10, 20]
    assert all(item.status is ObservationStatus.RUNNING for item in envelopes)

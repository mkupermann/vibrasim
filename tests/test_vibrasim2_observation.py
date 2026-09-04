import pickle

import numpy as np
import pytest

from vibrasim2.observation import (
    EdgeKind,
    EdgeState,
    ObservationEnvelope,
    ObservationStatus,
    WireframeFrame,
)


def make_frame() -> WireframeFrame:
    return WireframeFrame(
        positions=np.array(((0.0, 0.0, 0.0), (1.0, 0.0, 0.5))),
        edges=np.array(((0, 1),), dtype=np.int32),
        edge_states=(EdgeState.SUPPLIED,),
        edge_kinds=(EdgeKind.MATTER,),
        field_lines=(np.array(((0.0, 0.0, 0.0), (0.0, 1.0, 0.2))),),
    )


def test_frame_defensively_copies_and_freezes_arrays():
    source = np.array(((0.0, 0.0, 0.0), (1.0, 0.0, 0.5)))
    edges = np.array(((0, 1),))
    line = np.array(((0.0, 0.0, 0.0), (0.0, 1.0, 0.2)))
    frame = WireframeFrame(
        source, edges, (EdgeState.SUPPLIED,), (EdgeKind.MATTER,), (line,)
    )
    source[0, 0] = 99.0
    edges[0, 0] = 99
    line[0, 0] = 99.0
    assert frame.positions[0, 0] == 0.0
    assert frame.edges[0, 0] == 0
    assert frame.field_lines[0][0, 0] == 0.0
    assert not frame.positions.flags.writeable
    assert not frame.edges.flags.writeable
    assert not frame.field_lines[0].flags.writeable


def test_envelope_is_spawn_serializable_and_has_no_verdict():
    envelope = ObservationEnvelope(
        schema_version=1, run_id="r1", stage="A", arm="cycle",
        source_centre=(4, 16), tick=10, simulation_time=0.5, sequence=1,
        emitted_monotonic_ns=100, status=ObservationStatus.RUNNING,
        display_scale=4.0, frame=make_frame(),
    )
    restored = pickle.loads(pickle.dumps(envelope))
    np.testing.assert_array_equal(restored.frame.positions, envelope.frame.positions)
    assert not hasattr(envelope, "verdict")


def test_unknown_schema_and_invalid_geometry_are_rejected():
    with pytest.raises(ValueError, match="schema_version"):
        ObservationEnvelope(
            2, "r1", "A", "cycle", (4, 16), 10, 0.5, 1, 100,
            ObservationStatus.RUNNING, 4.0, make_frame(),
        )
    with pytest.raises(ValueError, match="edge kind"):
        WireframeFrame(
            np.zeros((2, 3)), np.array(((0, 1),)),
            (EdgeState.SUPPLIED,), (),
        )

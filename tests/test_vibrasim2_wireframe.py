import threading
from pathlib import Path

import numpy as np

from vibrasim2.observation import EdgeKind, EdgeState, WireframeFrame
from vibrasim2.wireframe import RenderCadence, build_geometry, iter_replay_cycles


def test_build_geometry_preserves_real_particles_and_edges_only():
    positions = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
        dtype=float,
    )
    frame = WireframeFrame(
        positions=positions,
        edges=np.array([[0, 1], [1, 2]], dtype=np.int32),
        edge_states=(EdgeState.SUPPLIED, EdgeState.SUPPLIED),
        edge_kinds=(EdgeKind.MATTER, EdgeKind.RECIPROCAL_COUPLING),
        field_lines=(np.array([[0.0, -1.0, 0.0], [1.0, -1.0, 0.0]]),),
    )

    geometry = build_geometry(frame)

    np.testing.assert_array_equal(geometry.particle_points, positions)
    np.testing.assert_array_equal(
        geometry.edge_segments,
        np.array(
            [
                [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
            ]
        ),
    )
    assert geometry.edge_states == (EdgeState.SUPPLIED, EdgeState.SUPPLIED)
    assert len(geometry.field_lines) == 1
    np.testing.assert_array_equal(geometry.field_lines[0], frame.field_lines[0])


def test_edge_endpoints_are_in_range():
    with np.testing.assert_raises_regex(ValueError, "edge endpoint"):
        WireframeFrame(
            positions=np.zeros((2, 3)),
            edges=np.array([[0, 2]], dtype=np.int32),
            edge_states=(EdgeState.SUPPLIED,),
            edge_kinds=(EdgeKind.MATTER,),
        )


def test_position_shape_is_n_by_three():
    with np.testing.assert_raises_regex(ValueError, "positions"):
        WireframeFrame(
            positions=np.zeros((2, 2)), edges=np.empty((0, 2), dtype=np.int32),
            edge_states=(), edge_kinds=(),
        )


def test_edge_shape_is_m_by_two():
    with np.testing.assert_raises_regex(ValueError, "edges"):
        WireframeFrame(
            positions=np.zeros((2, 3)), edges=np.zeros((2, 3), dtype=np.int32),
            edge_states=(EdgeState.SUPPLIED, EdgeState.SUPPLIED),
            edge_kinds=(EdgeKind.MATTER, EdgeKind.MATTER),
        )


def test_each_edge_has_one_state():
    with np.testing.assert_raises_regex(ValueError, "one edge state"):
        WireframeFrame(
            positions=np.zeros((2, 3)), edges=np.array([[0, 1]], dtype=np.int32),
            edge_states=(), edge_kinds=(EdgeKind.MATTER,),
        )


def test_field_lines_are_finite_two_point_polylines():
    with np.testing.assert_raises_regex(ValueError, "field lines"):
        WireframeFrame(
            positions=np.zeros((2, 3)), edges=np.empty((0, 2), dtype=np.int32),
            edge_states=(), edge_kinds=(),
            field_lines=(np.array([[0.0, 0.0, np.nan], [1.0, 0.0, 0.0]]),),
        )


def test_supplied_edge_colour_is_fixed_neutral_rgb():
    frame = WireframeFrame(
        positions=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
        edges=np.array([[0, 1], [0, 1], [0, 1]], dtype=np.int32),
        edge_states=(EdgeState.SUPPLIED, EdgeState.SUPPLIED, EdgeState.SUPPLIED),
        edge_kinds=(EdgeKind.MATTER, EdgeKind.RECIPROCAL_COUPLING,
                    EdgeKind.MATERIAL_ONLY_CONTROL),
    )

    geometry = build_geometry(frame)

    np.testing.assert_array_equal(
        geometry.edge_colors,
        np.array(
            [
                [150, 170, 185],
                [150, 170, 185],
                [150, 170, 185],
            ],
            dtype=np.uint8,
        ),
    )


def test_render_cadence_keeps_ui_polling_separate_from_two_second_frames():
    cadence = RenderCadence(frame_interval=2.0)

    assert cadence.frame_due(now=10.0, playing=True, step_requested=False)
    assert not cadence.frame_due(now=11.9, playing=True, step_requested=False)
    assert cadence.frame_due(now=12.0, playing=True, step_requested=False)
    assert not cadence.frame_due(now=20.0, playing=False, step_requested=False)
    assert cadence.frame_due(now=20.0, playing=False, step_requested=True)
    assert not cadence.frame_due(now=20.1, playing=True, step_requested=False)
    assert cadence.frame_due(now=22.0, playing=True, step_requested=False)


def test_replay_cycles_repeat_only_when_requested():
    calls = []

    def source(_path):
        calls.append(len(calls))
        return iter(("a", "b"))

    assert tuple(iter_replay_cycles(Path("run"), loop=False, source_factory=source)) == ("a", "b")
    assert calls == [0]

    stop = threading.Event()
    values = []
    for value in iter_replay_cycles(Path("run"), loop=True, stop_event=stop, source_factory=source):
        values.append(value)
        if len(values) == 5:
            stop.set()
    assert values == ["a", "b", "a", "b", "a"]
    assert calls == [0, 1, 2, 3]


def test_replay_cycles_do_not_spin_on_empty_source():
    calls = []

    def empty(_path):
        calls.append(True)
        return iter(())

    assert tuple(iter_replay_cycles(Path("run"), loop=True, source_factory=empty)) == ()
    assert calls == [True]

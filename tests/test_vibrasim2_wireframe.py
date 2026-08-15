import numpy as np

from vibrasim2.wireframe import BondState, RenderCadence, WireframeFrame, build_geometry


def test_build_geometry_preserves_real_particles_and_bonds_only():
    positions = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
        dtype=float,
    )
    frame = WireframeFrame(
        positions=positions,
        bonds=np.array([[0, 1], [1, 2]], dtype=np.int32),
        bond_states=(BondState.STABLE, BondState.FORMING),
        field_lines=(np.array([[0.0, -1.0, 0.0], [1.0, -1.0, 0.0]]),),
    )

    geometry = build_geometry(frame)

    np.testing.assert_array_equal(geometry.particle_points, positions)
    np.testing.assert_array_equal(
        geometry.bond_segments,
        np.array(
            [
                [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
            ]
        ),
    )
    assert geometry.bond_states == (BondState.STABLE, BondState.FORMING)
    assert len(geometry.field_lines) == 1
    np.testing.assert_array_equal(geometry.field_lines[0], frame.field_lines[0])


def test_frame_rejects_geometry_that_cannot_come_from_the_simulation():
    with np.testing.assert_raises_regex(ValueError, "bond endpoint"):
        WireframeFrame(
            positions=np.zeros((2, 3)),
            bonds=np.array([[0, 2]], dtype=np.int32),
            bond_states=(BondState.BREAKING,),
        )


def test_geometry_uses_fixed_state_colors():
    frame = WireframeFrame(
        positions=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
        bonds=np.array([[0, 1], [0, 1], [0, 1]], dtype=np.int32),
        bond_states=(BondState.STABLE, BondState.FORMING, BondState.BREAKING),
    )

    geometry = build_geometry(frame)

    np.testing.assert_array_equal(
        geometry.bond_colors,
        np.array(
            [
                [120, 220, 235],
                [80, 230, 140],
                [245, 145, 65],
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

from dataclasses import fields, replace

import numpy as np
import pytest

from vibrasim2.p0.types import (
    ChannelMode,
    P0Config,
    P0State,
    P0StateSnapshot,
    RunCell,
    RunPurpose,
    Topology,
)


def make_state() -> P0State:
    return P0State(
        np.zeros((32, 32)),
        np.zeros((32, 32)),
        np.zeros(6),
        np.zeros(6),
    )


def test_registered_state_shapes_are_exact():
    config = P0Config.registered()
    state = make_state()

    assert config.grid_shape == (32, 32)
    assert state.u.shape == (32, 32)
    assert state.p.shape == (32, 32)
    assert state.q.shape == (6,)
    assert state.r.shape == (6,)


def test_state_defensively_copies_and_freezes_all_arrays():
    originals = [
        np.zeros((2, 3), dtype=np.float32),
        np.ones((2, 3), dtype=np.float32),
        np.arange(4, dtype=np.int64),
        np.arange(4, dtype=np.int64) + 10,
    ]
    state = P0State(*originals)
    for original in originals:
        original[...] = 99

    expected = (
        np.zeros((2, 3)),
        np.ones((2, 3)),
        np.arange(4),
        np.arange(4) + 10,
    )
    for value, want in zip((state.u, state.p, state.q, state.r), expected, strict=True):
        np.testing.assert_array_equal(value, want)
        assert value.dtype == np.float64
        assert not value.flags.writeable
        with pytest.raises(ValueError):
            value.flat[0] = 7


def test_state_rejects_empty_or_incompatible_shapes():
    with pytest.raises(ValueError, match="non-empty"):
        P0State(np.empty((0, 2)), np.empty((0, 2)), np.zeros(1), np.zeros(1))
    with pytest.raises(ValueError, match="matching two-dimensional"):
        P0State(np.zeros((2, 2)), np.zeros((2, 3)), np.zeros(1), np.zeros(1))
    with pytest.raises(ValueError, match="matching one-dimensional"):
        P0State(np.zeros((2, 2)), np.zeros((2, 2)), np.zeros(1), np.zeros(2))


def test_registered_config_rejects_source_override():
    with pytest.raises(ValueError, match="registered P0 configuration"):
        replace(P0Config.registered(), source_centres=((5, 5),)).assert_registered()


def test_slug_contains_no_seed_dimension():
    cell = RunCell(
        Topology.CYCLE,
        ChannelMode.FULL,
        RunPurpose.PRIMARY,
        (4, 16),
        0.05,
        2000,
    )

    assert cell.slug == "primary-full-cycle-x4-y16-dt0.05"
    assert "seed" not in cell.slug
    assert "seed" not in {field.name for field in fields(RunCell)}
    assert "seed" not in {field.name for field in fields(P0Config)}


def test_arm_labels_are_unambiguous():
    source = (4, 16)
    labels = (
        RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.PRIMARY, source, 0.05, 2000).arm_label,
        RunCell(Topology.BRANCH, ChannelMode.FULL, RunPurpose.PRIMARY, source, 0.05, 2000).arm_label,
        RunCell(Topology.CYCLE, ChannelMode.NO_BONDS, RunPurpose.PRIMARY, source, 0.05, 2000).arm_label,
        RunCell(Topology.CYCLE, ChannelMode.DECOUPLED, RunPurpose.PRIMARY, source, 0.05, 2000).arm_label,
        RunCell(Topology.CYCLE, ChannelMode.BROKEN_PAIR, RunPurpose.SENSITIVITY, source, 0.05, 2000).arm_label,
        RunCell(Topology.BRANCH, ChannelMode.BROKEN_PAIR, RunPurpose.SENSITIVITY, source, 0.05, 2000).arm_label,
    )

    assert labels == (
        "cycle",
        "branch",
        "no_bonds",
        "decoupled",
        "cycle:broken_pair",
        "branch:broken_pair",
    )


def test_state_preserves_nonfinite_values_for_verdict():
    u = np.zeros((2, 2))
    u[0, 1] = np.nan

    state = P0State(u, np.zeros((2, 2)), np.zeros(1), np.zeros(1))
    snapshot = P0StateSnapshot(0, 0.0, state)

    assert np.isnan(snapshot.state.u[0, 1])

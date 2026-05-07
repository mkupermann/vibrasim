"""Tests for log-frequency-to-port-position mapping (AC1)."""
import numpy as np
import pytest
from agent.encoder_audio import freq_to_port_position


def test_AC1a_freq_min_at_left_edge():
    pos = freq_to_port_position(
        50.0, freq_min=50.0, freq_max=8000.0,
        port_origin=(0.0, 0.0, 0.0), port_size=(15.0, 15.0, 15.0),
        rng=np.random.default_rng(0),
    )
    assert pos[0] == pytest.approx(0.0, abs=0.01)


def test_AC1b_freq_max_at_right_edge():
    pos = freq_to_port_position(
        8000.0, freq_min=50.0, freq_max=8000.0,
        port_origin=(0.0, 0.0, 0.0), port_size=(15.0, 15.0, 15.0),
        rng=np.random.default_rng(0),
    )
    assert pos[0] == pytest.approx(15.0, abs=0.01)


def test_AC1c_geometric_mean_at_center():
    """632.5 Hz is geometric mean of 50 and 8000; should be at port centre."""
    pos = freq_to_port_position(
        np.sqrt(50.0 * 8000.0), freq_min=50.0, freq_max=8000.0,
        port_origin=(0.0, 0.0, 0.0), port_size=(15.0, 15.0, 15.0),
        rng=np.random.default_rng(0),
    )
    assert pos[0] == pytest.approx(7.5, rel=0.05)


def test_AC1d_y_z_are_random_within_port():
    """Y and Z should vary across calls (drawn from RNG)."""
    rng = np.random.default_rng(42)
    pos1 = freq_to_port_position(1000.0, port_size=(15.0, 15.0, 15.0), rng=rng)
    pos2 = freq_to_port_position(1000.0, port_size=(15.0, 15.0, 15.0), rng=rng)
    assert pos1[1] != pos2[1] or pos1[2] != pos2[2]
    # X is deterministic given freq
    assert pos1[0] == pos2[0]


def test_AC1e_clamping_below_freq_min():
    pos = freq_to_port_position(
        10.0, freq_min=50.0, freq_max=8000.0,
        port_origin=(0.0, 0.0, 0.0), port_size=(15.0, 15.0, 15.0),
        rng=np.random.default_rng(0),
    )
    assert pos[0] == pytest.approx(0.0, abs=0.01)


def test_AC1f_clamping_above_freq_max():
    pos = freq_to_port_position(
        20000.0, freq_min=50.0, freq_max=8000.0,
        port_origin=(0.0, 0.0, 0.0), port_size=(15.0, 15.0, 15.0),
        rng=np.random.default_rng(0),
    )
    assert pos[0] == pytest.approx(15.0, abs=0.01)

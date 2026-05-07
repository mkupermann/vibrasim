"""Tests for retinotopic position mapping (VC6)."""
import numpy as np
import pytest
from agent.encoder_video import patch_to_port_position, feature_magnitude_to_frequency


def test_VC6_lower_left_patch_maps_to_lower_left_of_port():
    pos = patch_to_port_position(
        patch_x=0, patch_y=0, orientation_id=0,
        patch_grid=(16, 16), n_orientations=8,
        port_origin=(0.0, 0.0, 45.0), port_size=(15.0, 15.0, 15.0),
    )
    # patch (0,0) → centre of first patch at (0+0.5)/16 × 15 = 0.46875
    assert pos[0] == pytest.approx(0.46875, abs=1e-3)
    assert pos[1] == pytest.approx(0.46875, abs=1e-3)
    # orientation_id=0 → centre of first depth bin: 45 + (0+0.5)/8 × 15 = 45.9375
    assert pos[2] == pytest.approx(45.9375, abs=1e-3)


def test_VC6b_upper_right_patch_maps_to_upper_right_of_port():
    pos = patch_to_port_position(
        patch_x=15, patch_y=15, orientation_id=7,
        patch_grid=(16, 16), n_orientations=8,
        port_origin=(0.0, 0.0, 45.0), port_size=(15.0, 15.0, 15.0),
    )
    # patch (15,15) → (15+0.5)/16 × 15 = 14.53125
    assert pos[0] == pytest.approx(14.53125, abs=1e-3)
    assert pos[1] == pytest.approx(14.53125, abs=1e-3)
    # orientation_id=7 → 45 + (7+0.5)/8 × 15 = 59.0625
    assert pos[2] == pytest.approx(59.0625, abs=1e-3)


def test_VC6c_orientation_4_at_mid_depth():
    pos = patch_to_port_position(
        patch_x=8, patch_y=8, orientation_id=4,
        patch_grid=(16, 16), n_orientations=8,
        port_origin=(0.0, 0.0, 45.0), port_size=(15.0, 15.0, 15.0),
    )
    # orientation_id=4 → 45 + (4+0.5)/8 × 15 = 53.4375
    assert pos[2] == pytest.approx(53.4375, abs=1e-3)


def test_VC6d_feature_magnitude_to_frequency_endpoints():
    assert feature_magnitude_to_frequency(0.0, freq_min=1000.0, freq_max=12000.0) == 1000.0
    assert feature_magnitude_to_frequency(1.0, freq_min=1000.0, freq_max=12000.0) == 12000.0
    assert feature_magnitude_to_frequency(0.5, freq_min=1000.0, freq_max=12000.0) == 6500.0

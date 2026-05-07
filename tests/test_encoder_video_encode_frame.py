"""Tests for frame encoding (VC3, VC4, VC5)."""
import numpy as np
from agent.encoder_video import encode_frame, build_oriented_filter_bank


def test_VC3_uniform_grey_produces_no_features():
    """Edge-free frame → no features above threshold."""
    frame = np.full((128, 128), 0.5, dtype=np.float32)
    features = encode_frame(frame, patch_grid=(16, 16), amplitude_threshold=0.05)
    assert features == []


def test_VC4_vertical_edge_image_produces_horizontal_filter_response():
    """A vertical line (left half black, right half white) produces a strong
    response from the filter oriented at 0° — the horizontal-gradient detector."""
    frame = np.zeros((128, 128), dtype=np.float32)
    frame[:, 64:] = 1.0  # right half white
    features = encode_frame(frame, patch_grid=(16, 16), amplitude_threshold=0.05)
    assert len(features) > 0
    # Filter index 0 = 0° orientation (horizontal direction → detects vertical edges)
    horizontal_responses = [f for f in features if f[2] == 0]
    assert len(horizontal_responses) > 0, (
        f"VC4: expected feature with orientation_id=0, got {[f[2] for f in features]}"
    )


def test_VC5_horizontal_edge_image_produces_vertical_filter_response():
    """A horizontal line (top half black, bottom half white) produces a strong
    response from the filter oriented at 90° — the vertical-gradient detector."""
    frame = np.zeros((128, 128), dtype=np.float32)
    frame[64:, :] = 1.0  # bottom half white
    features = encode_frame(frame, patch_grid=(16, 16), amplitude_threshold=0.05)
    assert len(features) > 0
    # Filter index 4 = 90° orientation (vertical direction → detects horizontal edges)
    vertical_responses = [f for f in features if f[2] == 4]
    assert len(vertical_responses) > 0, (
        f"VC5: expected feature with orientation_id=4, got {[f[2] for f in features]}"
    )


def test_VC3b_below_threshold_filtered():
    rng = np.random.default_rng(0)
    # Tiny noise — magnitude well below 0.05 threshold
    frame = (0.5 + 0.001 * rng.standard_normal((128, 128))).astype(np.float32)
    features = encode_frame(frame, patch_grid=(16, 16), amplitude_threshold=0.05)
    assert features == []


def test_VC4b_returns_5tuples():
    """encode_frame returns (patch_x, patch_y, orientation_id, magnitude, sign)."""
    frame = np.zeros((128, 128), dtype=np.float32)
    frame[:, 64:] = 1.0
    features = encode_frame(frame, patch_grid=(16, 16))
    assert len(features) > 0
    f = features[0]
    assert len(f) == 5
    assert isinstance(f[0], int) or isinstance(f[0], np.integer)
    assert isinstance(f[1], int) or isinstance(f[1], np.integer)
    assert isinstance(f[2], int) or isinstance(f[2], np.integer)
    assert isinstance(f[3], float)
    assert isinstance(f[4], (bool, np.bool_))

"""Tests that distinct shapes produce distinct port firing patterns (VC8)."""
import numpy as np
from agent.encoder_video import (
    downsample_frame, encode_frame, patch_to_port_position,
)


def _features_to_position_set(features, patch_grid=(16, 16), n_orientations=8):
    return {(f[0], f[1], f[2]) for f in features}


def test_VC8_distinct_shapes_produce_distinct_patterns():
    """Vertical line, horizontal line, and half-and-half produce port firing
    patterns whose pairwise Jaccard similarity is < 0.5.

    Note: the vertical line is placed at x=160 (left quarter) so it occupies
    a different retinotopic column than the half-and-half edge at x=320.
    Both fire different patch columns after 128×128 downsampling.
    """
    # Vertical line (left-quarter column)
    f_vert = np.zeros((480, 640, 3), dtype=np.uint8)
    f_vert[:, 160, :] = 255  # one-pixel vertical line at x=160

    # Horizontal line (top-quarter row)
    f_horiz = np.zeros((480, 640, 3), dtype=np.uint8)
    f_horiz[120, :, :] = 255  # one-pixel horizontal line at y=120

    # Half-and-half (right half white, edge at x=320)
    f_half = np.zeros((480, 640, 3), dtype=np.uint8)
    f_half[:, 320:, :] = 255

    features_v = encode_frame(downsample_frame(f_vert), amplitude_threshold=0.05)
    features_h = encode_frame(downsample_frame(f_horiz), amplitude_threshold=0.05)
    features_b = encode_frame(downsample_frame(f_half), amplitude_threshold=0.05)

    set_v = _features_to_position_set(features_v)
    set_h = _features_to_position_set(features_h)
    set_b = _features_to_position_set(features_b)

    def jaccard(a, b):
        if not a and not b:
            return 1.0
        return len(a & b) / max(len(a | b), 1)

    j_vh = jaccard(set_v, set_h)
    j_vb = jaccard(set_v, set_b)
    j_hb = jaccard(set_h, set_b)
    print(f"VC8 jaccards: V↔H={j_vh:.2f}, V↔B={j_vb:.2f}, H↔B={j_hb:.2f}")
    assert j_vh < 0.5, f"VC8: vertical vs horizontal too similar ({j_vh})"
    assert j_vb < 0.5, f"VC8: vertical vs half too similar ({j_vb})"
    assert j_hb < 0.5, f"VC8: horizontal vs half too similar ({j_hb})"

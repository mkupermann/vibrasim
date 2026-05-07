"""Headline integration test I4 — video encoding distinctness."""
import numpy as np
from agent.encoder_video import (
    downsample_frame, encode_frame, patch_to_port_position,
)


def _feature_set(features):
    """Convert features to a set of (px, py, o) tuples for similarity."""
    return {(f[0], f[1], f[2]) for f in features}


def test_I4_video_encoding_distinctness():
    """Three 256×256 frames — horizontal line, vertical line, circle —
    produce port firing patterns with pairwise cosine similarity < 0.5.
    """
    # Horizontal line
    f_h = np.zeros((256, 256), dtype=np.uint8)
    f_h[128, :] = 255

    # Vertical line
    f_v = np.zeros((256, 256), dtype=np.uint8)
    f_v[:, 128] = 255

    # Circle
    f_c = np.zeros((256, 256), dtype=np.uint8)
    yy, xx = np.ogrid[:256, :256]
    cx, cy, r = 128, 128, 60
    mask = (xx - cx) ** 2 + (yy - cy) ** 2
    f_c[(mask >= (r - 2) ** 2) & (mask <= (r + 2) ** 2)] = 255

    features = [
        encode_frame(downsample_frame(f), amplitude_threshold=0.05)
        for f in (f_h, f_v, f_c)
    ]
    sets = [_feature_set(fs) for fs in features]
    sizes = [len(s) for s in sets]
    print(f"I4 set sizes: {sizes}")

    def cosine(a, b):
        # Treat sets as binary vectors over their union.
        u = a | b
        if not u:
            return 1.0
        va = np.array([1 if e in a else 0 for e in u])
        vb = np.array([1 if e in b else 0 for e in u])
        norm_a = float(np.linalg.norm(va))
        norm_b = float(np.linalg.norm(vb))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(va @ vb / (norm_a * norm_b))

    cos_hv = cosine(sets[0], sets[1])
    cos_hc = cosine(sets[0], sets[2])
    cos_vc = cosine(sets[1], sets[2])
    print(f"I4 cosines: H↔V={cos_hv:.2f}, H↔C={cos_hc:.2f}, V↔C={cos_vc:.2f}")
    assert cos_hv < 0.5
    assert cos_hc < 0.5
    assert cos_vc < 0.5

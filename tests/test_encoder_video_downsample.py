"""Tests for frame downsampling (VC1)."""
import numpy as np
from agent.encoder_video import downsample_frame


def test_VC1_downsample_640_480_rgb_to_128_128_grayscale():
    """640×480 RGB uint8 → 128×128 grayscale float32 in [0, 1]."""
    rng = np.random.default_rng(0)
    frame = rng.integers(0, 256, size=(480, 640, 3), dtype=np.uint8)
    out = downsample_frame(frame, output_size=(128, 128))
    assert out.shape == (128, 128)
    assert out.dtype == np.float32
    assert (out >= 0.0).all() and (out <= 1.0).all()


def test_VC1b_uniform_grey_input_produces_uniform_output():
    frame = np.full((480, 640, 3), 128, dtype=np.uint8)
    out = downsample_frame(frame, output_size=(128, 128))
    # All pixels should be very close to 128/255 ≈ 0.502
    assert abs(float(out.mean()) - 128.0 / 255.0) < 0.01
    assert float(out.std()) < 0.05


def test_VC1c_already_grayscale_input_works():
    """A 2D grayscale input should not crash on the RGB-to-luma branch."""
    frame = np.full((480, 640), 200, dtype=np.uint8)
    out = downsample_frame(frame, output_size=(128, 128))
    assert out.shape == (128, 128)
    assert abs(float(out.mean()) - 200.0 / 255.0) < 0.01

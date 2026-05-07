"""Tests for oriented filter bank construction (VC2)."""
import numpy as np
from agent.encoder_video import build_oriented_filter_bank


def test_VC2_filter_bank_shape_and_count():
    bank = build_oriented_filter_bank()
    # 8 orientations by default, 5×5 kernel
    assert bank.shape == (8, 5, 5)
    assert bank.dtype == np.float32


def test_VC2b_each_filter_zero_mean_unit_norm():
    bank = build_oriented_filter_bank()
    for i in range(bank.shape[0]):
        f = bank[i]
        assert abs(float(f.mean())) < 1e-5, f"filter {i} mean={f.mean()}"
        assert abs(float(np.linalg.norm(f)) - 1.0) < 1e-5, (
            f"filter {i} norm={np.linalg.norm(f)}"
        )


def test_VC2c_orientations_are_distinct():
    """No two orientation filters should be identical."""
    bank = build_oriented_filter_bank()
    n = bank.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            cosine = float(
                np.sum(bank[i] * bank[j]) /
                (np.linalg.norm(bank[i]) * np.linalg.norm(bank[j]))
            )
            assert abs(cosine) < 0.99, (
                f"filters {i} and {j} too similar (cos={cosine})"
            )

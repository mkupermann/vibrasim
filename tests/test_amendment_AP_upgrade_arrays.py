"""Plan A.5 Task 8: verify the upgrade-target arrays mirror the dicts."""
import numpy as np
from world.physics import (
    _UPGRADE_TARGET, _UPGRADE_TARGET_FUSION,
    _UPGRADE_TARGET_ARRAY, _UPGRADE_TARGET_FUSION_ARRAY,
)


def test_upgrade_target_array_mirrors_dict():
    """Every (li, lj) entry in the dict must match the array, and every
    (li, lj) NOT in the dict must be -1 in the array."""
    for li in range(12):
        for lj in range(12):
            expected = _UPGRADE_TARGET.get((li, lj), -1)
            assert _UPGRADE_TARGET_ARRAY[li, lj] == expected, (
                f"mismatch at ({li}, {lj}): array={_UPGRADE_TARGET_ARRAY[li, lj]}, "
                f"dict={expected}"
            )


def test_upgrade_target_fusion_array_mirrors_dict():
    """Same for the fusion table."""
    for li in range(12):
        for lj in range(12):
            expected = _UPGRADE_TARGET_FUSION.get((li, lj), -1)
            assert _UPGRADE_TARGET_FUSION_ARRAY[li, lj] == expected


def test_upgrade_target_array_dtype_and_shape():
    """Arrays are (12, 12) int8."""
    assert _UPGRADE_TARGET_ARRAY.shape == (12, 12)
    assert _UPGRADE_TARGET_ARRAY.dtype == np.int8
    assert _UPGRADE_TARGET_FUSION_ARRAY.shape == (12, 12)
    assert _UPGRADE_TARGET_FUSION_ARRAY.dtype == np.int8

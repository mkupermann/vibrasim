"""Tests for binding rule — F1a level (no bridges, no plasticity)."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.binding import pred_coherence


def test_pred_coherence_returns_one_for_equal_frequencies():
    # F1a simplification: pred_coherence is 1.0 if |f_a - f_b| < eps,
    # else 0.0. Full cross-correlation deferred to F2.
    assert pred_coherence(200.0, 200.0, eps=1.0) == 1.0
    # |200.4 - 199.7| = 0.7 < 1.0 → 1.0
    assert pred_coherence(200.4, 199.7, eps=1.0) == 1.0


def test_pred_coherence_returns_zero_for_different_frequencies():
    assert pred_coherence(200.0, 300.0, eps=1.0) == 0.0
    assert pred_coherence(100.0, 100.5, eps=0.1) == 0.0


def test_pred_coherence_at_boundary_is_zero():
    # Exactly at eps the difference is not strictly < eps → 0.0
    assert pred_coherence(200.0, 201.0, eps=1.0) == 0.0

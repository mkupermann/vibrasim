"""Tests for tools/measure_network_activity.py."""
import numpy as np
import pytest

from tools.measure_network_activity import score_pattern_recognition


def test_score_perfect_match():
    """Output activity exactly matches expected → score 1.0."""
    fm = [
        [0, 0, 0],
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]
    output_indices = [1, 2]
    expected = [[1, 0]]
    windows = [(1, 2)]  # snapshot indices 1..2
    score = score_pattern_recognition(fm, output_indices, expected, windows)
    assert score == pytest.approx(1.0)


def test_score_no_match():
    fm = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    output_indices = [1, 2]
    expected = [[1, 1]]
    windows = [(0, 2)]
    score = score_pattern_recognition(fm, output_indices, expected, windows)
    assert score == pytest.approx(0.0)


def test_score_partial_match():
    fm = [
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
    ]
    output_indices = [1, 2, 3]
    expected = [[1, 1, 1]]  # all three should fire
    windows = [(0, 1)]
    # Observed (max over window): [1, 1, 0] → 2/3 match
    score = score_pattern_recognition(fm, output_indices, expected, windows)
    assert score == pytest.approx(2.0 / 3.0)


def test_score_multiple_windows():
    fm = [
        [0, 1, 0],   # t=0: only neuron 1 fires
        [0, 0, 1],   # t=1: only neuron 2 fires
        [0, 0, 0],   # t=2: silence
    ]
    output_indices = [1, 2]
    expected = [
        [1, 0],  # window 0..0 should show pattern [1, 0]
        [0, 1],  # window 1..1 should show pattern [0, 1]
    ]
    windows = [(0, 0), (1, 1)]
    score = score_pattern_recognition(fm, output_indices, expected, windows)
    assert score == pytest.approx(1.0)  # both windows match perfectly


def test_score_empty_inputs():
    score = score_pattern_recognition([[0, 0, 0]], [], [], [])
    assert score == 0.0


def test_score_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        score_pattern_recognition([[0, 0]], [0, 1], [[1, 0]], [(0, 0), (1, 1)])

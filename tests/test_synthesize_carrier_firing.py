"""Tests for tools/synthesize_carrier_firing.py."""
import numpy as np
import pytest

from tools.synthesize_carrier_firing import synthesize_carrier_firing


def test_shape_and_dtype():
    fm, times = synthesize_carrier_firing(
        n_neurons=4, n_snapshots=50, dt=0.1,
        carrier_frequency=2.0, resonating_indices=[1],
    )
    assert fm.shape == (50, 4)
    assert fm.dtype == np.int8
    assert len(times) == 50
    assert times[0] == 0.0
    assert pytest.approx(times[-1]) == 4.9


def test_resonating_neurons_have_higher_firing_rate():
    fm, _ = synthesize_carrier_firing(
        n_neurons=4, n_snapshots=200, dt=0.1,
        carrier_frequency=2.0, resonating_indices=[0, 2],
        firing_probability_resonating=0.6,
        firing_probability_silent=0.05,
        rng_seed=42,
    )
    rates = fm.mean(axis=0)
    # Resonating: ~30% (half of 60% since rhythm is positive half the time)
    # Silent: ~5%
    assert rates[0] > rates[1]
    assert rates[2] > rates[3]
    assert rates[0] > 0.10  # well above silent baseline
    assert rates[1] < 0.15  # near silent baseline


def test_phase_offset_changes_firing_pattern():
    fm0, _ = synthesize_carrier_firing(
        n_neurons=2, n_snapshots=100, dt=0.1,
        carrier_frequency=2.0, resonating_indices=[0], phase_offsets=[0.0],
        rng_seed=42,
    )
    fm_pi, _ = synthesize_carrier_firing(
        n_neurons=2, n_snapshots=100, dt=0.1,
        carrier_frequency=2.0, resonating_indices=[0], phase_offsets=[np.pi],
        rng_seed=42,
    )
    # The firing pattern of neuron 0 should differ between phase=0 and phase=pi
    # (they're 180° out of phase, so when one fires the other doesn't).
    assert not np.array_equal(fm0[:, 0], fm_pi[:, 0])


def test_invalid_phase_offsets_length_rejected():
    with pytest.raises(ValueError):
        synthesize_carrier_firing(
            n_neurons=4, n_snapshots=50, dt=0.1,
            carrier_frequency=2.0, resonating_indices=[1, 2],
            phase_offsets=[0.0],  # one offset for two indices
        )

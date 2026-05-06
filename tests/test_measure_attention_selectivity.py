"""Tests for tools/measure_attention_selectivity.py."""
import numpy as np
import pytest

from tools.measure_attention_selectivity import measure_selectivity, _phase_grid_search
from tools.synthesize_carrier_firing import synthesize_carrier_firing


def test_uniform_silent_network_low_selectivity():
    """All-zero firing matrix → resonance scores all 0, low selectivity."""
    fm = np.zeros((50, 4), dtype=np.float64)
    times = np.arange(50) * 0.1
    result = measure_selectivity(fm, times, carrier_frequency=2.0)
    assert all(abs(r) < 0.05 for r in result["resonance_scores"])
    assert result["resonating_indices"] == []
    # selectivity_index is 0 when mean_abs is essentially 0
    assert result["selectivity_index"] < 0.1


def test_one_resonator_in_silent_network():
    """1 of 5 fires on the carrier rhythm, others silent → only that one in resonating subset."""
    fm, times = synthesize_carrier_firing(
        n_neurons=5, n_snapshots=200, dt=0.1,
        carrier_frequency=2.0, resonating_indices=[2],
        firing_probability_resonating=0.8, firing_probability_silent=0.0,
        rng_seed=42,
    )
    result = measure_selectivity(np.asarray(fm), times, carrier_frequency=2.0)
    assert 2 in result["resonating_indices"]
    # Silent neurons should not be in the resonating subset
    for i in (0, 1, 3, 4):
        assert i not in result["resonating_indices"]


def test_multiple_resonators_recovered():
    """Synthesise 3 of 8 with phase 0 → measurement recovers all three."""
    indices = [1, 3, 5]
    fm, times = synthesize_carrier_firing(
        n_neurons=8, n_snapshots=200, dt=0.1,
        carrier_frequency=2.0, resonating_indices=indices,
        phase_offsets=[0.0, 0.0, 0.0],
        firing_probability_resonating=0.7, firing_probability_silent=0.02,
        rng_seed=42,
    )
    result = measure_selectivity(np.asarray(fm), times, carrier_frequency=2.0)
    for i in indices:
        assert i in result["resonating_indices"]


def test_phase_coherence_aligned_resonators():
    """All resonators at phase 0 → coherence > 0.85."""
    fm, times = synthesize_carrier_firing(
        n_neurons=5, n_snapshots=200, dt=0.1,
        carrier_frequency=2.0, resonating_indices=[0, 1, 2],
        phase_offsets=[0.0, 0.0, 0.0],
        firing_probability_resonating=0.8, firing_probability_silent=0.02,
        rng_seed=42,
    )
    result = measure_selectivity(np.asarray(fm), times, carrier_frequency=2.0)
    assert result["phase_coherence"] > 0.85


def test_phase_coherence_misaligned_resonators():
    """Resonators with random phases → low coherence."""
    fm, times = synthesize_carrier_firing(
        n_neurons=8, n_snapshots=200, dt=0.1,
        carrier_frequency=2.0, resonating_indices=[0, 1, 2, 3, 4, 5, 6, 7],
        phase_offsets=[0.0, np.pi / 2, np.pi, 3 * np.pi / 2,
                       np.pi / 4, 3 * np.pi / 4, 5 * np.pi / 4, 7 * np.pi / 4],
        firing_probability_resonating=0.8, firing_probability_silent=0.02,
        rng_seed=42,
    )
    result = measure_selectivity(np.asarray(fm), times, carrier_frequency=2.0)
    # 8 evenly-spaced phases → mean vector ≈ 0
    if len(result["resonating_indices"]) >= 4:
        assert result["phase_coherence"] < 0.4


def test_wrong_carrier_frequency_no_resonance():
    """Synthesise resonators at 2 Hz but measure at 5 Hz → no significant resonance."""
    fm, times = synthesize_carrier_firing(
        n_neurons=4, n_snapshots=200, dt=0.1,
        carrier_frequency=2.0, resonating_indices=[1],
        firing_probability_resonating=0.7, firing_probability_silent=0.02,
        rng_seed=42,
    )
    result = measure_selectivity(np.asarray(fm), times, carrier_frequency=5.0)
    # The resonator is now off-frequency; should have low resonance score
    assert result["resonance_scores"][1] < 0.4


def test_phase_grid_search_recovers_phase():
    """A pure cosine signal at known phase should recover the phase."""
    n = 200
    times = np.arange(n) * 0.05
    target_phase = np.pi / 3
    signal = np.sin(2.0 * np.pi * 2.0 * times + target_phase)
    # Make it non-constant binary-like by thresholding
    binary = (signal > 0).astype(np.float64)
    phase, corr = _phase_grid_search(binary, times, carrier_frequency=2.0, n_phases=32)
    # 16 or 32 phases → max error ~π/16
    delta = abs((phase - target_phase + np.pi) % (2 * np.pi) - np.pi)
    assert delta < np.pi / 8
    assert corr > 0.7


def test_invalid_dimensions_raises():
    with pytest.raises(ValueError):
        measure_selectivity(np.zeros(5), np.zeros(5), carrier_frequency=2.0)


def test_mismatched_times_length_raises():
    fm = np.zeros((10, 4))
    times = np.zeros(5)
    with pytest.raises(ValueError):
        measure_selectivity(fm, times, carrier_frequency=2.0)

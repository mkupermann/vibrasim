"""Tests for tuned PHASE4 emissions: frequency-band fan."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import _emit_vibrations


def _world_for_emit(emit_band_ratios=(0.08, 1.0, 12.5)):
    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=64,
        n_nodes_max=4,
        rng_seed=42,
        neuron_dynamics_enabled=True,
        n_emit=12,
        emit_freq=10000.0,
        emit_band_ratios=emit_band_ratios,
    )
    w = World(cfg)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = 4
    w.k_alive[0] = True
    w.k_count = 1
    return w


def test_emissions_span_three_frequency_bands():
    """With emit_band_ratios=(0.08, 1.0, 12.5), emitted vibrations should
    populate three distinct frequency clusters around base/0.08*base/12.5*base."""
    w = _world_for_emit()
    _emit_vibrations(w, atom_idx=0)
    alive_idx = np.where(w.s_alive)[0]
    assert len(alive_idx) == 12
    freqs = w.s_freq[alive_idx]
    base = 10000.0
    n_low = int(np.sum((freqs > 0.7 * 0.08 * base) & (freqs < 1.3 * 0.08 * base)))
    n_mid = int(np.sum((freqs > 0.7 * base) & (freqs < 1.3 * base)))
    n_high = int(np.sum((freqs > 0.7 * 12.5 * base) & (freqs < 1.3 * 12.5 * base)))
    assert n_low >= 2 and n_mid >= 2 and n_high >= 2, (
        f"emission distribution: low={n_low}, mid={n_mid}, high={n_high}"
    )


def test_emissions_position_at_atom():
    """Every emission spawns at the firing atom's position (within ε)."""
    w = _world_for_emit()
    _emit_vibrations(w, atom_idx=0)
    alive_idx = np.where(w.s_alive)[0]
    assert (np.abs(w.s_pos[alive_idx] - [50.0, 50.0, 50.0]) < 0.001).all()


def test_emissions_have_isotropic_velocities():
    """Velocity magnitudes should equal cfg.emit_speed (isotropic directions)."""
    w = _world_for_emit()
    _emit_vibrations(w, atom_idx=0)
    alive_idx = np.where(w.s_alive)[0]
    speeds = np.linalg.norm(w.s_vel[alive_idx], axis=1)
    expected = w.config.emit_speed
    assert np.allclose(speeds, expected, rtol=1e-6)

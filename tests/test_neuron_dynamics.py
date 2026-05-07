"""Tests for the PHASE4-R1/R2/R3 neuron dynamics in world.physics.neuron_dynamics."""
import numpy as np
import pytest

from world.config import WorldConfig
from world.state import World
from world.physics import neuron_dynamics, tick


def _world_with_atom(centre, *, enabled=True, theta_fire=4.0, n_emit=8,
                     r_integrate=5.0, t_refractory=0.05, tau_membrane=0.5):
    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=128,
        n_nodes_max=4,
        box_size=(200.0, 200.0, 200.0),
        rng_seed=42,
        neuron_dynamics_enabled=enabled,
        theta_fire=theta_fire,
        n_emit=n_emit,
        r_integrate=r_integrate,
        t_refractory=t_refractory,
        tau_membrane=tau_membrane,
        repulsion_cell_size=200.0,
    )
    w = World(cfg)
    # One level-4 atom at centre
    idx = 0
    w.k_pos[idx] = centre
    w.k_freq[idx] = 30000.0
    w.k_pol[idx] = True
    w.k_level[idx] = 4
    w.k_alive[idx] = True
    w.k_birth[idx] = 0.0
    w.k_count = 1
    return w


def _seed_vibrations(w, positions):
    """Place vibrations at the given positions (alive, with zero velocity)."""
    for i, p in enumerate(positions):
        w.s_pos[i] = p
        w.s_vel[i] = 0.0
        w.s_freq[i] = 1000.0
        w.s_pol[i] = bool(i % 2)
        w.s_alive[i] = True
    w.n_alive = max(w.n_alive, len(positions))


def test_disabled_is_noop():
    """When neuron_dynamics_enabled=False, no charge accumulates."""
    centre = np.array([100.0, 100.0, 100.0])
    w = _world_with_atom(centre, enabled=False)
    _seed_vibrations(w, [centre.tolist() for _ in range(10)])
    neuron_dynamics(w, dt=0.01)
    assert w.k_charge[0] == 0.0
    assert len(w.firing_events) == 0


def test_charge_accumulates_from_nearby_vibrations():
    centre = np.array([100.0, 100.0, 100.0])
    w = _world_with_atom(centre, theta_fire=100.0, r_integrate=5.0)
    _seed_vibrations(w, [centre.tolist() for _ in range(7)])
    neuron_dynamics(w, dt=0.001)  # tiny dt → minimal decay
    assert w.k_charge[0] >= 7.0


def test_far_vibrations_do_not_charge():
    centre = np.array([100.0, 100.0, 100.0])
    w = _world_with_atom(centre, theta_fire=100.0, r_integrate=5.0)
    _seed_vibrations(w, [[10.0, 10.0, 10.0]] * 10)
    neuron_dynamics(w, dt=0.001)
    assert w.k_charge[0] == 0.0


def test_threshold_triggers_emission():
    centre = np.array([100.0, 100.0, 100.0])
    w = _world_with_atom(centre, theta_fire=4.0, n_emit=8, r_integrate=5.0)
    _seed_vibrations(w, [centre.tolist() for _ in range(5)])
    n_alive_before_dynamics = int(w.s_alive.sum())
    neuron_dynamics(w, dt=0.001)
    n_alive_after = int(w.s_alive.sum())
    assert len(w.firing_events) == 1
    assert n_alive_after == n_alive_before_dynamics + 8
    # After firing the charge resets
    assert w.k_charge[0] == 0.0


def test_refractory_blocks_subsequent_firing():
    centre = np.array([100.0, 100.0, 100.0])
    w = _world_with_atom(centre, theta_fire=4.0, n_emit=8, r_integrate=5.0,
                         t_refractory=0.10)
    # First charge to fire
    _seed_vibrations(w, [centre.tolist() for _ in range(8)])
    neuron_dynamics(w, dt=0.001)
    assert len(w.firing_events) == 1
    # Tick forward a small amount (still within refractory)
    w.t += 0.05
    neuron_dynamics(w, dt=0.001)
    # Should not have fired again
    assert len(w.firing_events) == 1
    # Past the refractory window: should be able to fire again with new input
    w.t += 0.10
    # Re-add input vibrations (some may have moved/been consumed)
    _seed_vibrations(w, [centre.tolist() for _ in range(8)])
    neuron_dynamics(w, dt=0.001)
    assert len(w.firing_events) == 2


def test_charge_decays_exponentially():
    centre = np.array([100.0, 100.0, 100.0])
    # tau = 0.1s; over 0.5s, charge should drop to e^-5 ≈ 0.0067
    w = _world_with_atom(centre, theta_fire=1000.0, tau_membrane=0.1)
    w.k_charge[0] = 100.0
    # Run dynamics with no nearby vibrations for 0.5s
    for _ in range(50):
        neuron_dynamics(w, dt=0.01)
    expected = 100.0 * np.exp(-0.5 / 0.1)
    assert w.k_charge[0] == pytest.approx(expected, rel=1e-3)


def test_tick_includes_neuron_dynamics_when_enabled():
    """Confirm tick() drives neuron_dynamics so a full simulation can fire."""
    centre = np.array([100.0, 100.0, 100.0])
    w = _world_with_atom(centre, theta_fire=4.0, n_emit=8, r_integrate=5.0)
    _seed_vibrations(w, [centre.tolist() for _ in range(8)])
    # One full tick should be enough to fire
    tick(w, dt=0.001)
    assert len(w.firing_events) >= 1

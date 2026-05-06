"""Tests for R1: recycling regeneration that doesn't saturate the buffer."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import ambient_regeneration


def _make_full_world(n_max: int = 32) -> World:
    """Allocate a world whose vibration buffer is already full."""
    cfg = WorldConfig(
        n_initial_vibrations=n_max,
        n_vibrations_max=n_max,
        box_size=(100.0, 100.0, 100.0),
        lambda_gen=1000.0,
        lambda_dec=1.0,   # target_count = int(1000/1 * 1e6) >> n_max
        rng_seed=42,
    )
    return World(cfg)


def test_recycling_regen_keeps_buffer_size_constant():
    """When buffer is full, regen must displace existing vibrations, not append."""
    w = _make_full_world(n_max=32)
    n_alive_before = int(w.s_alive.sum())
    assert n_alive_before == 32

    for _ in range(100):
        ambient_regeneration(w, dt=1.0 / 60.0)
        assert int(w.s_alive.sum()) <= 32, (
            f"R1 violation: alive count {int(w.s_alive.sum())} exceeded buffer 32"
        )


def test_recycling_regen_picks_far_field_vibrations():
    """The displaced vibration should come from the far field, not from any active region.

    Active region = within 2× r_2 of any existing node. With no nodes, all
    vibrations are 'far field' and any can be picked.
    """
    w = _make_full_world(n_max=32)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_alive[0] = True
    w.k_level[0] = 4
    w.k_count = 1
    w.s_pos[:32] = [50.5, 50.5, 50.5]
    pos_before = w.s_pos[:32].copy()
    for _ in range(20):
        ambient_regeneration(w, dt=1.0 / 60.0)
    moved = np.any(np.abs(w.s_pos[:32] - pos_before) > 1.0, axis=1).sum()
    assert moved == 0, f"R1 violation: {moved} vibrations were displaced from the active region"

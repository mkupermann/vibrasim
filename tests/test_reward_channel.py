"""Tests for RewardChannel (RC1, RC2, RC3)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from agent.reward import RewardChannel


def _make_world():
    return World(WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=64,
        box_size=(60.0, 60.0, 60.0),
        reward_port_origin=(45.0, 45.0, 0.0),
        reward_port_size=(15.0, 15.0, 15.0),
        reward_burst_size=12,
        reward_burst_freq=30000.0,
    ))


def test_RC1_fire_positive_injects_burst_with_positive_polarity():
    w = _make_world()
    rc = RewardChannel(rng=np.random.default_rng(0))
    n_alive_before = int(w.s_alive.sum())
    n = rc.fire_positive(w)
    n_alive_after = int(w.s_alive.sum())
    assert n == 12
    assert n_alive_after == n_alive_before + 12
    new_idx = np.where(w.s_alive)[0]
    pos = w.s_pos[new_idx]
    assert ((pos[:, 0] >= 45) & (pos[:, 0] <= 60)).all()
    assert ((pos[:, 1] >= 45) & (pos[:, 1] <= 60)).all()
    assert ((pos[:, 2] >= 0) & (pos[:, 2] <= 15)).all()
    assert (w.s_freq[new_idx] == 30000.0).all()
    assert (w.s_pol[new_idx] == True).all()
    assert (w.s_reward_polarity[new_idx] == 1).all()


def test_RC2_fire_negative_symmetric_with_negative_polarity():
    w = _make_world()
    rc = RewardChannel(rng=np.random.default_rng(0))
    n = rc.fire_negative(w)
    new_idx = np.where(w.s_alive)[0]
    assert (w.s_pol[new_idx] == False).all()
    assert (w.s_reward_polarity[new_idx] == -1).all()


def test_RC3_is_in_reward_port_bounds():
    rc = RewardChannel()
    assert rc.is_in_reward_port(np.array([47.5, 47.5, 7.5]))   # centre
    assert rc.is_in_reward_port(np.array([45.0, 45.0, 0.0]))   # corner
    assert rc.is_in_reward_port(np.array([60.0, 60.0, 15.0]))  # opposite corner
    assert not rc.is_in_reward_port(np.array([44.9, 47.5, 7.5]))   # outside x
    assert not rc.is_in_reward_port(np.array([47.5, 47.5, 15.1]))  # outside z
    assert not rc.is_in_reward_port(np.array([0.0, 0.0, 0.0]))     # nowhere near

"""G3 — synaptic_post_search_samples extends bridge reach along orientation.

CONCEPT §10.8 candidate amendment 2: synaptic_transmission previously
searched for post-atoms at a single point M + r_bridge * o_unit. Bridges
placed mid-segment in a long source→target diagonal could not reach the
target port atoms at this single-sample distance.

G3 adds cfg.synaptic_post_search_samples (default 1, legacy behaviour).
At N > 1, the post-search samples at distances r_bridge, 2*r_bridge, …,
N*r_bridge along the orientation ray.

G3-1: with samples=1, behaviour identical to pre-amendment (regression).
G3-2: with samples=4, a bridge placed at mid-segment with orientation
      pointing toward a far target port reaches a post-atom in that port,
      where samples=1 cannot.
"""
import numpy as np
import pytest

from world.config import WorldConfig
from world.state import World
from world.physics import synaptic_transmission


def _make_world(samples: int) -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=128, n_nodes_max=64,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        stdp_enabled=True,
        r_bridge=8.0,
        synaptic_transmission_strength=1.0,
        synaptic_transmission_threshold=1.0,
        synaptic_post_search_samples=samples,
    )
    return World(cfg)


def _seed_atom(w: World, idx: int, pos, freq: float = 1000.0):
    w.k_pos[idx] = pos
    w.k_level[idx] = 4
    w.k_alive[idx] = True
    w.k_freq[idx] = freq
    w.k_pol[idx] = (idx % 2 == 0)
    w.k_charge[idx] = 0.0
    w.k_count = max(w.k_count, idx + 1)


def _seed_bridge_molecule(w: World, idx: int, pos, orientation, strength: float = 100.0):
    w.k_pos[idx] = pos
    w.k_level[idx] = 5
    w.k_alive[idx] = True
    w.k_freq[idx] = 1000.0
    w.k_pol[idx] = True
    w.k_strength[idx] = strength
    o = np.asarray(orientation, dtype=np.float64)
    w.k_orientation[idx] = o / np.linalg.norm(o)
    w.k_count = max(w.k_count, idx + 1)


def _seed_aligned_vibration(w: World, idx: int, pos, vel):
    w.s_pos[idx] = pos
    v = np.asarray(vel, dtype=np.float64)
    w.s_vel[idx] = v / np.linalg.norm(v) * 5.0
    w.s_alive[idx] = True
    w.s_freq[idx] = 1000.0
    w.s_pol[idx] = True
    if idx >= w.n_alive:
        w.n_alive = idx + 1


def test_G3_samples_1_preserves_legacy_behaviour():
    """samples=1 ↔ exactly one sample at distance r_bridge (regression check)."""
    w = _make_world(samples=1)

    bridge_pos = (30.0, 30.0, 30.0)
    o_unit = np.array([1.0, 0.0, 0.0])
    _seed_bridge_molecule(w, 0, bridge_pos, o_unit, strength=100.0)
    # Post atom at r_bridge ahead — should be found
    _seed_atom(w, 1, (38.0, 30.0, 30.0))
    # Post atom at 3 × r_bridge ahead — should NOT be found (samples=1)
    _seed_atom(w, 2, (54.0, 30.0, 30.0))

    _seed_aligned_vibration(w, 0, (29.0, 30.0, 30.0), (1.0, 0.0, 0.0))

    n_events = synaptic_transmission(w, dt=1.0 / 60)
    assert n_events == 1, f"samples=1: expected 1 deposit event, got {n_events}"
    assert w.k_charge[1] > 0, "samples=1: near post-atom should have received charge"
    assert w.k_charge[2] == 0, "samples=1: far post-atom must NOT have received charge"


def test_G3_samples_4_reaches_far_target():
    """samples=4 reaches a post-atom at distance 3*r_bridge that samples=1 can't."""
    w = _make_world(samples=4)

    bridge_pos = (30.0, 30.0, 30.0)
    o_unit = np.array([1.0, 0.0, 0.0])
    _seed_bridge_molecule(w, 0, bridge_pos, o_unit, strength=100.0)
    # ONLY a far post-atom — no near one. samples=1 wouldn't find it; samples=4 does.
    _seed_atom(w, 1, (54.0, 30.0, 30.0))  # at distance 3 * r_bridge = 24

    _seed_aligned_vibration(w, 0, (29.0, 30.0, 30.0), (1.0, 0.0, 0.0))

    n_events = synaptic_transmission(w, dt=1.0 / 60)
    assert n_events >= 1, f"samples=4: expected ≥1 deposit event, got {n_events}"
    assert w.k_charge[1] > 0, (
        "samples=4: far post-atom should have received charge via extended search"
    )


def test_G3_samples_4_default_off_via_default_config():
    """Default cfg.synaptic_post_search_samples is 1 — behaviour unchanged."""
    cfg = WorldConfig()
    assert cfg.synaptic_post_search_samples == 1, (
        f"G3 default must be 1 (legacy); got {cfg.synaptic_post_search_samples}"
    )

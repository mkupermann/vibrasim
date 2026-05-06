"""Plan A.5 JIT correctness tests (AP7-AP11)."""
import numpy as np
import pytest
from dataclasses import replace
from world.config import WorldConfig
from world.state import World
from world.physics import decay_unstable_nodes, decay_high_level_nodes, move_nodes


def _build_test_world(jit: bool, rng_seed: int = 42):
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=4, n_nodes_max=128,
        box_size=(100.0, 100.0, 100.0), rng_seed=rng_seed,
        slot_recycling_enabled=False,  # isolate JIT effects
        numba_jit_enabled=jit,
        pair_decay_time=2.0, triad_decay_time=10.0,
    )
    return World(cfg)


def _populate_nodes(w, n=50, level=2):
    for i in range(n):
        w.k_pos[i] = w.rng.uniform(0, 100, size=3)
        w.k_vel[i] = w.rng.uniform(-1, 1, size=3)
        w.k_freq[i] = 1000.0 + i
        w.k_pol[i] = bool(i % 2)
        w.k_level[i] = level
        w.k_alive[i] = True
        w.k_birth[i] = 0.0
        w.k_comp_offset[i] = 0
        w.k_comp_offset[i + 1] = 0
    w.k_count = n


def test_AP7_decay_unstable_nodes_jit_matches_python():
    """JIT and Python paths must produce identical k_alive after one tick
    given the same RNG seed."""
    w_py = _build_test_world(jit=False, rng_seed=42)
    _populate_nodes(w_py, n=50, level=2)
    w_py.t = 5.0  # so age=5 > tau=2, decay probability is meaningful
    decay_unstable_nodes(w_py, dt=0.1)

    w_jit = _build_test_world(jit=True, rng_seed=42)
    _populate_nodes(w_jit, n=50, level=2)
    w_jit.t = 5.0
    decay_unstable_nodes(w_jit, dt=0.1)

    assert np.array_equal(w_py.k_alive, w_jit.k_alive), (
        f"JIT and Python differ. py: {int(w_py.k_alive[:50].sum())} alive, "
        f"jit: {int(w_jit.k_alive[:50].sum())} alive"
    )


def test_AP8_decay_high_level_nodes_jit_matches_python():
    """JIT and Python paths must produce identical k_alive after one decay
    tick on level-5+ molecules, given the same RNG seed."""
    cfg_kwargs = dict(lambda_dec_mol=0.5)  # aggressive enough to drive multiple decays
    w_py = _build_test_world(jit=False, rng_seed=42)
    w_py.config = replace(w_py.config, **cfg_kwargs)
    _populate_nodes(w_py, n=50, level=5)
    w_py.k_strength[:50] = w_py.rng.uniform(1.0, 50.0, size=50)
    decay_high_level_nodes(w_py, dt=0.01)

    w_jit = _build_test_world(jit=True, rng_seed=42)
    w_jit.config = replace(w_jit.config, **cfg_kwargs)
    _populate_nodes(w_jit, n=50, level=5)
    w_jit.k_strength[:50] = w_jit.rng.uniform(1.0, 50.0, size=50)
    decay_high_level_nodes(w_jit, dt=0.01)

    assert np.array_equal(w_py.k_alive, w_jit.k_alive), (
        f"JIT and Python differ. py: {int(w_py.k_alive[:50].sum())} alive, "
        f"jit: {int(w_jit.k_alive[:50].sum())} alive"
    )


def test_AP9_move_nodes_jit_matches_python():
    """JIT and Python paths must produce identical k_pos after one move tick.

    No RNG involved; pure numerical equality (within float64 tolerance)
    is the right assertion."""
    w_py = _build_test_world(jit=False, rng_seed=42)
    _populate_nodes(w_py, n=100, level=4)
    move_nodes(w_py, dt=0.01)

    w_jit = _build_test_world(jit=True, rng_seed=42)
    _populate_nodes(w_jit, n=100, level=4)
    move_nodes(w_jit, dt=0.01)

    assert np.allclose(w_py.k_pos, w_jit.k_pos, rtol=1e-12, atol=1e-12), (
        "JIT and Python move_nodes paths produce different k_pos"
    )

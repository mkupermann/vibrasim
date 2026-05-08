"""G1 — JIT bind_vibrations_to_electrons via candidate-batch refactor.

Mirrors the A.5 AP-style equivalence pattern: with the same RNG seed and the
same WorldConfig, a World run with `numba_jit_enabled=True` produces the same
structure-count trajectory as the legacy Python path.

The Python path is materially slower per tick once K grows (the legacy
`break`-per-i loop pays Python overhead for every neighbour scan), so this
test runs at a small scope where the binding chain fires a handful of times
in both paths and exact-count equality is checkable in seconds.
"""
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick


def _make_config(numba_jit_enabled: bool) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=200, n_vibrations_max=512, n_nodes_max=1024,
        box_size=(40.0, 40.0, 40.0),
        rng_seed=42,
        numba_jit_enabled=numba_jit_enabled,
        slot_recycling_enabled=True,
    )


def _run_n_ticks(cfg: WorldConfig, n_ticks: int) -> dict:
    w = World(cfg)
    for _ in range(n_ticks):
        tick(w, cfg.dt)
    return {
        "n_alive": int(w.n_alive),
        "K": int(w.k_count),
        "n_electrons": int(((w.k_level == 1) & w.k_alive).sum()),
        "n_pairs": int(((w.k_level == 2) & w.k_alive).sum()),
        "n_triads": int(((w.k_level == 3) & w.k_alive).sum()),
        "n_atoms": int(((w.k_level == 4) & w.k_alive).sum()),
    }


def test_G1_equivalence_jit_vs_python_short():
    """Same RNG seed → identical structure counts after 30 ticks (JIT vs Python).

    Short scope (30 ticks) keeps the Python path tractable while exercising
    bind_vibrations_to_electrons enough that any divergence in the JIT
    candidate-filter would show up. Both paths share the same upstream
    candidate-list build (grid-based) so the iteration order is identical
    and exact-count equality holds.
    """
    n_ticks = 30
    state_jit = _run_n_ticks(_make_config(True), n_ticks)
    state_py = _run_n_ticks(_make_config(False), n_ticks)

    assert state_jit["K"] == state_py["K"], (
        f"K diverges: jit={state_jit['K']}, python={state_py['K']}"
    )
    for key in ("n_electrons", "n_pairs", "n_triads", "n_atoms"):
        assert state_jit[key] == state_py[key], (
            f"{key} diverges: jit={state_jit[key]}, python={state_py[key]}"
        )
    # Sanity: the binding chain actually fired in this window.
    assert state_jit["n_electrons"] > 0, (
        f"binding never fired in 30 ticks (jit) — test config may be too sparse: "
        f"electrons={state_jit['n_electrons']}, K={state_jit['K']}"
    )

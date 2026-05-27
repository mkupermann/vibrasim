"""BET-084 — Molecular Chain Formation from substrate physics.

Pre-registered bars (docs/amendments/bet_084_molecular_chains.md):
  T84a  >= 10 atoms (level 4) in 60s
  T84b  >= 5 molecules (level >= 5) in 120s
  T84c  >= 1 structure at level >= 8 in 300s
  T84d  max level at 300s > max level at 120s
  T84e  total alive nodes < n_nodes_max * 0.9 at all times
"""
import pytest
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def _make_dense_world():
    """Dense world optimized for chain formation."""
    cfg = WorldConfig(
        n_initial_vibrations=2000,
        box_size=(30.0, 30.0, 30.0),
        r_1=8.0,
        r_2=12.0,
        freq_tolerance=0.008,
        pair_decay_time=3.0,
        triad_decay_time=20.0,
        mol_fusion_enabled=True,
        n_nodes_max=4096,
        n_vibrations_max=8192,
        lambda_gen=0.001,   # regenerate vibrations
        lambda_dec=0.0,     # no ambient decay
        rng_seed=42,
    )
    return World(cfg)


def _count_by_level(world):
    """Return dict: level -> count of alive nodes at that level."""
    K = world.k_count
    if K == 0:
        return {}
    alive = world.k_alive[:K]
    levels = world.k_level[:K]
    counts = {}
    for lvl in range(1, 33):
        c = int(np.sum(alive & (levels == lvl)))
        if c > 0:
            counts[lvl] = c
    return counts


def _max_level(world):
    K = world.k_count
    if K == 0:
        return 0
    alive_levels = world.k_level[:K][world.k_alive[:K]]
    return int(alive_levels.max()) if len(alive_levels) > 0 else 0


@pytest.mark.slow
def test_T84_chain_formation():
    """Full BET-084: 300s simulation, check chain formation."""
    world = _make_dense_world()
    dt = world.config.dt
    max_nodes_ever = 0

    # Phase 1: 60s — atoms should form
    steps_60 = int(60.0 / dt)
    for _ in range(steps_60):
        tick(world, dt)
        alive_count = int(np.sum(world.k_alive[:world.k_count]))
        max_nodes_ever = max(max_nodes_ever, alive_count)

    counts_60 = _count_by_level(world)
    n_atoms_60 = counts_60.get(4, 0)
    print(f"\n60s: {counts_60}")
    print(f"  Atoms: {n_atoms_60}")

    # T84a
    assert n_atoms_60 >= 10, f"T84a FAIL: {n_atoms_60} atoms < 10"

    # Phase 2: 120s — molecules should form
    steps_120 = int(60.0 / dt)  # another 60s
    for _ in range(steps_120):
        tick(world, dt)
        alive_count = int(np.sum(world.k_alive[:world.k_count]))
        max_nodes_ever = max(max_nodes_ever, alive_count)

    counts_120 = _count_by_level(world)
    n_mol_120 = sum(v for k, v in counts_120.items() if k >= 5)
    max_level_120 = _max_level(world)
    print(f"\n120s: {counts_120}")
    print(f"  Molecules (>=5): {n_mol_120}, max level: {max_level_120}")

    # T84b
    assert n_mol_120 >= 5, f"T84b FAIL: {n_mol_120} molecules < 5"

    # Phase 3: 300s — chains should form
    steps_300 = int(180.0 / dt)  # another 180s
    for _ in range(steps_300):
        tick(world, dt)
        alive_count = int(np.sum(world.k_alive[:world.k_count]))
        max_nodes_ever = max(max_nodes_ever, alive_count)

    counts_300 = _count_by_level(world)
    max_level_300 = _max_level(world)
    n_chains = sum(v for k, v in counts_300.items() if k >= 8)
    print(f"\n300s: {counts_300}")
    print(f"  Chains (>=8): {n_chains}, max level: {max_level_300}")

    # T84c
    assert n_chains >= 1, f"T84c FAIL: no structures at level >= 8"

    # T84d
    assert max_level_300 > max_level_120, \
        f"T84d FAIL: max level didn't grow ({max_level_300} <= {max_level_120})"

    # T84e
    assert max_nodes_ever < world.config.n_nodes_max * 0.9, \
        f"T84e FAIL: nodes peaked at {max_nodes_ever} >= {world.config.n_nodes_max * 0.9}"

    print(f"\nBET-084 ALL BARS PASSED")
    print(f"  Max level reached: {max_level_300}")
    print(f"  Peak nodes: {max_nodes_ever}")


def test_T84_smoke():
    """Quick 10s smoke test — verify fusion machinery works."""
    world = _make_dense_world()
    dt = world.config.dt

    for _ in range(int(10.0 / dt)):
        tick(world, dt)

    counts = _count_by_level(world)
    print(f"\n10s smoke: {counts}")
    # Should have at least some electrons
    assert counts.get(1, 0) > 0 or counts.get(2, 0) > 0 or counts.get(4, 0) > 0, \
        "Smoke FAIL: no binding at all"

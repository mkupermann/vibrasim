"""R-15 substrate snapshot persistence + interval emission.

Pre-registered acceptance from R-15 in ``.eqmod/autopilot/QUEUE.yaml``:

  * ``test_roundtrip_preserves_substrate_state``  PASSES
  * ``test_snapshot_emits_at_configured_interval``  PASSES

The roundtrip test saves a synthetic substrate (populated Quanta, Nodes,
Bridges, and a non-trivial Grid temperature field) to ``.npz``, reloads
it, asserts every SoA array is bit-identical, then runs one
``dynamics.tick`` against both copies and asserts the post-tick state is
also bit-identical — confirming the loaded substrate reproduces the
dynamics of the saved one.

The interval-emit test drives the encoder-free training runner for 500
ticks with ``EQMOD_SNAPSHOT_EVERY_TICKS=100`` and asserts exactly 5
snapshots land in the configured ``EQMOD_SNAPSHOT_OUT_DIR`` at ticks
``{100, 200, 300, 400, 500}``. ``input_kind="no_input"`` is used so the
test does not depend on the R-7 corpus manifest.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from agent.flux.snapshot import (
    SNAPSHOT_FORMAT_VERSION,
    load_substrate_snapshot,
    save_substrate_snapshot,
)
from world.flux import dynamics
from world.flux.binding import BindingConfig
from world.flux.bridges import Bridges
from world.flux.decay import DecayConfig
from world.flux.grid import Grid
from world.flux.plasticity import PlasticityConfig
from world.flux.quantum import Quanta
from world.flux.structures import Nodes
from world.flux.thermal import ThermalConfig


def _build_substrate(seed: int = 13) -> tuple[Quanta, Nodes, Bridges, Grid, int]:
    rng = np.random.default_rng(seed)

    quanta = Quanta(max_quanta=128)
    for _ in range(20):
        quanta.add(
            pos=rng.random(3).tolist(),
            vel=rng.normal(size=3).tolist(),
            freq=float(rng.uniform(1.0, 9.0)),
            polarity=int(rng.choice([-1, 1])),
            energy=float(rng.uniform(0.1, 1.0)),
        )

    nodes = Nodes(max_nodes=32)
    node_slots = []
    for _ in range(6):
        s = nodes.add(
            pos=rng.random(3).tolist(),
            energy=float(rng.uniform(0.5, 1.5)),
            freq=float(rng.uniform(1.0, 9.0)),
            born_tick=int(rng.integers(0, 100)),
        )
        node_slots.append(s)
    # Exercise the alive mask + _next_search cursor.
    nodes.remove(node_slots[2])

    bridges = Bridges(max_bridges=64)
    alive_node_slots = [s for s in node_slots if nodes.alive[s]]
    for _ in range(10):
        src = int(rng.choice(alive_node_slots))
        dst = int(rng.choice(alive_node_slots))
        bridges.add(
            src=src, dst=dst,
            weight=float(rng.uniform(0.1, 2.0)),
            born_tick=int(rng.integers(0, 100)),
        )

    grid = Grid(dims=(4, 3, 2), voxel_size=0.5, T_smoothing=0.2)
    grid.T = rng.random(grid.dims).astype(np.float64)

    return quanta, nodes, bridges, grid, 4242


def _one_tick(
    quanta: Quanta, nodes: Nodes, bridges: Bridges, grid: Grid,
    tick: int, rng_seed: int = 7,
) -> None:
    binding_cfg = BindingConfig(
        alpha=4.0, beta=4.0, T_crit=2.0, eta=0.1, r=1.5,
        coherence_eps=1.0, r_bridge=2.0, bridge_w0=1.0,
    )
    decay_cfg = DecayConfig(gamma=500.0, T_decay_crit=0.035)
    plasticity_cfg = PlasticityConfig(
        gamma=0.1, lam=0.1, flux_min=1.0, w_min=0.05, r_flux=0.75,
    )
    thermal_cfg = ThermalConfig(
        buoyancy_g=2.0, damping_mu=0.5, T_ref=0.0,
        T_hot_floor=5.0, T_cold_ceiling=0.0, pressure_coeff=1.0,
    )
    rng = np.random.default_rng(rng_seed)
    dynamics.tick(
        quanta=quanta, grid=grid, dt=0.1, injector=None,
        nodes=nodes, binding_cfg=binding_cfg, decay_cfg=decay_cfg,
        bridges=bridges, plasticity_cfg=plasticity_cfg,
        thermal_cfg=thermal_cfg, rng=rng, tick_index=tick,
    )


def test_roundtrip_preserves_substrate_state(tmp_path: Path) -> None:
    q1, n1, b1, g1, tick = _build_substrate()
    path = tmp_path / "snap.npz"
    saved = save_substrate_snapshot(path, q1, n1, b1, g1, tick)
    assert saved == path
    assert path.is_file(), "save_substrate_snapshot did not write the file"

    q2, n2, b2, g2, tick2 = load_substrate_snapshot(path)

    assert tick2 == tick

    # --- Quanta: every SoA array bit-identical, plus container scalars ---
    np.testing.assert_array_equal(q1.pos, q2.pos)
    np.testing.assert_array_equal(q1.vel, q2.vel)
    np.testing.assert_array_equal(q1.freq, q2.freq)
    np.testing.assert_array_equal(q1.polarity, q2.polarity)
    np.testing.assert_array_equal(q1.energy, q2.energy)
    np.testing.assert_array_equal(q1.alive, q2.alive)
    assert q2.max_quanta == q1.max_quanta
    assert q2._next_search == q1._next_search

    # --- Nodes ---
    np.testing.assert_array_equal(n1.pos, n2.pos)
    np.testing.assert_array_equal(n1.energy, n2.energy)
    np.testing.assert_array_equal(n1.freq, n2.freq)
    np.testing.assert_array_equal(n1.born_tick, n2.born_tick)
    np.testing.assert_array_equal(n1.alive, n2.alive)
    assert n2.max_nodes == n1.max_nodes
    assert n2._next_search == n1._next_search

    # --- Bridges ---
    np.testing.assert_array_equal(b1.src, b2.src)
    np.testing.assert_array_equal(b1.dst, b2.dst)
    np.testing.assert_array_equal(b1.weight, b2.weight)
    np.testing.assert_array_equal(b1.last_flux_tick, b2.last_flux_tick)
    np.testing.assert_array_equal(b1.alive, b2.alive)
    assert b2.max_bridges == b1.max_bridges
    assert b2._next_search == b1._next_search

    # --- Grid ---
    assert g2.dims == g1.dims
    assert g2.voxel_size == g1.voxel_size
    assert g2.T_smoothing == g1.T_smoothing
    np.testing.assert_array_equal(g1.T, g2.T)

    # --- Dynamics reproduces: one tick on each copy must yield the same
    # post-state, proving the saved snapshot fully captures simulation
    # state (not just the obvious arrays).
    _one_tick(q1, n1, b1, g1, tick)
    _one_tick(q2, n2, b2, g2, tick)
    np.testing.assert_array_equal(q1.pos, q2.pos)
    np.testing.assert_array_equal(q1.energy, q2.energy)
    np.testing.assert_array_equal(q1.alive, q2.alive)
    np.testing.assert_array_equal(n1.energy, n2.energy)
    np.testing.assert_array_equal(n1.alive, n2.alive)
    np.testing.assert_array_equal(b1.weight, b2.weight)
    np.testing.assert_array_equal(b1.alive, b2.alive)
    np.testing.assert_array_equal(g1.T, g2.T)


def test_snapshot_emits_at_configured_interval(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("EQMOD_SNAPSHOT_EVERY_TICKS", "100")
    monkeypatch.setenv("EQMOD_SNAPSHOT_OUT_DIR", str(tmp_path))

    # Imported lazily so monkeypatched env is read on each test invocation.
    from agent.flux.encoder_free_training import (
        EncoderFreeTrainingConfig,
        run_encoder_free_training,
    )

    cfg = EncoderFreeTrainingConfig(
        n_ticks_train=500,
        babble_n_samples=16,  # minimum 1 tick of babble — keep the test fast
        grid_dims=(8, 8, 4),
        max_quanta=2_000,
        max_nodes=200,
        max_bridges=2_000,
    )
    run_encoder_free_training(cfg, input_kind="no_input")

    files = sorted(tmp_path.glob("snapshot_tick_*.npz"))
    assert len(files) == 5, (
        f"expected 5 snapshots at ticks {{100,200,300,400,500}}, "
        f"got {len(files)}: {[f.name for f in files]}"
    )

    actual_ticks = set()
    for f in files:
        # filename: snapshot_tick_00000100.npz
        actual_ticks.add(int(f.stem.split("_")[-1]))
    assert actual_ticks == {100, 200, 300, 400, 500}, (
        f"snapshot tick set {sorted(actual_ticks)} != "
        "expected {100, 200, 300, 400, 500}"
    )

    # Sanity: every emitted file is a valid snapshot of the declared format.
    sample = np.load(files[0])
    assert int(sample["format_version"]) == SNAPSHOT_FORMAT_VERSION
    assert int(sample["tick"]) == 100

"""Substrate snapshot persistence (R-15 infrastructure).

Save and reload a flux substrate's full state — Quanta + Nodes + Bridges
+ Grid + tick counter — to a single ``.npz`` file. Round-trip is
bit-identical for all SoA arrays so loaded substrate dynamics reproduce
the saved state exactly. Internal ``_next_search`` cursors are preserved
so subsequent ``add`` calls hit the same free slots in the same order.

Pre-registered for R-15 in
``docs/superpowers/plans/2026-05-19-flux-encoder-free-iter2.md`` (R-LR-8
infrastructure): snapshots are emitted at a configurable cadence during
``agent.flux.encoder_free_training.run_encoder_free_training`` to enable
offline bridge-spectrum analysis without re-running the long substrate.

Env-var contract:
    EQMOD_SNAPSHOT_EVERY_TICKS : positive int → emit cadence; 0 / unset = off
    EQMOD_SNAPSHOT_OUT_DIR     : directory path → required when emission is on

Filename convention: ``snapshot_tick_<8-digit-zero-padded-tick>.npz``.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from world.flux.bridges import Bridges
from world.flux.grid import Grid
from world.flux.quantum import Quanta
from world.flux.structures import Nodes


SNAPSHOT_FORMAT_VERSION = 1
SNAPSHOT_FILENAME_TEMPLATE = "snapshot_tick_{tick:08d}.npz"


def snapshot_filename(out_dir: Path, tick: int) -> Path:
    """Canonical snapshot path for a given tick."""
    return Path(out_dir) / SNAPSHOT_FILENAME_TEMPLATE.format(tick=int(tick))


def save_substrate_snapshot(
    path: str | Path,
    quanta: Quanta,
    nodes: Nodes,
    bridges: Bridges,
    grid: Grid,
    tick: int,
) -> Path:
    """Write substrate state to ``path`` as ``.npz``; return the path written."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        p,
        format_version=np.int64(SNAPSHOT_FORMAT_VERSION),
        tick=np.int64(tick),
        # Quanta SoA
        q_pos=quanta.pos,
        q_vel=quanta.vel,
        q_freq=quanta.freq,
        q_polarity=quanta.polarity,
        q_energy=quanta.energy,
        q_alive=quanta.alive,
        q_max=np.int64(quanta.max_quanta),
        q_next_search=np.int64(quanta._next_search),
        # Nodes SoA
        n_pos=nodes.pos,
        n_energy=nodes.energy,
        n_freq=nodes.freq,
        n_born_tick=nodes.born_tick,
        n_alive=nodes.alive,
        n_max=np.int64(nodes.max_nodes),
        n_next_search=np.int64(nodes._next_search),
        # Bridges SoA
        b_src=bridges.src,
        b_dst=bridges.dst,
        b_weight=bridges.weight,
        b_last_flux_tick=bridges.last_flux_tick,
        b_alive=bridges.alive,
        b_max=np.int64(bridges.max_bridges),
        b_next_search=np.int64(bridges._next_search),
        # Grid
        g_dims=np.asarray(grid.dims, dtype=np.int64),
        g_voxel_size=np.float64(grid.voxel_size),
        g_T_smoothing=np.float64(grid.T_smoothing),
        g_T=grid.T,
    )
    return p


def load_substrate_snapshot(
    path: str | Path,
) -> tuple[Quanta, Nodes, Bridges, Grid, int]:
    """Read snapshot ``.npz``; return ``(quanta, nodes, bridges, grid, tick)``.

    All SoA arrays and internal ``_next_search`` cursors are restored
    bit-identical to the saved state.
    """
    with np.load(str(path)) as f:
        version = int(f["format_version"])
        if version != SNAPSHOT_FORMAT_VERSION:
            raise ValueError(
                f"snapshot format_version={version} != "
                f"expected {SNAPSHOT_FORMAT_VERSION}; refusing to load"
            )

        quanta = Quanta(max_quanta=int(f["q_max"]))
        quanta.pos[:] = f["q_pos"]
        quanta.vel[:] = f["q_vel"]
        quanta.freq[:] = f["q_freq"]
        quanta.polarity[:] = f["q_polarity"]
        quanta.energy[:] = f["q_energy"]
        quanta.alive[:] = f["q_alive"]
        quanta._next_search = int(f["q_next_search"])

        nodes = Nodes(max_nodes=int(f["n_max"]))
        nodes.pos[:] = f["n_pos"]
        nodes.energy[:] = f["n_energy"]
        nodes.freq[:] = f["n_freq"]
        nodes.born_tick[:] = f["n_born_tick"]
        nodes.alive[:] = f["n_alive"]
        nodes._next_search = int(f["n_next_search"])

        bridges = Bridges(max_bridges=int(f["b_max"]))
        bridges.src[:] = f["b_src"]
        bridges.dst[:] = f["b_dst"]
        bridges.weight[:] = f["b_weight"]
        bridges.last_flux_tick[:] = f["b_last_flux_tick"]
        bridges.alive[:] = f["b_alive"]
        bridges._next_search = int(f["b_next_search"])

        dims = tuple(int(x) for x in f["g_dims"])
        grid = Grid(
            dims=dims,
            voxel_size=float(f["g_voxel_size"]),
            T_smoothing=float(f["g_T_smoothing"]),
        )
        grid.T[:] = f["g_T"]

        tick = int(f["tick"])
    return quanta, nodes, bridges, grid, tick


def get_snapshot_settings() -> tuple[int, Path | None]:
    """Read ``EQMOD_SNAPSHOT_EVERY_TICKS`` + ``EQMOD_SNAPSHOT_OUT_DIR`` from env.

    Returns ``(every_ticks, out_dir)``. ``every_ticks=0`` means emission is
    disabled. When emission is enabled (``every_ticks > 0``), an empty
    ``EQMOD_SNAPSHOT_OUT_DIR`` is treated as a misconfiguration and
    ``out_dir`` is returned as ``None`` so the caller can short-circuit.
    """
    raw = os.environ.get("EQMOD_SNAPSHOT_EVERY_TICKS", "0").strip()
    try:
        every = int(raw)
    except ValueError:
        every = 0
    if every < 0:
        every = 0
    out_dir_str = os.environ.get("EQMOD_SNAPSHOT_OUT_DIR", "").strip()
    out_dir: Path | None = Path(out_dir_str) if out_dir_str else None
    return every, out_dir

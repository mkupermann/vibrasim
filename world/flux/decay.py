"""Node decay — minimal F1a form.

Per spec §5.4 ("Decay"), nodes whose local environment is hot dissociate.
The full spec version ties decay to bridge-flux (F1b mechanic): a node
loses bridges when flux drops, and dissociates when it has no bridges.
F1a has no bridges, so decay is driven directly by T_local instead.

This minimal form was added in F1a (not deferred to F1b) because T3 needs
hot-zone nodes to dissociate or floor-binding accumulates without bound
and the crystallisation ratio never exceeds 1.0. See
`docs/flux/phase-log.md` 2026-05-11 entry for the calibration record.

Decay rule:
    p_decay = sigmoid(gamma * (T_local - T_decay_crit))

When T_local >> T_decay_crit (hot voxel), decay is likely.
When T_local << T_decay_crit (cold voxel), decay is rare.

Energy accounting:
- A decaying node's energy is exported as decay heat (leaves the system,
  parallel to absorption at cold faces and binding η-export).
- The auditor records this via `record_decay_heat`.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass

from world.flux.grid import Grid
from world.flux.structures import Nodes


@dataclass
class DecayConfig:
    """Tunable parameters of the node decay rule.

    F1a defaults are the values that make T3 pass; record any change in
    `docs/flux/phase-log.md` so F1b can pick up the calibration.
    """
    gamma: float = 100.0         # gain on T-excess
    T_decay_crit: float = 0.02   # threshold T above which decay fires


def decay_probability(T_local: float, cfg: DecayConfig) -> float:
    """p_decay = sigmoid(gamma * (T_local - T_decay_crit))."""
    x = cfg.gamma * (T_local - cfg.T_decay_crit)
    if x >= 0:
        return 1.0 / (1.0 + np.exp(-x))
    ex = np.exp(x)
    return ex / (1.0 + ex)


def attempt_decay(nodes: Nodes, grid: Grid, cfg: DecayConfig,
                  rng: np.random.Generator) -> float:
    """Run one tick's decay pass.

    For each alive node, read the ALTITUDE-MEAN T (mean of grid.T over
    the node's xy-layer at its z-voxel). Using a layer-mean instead of
    a per-voxel T smooths over the spatial sparseness of injection: a
    cold pocket inside the hot floor is still surrounded by warm
    neighbours, and a node there is still in a thermally-active region.
    Per-voxel T failed to differentiate floor from ceiling in T3
    sweeps because injection only touches ~5% of floor voxels per
    tick. The layer-mean is the F1a proxy for spec §5.4's
    bridge-flux-based decay; the bridge mechanism (F1b) will replace
    it. See `docs/flux/phase-log.md` 2026-05-11 entry.

    For each node:
      - read T_layer = mean(grid.T[:, :, iz])
      - sample uniform against decay_probability(T_layer)
      - if decay fires, remove node and add energy to returned heat

    Returns total decay heat exported this tick. Caller records into
    the auditor.
    """
    if nodes.n_alive() == 0:
        return 0.0
    # Pre-compute per-layer mean T once per tick
    T_layer = grid.T.mean(axis=(0, 1))  # shape (Lz,)
    total_heat = 0.0
    alive_idx = np.where(nodes.alive)[0]
    for slot in alive_idx:
        cx, cy, cz = nodes.pos[slot]
        ix, iy, iz = grid.pos_to_voxel((cx, cy, cz))
        T_local = float(T_layer[iz])
        p = decay_probability(T_local, cfg)
        if rng.random() < p:
            e = nodes.remove(int(slot))
            total_heat += e
    return total_heat

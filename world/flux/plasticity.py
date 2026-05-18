"""Plasticity — Hebbian-with-flux rules + bridge pruning + node dissociation.

Per spec §5.5:
    w(t+1) = w(t) + γ * flux_through(t)
    w(t+1) -= λ * max(0, flux_min - flux_through(t))

Bridges with weight < w_min are removed. Nodes that no longer appear
as src or dst of any alive bridge are dissociated; their energy is
returned to the export channel (decay heat).

This module replaces the F1a `decay.py` T-based stub.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass

from world.flux.bridges import Bridges
from world.flux.structures import Nodes
from world.flux.quantum import Quanta


@dataclass
class PlasticityConfig:
    """Tunable parameters of the Hebbian plasticity + decay rules.

    gamma: strengthening rate per unit flux.
    lam:   decay rate when flux is below flux_min.
    flux_min: bridge-flux threshold under which decay applies.
    w_min: bridge breakage threshold.
    r_flux: half-thickness of the bridge "tube" used to count quanta
            passing through.
    """
    gamma: float = 0.1
    lam: float = 0.1
    flux_min: float = 1.0
    w_min: float = 0.05
    r_flux: float = 0.75


def count_flux_through(bridges: Bridges, nodes: Nodes,
                        quanta: Quanta, cfg: PlasticityConfig) -> np.ndarray:
    """Return shape (max_bridges,) of int flux counts.

    For each alive bridge connecting nodes (a, b), count alive quanta
    whose perpendicular distance to the line-segment ab is < r_flux.
    A self-bridge (a == b) counts quanta within r_flux of the node's
    position (sphere test).

    Naive O(N_quanta * N_bridges_alive) — fine at F1b scale.
    """
    flux = np.zeros(bridges.max_bridges, dtype=np.int64)
    if bridges.n_alive() == 0 or quanta.n_alive() == 0:
        return flux
    qp = quanta.pos[quanta.alive]  # (Nq, 3)
    r2 = cfg.r_flux * cfg.r_flux
    alive_brs = np.where(bridges.alive)[0]
    for slot in alive_brs:
        src = int(bridges.src[slot])
        dst = int(bridges.dst[slot])
        # Both endpoints must be alive nodes
        if not (nodes.alive[src] and nodes.alive[dst]):
            continue
        a = nodes.pos[src]
        b = nodes.pos[dst]
        if src == dst:
            # Self-bridge: sphere around the node
            diff = qp - a
            d2 = (diff * diff).sum(axis=-1)
            flux[slot] = int((d2 < r2).sum())
            continue
        # Segment ab: foot-of-perpendicular distance from each quantum
        ab = b - a
        ab_len2 = float((ab * ab).sum())
        if ab_len2 == 0.0:
            # Degenerate (shouldn't happen unless coincident nodes)
            diff = qp - a
            d2 = (diff * diff).sum(axis=-1)
            flux[slot] = int((d2 < r2).sum())
            continue
        # t = clamp(((qp - a) · ab) / |ab|^2, 0, 1)
        ap = qp - a
        t = (ap @ ab) / ab_len2
        t = np.clip(t, 0.0, 1.0)
        # closest point on segment
        cp = a + t[:, None] * ab
        diff = qp - cp
        d2 = (diff * diff).sum(axis=-1)
        flux[slot] = int((d2 < r2).sum())
    return flux


def apply_plasticity(bridges: Bridges, flux_counts: np.ndarray,
                      cfg: PlasticityConfig, tick_index: int,
                      *, activation_field=None, nodes=None) -> None:
    """In-place update of bridge weights per spec §5.5.

    Default (F1b) rule:
        w_new = w_old + gamma * flux - lam * max(0, flux_min - flux)

    R-12 spec §5.8 extension (opt-in via `activation_field`): the
    strengthening term is multiplied by the bridge-endpoint coincidence
    read-out:

        w_new = w_old + gamma * flux * coincidence(i, j)
                       - lam * max(0, flux_min - flux)

    where coincidence is in [0, ~1] in practice. Bridges between voxels
    that are both active learn faster; bridges between silent voxels
    near-not at all. The decay term is unchanged — the field smooths
    the *signal*, not the silence.

    If `activation_field` is None (the F1b path), behaviour is bit-for-
    bit identical to the pre-R-12 rule. `nodes` is only required when
    `activation_field` is given (to look up bridge-endpoint positions).
    """
    alive = bridges.alive
    if not alive.any():
        return
    f = flux_counts.astype(np.float64)
    strengthen = cfg.gamma * f
    if activation_field is not None:
        if nodes is None:
            raise ValueError(
                "apply_plasticity: nodes required when activation_field "
                "is provided (need bridge-endpoint positions for the "
                "coincidence read-out)"
            )
        coincidence = _bridge_coincidence(bridges, nodes, activation_field)
        strengthen = strengthen * coincidence
    deficit = np.maximum(0.0, cfg.flux_min - f)
    decay = cfg.lam * deficit
    delta = strengthen - decay
    bridges.weight[alive] += delta[alive]
    # last_flux_tick: mark where flux was nonzero this tick
    had_flux = alive & (f > 0)
    bridges.last_flux_tick[had_flux] = int(tick_index)


def _bridge_coincidence(bridges: Bridges, nodes: Nodes,
                         activation_field) -> np.ndarray:
    """Per-bridge coincidence array (shape: max_bridges).

    Dead bridges and bridges with dead endpoints get coincidence 0
    (they don't enter the update anyway).
    """
    out = np.zeros(bridges.max_bridges, dtype=np.float64)
    alive_idx = np.where(bridges.alive)[0]
    if alive_idx.size == 0:
        return out
    src_slots = bridges.src[alive_idx]
    dst_slots = bridges.dst[alive_idx]
    src_alive = nodes.alive[src_slots]
    dst_alive = nodes.alive[dst_slots]
    valid = src_alive & dst_alive
    if not valid.any():
        return out
    valid_idx = alive_idx[valid]
    src_pos = nodes.pos[bridges.src[valid_idx]]
    dst_pos = nodes.pos[bridges.dst[valid_idx]]
    out[valid_idx] = activation_field.coincidence_for_bridges(
        src_pos, dst_pos
    )
    return out


def prune_bridges_and_nodes(bridges: Bridges, nodes: Nodes,
                             cfg: PlasticityConfig) -> float:
    """Remove low-weight bridges and orphaned nodes.

    Returns total energy returned to the export channel by node
    dissociations this call.
    """
    # 1. Remove bridges below w_min
    weak = np.where(bridges.alive & (bridges.weight < cfg.w_min))[0]
    for s in weak:
        bridges.remove(int(s))
    # 2. Dissociate orphan nodes
    if nodes.n_alive() == 0:
        return 0.0
    endpoints: set[int] = set()
    alive_br = np.where(bridges.alive)[0]
    for s in alive_br:
        endpoints.add(int(bridges.src[s]))
        endpoints.add(int(bridges.dst[s]))
    total_heat = 0.0
    for slot in np.where(nodes.alive)[0]:
        if int(slot) not in endpoints:
            e = nodes.remove(int(slot))
            total_heat += e
    return total_heat

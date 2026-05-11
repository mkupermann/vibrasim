"""Binding mechanism — the single rule that replaces 6 engineered levels.

Per spec §3, a bond forms between two or more vibrations within distance
`r` and time window `τ` with probability:

    p_bind = sigmoid(α * pred_coherence + β * (T_crit - T_local))

In F1a this is implemented in its scope-minimal form:
- `pred_coherence` is frequency-equality within `eps` (1.0 or 0.0), not
  the full windowed cross-correlation. T3 uses single-frequency
  injection, so this collapses trivially to 1.0 for all candidate pairs.
  The full cross-correlation version arrives in F2 when the cochlea
  brings multi-frequency input.
- Binding consumes quanta (frees their slots) and creates one Node.
- Binding is exothermic: a fraction `η` of total binding energy is
  exported as heat (added to the auditor).
- F1a binds in groups of exactly 2 per event. F1b will generalise.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.structures import Nodes


def pred_coherence(freq_a: float, freq_b: float,
                   eps: float = 1.0) -> float:
    """Simplified F1a coherence: 1.0 iff |freq_a - freq_b| < eps.

    The spec defines pred_coherence as a windowed temporal
    cross-correlation of frequency-amplitude trajectories. F1a's
    single-frequency injection makes all pairs trivially coherent;
    the binary form here matches that regime exactly. Full version
    arrives in F2 with multi-frequency cochlea input.
    """
    return 1.0 if abs(freq_a - freq_b) < eps else 0.0


def find_pairs_within(quanta: Quanta, r: float) -> np.ndarray:
    """Return shape (M, 2) int array of (i, j) pairs with i<j where the
    two alive quanta are within Euclidean distance r of each other.

    Naive O(N^2/2) algorithm — fine at F1a scale (≤ 1000 alive quanta).
    A KD-tree or cell-list optimisation is the F1b/F2 concern.
    """
    alive_idx = np.where(quanta.alive)[0]
    n = alive_idx.size
    if n < 2:
        return np.zeros((0, 2), dtype=np.int64)

    pos = quanta.pos[alive_idx]  # (n, 3)
    # Pairwise squared distances
    diff = pos[:, None, :] - pos[None, :, :]  # (n, n, 3)
    d2 = (diff * diff).sum(axis=-1)  # (n, n)
    r2 = r * r

    # Upper-triangle mask, strictly within r (d2 < r2)
    i_local, j_local = np.where(np.triu(d2 < r2, k=1))
    if i_local.size == 0:
        return np.zeros((0, 2), dtype=np.int64)
    pairs = np.stack([alive_idx[i_local], alive_idx[j_local]], axis=1)
    return pairs.astype(np.int64)


@dataclass
class BindingConfig:
    """Tunable parameters of the single binding rule (spec §3).

    Defaults are F1a starting values — calibration sweeps live in the
    F1a task 10 phase-log notes once T3 results are in.
    """
    alpha: float = 4.0          # gain on coherence term
    beta: float = 4.0           # gain on temperature gap
    T_crit: float = 5.0         # critical temperature for binding
    eta: float = 0.1            # heat-export fraction (η ∈ [0, 1))
    r: float = 1.5              # binding radius (Euclidean)
    coherence_eps: float = 1.0  # frequency-equality tolerance (F1a)


def binding_probability(pred_coh: float, T_local: float,
                         cfg: BindingConfig) -> float:
    """Compute p_bind = sigmoid(α * pred_coh + β * (T_crit - T_local)).

    Returns a float in (0, 1).
    """
    x = cfg.alpha * pred_coh + cfg.beta * (cfg.T_crit - T_local)
    # Stable sigmoid
    if x >= 0:
        return 1.0 / (1.0 + np.exp(-x))
    else:
        ex = np.exp(x)
        return ex / (1.0 + ex)


def attempt_binding(quanta: Quanta, nodes: Nodes, grid: Grid,
                    cfg: BindingConfig, tick_index: int,
                    rng: np.random.Generator) -> float:
    """Run one tick's binding pass.

    Finds all alive quanta pairs within distance r. For each pair:
      - skip if frequency mismatch (pred_coherence < 1.0)
      - read T_local at the pair's centroid voxel
      - compute p_bind; sample uniform → if < p_bind, BIND

    A binding event: consumes both quanta, creates one new node at the
    centroid with energy = (1 - η) * sum(quanta.energy), exports
    η * sum(quanta.energy) as heat (return value).

    Returns the total heat exported this tick (sum across all binding
    events). Caller is responsible for recording into the auditor.

    F1a only binds in PAIRS (2 quanta → 1 node). F1b will generalise.
    """
    pairs = find_pairs_within(quanta, cfg.r)
    if pairs.shape[0] == 0:
        return 0.0

    total_heat = 0.0
    # Iterate pairs; once a quantum is consumed in this tick it cannot
    # bind again, so track which slots have already participated.
    consumed = set()
    for p in pairs:
        i, j = int(p[0]), int(p[1])
        if i in consumed or j in consumed:
            continue

        # Coherence gate (F1a: frequency-equality)
        coh = pred_coherence(quanta.freq[i], quanta.freq[j],
                              eps=cfg.coherence_eps)
        if coh <= 0.0:
            continue

        # Temperature at pair centroid
        cx = 0.5 * (quanta.pos[i, 0] + quanta.pos[j, 0])
        cy = 0.5 * (quanta.pos[i, 1] + quanta.pos[j, 1])
        cz = 0.5 * (quanta.pos[i, 2] + quanta.pos[j, 2])
        ix, iy, iz = grid.pos_to_voxel((cx, cy, cz))
        T_local = float(grid.T[ix, iy, iz])

        # Binding probability
        p_bind = binding_probability(pred_coh=coh, T_local=T_local,
                                       cfg=cfg)
        # Sample
        if rng.random() >= p_bind:
            continue

        # BIND
        e_in = float(quanta.energy[i] + quanta.energy[j])
        heat = cfg.eta * e_in
        e_node = e_in - heat
        f_mean = 0.5 * (quanta.freq[i] + quanta.freq[j])
        slot = nodes.add(pos=(cx, cy, cz), energy=e_node,
                          freq=f_mean, born_tick=tick_index)
        if slot < 0:
            # Nodes buffer full; do not bind, leave quanta intact
            continue

        # Consume the two quanta
        quanta.remove(i)
        quanta.remove(j)
        consumed.add(i)
        consumed.add(j)
        total_heat += heat

    return total_heat

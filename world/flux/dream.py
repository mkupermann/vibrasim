"""G15 — The Dreaming Substrate (Flux Port).

Offline replay + concept blending + cross-modal hallucination for the
Flux substrate (F1c+). Adapted from the Legacy substrate's dream.py.

Biological grounding:
  - Wilson & McNaughton 1994 (Science) — hippocampal place-cell sequence
    replay during slow-wave sleep.
  - Buzsáki 2015 (Neuron) — sharp-wave ripples (SWR) gate memory
    consolidation.
  - Lewis & Durrant 2011 (Trends Cog Sci) — overlapping replays merge
    schemas; concept blending is a sleep-mediated capacity.

What this module gives the Flux substrate:
  1. **Sleep / replay.** External inputs are gated off. The substrate
     selects high-energy nodes and re-injects them. The existing
     binding + plasticity path then runs offline, consolidating
     structures that were otherwise transient.
  2. **Concept blending.** When two distinct trained pattern_ids both
     activate within `dream_blend_co_activation_window` seconds, a new
     blended node may be allocated at their spatial midpoint. The new
     node inherits a fresh pattern_id and can subsequently fire on its
     own.
  3. **Cross-modal hallucination.** Because F1b bridges are active during
     dreaming, replay seeds in one region drive quanta through bridges
     into other regions — enabling cross-modal generation.

Run flow per tick when `cfg.dream_mode_enabled`:
  1. Pick `dream_replay_seeds_per_tick` nodes with the highest energy
     among nodes whose `pattern_id != 0` (i.e. trained engram members).
  2. Inject `dream_replay_seed_energy` directly into each seed node.
  3. Track which `pattern_id`s have had any seed fire within the
     co-activation window. Pairs of co-active patterns become candidates
     for concept blending.
  4. For each candidate pair, find nodes from each pattern firing within
     the window. If at least `dream_blend_min_overlap_nodes` from each
     pattern fire, allocate a new BLENDED node at the centroid of the
     intersection, with a fresh pattern_id.

Caller is responsible for:
  - Setting `cfg.dream_mode_enabled = True` and gating their own input
    feeds OFF (i.e. don't call inject_into_substrate).
  - Calling `apply_dream(quanta, nodes, grid, dt)` once per tick BEFORE
    the main dynamics step — so seeded energy actually triggers
    activity within the same tick.

Returns a dict with diagnostic counters: replay_seeds_fired, blend_events.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.flux.quantum import Quanta
    from world.flux.structures import Nodes
    from world.flux.grid import Grid


@dataclass
class DreamConfig:
    """Configuration for G15 dreaming in Flux substrate."""
    # Dream mode toggle
    dream_mode_enabled: bool = False
    
    # Replay parameters
    dream_replay_seeds_per_tick: int = 5      # Number of nodes to seed per tick
    dream_replay_seed_energy: float = 10.0   # Energy to inject per seed
    
    # Concept blending parameters
    dream_blend_co_activation_window: float = 0.5  # Seconds for co-activation
    dream_blend_min_overlap_nodes: int = 2      # Min nodes per pattern to blend
    
    # Pattern tracking
    pattern_id_field: str = "pattern_id"  # Field name for pattern_id in nodes
    
    # NREM/REM gating (G18)
    dream_nrem_rem_ratio: tuple[int, int] = (4, 1)  # 4:1 NREM:REM ratio


def apply_dream(
    quanta: "Quanta",
    nodes: "Nodes",
    grid: "Grid",
    dt: float,
    cfg: DreamConfig | None = None,
    tick_index: int = 0,
    rng: np.random.Generator | None = None,
) -> dict:
    """One dream tick for Flux substrate. Returns diagnostic counts."""
    if cfg is None:
        cfg = DreamConfig()
    
    out = {
        "replay_seeds_fired": 0,
        "blend_events": 0,
        "co_active_patterns": 0,
    }
    
    if not cfg.dream_mode_enabled:
        return out
    
    if nodes is None or nodes.n_alive() < 2:
        return out
    
    # Use provided RNG or create one
    if rng is None:
        rng = np.random.default_rng()
    
    # 1. Identify trained-engram nodes (alive, pattern_id != 0)
    alive_mask = nodes.alive
    n_alive = nodes.n_alive()
    if n_alive < 2:
        return out
    
    alive_indices = np.where(alive_mask)[0]
    pattern_ids = nodes.pattern_id[alive_indices]
    
    # Filter to nodes with pattern_id != 0 (trained engrams)
    engram_mask = pattern_ids != 0
    if not engram_mask.any():
        return out
    
    engram_indices = alive_indices[engram_mask]
    engram_pattern_ids = pattern_ids[engram_mask]
    
    # 2. Among those, pick seeds biased toward high energy.
    energies = nodes.energy[engram_indices]
    n_seeds = min(cfg.dream_replay_seeds_per_tick, len(engram_indices))
    
    if n_seeds <= 0:
        return out
    
    # Normalize energies to probabilities
    if energies.sum() > 0:
        probs = energies / energies.sum()
    else:
        probs = np.ones_like(energies) / len(energies)
    
    # Sample seeds without replacement
    seed_local_indices = rng.choice(
        len(engram_indices),
        size=n_seeds,
        replace=False,
        p=probs
    )
    seed_global_indices = engram_indices[seed_local_indices]
    
    # Inject energy into each seed node
    for idx in seed_global_indices:
        nodes.energy[idx] += cfg.dream_replay_seed_energy
    
    out["replay_seeds_fired"] = n_seeds
    
    # 3. Concept blending
    # Track which pattern_ids were active in this tick
    active_patterns = set(engram_pattern_ids[seed_local_indices])
    out["co_active_patterns"] = len(active_patterns)
    
    # For each pair of active patterns, check for blending
    if len(active_patterns) >= 2 and cfg.dream_blend_min_overlap_nodes >= 1:
        # Get all nodes for each active pattern
        pattern_to_nodes = {}
        for pid in active_patterns:
            # Find all alive nodes with this pattern_id
            pid_mask = (nodes.pattern_id == pid) & nodes.alive
            pattern_to_nodes[pid] = np.where(pid_mask)[0]
        
        # Check all pairs of patterns
        patterns_list = list(active_patterns)
        for i in range(len(patterns_list)):
            for j in range(i + 1, len(patterns_list)):
                pid1, pid2 = patterns_list[i], patterns_list[j]
                nodes1 = pattern_to_nodes[pid1]
                nodes2 = pattern_to_nodes[pid2]
                
                # Check if we have enough overlap
                if (len(nodes1) >= cfg.dream_blend_min_overlap_nodes and
                    len(nodes2) >= cfg.dream_blend_min_overlap_nodes):
                    # Create a new blended node at the centroid
                    centroid = np.mean(np.vstack([
                        nodes.pos[nodes1],
                        nodes.pos[nodes2]
                    ]), axis=0)
                    total_energy = nodes.energy[nodes1].sum() + nodes.energy[nodes2].sum()
                    avg_freq = np.mean(np.concatenate([
                        nodes.freq[nodes1],
                        nodes.freq[nodes2]
                    ]))
                    
                    # Allocate new node (with new pattern_id)
                    new_pattern_id = max(nodes.pattern_id.max(), 0) + 1
                    new_slot = nodes.add(
                        pos=centroid,
                        energy=total_energy * 0.5,  # 50% of combined energy
                        freq=avg_freq,
                        born_tick=tick_index,
                        pattern_id=new_pattern_id
                    )
                    
                    if new_slot >= 0:
                        out["blend_events"] += 1
    
    return out

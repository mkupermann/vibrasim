"""G15 — The Dreaming Substrate.

Offline replay + concept blending + cross-modal hallucination on top of
the EQMOD continuous-physics emergent-atom substrate.

Biological grounding (load-bearing references):
  - Wilson & McNaughton 1994 (Science) — hippocampal place-cell sequence
    replay during slow-wave sleep.
  - Buzsáki 2015 (Neuron) — sharp-wave ripples (SWR) gate memory
    consolidation; replays trigger cortical plasticity.
  - Magee 2026 (Nat Neurosci) — BTSP eligibility traces persist across
    seconds; replay events that fall inside the trace window consolidate
    bridges via plateau-gated potentiation.
  - Hobson AIM model — dream content is a forward-modelling pass over
    learnt structure with the input gate closed.
  - Lewis & Durrant 2011 (Trends Cog Sci) — overlapping replays merge
    schemas; concept blending is a sleep-mediated capacity.

What this module gives the substrate that nothing else does:
  1. **Sleep / replay.** External inputs are gated off. The substrate
     selects high-eligibility seed atoms and re-fires them. The existing
     bridge-atom-propagation + BTSP path then runs offline, consolidating
     bridges that were otherwise transient.
  2. **Concept blending.** When two distinct trained pattern_ids both
     activate within `dream_blend_co_activation_window` seconds, a new
     blended atom may be allocated at their spatial midpoint. The new
     atom inherits a fresh pattern_id and can subsequently fire on its
     own. This is the substrate's creativity mechanism — emergent
     concepts that were not directly trained.
  3. **Cross-modal hallucination.** Because G13 bidirectional bridges
     are active during dreaming, replay seeds in (e.g.) the visual port
     drive vibrations through bridges into the audio output port —
     so a dream of "water" (visual replay) emits the audio fingerprint
     of the word "water" through the speaker.

Run flow per tick when `cfg.dream_mode_enabled`:
  1. Pick `dream_replay_seeds_per_tick` atoms with the highest eligibility
     trace among atoms whose `pattern_id != 0` (i.e. trained engram
     members). Bias toward but don't lock onto a single pattern.
  2. Inject `dream_replay_seed_charge` of charge directly into each seed
     atom — this triggers firing on the next neuron_dynamics step, which
     then chains through bridges and BTSP exactly as in normal operation.
  3. Track which `pattern_id`s have had any seed fire within the
     co-activation window. Pairs of co-active patterns become candidates
     for concept blending.
  4. For each candidate pair, find atoms from each pattern firing within
     the window. If at least `dream_blend_min_overlap_atoms` from each
     pattern fire, allocate a new BLENDED atom at the centroid of the
     intersection, with a fresh pattern_id.

Caller is responsible for:
  - Setting `cfg.dream_mode_enabled = True` and gating their own audio /
    video input feeds OFF (i.e. don't call inject_into_substrate).
  - Calling `apply_dream(world, dt)` once per tick BEFORE
    `neuron_dynamics(world, dt)` — so seeded charge actually triggers
    firings within the same tick.

Returns a dict with diagnostic counters: replay_seeds_fired, blend_events.
"""
from __future__ import annotations
import numpy as np


def apply_dream(world, dt: float) -> dict:
    """One dream tick. Returns diagnostic counts."""
    cfg = world.config
    out = {"replay_seeds_fired": 0, "blend_events": 0,
           "co_active_patterns": 0}
    if not getattr(cfg, "dream_mode_enabled", False):
        return out
    K = world.k_count
    if K == 0:
        return out

    # 1. Identify trained-engram atoms (level-4, alive, pattern_id != 0)
    atom_mask = (world.k_alive[:K]
                 & (world.k_level[:K] == 4)
                 & (world.k_pattern_id[:K] != 0))
    if not atom_mask.any():
        return out

    # 2. Among those, pick seeds biased toward high eligibility trace.
    # Atoms with strong recent firings are preferred — this matches the
    # SWR observation that recently-active place cells dominate replay.
    elig = world.k_eligibility[:K].astype(np.float64) * atom_mask.astype(np.float64)
    n_seeds = int(cfg.dream_replay_seeds_per_tick)
    if n_seeds <= 0:
        return out

    eligible_atom_indices = np.where(atom_mask)[0]
    if len(eligible_atom_indices) == 0:
        return out

    # If no atom has positive eligibility, sample uniformly so dreaming
    # bootstraps even from a cold substrate.
    weights = elig[eligible_atom_indices]
    n_pick = min(n_seeds, len(eligible_atom_indices))
    n_nonzero = int(np.count_nonzero(weights))
    # np.random.choice(replace=False) requires at least `size` non-zero
    # entries in p. When we have fewer high-eligibility atoms than seeds,
    # fall back to a small uniform floor so all atoms are pickable.
    if n_nonzero < n_pick:
        weights = weights + 1e-6
    if weights.sum() <= 0.0:
        weights = np.ones_like(weights)
    weights = weights / weights.sum()

    seed_local = world.rng.choice(
        len(eligible_atom_indices), size=n_pick, replace=False, p=weights,
    )
    seed_indices = eligible_atom_indices[seed_local]

    # 3. Inject replay charge into each seed atom. This will trigger
    # neuron_dynamics → firing → bridge propagation → BTSP, all on the
    # same tick.
    seed_charge = float(cfg.dream_replay_seed_charge)
    for si in seed_indices:
        world.k_charge[int(si)] += seed_charge
        out["replay_seeds_fired"] += 1

    # 4. Co-activation tracking and concept blending.
    if not getattr(cfg, "dream_blend_enabled", True):
        return out

    # Look at the firing log within the co-activation window.
    window = float(cfg.dream_blend_co_activation_window)
    t_now = world.t
    recent_fires_by_pattern: dict[int, list[int]] = {}
    for t_fire, atom_idx in world.firing_events:
        if t_fire < t_now - window:
            continue
        if atom_idx >= K:
            continue
        if not world.k_alive[atom_idx]:
            continue
        pid = int(world.k_pattern_id[int(atom_idx)])
        if pid == 0:
            continue
        recent_fires_by_pattern.setdefault(pid, []).append(int(atom_idx))

    out["co_active_patterns"] = len(recent_fires_by_pattern)
    if len(recent_fires_by_pattern) < 2:
        return out

    min_overlap = int(cfg.dream_blend_min_overlap_atoms)
    pids = sorted(p for p in recent_fires_by_pattern.keys() if p > 0)
    box = np.asarray(cfg.box_size, dtype=np.float64)

    # Track patterns we've already blended this tick to avoid creating
    # multiple blends per (pid_a, pid_b) — one cycle, one new concept.
    blended_pairs: set[tuple[int, int]] = set()

    for i in range(len(pids)):
        for j in range(i + 1, len(pids)):
            pid_a = pids[i]
            pid_b = pids[j]
            atoms_a = list(set(recent_fires_by_pattern[pid_a]))
            atoms_b = list(set(recent_fires_by_pattern[pid_b]))
            if (len(atoms_a) < min_overlap
                    or len(atoms_b) < min_overlap):
                continue

            # Centroid of co-firing atoms — our blended-concept anchor.
            pos_a = world.k_pos[atoms_a]
            pos_b = world.k_pos[atoms_b]
            # Periodic-aware centroid: take centroid of A, then unwrap B
            # toward A so the blended position straddles the two clusters
            # without wrapping artifacts.
            ca = pos_a.mean(axis=0)
            cb = pos_b.mean(axis=0)
            db = cb - ca
            db -= box * np.round(db / box)
            blended_pos = (ca + (ca + db)) * 0.5
            blended_pos = blended_pos % box

            # Use the average frequency of the two clusters
            freq_a = float(np.mean(world.k_freq[atoms_a]))
            freq_b = float(np.mean(world.k_freq[atoms_b]))
            blended_freq = float(np.sqrt(max(freq_a * freq_b, 1.0)))

            # Allocate the new atom.
            constituents_arr = np.array(
                atoms_a[:8] + atoms_b[:8], dtype=np.int32
            )
            # Use a fresh pattern_id (never used before).
            existing_pids = set(int(p) for p in world.k_pattern_id[:K])
            new_pid = max(existing_pids) + 1 if existing_pids else 1

            saved_active = world.active_pattern_id
            world.active_pattern_id = new_pid
            new_atom_idx = world.allocate_node(
                pos=blended_pos, freq=blended_freq, pol=True,
                level=4, constituents=constituents_arr, comp_kind=2,
            )
            world.active_pattern_id = saved_active

            if new_atom_idx >= 0:
                # Tag it as a "blended" atom by marking eligibility high
                # so subsequent BTSP picks it up immediately.
                world.k_eligibility[new_atom_idx] = 2.0
                # Bias its strength a little so it survives initial decay.
                world.k_strength[new_atom_idx] = 1.5
                blended_pairs.add((pid_a, pid_b))
                out["blend_events"] += 1

    return out


def begin_dream_state(world) -> None:
    """Convenience helper: enter dream state in-place (mutate cfg via
    dataclasses.replace to a new frozen WorldConfig if needed).

    Note: WorldConfig is frozen, so callers that need to *toggle* dream
    mode at runtime should construct two configs ahead of time, OR
    operate on a non-frozen wrapper. For test purposes, the World's cfg
    can be swapped wholesale via `world.config = new_cfg`.
    """
    from dataclasses import replace
    world.config = replace(world.config, dream_mode_enabled=True)


def end_dream_state(world) -> None:
    from dataclasses import replace
    world.config = replace(world.config, dream_mode_enabled=False)

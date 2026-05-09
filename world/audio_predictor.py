"""Predictive Babble — audio-pattern next-step predictor.

This module is the prediction-error backbone for the predictive-babble
design (`docs/superpowers/specs/2026-05-10-predictive-babble-design.md`,
section 3, row `world/audio_predictor.py`).

It is a clean *extension* of the existing `world.self_aware` machinery,
not a duplicate. `self_aware` tracks a per-pattern_id firing-rate
histogram across the entire substrate (the substrate's model of "what
am I doing right now"). `audio_predictor` tracks a *transition* model
restricted to firings inside the audio_input port (the substrate's
model of "given the last phoneme-scale event I heard, which one comes
next"). The two coexist on different objects and never share state.

The prediction target is the next pattern_id firing in the audio_input
port, on phoneme-scale (~100 ms) granularity. The metric is categorical
cross-entropy / perplexity over the predicted pattern_id distribution
against the actual next-firing pattern_id, evaluated on the dev split
every K cycles per the spec.

Initial implementation: a first-order Markov model with Laplace
smoothing. A simple, well-understood baseline. Higher-order or neural
predictors can replace this without changing the public API.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path  # noqa: F401  (spec lists pathlib in allowed imports)
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:  # avoid runtime cycle with world.state
    from world.state import World


@dataclass
class AudioPredictor:
    """First-order Markov predictor over audio-port pattern_id firings.

    State:
      - ``_counts`` maps ``prev_pid`` -> dict of ``next_pid`` -> integer
        transition count. Stored sparsely so unseen pids cost nothing.
      - ``_vocab`` is the set of pattern_ids ever seen (as either prev
        or next). ``vocabulary_size()`` returns ``len(self._vocab)``.
      - ``_last_seen_pid`` lets ``observe_world`` chain across calls:
        each call resumes from the last firing the previous call saw.
      - ``_last_seen_t`` lets ``observe_world`` skip events the
        predictor already consumed (firing_events is append-only and
        the timestamp is monotonically non-decreasing per tick).

    The predictor is independent of any World instance; ``observe_world``
    is a convenience for the autonomous loop and is defensively coded
    so a missing port or empty firing log returns 0 silently.
    """

    alpha: float = 0.01
    _counts: dict[int, dict[int, int]] = field(default_factory=dict)
    _vocab: set[int] = field(default_factory=set)
    _last_seen_pid: int | None = None
    _last_seen_t: float = -math.inf

    # --- core API ----------------------------------------------------

    def observe(self, prev_pid: int, next_pid: int) -> None:
        """Record one observed transition prev_pid -> next_pid."""
        prev_pid = int(prev_pid)
        next_pid = int(next_pid)
        row = self._counts.setdefault(prev_pid, {})
        row[next_pid] = row.get(next_pid, 0) + 1
        self._vocab.add(prev_pid)
        self._vocab.add(next_pid)

    def predict_distribution(self, prev_pid: int) -> dict[int, float]:
        """Return P(next_pid | prev_pid) over the current vocabulary.

        Uses Laplace smoothing: each next_pid gets ``+alpha`` pseudocount.
        For an unseen ``prev_pid`` (no observed transitions out of it)
        the distribution is uniform over the vocabulary — the maximum-
        entropy fallback that does not lie about confidence.
        """
        prev_pid = int(prev_pid)
        vocab = sorted(self._vocab)
        V = len(vocab)
        if V == 0:
            return {}
        row = self._counts.get(prev_pid, {})
        total = sum(row.values())
        denom = total + self.alpha * V
        if total == 0:
            # Unseen prev_pid: uniform over vocab. With Laplace this
            # falls out naturally (alpha / (alpha * V) = 1/V).
            return {pid: 1.0 / V for pid in vocab}
        return {
            pid: (row.get(pid, 0) + self.alpha) / denom for pid in vocab
        }

    def perplexity(self, sequence: list[int]) -> float:
        """Categorical perplexity = exp(-mean log P(x_i | x_{i-1})).

        A sequence shorter than 2 has no transitions and returns NaN —
        the caller must filter those upstream rather than us silently
        masking the case.
        """
        if len(sequence) < 2:
            return float("nan")
        log_probs: list[float] = []
        vocab = sorted(self._vocab)
        V = len(vocab)
        if V == 0:
            return float("nan")
        for prev, nxt in zip(sequence[:-1], sequence[1:]):
            prev = int(prev)
            nxt = int(nxt)
            row = self._counts.get(prev, {})
            total = sum(row.values())
            denom = total + self.alpha * V
            if total == 0:
                # Unseen prev: uniform 1/V.
                p = 1.0 / V
            else:
                p = (row.get(nxt, 0) + self.alpha) / denom
            # Clamp to a tiny floor so log doesn't explode if alpha is 0
            # and an unseen next is queried. With alpha > 0 this is
            # belt-and-braces.
            p = max(p, 1e-300)
            log_probs.append(math.log(p))
        mean_log_p = sum(log_probs) / len(log_probs)
        return math.exp(-mean_log_p)

    def vocabulary_size(self) -> int:
        return len(self._vocab)

    def reset(self) -> None:
        self._counts.clear()
        self._vocab.clear()
        self._last_seen_pid = None
        self._last_seen_t = -math.inf

    # --- world bridge -------------------------------------------------

    def observe_world(self, world: "World", port: str = "audio_input") -> int:
        """Read recent firings from the world's audio port and update.

        Filters firing_events to those whose atom position falls inside
        the configured port box. Iterates strictly after
        ``_last_seen_t`` so repeated calls chain correctly without
        double-counting. Returns the number of *new transitions*
        recorded (i.e. the number of (prev, next) pairs added).

        Defensive by spec: missing config attributes, dead atoms, or
        out-of-range indices are skipped silently rather than asserted.
        Asserting here would mask real config drift only by *crashing
        the whole loop*, which is worse than degrading gracefully.
        """
        cfg = world.config
        if port == "audio_input":
            origin_attr = "audio_input_port_origin"
            size_attr = "audio_input_port_size"
        elif port == "audio_output":
            origin_attr = "audio_output_port_origin"
            size_attr = "audio_output_port_size"
        else:
            return 0
        origin = getattr(cfg, origin_attr, None)
        size = getattr(cfg, size_attr, None)
        if origin is None or size is None:
            return 0
        ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        sx, sy, sz = float(size[0]), float(size[1]), float(size[2])

        K = int(getattr(world, "k_count", 0))
        if K == 0:
            return 0

        events = getattr(world, "firing_events", None)
        if not events:
            return 0

        # Local refs for speed; defensive against missing fields.
        k_pos = world.k_pos
        k_alive = world.k_alive
        k_pattern_id = world.k_pattern_id

        prev_pid = self._last_seen_pid
        new_transitions = 0
        new_last_t = self._last_seen_t
        new_last_pid = prev_pid
        for t_fire, atom_idx in events:
            if t_fire <= self._last_seen_t:
                continue
            if atom_idx < 0 or atom_idx >= K:
                continue
            if not bool(k_alive[atom_idx]):
                continue
            pos = k_pos[atom_idx]
            if not (ox <= pos[0] <= ox + sx
                    and oy <= pos[1] <= oy + sy
                    and oz <= pos[2] <= oz + sz):
                continue
            pid = int(k_pattern_id[atom_idx])
            # Track every observed pid in vocab even if we have no prev
            # yet — vocab growing on the very first firing matches the
            # test expectation in test_observe_world_reads_audio_input_port.
            self._vocab.add(pid)
            if prev_pid is not None:
                self.observe(prev_pid, pid)
                new_transitions += 1
            prev_pid = pid
            new_last_pid = pid
            new_last_t = float(t_fire)
        self._last_seen_pid = new_last_pid
        self._last_seen_t = new_last_t
        return new_transitions

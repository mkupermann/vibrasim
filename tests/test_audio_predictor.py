"""Tests for `world/audio_predictor.py` and the minimal `audio_io`
hook on `agent/autonomous_loop.py`.

All synthetic — no real World tick path is exercised at sample rate
(both audio_io tests below stub the AudioIO protocol). Should run in
under 2 seconds.

F3b reference: each test that has a conditional assertion path uses
``pytest.fail`` on the unreachable branch so a silent pass cannot hide
a logic error in the predictor or the loop hook.
"""
from __future__ import annotations

import math
from pathlib import Path  # noqa: F401  (spec lists pathlib in allowed imports)

import numpy as np
import pytest

from world.audio_predictor import AudioPredictor
from world.config import WorldConfig
from world.state import World


# ---------------------------------------------------------------------
# 1. AudioPredictor unit tests
# ---------------------------------------------------------------------


def test_uniform_prior_perplexity_equals_vocab_size():
    """Fresh predictor with vocab built but no transitions out of the
    queried prev: perplexity on an unseen sequence is approximately V.

    Prior reasoning: with Laplace alpha and zero observed counts on a
    given prev, P(any | prev) = 1/V; -log(1/V) = log V; perplexity = V.
    """
    p = AudioPredictor(alpha=0.01)
    # Seed vocab without seeding any transitions whose prev appears in
    # our held-out sequence. We grow the vocab by adding pids directly,
    # then query a held-out sequence whose every prev is unseen-as-
    # source — Laplace then makes P(any | prev) = 1/V exactly.
    for pid in [1, 2, 3, 4, 5, 99]:
        p._vocab.add(pid)  # type: ignore[attr-defined]
    V = p.vocabulary_size()
    assert V == 6, f"expected vocab=6, got {V}"
    # Sequence whose every consecutive (prev, next) has prev unseen as
    # a source pid in _counts (which is empty here).
    seq = [1, 2, 3, 4, 5, 99]
    pp = p.perplexity(seq)
    if not math.isfinite(pp):
        pytest.fail(f"perplexity should be finite, got {pp}")
    # Within 5 % of V — Laplace + the alternating prev=99 case both
    # give 1/V exactly, so we should be on the nose.
    assert abs(pp - V) / V <= 0.05, (
        f"perplexity {pp} not within 5% of V={V}"
    )


def test_perplexity_drops_on_learned_markov_sequence():
    """Train on a deterministic Markov chain; held-out perplexity ~1."""
    seq = [((i % 3) + 1) for i in range(100)]  # 1,2,3,1,2,3,...
    p = AudioPredictor(alpha=0.01)
    train, held = seq[:80], seq[80:]
    for prev, nxt in zip(train[:-1], train[1:]):
        p.observe(prev, nxt)
    pp = p.perplexity(held)
    if not math.isfinite(pp):
        pytest.fail(f"perplexity not finite: {pp}")
    assert pp <= 2.0, (
        f"deterministic chain perplexity {pp} should be near 1, got > 2"
    )


def test_perplexity_on_random_sequence_stays_near_vocab_size():
    """Random transitions over V=5 → perplexity close to V (high entropy)."""
    rng = np.random.default_rng(7)
    V = 5
    train = [int(x) for x in rng.integers(1, V + 1, size=101)]
    held = [int(x) for x in rng.integers(1, V + 1, size=51)]
    p = AudioPredictor(alpha=0.01)
    for prev, nxt in zip(train[:-1], train[1:]):
        p.observe(prev, nxt)
    assert p.vocabulary_size() == V
    pp = p.perplexity(held)
    if not math.isfinite(pp):
        pytest.fail(f"perplexity not finite: {pp}")
    # Random transitions over V=5 should give ~5; allow 30 % slack.
    assert abs(pp - V) / V <= 0.30, (
        f"random-sequence perplexity {pp} too far from V={V}"
    )


def test_predict_distribution_sums_to_one():
    """For any prev_pid in vocab, P sums to 1.0 within float epsilon."""
    p = AudioPredictor(alpha=0.01)
    transitions = [(1, 2), (1, 3), (2, 1), (3, 1), (3, 2), (2, 2)]
    for prev, nxt in transitions:
        p.observe(prev, nxt)
    for prev in sorted(p._vocab):  # type: ignore[attr-defined]
        dist = p.predict_distribution(prev)
        s = sum(dist.values())
        assert abs(s - 1.0) <= 1e-9, (
            f"distribution for prev={prev} sums to {s}, not 1"
        )


def _make_minimal_world_with_audio_firings(
    pids_in_order: list[int], rng_seed: int = 0,
) -> World:
    """Build a tiny World with one atom per pid placed inside the
    audio_input port and append firings for them in the given order."""
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=8,
        n_nodes_max=64, box_size=(60.0, 60.0, 60.0),
        rng_seed=rng_seed, neuron_dynamics_enabled=False,
        stdp_enabled=False, btsp_enabled=False,
        dream_mode_enabled=False, self_aware_enabled=False,
        self_modify_enabled=False,
    )
    world = World(cfg)
    # The default port is at origin (0,0,0) with size (15,15,15).
    # Allocate atoms inside it, one per unique pid.
    unique = sorted(set(pids_in_order))
    pid_to_idx: dict[int, int] = {}
    for n, pid in enumerate(unique):
        # active_pattern_id is what allocate_node tags the new atom with.
        world.active_pattern_id = pid
        idx = world.allocate_node(
            pos=np.array([1.0 + n, 1.0, 1.0]),
            freq=1000.0, pol=True, level=4,
            constituents=np.array([], dtype=np.int32),
            comp_kind=2,
        )
        if idx < 0:
            pytest.fail(f"could not allocate atom for pid={pid}")
        pid_to_idx[pid] = idx
    world.active_pattern_id = 0
    # Append firings in order, monotonically increasing time.
    for k, pid in enumerate(pids_in_order):
        world.firing_events.append(((k + 1) * 0.01, pid_to_idx[pid]))
    world.t = (len(pids_in_order) + 1) * 0.01
    return world


def test_observe_world_reads_audio_input_port():
    """observe_world picks up firings inside the audio_input port,
    grows vocab, and reports the right transition count."""
    pids = [1, 2, 3, 1, 2, 3]
    world = _make_minimal_world_with_audio_firings(pids)
    p = AudioPredictor(alpha=0.01)
    n = p.observe_world(world, port="audio_input")
    # Six firings → first one only seeds prev, remaining five form
    # transitions: (1->2),(2->3),(3->1),(1->2),(2->3) = 5 transitions.
    if n != 5:
        pytest.fail(
            f"expected 5 transitions, got {n} (pids={pids})"
        )
    assert p.vocabulary_size() == 3, (
        f"expected vocab size 3, got {p.vocabulary_size()}"
    )
    # Calling again with no new firings appended adds nothing.
    n2 = p.observe_world(world, port="audio_input")
    if n2 != 0:
        pytest.fail(f"second call should be a no-op, got {n2} new")


def test_unseen_prev_pid_returns_uniform():
    """predict_distribution on a never-observed prev returns uniform."""
    p = AudioPredictor(alpha=0.01)
    for prev, nxt in [(1, 2), (2, 1), (1, 3), (3, 2)]:
        p.observe(prev, nxt)
    V = p.vocabulary_size()
    assert V == 3
    dist = p.predict_distribution(prev_pid=999)  # never observed
    if not dist:
        pytest.fail("expected non-empty uniform distribution for unseen prev")
    expected = 1.0 / V
    for pid, p_val in dist.items():
        assert abs(p_val - expected) <= 1e-12, (
            f"unseen-prev dist not uniform: P({pid})={p_val}, exp={expected}"
        )
    assert abs(sum(dist.values()) - 1.0) <= 1e-9


# ---------------------------------------------------------------------
# 2. AutonomousLoop hook tests
# ---------------------------------------------------------------------


class _StubAudioIO:
    """Minimal stub that records inject_into_substrate calls.

    The real AudioIO does encode → vibration injection. The loop only
    needs to *call* it; we don't want portaudio loaded for this test.
    """

    def __init__(self) -> None:
        self.calls: list[float] = []

    def inject_into_substrate(self, world, dt: float) -> int:
        self.calls.append(float(dt))
        return 0


def test_autonomous_loop_default_no_audio_io():
    """Default config has audio_io=None and behaviour is unchanged."""
    from agent.autonomous_loop import (
        AutonomousLoop, AutonomousLoopConfig, build_autonomous_world,
    )
    world = build_autonomous_world()
    cfg = AutonomousLoopConfig(
        awake_seconds_per_cycle=0.5,
        dream_seconds_per_cycle=0.25,
    )
    if cfg.audio_io is not None:
        pytest.fail("default audio_io should be None")
    loop = AutonomousLoop(world, cfg)
    pre_t = world.t
    loop.cycle += 1
    loop._run_awake_phase()
    if world.t <= pre_t:
        pytest.fail(
            f"awake phase did not advance world.t (pre={pre_t}, post={world.t})"
        )


def test_autonomous_loop_with_audio_io_consumes_block():
    """Stub audio_io is called once per awake phase with target_sec."""
    from agent.autonomous_loop import (
        AutonomousLoop, AutonomousLoopConfig, build_autonomous_world,
    )
    world = build_autonomous_world()
    stub = _StubAudioIO()
    cfg = AutonomousLoopConfig(
        awake_seconds_per_cycle=0.5,
        dream_seconds_per_cycle=0.25,
        audio_io=stub,
    )
    loop = AutonomousLoop(world, cfg)
    loop.cycle += 1
    loop._run_awake_phase()
    if len(stub.calls) != 1:
        pytest.fail(
            f"expected exactly one inject_into_substrate call, got {len(stub.calls)}"
        )
    assert abs(stub.calls[0] - cfg.awake_seconds_per_cycle) <= 1e-9, (
        f"inject_into_substrate dt={stub.calls[0]} != target {cfg.awake_seconds_per_cycle}"
    )
    # Run a second awake phase; the stub should be called again.
    loop.cycle += 1
    loop._run_awake_phase()
    if len(stub.calls) != 2:
        pytest.fail(f"expected 2 calls after 2 awake phases, got {len(stub.calls)}")

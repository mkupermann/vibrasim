"""Unit tests for `agent/babble.py` (predictive-babble iteration 4b).

Synthetic-only — no real audio, no full curriculum, no microphone, no
speakers. The whole file completes in well under 10 seconds.

Coverage matches the brief in the iteration-4b plan:

1. Output array length matches duration_seconds * sample_rate (within
   the small ISTFT-padding tolerance the decoder applies).
2. No firings → silence.
3. Synthetic firings → substantively non-silent waveform.
4. The caller's loop config is not mutated (input gating runs on a copy).
5. ``output_path`` writes a real wav file readable by scipy.io.wavfile.
6. Only firings inside the audio_OUTPUT port land in the waveform; firings
   placed in the audio_INPUT port are filtered out.
7. Empty world (k_count=0) returns silence without crashing.

Each conditional uses ``pytest.fail`` on the unreachable branch — no
silent-pass paths (cf. the F3b silent-pass bug recorded in project memory).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
import scipy.io.wavfile
import scipy.signal

from agent.autonomous_loop import (
    AutonomousLoopConfig,
    build_autonomous_world,
)
from agent.babble import BabbleRunner
from agent.encoder_audio import freq_to_port_position
from world.config import WorldConfig
from world.state import World


# --- helpers ----------------------------------------------------------


def _make_loop_cfg(**overrides) -> AutonomousLoopConfig:
    """Tiny loop config with audio_io=None by default."""
    base = dict(
        awake_seconds_per_cycle=1.0,
        dream_seconds_per_cycle=0.5,
        stagnation_threshold=0.001,
        stagnation_window=2,
    )
    base.update(overrides)
    return AutonomousLoopConfig(**base)


def _allocate_atom_at(world: World, pos: np.ndarray, freq: float, pol: bool) -> int:
    """Allocate a level-4 atom at a chosen position. Returns the slot index."""
    idx = world.allocate_node(
        pos=pos.copy(),
        freq=freq,
        pol=pol,
        level=4,
        constituents=np.array([], dtype=np.int32),
        comp_kind=2,
    )
    if idx < 0:
        pytest.fail(f"allocate_node returned -1 (capacity?) at pos={pos}")
    return idx


def _output_port_position(
    cfg: WorldConfig, freq: float, rng: np.random.Generator
) -> np.ndarray:
    """Position inside the audio_OUTPUT port that decodes back to ``freq``."""
    pos = freq_to_port_position(
        freq=freq,
        freq_min=float(cfg.audio_freq_min),
        freq_max=float(cfg.audio_freq_max),
        port_origin=tuple(cfg.audio_output_port_origin),
        port_size=tuple(cfg.audio_output_port_size),
        rng=rng,
    )
    return np.array(pos, dtype=np.float64)


def _input_port_position(
    cfg: WorldConfig, freq: float, rng: np.random.Generator
) -> np.ndarray:
    """Position inside the audio_INPUT port that decodes back to ``freq``."""
    pos = freq_to_port_position(
        freq=freq,
        freq_min=float(cfg.audio_freq_min),
        freq_max=float(cfg.audio_freq_max),
        port_origin=tuple(cfg.audio_input_port_origin),
        port_size=tuple(cfg.audio_input_port_size),
        rng=rng,
    )
    return np.array(pos, dtype=np.float64)


def _empty_world() -> World:
    """Minimal World with no atoms — k_count starts at 0, no firings."""
    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=8,
        n_nodes_max=16,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=7,
        # All learning machinery off — tick() should be a near-no-op.
        neuron_dynamics_enabled=False,
        stdp_enabled=False,
        bridge_atom_propagation_enabled=False,
        btsp_enabled=False,
        dream_mode_enabled=False,
        self_aware_enabled=False,
        self_modify_enabled=False,
        workspace_broadcast_enabled=False,
        graceful_capacity=True,
    )
    return World(cfg)


# --- 1. duration matches sample_rate * duration_seconds ---------------


def test_babble_produces_wav_of_correct_duration():
    world = build_autonomous_world()
    runner = BabbleRunner(
        world=world,
        autonomous_loop_cfg=_make_loop_cfg(),
        duration_seconds=1.0,
        output_path=None,
        sample_rate=16000,
    )
    samples, written = runner.run()

    assert written is None
    assert isinstance(samples, np.ndarray)
    assert samples.dtype == np.float32

    expected = 16000  # 1.0 sec * 16 kHz
    # decode_block truncates/pads to exactly n_target. Allow ±10 samples
    # of tolerance against future ISTFT-padding tweaks.
    assert abs(samples.size - expected) <= 10, (
        f"got {samples.size} samples; expected {expected}"
    )


# --- 2. no firings -> silence -----------------------------------------


def test_babble_with_no_firings_returns_silence():
    """Run on a fresh empty World — no firings can be produced."""
    world = _empty_world()
    runner = BabbleRunner(
        world=world,
        autonomous_loop_cfg=_make_loop_cfg(),
        duration_seconds=0.5,
        output_path=None,
        sample_rate=16000,
    )
    samples, written = runner.run()
    assert written is None
    if samples.size == 0:
        pytest.fail("decode_block returned empty array; expected silence frame")

    rms = float(np.sqrt(np.mean(samples.astype(np.float64) ** 2)))
    if not np.allclose(samples, 0.0, atol=1e-6) and rms >= 1e-3:
        pytest.fail(f"expected silence, got rms={rms:.6f}")
    # If we reach here the waveform is silence (either exactly zero
    # or RMS < 1e-3) — the explicit branch above guards against
    # silent-passing on a non-silent buffer.


# --- 3. synthetic firings -> non-silence ------------------------------


def test_babble_with_synthetic_firings_produces_nonsilence():
    world = build_autonomous_world()
    cfg = world.config
    rng = np.random.default_rng(seed=1234)

    # Hand-place an atom inside the audio_output port at a known
    # frequency, then synthesise 50 firings on it.
    target_freq = 1500.0
    pos = _output_port_position(cfg, target_freq, rng)
    atom_idx = _allocate_atom_at(world, pos, freq=target_freq, pol=True)

    # Pre-fill firing_events with a baseline + 50 firings stamped at
    # times the runner will see *after* it advances world.t.
    duration = 1.0
    start_t = float(world.t)
    # Distribute firings uniformly across the babble window.
    n_firings = 50
    fire_times = np.linspace(
        start_t + 0.01, start_t + duration - 0.01, n_firings,
    )
    for ft in fire_times:
        world.firing_events.append((float(ft), int(atom_idx)))

    runner = BabbleRunner(
        world=world,
        autonomous_loop_cfg=_make_loop_cfg(),
        duration_seconds=duration,
        output_path=None,
        sample_rate=16000,
    )
    samples, _ = runner.run()
    rms = float(np.sqrt(np.mean(samples.astype(np.float64) ** 2)))
    if rms <= 1e-3:
        pytest.fail(
            f"expected non-silent babble (rms > 1e-3), got rms={rms:.6f}"
        )


# --- 4. caller's loop config is not mutated --------------------------


@dataclass
class _StubAudioIO:
    name: str = "stub"


def test_babble_does_not_mutate_caller_config():
    world = build_autonomous_world()
    stub = _StubAudioIO(name="caller-owned")
    cfg = _make_loop_cfg()
    # Mutating audio_io directly via attribute set; AutonomousLoopConfig
    # is a dataclass so this is straightforward.
    cfg.audio_io = stub  # type: ignore[assignment]

    runner = BabbleRunner(
        world=world,
        autonomous_loop_cfg=cfg,
        duration_seconds=0.2,
    )
    runner.run()

    if cfg.audio_io is None:
        pytest.fail("caller config was mutated: audio_io was reset to None")
    if cfg.audio_io is not stub:
        pytest.fail(
            f"caller config audio_io changed identity: got {cfg.audio_io!r}"
        )
    # And the runner's gated copy must have audio_io=None.
    if runner._gated_cfg is None:
        pytest.fail("runner did not record its gated config copy")
    if getattr(runner._gated_cfg, "audio_io", "missing") is not None:
        pytest.fail(
            "gated config still has audio_io set — input gating failed"
        )


# --- 5. write_wav round-trips to disk ---------------------------------


def test_babble_writes_wav_to_disk(tmp_path: Path):
    world = build_autonomous_world()
    out = tmp_path / "subdir" / "babble.wav"

    runner = BabbleRunner(
        world=world,
        autonomous_loop_cfg=_make_loop_cfg(),
        duration_seconds=0.3,
        output_path=out,
        sample_rate=16000,
    )
    samples, written = runner.run()

    if written is None:
        pytest.fail("output_path was set but written path is None")
    if written != out:
        pytest.fail(f"runner wrote to {written}, expected {out}")
    if not out.exists():
        pytest.fail(f"wav file not found on disk at {out}")

    sr, data = scipy.io.wavfile.read(str(out))
    if sr != 16000:
        pytest.fail(f"wav sample rate is {sr}, expected 16000")
    if data.dtype != np.int16:
        pytest.fail(f"wav dtype is {data.dtype}, expected int16")
    if data.size <= 0:
        pytest.fail(f"wav has no samples (size={data.size})")


# --- 6. only audio_OUTPUT port firings reach the waveform -------------


def test_babble_filters_only_audio_output_port():
    """Firings inside the audio_INPUT port must be excluded.

    We inject many firings at f1 inside the INPUT port and many at f2
    inside the OUTPUT port. The decoded waveform's spectrum must peak
    at f2, not f1.
    """
    world = build_autonomous_world()
    cfg = world.config
    rng = np.random.default_rng(seed=99)

    f_input = 250.0   # would land in the INPUT port if not filtered
    f_output = 3000.0  # legitimate output port frequency

    # Pick positions that are well-separated bin-wise.
    pos_in = _input_port_position(cfg, f_input, rng)
    pos_out = _output_port_position(cfg, f_output, rng)

    idx_in = _allocate_atom_at(world, pos_in, freq=f_input, pol=True)
    idx_out = _allocate_atom_at(world, pos_out, freq=f_output, pol=True)

    duration = 1.0
    start_t = float(world.t)
    n = 80
    fire_times = np.linspace(start_t + 0.01, start_t + duration - 0.01, n)
    for ft in fire_times:
        world.firing_events.append((float(ft), int(idx_in)))
        world.firing_events.append((float(ft), int(idx_out)))

    runner = BabbleRunner(
        world=world,
        autonomous_loop_cfg=_make_loop_cfg(),
        duration_seconds=duration,
        sample_rate=16000,
    )
    samples, _ = runner.run()

    # Welch PSD — find peak frequency.
    freqs, psd = scipy.signal.welch(
        samples.astype(np.float64), fs=16000, nperseg=2048,
    )
    peak_idx = int(np.argmax(psd))
    peak_freq = float(freqs[peak_idx])

    # The peak should be near f_output and far from f_input.
    out_match = abs(peak_freq - f_output) < 200.0
    in_match = abs(peak_freq - f_input) < 200.0
    if in_match and not out_match:
        pytest.fail(
            f"peak at {peak_freq:.1f} Hz matches INPUT-port f1={f_input}"
            " — output filter failed to exclude input-port firings"
        )
    if not out_match:
        pytest.fail(
            f"peak at {peak_freq:.1f} Hz does not match OUTPUT-port "
            f"f2={f_output}; input f1={f_input}"
        )


# --- 7. k_count=0 world -----------------------------------------------


def test_babble_handles_empty_world():
    world = _empty_world()
    assert world.k_count == 0  # sanity

    runner = BabbleRunner(
        world=world,
        autonomous_loop_cfg=_make_loop_cfg(),
        duration_seconds=0.2,
        sample_rate=16000,
    )
    # Must not crash.
    samples, written = runner.run()
    assert written is None
    if samples.size <= 0:
        pytest.fail("expected a non-empty silence buffer, got size 0")
    rms = float(np.sqrt(np.mean(samples.astype(np.float64) ** 2)))
    if rms >= 1e-3:
        pytest.fail(
            f"empty world should produce silence, got rms={rms:.6f}"
        )

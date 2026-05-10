"""Unit tests for ``agent/corpus_audio_feeder.py``.

The :class:`CorpusAudioFeeder` is the file-backed analogue of
:class:`agent.audio_io.AudioIO`. These tests verify the duck-typed
``inject_into_substrate`` contract that the autonomous loop's awake
phase relies on (see ``agent/autonomous_loop.py:225``):

1. With no stage loaded the feeder must return 0 (no-op, never raise).
2. ``load_stage`` populates the buffer and pulls the read pointer to 0.
3. Subsequent ``inject_into_substrate`` calls drain samples in order
   and consume ``int(dt * sample_rate)`` samples per call.
4. When the corpus is exhausted the read pointer wraps to the start
   of the file (long training runs on one stage are continuous).
5. ``reset`` rewinds to sample 0 of the currently loaded stage.
6. Loading the same path twice does not accumulate state — the
   pointer goes back to zero either way (the stage advance contract
   is "you start fresh").

Each conditional uses ``pytest.fail`` on the unreachable branch — no
silent-pass paths.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.corpus_audio_feeder import CorpusAudioFeeder
from world.config import WorldConfig
from world.state import World


# ---------------------------------------------------------------------
# Helpers


def _world_for_audio() -> World:
    """Tiny World fixture matching tests/test_audio_io_injection.py."""
    return World(WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=512,
        box_size=(60.0, 60.0, 60.0),
        audio_io_enabled=True,
        audio_input_port_origin=(0.0, 0.0, 0.0),
        audio_input_port_size=(15.0, 15.0, 15.0),
    ))


def _write_synthetic_corpus(
    tmp_path: Path,
    duration_s: float = 1.0,
    sample_rate: int = 16000,
    name: str = "stage1",
) -> tuple[Path, Path]:
    """Write a synthetic 1 kHz tone f32.raw + manifest under tmp_path/{name}.

    Returns ``(train_path, manifest_path)``.
    """
    sub = tmp_path / name
    sub.mkdir(parents=True, exist_ok=True)
    n = int(round(duration_s * sample_rate))
    t = np.arange(n, dtype=np.float32) / sample_rate
    audio = (0.5 * np.sin(2 * np.pi * 1000.0 * t)).astype(np.float32)
    train_path = sub / "train.f32.raw"
    audio.tofile(train_path)
    manifest_path = sub / "manifest.json"
    manifest_path.write_text(json.dumps({
        "name": name,
        "sample_rate": int(sample_rate),
        "n_samples": int(n),
        "duration_seconds": float(duration_s),
    }, indent=2))
    return train_path, manifest_path


# ---------------------------------------------------------------------
# Tests


def test_feeder_returns_zero_when_no_stage_loaded() -> None:
    """A fresh feeder with no load_stage call injects nothing."""
    world = _world_for_audio()
    feeder = CorpusAudioFeeder(sample_rate=16000)

    n_alive_before = int(world.s_alive.sum())
    n = feeder.inject_into_substrate(world, dt=0.1)
    n_alive_after = int(world.s_alive.sum())

    if n != 0:
        pytest.fail(
            f"feeder with no stage returned {n} injected (expected 0)"
        )
    if n_alive_after != n_alive_before:
        pytest.fail(
            f"world.s_alive changed from {n_alive_before} to "
            f"{n_alive_after} despite no stage loaded"
        )
    if feeder.current_stage_path is not None:
        pytest.fail(
            f"current_stage_path is {feeder.current_stage_path!r}, "
            "expected None for an unloaded feeder"
        )


def test_feeder_loads_stage_and_advances_pointer(tmp_path: Path) -> None:
    """Two successive injects must drain sequential blocks."""
    train_path, manifest_path = _write_synthetic_corpus(
        tmp_path, duration_s=1.0, sample_rate=16000, name="stage1",
    )
    world = _world_for_audio()
    feeder = CorpusAudioFeeder(sample_rate=16000)
    feeder.load_stage(train_path, manifest_path)

    if feeder.current_stage_path != train_path:
        pytest.fail(
            f"current_stage_path is {feeder.current_stage_path!r}, "
            f"expected {train_path!r}"
        )

    # First inject — 0.1 s = 1600 samples worth.
    n_first = feeder.inject_into_substrate(world, dt=0.1)
    if n_first <= 0:
        pytest.fail(
            f"first inject returned {n_first} (expected > 0); "
            "1 kHz tone should produce STFT bins above amplitude_threshold"
        )

    pointer_after_first = feeder._read_pos
    if pointer_after_first <= 0:
        pytest.fail(
            f"read pointer is {pointer_after_first} after first inject; "
            "it should advance"
        )

    # Second inject — pointer must continue from where we left off.
    n_second = feeder.inject_into_substrate(world, dt=0.1)
    pointer_after_second = feeder._read_pos
    if n_second <= 0:
        pytest.fail(
            f"second inject returned {n_second} (expected > 0)"
        )
    if pointer_after_second <= pointer_after_first:
        pytest.fail(
            "second inject did not advance the pointer past the first; "
            f"first={pointer_after_first} second={pointer_after_second}"
        )


def test_feeder_loops_when_corpus_exhausted(tmp_path: Path) -> None:
    """A 0.5 s corpus served via two 1.0 s requests must wrap around."""
    train_path, manifest_path = _write_synthetic_corpus(
        tmp_path, duration_s=0.5, sample_rate=16000, name="short",
    )
    world = _world_for_audio()
    feeder = CorpusAudioFeeder(sample_rate=16000)
    feeder.load_stage(train_path, manifest_path)

    # First inject consumes 0.5 s worth (exactly the corpus length)
    # and would normally land the pointer at sample 0 again.
    n_first = feeder.inject_into_substrate(world, dt=0.5)
    if n_first <= 0:
        pytest.fail(
            f"first inject returned {n_first} (expected > 0)"
        )
    # 8000 samples consumed, pointer at 0 (wrapped exactly once).
    if feeder._read_pos != 0:
        pytest.fail(
            f"after consuming all 8000 samples, pointer is "
            f"{feeder._read_pos}; expected 0 (wrap at the end)"
        )

    # Second inject of 0.5 s should pull from sample 0 again — the
    # corpus is being looped.
    n_second = feeder.inject_into_substrate(world, dt=0.5)
    if n_second <= 0:
        pytest.fail(
            f"second inject (looped) returned {n_second}; "
            "expected > 0 (looping should produce identical content)"
        )

    # Single inject of 1.0 s on a 0.5 s corpus — wraps exactly once
    # internally. Use a fresh world to keep the s_alive bookkeeping clean.
    world2 = _world_for_audio()
    feeder2 = CorpusAudioFeeder(sample_rate=16000)
    feeder2.load_stage(train_path, manifest_path)
    n_loop_in_one_call = feeder2.inject_into_substrate(world2, dt=1.0)
    if n_loop_in_one_call <= 0:
        pytest.fail(
            f"single 1.0 s inject on 0.5 s corpus returned "
            f"{n_loop_in_one_call}; expected > 0 with internal wrap"
        )


def test_feeder_reset_returns_to_start(tmp_path: Path) -> None:
    """``reset`` rewinds to sample 0; subsequent inject reads from start."""
    train_path, manifest_path = _write_synthetic_corpus(
        tmp_path, duration_s=1.0, sample_rate=16000, name="resetme",
    )
    world = _world_for_audio()
    feeder = CorpusAudioFeeder(sample_rate=16000)
    feeder.load_stage(train_path, manifest_path)

    feeder.inject_into_substrate(world, dt=0.2)
    if feeder._read_pos == 0:
        pytest.fail(
            "read pointer is still 0 after a 0.2 s inject; "
            "_next_block did not advance"
        )

    feeder.reset()
    if feeder._read_pos != 0:
        pytest.fail(
            f"after reset, pointer is {feeder._read_pos}; expected 0"
        )

    # The buffer itself must still be loaded (reset does not unload).
    if feeder.current_stage_path is None:
        pytest.fail(
            "reset cleared the loaded stage; it should only rewind "
            "the read pointer"
        )


def test_feeder_load_stage_is_idempotent(tmp_path: Path) -> None:
    """Loading the same path twice rewinds the pointer; no accumulation."""
    train_path, manifest_path = _write_synthetic_corpus(
        tmp_path, duration_s=1.0, sample_rate=16000, name="idempotent",
    )
    world = _world_for_audio()
    feeder = CorpusAudioFeeder(sample_rate=16000)
    feeder.load_stage(train_path, manifest_path)

    feeder.inject_into_substrate(world, dt=0.2)
    pointer_after_inject = feeder._read_pos
    if pointer_after_inject == 0:
        pytest.fail(
            "pointer did not advance after inject; cannot test idempotency"
        )
    buffer_size_before = feeder._audio.size

    # Reload same path. Pointer must reset to 0; buffer size unchanged.
    feeder.load_stage(train_path, manifest_path)
    if feeder._read_pos != 0:
        pytest.fail(
            f"after reloading same path, pointer is {feeder._read_pos}; "
            "expected 0"
        )
    if feeder._audio.size != buffer_size_before:
        pytest.fail(
            f"buffer size changed from {buffer_size_before} to "
            f"{feeder._audio.size} on re-load; load_stage should "
            "replace, not append"
        )


def test_feeder_rejects_mismatched_sample_rate(tmp_path: Path) -> None:
    """A manifest sample-rate mismatch must raise, not silently mis-encode."""
    sub = tmp_path / "wrong_sr"
    sub.mkdir(parents=True, exist_ok=True)
    n = 16000  # 1 sec at 16 kHz
    audio = np.zeros(n, dtype=np.float32)
    train_path = sub / "train.f32.raw"
    audio.tofile(train_path)
    manifest_path = sub / "manifest.json"
    manifest_path.write_text(json.dumps({
        "name": "wrong_sr", "sample_rate": 22050, "n_samples": n,
    }))

    feeder = CorpusAudioFeeder(sample_rate=16000)
    with pytest.raises(ValueError, match="sample rate"):
        feeder.load_stage(train_path, manifest_path)


def test_feeder_caps_vibrations_on_high_entropy_audio(tmp_path: Path) -> None:
    """White noise produces hundreds of emissions per block; cap must hold.

    Without the cap, high-entropy audio floods n_vibrations_max within a
    few cycles and physics tick scales O(N²) until awake phases take
    minutes of wall-clock — controls stalled indefinitely in the synthetic
    full-mode demo before this fix.
    """
    sub = tmp_path / "noise"
    sub.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(0)
    audio = rng.normal(0, 0.5, size=16000).astype(np.float32)
    train_path = sub / "train.f32.raw"
    audio.tofile(train_path)
    manifest_path = sub / "manifest.json"
    manifest_path.write_text(json.dumps({
        "name": "noise", "sample_rate": 16000,
        "n_samples": int(audio.size), "duration_seconds": 1.0,
    }))

    # Default cap = 256.
    world_default = _world_for_audio()
    feeder_default = CorpusAudioFeeder(sample_rate=16000)
    feeder_default.load_stage(train_path, manifest_path)
    n_default = feeder_default.inject_into_substrate(world_default, dt=0.5)

    # Aggressive cap = 32.
    world_capped = _world_for_audio()
    feeder_capped = CorpusAudioFeeder(
        sample_rate=16000, max_vibrations_per_inject=32,
    )
    feeder_capped.load_stage(train_path, manifest_path)
    n_capped = feeder_capped.inject_into_substrate(world_capped, dt=0.5)

    # Disabled cap (cap=0) — would inject everything (bounded only by
    # n_vibrations_max in the World fixture, which is 512).
    world_uncapped = _world_for_audio()
    feeder_uncapped = CorpusAudioFeeder(
        sample_rate=16000, max_vibrations_per_inject=0,
    )
    feeder_uncapped.load_stage(train_path, manifest_path)
    n_uncapped = feeder_uncapped.inject_into_substrate(world_uncapped, dt=0.5)

    if n_capped > 32:
        pytest.fail(
            f"cap=32 produced {n_capped} injections (expected ≤ 32)"
        )
    if n_default > 256:
        pytest.fail(
            f"default cap=256 produced {n_default} injections (expected ≤ 256)"
        )
    if not (n_uncapped >= n_default >= n_capped):
        pytest.fail(
            f"expected uncapped >= default >= capped, got "
            f"uncapped={n_uncapped} default={n_default} capped={n_capped}"
        )
    # Sanity: the cap is biting on white noise (default would otherwise
    # emit far more than 256 emissions across 31 blocks of 0.5 s audio).
    if n_uncapped <= n_default:
        pytest.fail(
            f"uncapped ({n_uncapped}) should exceed default cap ({n_default}) "
            "on white noise — otherwise the cap isn't actually biting"
        )

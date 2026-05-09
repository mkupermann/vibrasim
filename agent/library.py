"""Substrate library — multi-pattern memory via per-pattern substrates.

The contract C asymmetry (visual1 fails, visual2 passes) is structural in
a single shared substrate: pair2's training inevitably bleeds into pair1's
bridges via geometric coupling no matter how the chain is gated. The
honest architecture is N parallel substrates, one per learned pattern,
with a thin classifier that routes test-phase stimuli to the right one.

This is how Person-of-Interest's "Machine" actually works in fiction —
many specialised memory banks plus a classifier that decides which to
query for any given input.

Usage:
    library = SubstrateLibrary()

    # Train one pattern per label:
    library.train_pattern("water", visual_glass, audio_water,
                          world_factory=_build_world, duration_sec=4.0)
    library.train_pattern("hand",  visual_hand,  audio_hand,
                          world_factory=_build_world, duration_sec=4.0)

    # At recall time the library classifies the visual + runs the matched
    # substrate:
    audio_out = library.recall(visual_glass, duration_sec=4.0)
    # → returns audio correlated with "water" because the visual matches
    #   the "water" pattern's training signature.

The classifier is intentionally simple: per pattern we store a normalised
representation of the training video (mean of frames, downsampled to
32x32). Recall picks the pattern whose stored representation has the
highest cosine similarity with the test frame's representation.

This keeps the substrate's role clean — each substrate stores a single
(visual → audio) association via Hebbian STDP, exactly what it can do
reliably (M4 minimal-smoke = 0.42 cosine). The "discrimination" emerges
from the LIBRARY, not from the substrate forcibly holding multiple
patterns at once.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Optional
from pathlib import Path

import numpy as np

from world.snapshot import save_snapshot, load_snapshot


@dataclass
class LibraryEntry:
    label: str
    world: object         # World instance
    audio_io: object      # AudioIO instance
    video_io: object      # VideoIO instance
    loop: object          # AgentLoop instance
    fingerprint: np.ndarray   # 32x32 mean-of-training-frames, normalised

    def cosine_to(self, frame: np.ndarray) -> float:
        """Cosine similarity between this entry's training fingerprint and
        a test frame. Both are downsampled to 32x32 grayscale + normalised."""
        return _frame_cosine(self.fingerprint, _make_fingerprint(frame))


def _make_fingerprint(frame: np.ndarray, size: int = 32) -> np.ndarray:
    """Downsample a frame to size×size grayscale, then normalise to unit L2."""
    if frame.ndim == 3:
        gray = frame.mean(axis=2).astype(np.float32)
    else:
        gray = frame.astype(np.float32)
    h, w = gray.shape
    # Simple block-mean downsample
    bh = h // size
    bw = w // size
    if bh < 1 or bw < 1:
        return gray.flatten() / max(np.linalg.norm(gray) + 1e-9, 1e-9)
    cropped = gray[: bh * size, : bw * size]
    cropped = cropped.reshape(size, bh, size, bw).mean(axis=(1, 3))
    flat = cropped.flatten()
    norm = float(np.linalg.norm(flat) + 1e-9)
    return flat / norm


def _frame_cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


class SubstrateLibrary:
    """N labelled (visual → audio) substrates plus a visual classifier."""

    def __init__(self) -> None:
        self.entries: dict[str, LibraryEntry] = {}

    def __len__(self) -> int:
        return len(self.entries)

    def labels(self) -> list[str]:
        return list(self.entries.keys())

    def train_pattern(self,
                      label: str,
                      visual_frames: list[np.ndarray] | np.ndarray,
                      audio_samples: np.ndarray,
                      world_factory: Callable,
                      duration_sec: float = 4.0,
                      pulse_period_ticks: int = 30) -> None:
        """Train a fresh substrate on the given (visual, audio) pair.
        `world_factory` returns (world, audio_io, video_io, loop, cfg)."""
        w, audio_io, video_io, loop, cfg = world_factory()

        # Coerce visual_frames to list for iteration
        if isinstance(visual_frames, np.ndarray) and visual_frames.ndim == 3:
            frames = [visual_frames]
        else:
            frames = list(visual_frames)

        # Compute fingerprint as mean of training frames
        if frames:
            mean_frame = np.mean([f.astype(np.float32) for f in frames], axis=0)
            fingerprint = _make_fingerprint(mean_frame)
        else:
            fingerprint = np.zeros(32 * 32, dtype=np.float32)

        n_ticks = int(duration_sec / cfg.dt)
        frame_idx = 0
        for tick_i in range(n_ticks):
            if tick_i % pulse_period_ticks == 0:
                # Cycle through training frames
                frame = frames[frame_idx % len(frames)] if frames else None
                if frame is not None:
                    video_io._write_frame_buffer(frame)
                # Audio is short enough that 0.5 sec / pulse repeats fit in
                audio_block_size = int(0.5 * cfg.audio_sample_rate)
                a0 = (tick_i // pulse_period_ticks) * audio_block_size
                a1 = a0 + audio_block_size
                if a0 < len(audio_samples):
                    block = audio_samples[a0: min(a1, len(audio_samples))]
                    audio_io._write_input_buffer(block)
                frame_idx += 1
            loop.step(cfg.dt)

        self.entries[label] = LibraryEntry(
            label=label, world=w, audio_io=audio_io, video_io=video_io,
            loop=loop, fingerprint=fingerprint,
        )

    def classify(self, frame: np.ndarray) -> Optional[str]:
        """Return the label whose training fingerprint is closest to the
        given frame. None if the library is empty or the best match scores
        below 0 (orthogonal/anti-correlated)."""
        if not self.entries:
            return None
        fp = _make_fingerprint(frame)
        best_label = None
        best_score = -np.inf
        for label, entry in self.entries.items():
            score = _frame_cosine(entry.fingerprint, fp)
            if score > best_score:
                best_score = score
                best_label = label
        if best_score <= 0:
            return None
        return best_label

    def recall(self,
               visual_frame: np.ndarray,
               duration_sec: float = 4.0,
               pulse_period_ticks: int = 30,
               purge_state: bool = True) -> tuple[Optional[str], np.ndarray]:
        """Classify visual_frame, run the matched substrate for
        duration_sec, return (label, audio_output_buffer)."""
        label = self.classify(visual_frame)
        if label is None:
            return None, np.zeros(0, dtype=np.float32)
        entry = self.entries[label]
        w = entry.world
        audio_io = entry.audio_io
        video_io = entry.video_io
        loop = entry.loop
        cfg = w.config

        # Optional state purge so test phase is clean
        if purge_state:
            w.s_alive[:] = False
            w.n_alive = 0
            K_now = w.k_count
            w.k_charge[:K_now] = 0.0
            w.k_refractory_until[:K_now] = 0.0
            audio_io._read_input_buffer(len(audio_io._input_buffer))
            n_drain = ((audio_io._output_write_pos - audio_io._output_read_pos)
                       % len(audio_io._output_buffer))
            if n_drain > 0:
                audio_io._read_output_buffer(n_drain)

        # Run the matched substrate with the visual stimulus only
        n_ticks = int(duration_sec / cfg.dt)
        for tick_i in range(n_ticks):
            if tick_i % pulse_period_ticks == 0:
                video_io._write_frame_buffer(visual_frame)
            loop.step(cfg.dt)

        # Drain audio output
        n_out = ((audio_io._output_write_pos - audio_io._output_read_pos)
                 % len(audio_io._output_buffer))
        if n_out == 0:
            return label, np.zeros(0, dtype=np.float32)
        audio_out = audio_io._read_output_buffer(n_out)
        return label, audio_out

    def save_to_dir(self, base_dir: Path) -> None:
        """Snapshot every substrate + fingerprint to base_dir/<label>/."""
        base_dir = Path(base_dir)
        base_dir.mkdir(parents=True, exist_ok=True)
        for label, entry in self.entries.items():
            entry_dir = base_dir / label
            entry_dir.mkdir(exist_ok=True)
            save_snapshot(entry.world, entry_dir / "world.npz")
            np.save(entry_dir / "fingerprint.npy", entry.fingerprint)

    def load_from_dir(self, base_dir: Path,
                      world_factory: Callable) -> None:
        """Restore a library from a directory written by save_to_dir."""
        base_dir = Path(base_dir)
        if not base_dir.exists():
            return
        for entry_dir in sorted(base_dir.iterdir()):
            if not entry_dir.is_dir():
                continue
            world_path = entry_dir / "world.npz"
            fp_path = entry_dir / "fingerprint.npy"
            if not (world_path.exists() and fp_path.exists()):
                continue
            label = entry_dir.name
            # Build fresh I/O wrappers for the loaded world
            _, audio_io, video_io, loop, _ = world_factory()
            try:
                w_loaded = load_snapshot(world_path)
            except Exception:
                continue
            # Rewire loop's world reference (loop holds the world)
            loop.world = w_loaded
            fingerprint = np.load(fp_path)
            self.entries[label] = LibraryEntry(
                label=label, world=w_loaded, audio_io=audio_io,
                video_io=video_io, loop=loop, fingerprint=fingerprint,
            )

"""Duck-typed AudioIO replacement that feeds audio from a corpus file.

Where :class:`agent.audio_io.AudioIO` reads from a live microphone via
sounddevice, :class:`CorpusAudioFeeder` reads from an on-disk f32.raw
file produced by :class:`agent.corpus_builder.CorpusBuilder`. Both
expose the same ``inject_into_substrate(world, dt)`` contract so the
autonomous loop's awake-phase hook (see
``agent/autonomous_loop.py:225``) can consume either without caring
which one is wired in.

Per the predictive-babble spec
(``docs/superpowers/specs/2026-05-10-predictive-babble-design.md``),
the trained substrate trains on offline corpora across four stages.
Live mic is only stage 4 (webcam recording). For stages 1-3 — and for
all three controls (white-noise / reversed-DE / French) at all four
stages — the substrate must read from a file feeder, not from a real
mic. This module is that feeder.

Implementation mirrors the encoding+injection logic in
:meth:`agent.audio_io.AudioIO.inject_into_substrate` so the substrate
sees the *same* per-frequency vibration emissions regardless of source.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import numpy as np

from agent.encoder_audio import encode_block, freq_to_port_position

if TYPE_CHECKING:  # avoid runtime import cycle with world.state
    from world.state import World


@dataclass
class CorpusAudioFeeder:
    """File-backed analogue of :class:`agent.audio_io.AudioIO`.

    Holds the active stage's audio in memory (loaded via
    :func:`numpy.fromfile`) and drains it sequentially on each
    :meth:`inject_into_substrate` call. When the corpus is exhausted
    the read pointer wraps to the start of the file so a long training
    run on one stage continues uninterrupted (the curriculum
    scheduler, not the feeder, decides when to advance to the next
    stage).

    The constructor takes only the substrate-facing audio parameters
    that matter for encoding. Port geometry defaults match
    :class:`agent.audio_io.AudioIO`'s defaults so a feeder built with
    no overrides drops into a default-configured world correctly.
    """

    sample_rate: int = 16000
    block_size: int = 256
    fft_size: int = 512
    amplitude_threshold: float = 0.01
    freq_min: float = 50.0
    freq_max: float = 8000.0
    input_port_origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    input_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
    emit_pair_band: float = 0.0
    rng: Optional[np.random.Generator] = None
    # Saturation guard: cap on vibrations injected PER ``inject_into_substrate``
    # call. The encoder emits one (freq, amplitude, polarity) per non-trivial
    # STFT bin per block; for high-entropy audio (white noise, multi-speaker
    # mix) that's 150–200 emissions × 30+ blocks per dt=0.5s call ≈ thousands
    # of vibrations. Without a cap, the substrate's audio_input port saturates
    # toward n_nodes_max=4096 within a few cycles, physics tick scales O(N²),
    # and a single awake phase takes 30+ minutes of wall-clock — controls
    # stall indefinitely. We keep only the top-K emissions by amplitude per
    # call, where K = max_vibrations_per_inject. Default 256 retains rich
    # spectral information for clean audio (trained_de) while bounding the
    # worst case for noisy audio. Set to 0 to disable the cap.
    max_vibrations_per_inject: int = 256

    # Internal state (not parameters; populated by load_stage).
    _audio: np.ndarray = field(
        default_factory=lambda: np.zeros(0, dtype=np.float32),
        init=False, repr=False,
    )
    _read_pos: int = field(default=0, init=False, repr=False)
    _current_stage_path: Optional[Path] = field(
        default=None, init=False, repr=False,
    )

    def __post_init__(self) -> None:
        if self.rng is None:
            self.rng = np.random.default_rng()

    # ------------------------------------------------------------------
    # Stage loading
    # ------------------------------------------------------------------

    def load_stage(self, train_path: Path, manifest_path: Path) -> None:
        """Replace the active corpus with a new stage.

        ``train_path`` must point at an f32.raw file (one mono float32
        sample per 4 bytes). ``manifest_path`` is read for the
        sample-rate cross-check; if the manifest's sample rate does
        not match this feeder's ``sample_rate`` we raise rather than
        silently mis-encode.

        Idempotent: loading the same path twice resets the pointer to
        zero (the substrate's training pass through this stage starts
        fresh whether or not it was already loaded).
        """
        train_path = Path(train_path)
        manifest_path = Path(manifest_path)
        if not train_path.exists():
            raise FileNotFoundError(
                f"corpus train file not found: {train_path}"
            )
        if not manifest_path.exists():
            raise FileNotFoundError(
                f"corpus manifest not found: {manifest_path}"
            )

        # Manifest sample-rate cross-check. Two formats are accepted:
        # the per-substrate split format produced by CorpusBuilder
        # (``{"sample_rate": 16000, "splits": {...}}``) and the simpler
        # mini-mode manifest (``{"sample_rate": 16000, "n_samples": ...}``).
        import json
        manifest = json.loads(manifest_path.read_text())
        manifest_sr = int(manifest.get("sample_rate", self.sample_rate))
        if manifest_sr != self.sample_rate:
            raise ValueError(
                f"manifest sample rate {manifest_sr} does not match "
                f"feeder sample rate {self.sample_rate}; resample "
                "upstream rather than silently reinterpreting samples"
            )

        audio = np.fromfile(train_path, dtype=np.float32)
        if audio.size == 0:
            raise ValueError(
                f"corpus train file is empty: {train_path}"
            )

        self._audio = audio
        self._read_pos = 0
        self._current_stage_path = train_path

    # ------------------------------------------------------------------
    # Pointer management
    # ------------------------------------------------------------------

    @property
    def current_stage_path(self) -> Optional[Path]:
        """Path of the currently loaded stage, or ``None`` if unloaded."""
        return self._current_stage_path

    def reset(self) -> None:
        """Rewind to the start of the currently loaded stage."""
        self._read_pos = 0

    def _next_block(self, n_samples: int) -> np.ndarray:
        """Return ``n_samples`` from the audio buffer, wrapping at the end.

        If the corpus is shorter than ``n_samples`` we tile from the
        start. The read pointer always lands on
        ``(start + n_samples) mod len`` so the next call resumes
        exactly where this one finished.
        """
        if self._audio.size == 0:
            return np.zeros(0, dtype=np.float32)
        if n_samples <= 0:
            return np.zeros(0, dtype=np.float32)

        L = self._audio.size
        # Build the slice in at most two pieces so the wrap is explicit.
        start = int(self._read_pos % L)
        remaining = n_samples
        chunks: list[np.ndarray] = []
        while remaining > 0:
            tail = L - start
            take = min(tail, remaining)
            chunks.append(self._audio[start:start + take])
            remaining -= take
            start = (start + take) % L
        out = np.concatenate(chunks).astype(np.float32, copy=False)
        self._read_pos = start
        return out

    # ------------------------------------------------------------------
    # Substrate injection (mirrors agent.audio_io.AudioIO)
    # ------------------------------------------------------------------

    def inject_into_substrate(self, world: "World", dt: float) -> int:
        """Read ``int(dt * sample_rate)`` samples and inject them.

        Mirrors :meth:`agent.audio_io.AudioIO.inject_into_substrate` so
        the substrate sees identical per-frequency vibration emissions
        whether the source is a live mic or a corpus file.

        Returns the number of vibrations injected. ``0`` if no stage
        is loaded.
        """
        if self._current_stage_path is None or self._audio.size == 0:
            return 0

        n_samples_to_drain = int(float(dt) * self.sample_rate)
        if n_samples_to_drain <= 0:
            return 0

        audio = self._next_block(n_samples_to_drain)
        if audio.size == 0:
            return 0

        n_blocks = audio.size // self.block_size
        n_injected = 0
        # Collect all emissions across all blocks first, then top-K-cap by
        # amplitude before injection. Without this cap, high-entropy audio
        # (white noise) floods n_nodes_max=4096 atoms within a few cycles
        # and tick-time becomes prohibitive.
        all_emissions: list[tuple[float, float, bool]] = []
        for b in range(n_blocks):
            block = audio[b * self.block_size : (b + 1) * self.block_size]
            if block.size < self.fft_size:
                block = np.pad(block, (0, self.fft_size - block.size))
            emissions = encode_block(
                block,
                sample_rate=self.sample_rate,
                fft_size=self.fft_size,
                amplitude_threshold=self.amplitude_threshold,
                freq_min=self.freq_min,
                freq_max=self.freq_max,
            )
            all_emissions.extend(emissions)

        # Top-K cap by amplitude descending. amplitude is the second
        # element of each emission tuple. cap=0 disables; otherwise keep
        # the K most energetic emissions and drop the rest.
        if self.max_vibrations_per_inject > 0 and \
                len(all_emissions) > self.max_vibrations_per_inject:
            all_emissions.sort(key=lambda e: e[1], reverse=True)
            all_emissions = all_emissions[: self.max_vibrations_per_inject]

        for f, _amplitude, polarity in all_emissions:
            pos = freq_to_port_position(
                f,
                freq_min=self.freq_min,
                freq_max=self.freq_max,
                port_origin=self.input_port_origin,
                port_size=self.input_port_size,
                rng=self.rng,
            )
            free_idx = np.where(~world.s_alive)[0]
            if len(free_idx) == 0:
                break
            i = int(free_idx[0])
            world.s_pos[i] = pos
            world.s_vel[i] = 0.0
            world.s_freq[i] = float(f)
            world.s_pol[i] = polarity
            world.s_alive[i] = True
            world.n_alive = max(world.n_alive, i + 1)
            n_injected += 1
            # Optional 8 %-band pair injection — same semantics as
            # AudioIO: helps atoms form quickly at the input port
            # under deterministic stimuli.
            if self.emit_pair_band > 0.0:
                free_idx = np.where(~world.s_alive)[0]
                if len(free_idx) == 0:
                    break
                j = int(free_idx[0])
                world.s_pos[j] = pos
                world.s_vel[j] = 0.0
                world.s_freq[j] = float(f) * (1.0 + self.emit_pair_band)
                world.s_pol[j] = (not polarity)
                world.s_alive[j] = True
                world.n_alive = max(world.n_alive, j + 1)
                n_injected += 1
        return n_injected

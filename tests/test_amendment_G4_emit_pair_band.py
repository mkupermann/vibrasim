"""G4 — audio/video encoder frequency-pair broadening.

CONCEPT §10.8 candidate amendment 3 (frequency-broadening at input ports):
under deterministic structured stimuli (single audio tones, oriented filter
peaks) the substrate's 8 %-rule binding has no compatible pair partners and
input-port atoms form too sparsely to feed the chain. G4 lets the encoder
inject an 8 %-pair partner alongside every primary emission, with opposite
polarity, so a binding-eligible pair is delivered in one inject call.

Default: 0.0 (off). Behaviour-equivalent to pre-amendment.

G4-1: AudioIO.emit_pair_band=0 → 1 vibration per emission (regression).
G4-2: AudioIO.emit_pair_band=0.08 → 2 vibrations per emission, paired by
      8 % freq + opposite polarity, ready to bind.
G4-3: VideoIO.emit_pair_band=0.08 → same pattern at video port.
G4-4: WorldConfig defaults audio_emit_pair_band=0.0, video_emit_pair_band=0.0.
"""
import numpy as np
import pytest

from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO
from agent.video_io import VideoIO


def _synth_tone(freq: float, duration: float, sample_rate: int = 16000,
                amplitude: float = 1.0) -> np.ndarray:
    t = np.arange(int(sample_rate * duration)) / sample_rate
    return (amplitude * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _make_world() -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=512, n_nodes_max=64,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
    )
    return World(cfg)


def test_G4_audio_emit_pair_band_off_legacy_count():
    """emit_pair_band=0 → exactly one vibration per emission (regression)."""
    w = _make_world()
    audio_io = AudioIO(
        sample_rate=16000, block_size=256, fft_size=512,
        amplitude_threshold=0.05,
        emit_pair_band=0.0,
        rng=np.random.default_rng(42),
    )
    audio_io._write_input_buffer(_synth_tone(1000.0, 0.5, amplitude=1.0))
    n_injected = audio_io.inject_into_substrate(w, dt=0.5)
    assert n_injected > 0, "G4-1: emission should fire under loud tone"
    # Every injected vibration should be at exactly the input frequency
    # band (no paired f * 1.08 vibrations).
    n_alive = int(w.s_alive[:w.n_alive].sum())
    freqs = w.s_freq[:w.n_alive][w.s_alive[:w.n_alive]]
    assert n_alive == n_injected, (
        f"G4-1: emit_pair_band=0 must produce 1 vib per emission; "
        f"got {n_alive} for {n_injected} emissions"
    )


def test_G4_audio_emit_pair_band_on_doubles_count_and_pairs_freqs():
    """emit_pair_band=0.08 → 2 vibrations per emission, 8 %-paired,
    opposite polarity."""
    w = _make_world()
    audio_io = AudioIO(
        sample_rate=16000, block_size=256, fft_size=512,
        amplitude_threshold=0.05,
        emit_pair_band=0.08,
        rng=np.random.default_rng(42),
    )
    audio_io._write_input_buffer(_synth_tone(1000.0, 0.5, amplitude=1.0))
    n_injected = audio_io.inject_into_substrate(w, dt=0.5)
    assert n_injected > 0, "G4-2: emission should fire under loud tone"
    assert n_injected % 2 == 0, (
        f"G4-2: emit_pair_band > 0 must inject vibrations in pairs; got odd {n_injected}"
    )
    # Group consecutive (i, i+1) and check the pair invariant.
    alive_mask = w.s_alive[:w.n_alive]
    alive_indices = np.where(alive_mask)[0]
    assert len(alive_indices) == n_injected
    for k in range(0, len(alive_indices), 2):
        i, j = alive_indices[k], alive_indices[k + 1]
        f_i, f_j = float(w.s_freq[i]), float(w.s_freq[j])
        ratio = abs(f_j - f_i) / min(f_i, f_j)
        assert abs(ratio - 0.08) < 1e-9, (
            f"G4-2: pair {k//2} freq ratio {ratio:.6f} ≠ 0.08 "
            f"(f_i={f_i}, f_j={f_j})"
        )
        assert bool(w.s_pol[i]) != bool(w.s_pol[j]), (
            f"G4-2: pair {k//2} polarities must differ"
        )


def test_G4_video_emit_pair_band_on_doubles_count():
    """VideoIO.emit_pair_band=0.08 → injected count is even (pairs)."""
    w = _make_world()
    video_io = VideoIO(
        fps=30, buffer_seconds=0.5, patch_grid=(4, 4),
        n_orientations=4, amplitude_threshold=0.01,
        emit_pair_band=0.08,
        rng=np.random.default_rng(42),
    )
    # Synthetic frame with a strong vertical edge in one patch
    frame = np.zeros((128, 128, 3), dtype=np.uint8)
    frame[:, 64:, :] = 255
    video_io._write_frame_buffer(frame)
    n_injected = video_io.inject_into_substrate(w, dt=1.0 / 30)
    assert n_injected > 0, "G4-3: video emission should fire on hard edge"
    assert n_injected % 2 == 0, (
        f"G4-3: video emit_pair_band > 0 must inject in pairs; got {n_injected}"
    )


def test_G4_default_off_in_world_config():
    """Default cfg has emit_pair_band=0.0 for both encoders (regression)."""
    cfg = WorldConfig()
    assert cfg.audio_emit_pair_band == 0.0
    assert cfg.video_emit_pair_band == 0.0

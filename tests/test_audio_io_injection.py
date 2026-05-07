"""Tests for AudioIO.inject_into_substrate (AC6)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO


def _world_for_audio():
    return World(WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=512,
        box_size=(60.0, 60.0, 60.0),
        audio_io_enabled=True,
        audio_input_port_origin=(0.0, 0.0, 0.0),
        audio_input_port_size=(15.0, 15.0, 15.0),
    ))


def test_AC6_inject_into_substrate_creates_vibrations_in_input_port():
    """Synthetic 1 kHz tone in input buffer → vibrations injected at the
    1 kHz-mapped position inside the input port."""
    w = _world_for_audio()
    io = AudioIO(
        sample_rate=16000, block_size=256, buffer_seconds=1.0,
        input_port_origin=(0.0, 0.0, 0.0),
        input_port_size=(15.0, 15.0, 15.0),
    )
    # Without starting threads, write a 1 kHz tone directly into the input buffer
    sample_rate = 16000
    duration = 0.5  # 500 ms
    n = int(sample_rate * duration)
    t = np.arange(n) / sample_rate
    audio = (0.5 * np.sin(2 * np.pi * 1000 * t)).astype(np.float32)
    io._write_input_buffer(audio)

    n_alive_before = int(w.s_alive.sum())
    n_injected = io.inject_into_substrate(w, dt=duration)
    n_alive_after = int(w.s_alive.sum())

    assert n_injected > 0, f"AC6: no vibrations injected"
    assert n_alive_after > n_alive_before
    # All injected vibrations within the input port box
    new_indices = np.where(w.s_alive)[0]
    pos = w.s_pos[new_indices]
    assert ((pos[:, 0] >= 0.0) & (pos[:, 0] <= 15.0)).all()
    assert ((pos[:, 1] >= 0.0) & (pos[:, 1] <= 15.0)).all()
    assert ((pos[:, 2] >= 0.0) & (pos[:, 2] <= 15.0)).all()
    # Frequencies near 1 kHz
    freqs = w.s_freq[new_indices]
    assert (np.abs(freqs - 1000.0) < 200.0).any()

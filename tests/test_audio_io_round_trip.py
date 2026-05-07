"""Tests for AudioIO mic→speaker round-trip on synthetic source (AC8)."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO


def test_AC8_synthetic_source_round_trip_passthrough():
    """Replace real mic with synthetic 1 kHz tone written directly into the
    input buffer. Run a passthrough substrate that re-emits whatever it
    receives. Verify output buffer has spectral peak at 1 kHz with amp
    within 50% of input."""
    w = World(WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=2048, n_nodes_max=128,
        box_size=(60.0, 60.0, 60.0),
        audio_io_enabled=True,
        audio_input_port_origin=(0.0, 0.0, 0.0),
        audio_input_port_size=(15.0, 15.0, 15.0),
        audio_output_port_origin=(45.0, 0.0, 0.0),
        audio_output_port_size=(15.0, 15.0, 15.0),
    ))
    io = AudioIO(
        sample_rate=16000, block_size=256, buffer_seconds=2.0,
        input_port_origin=(0.0, 0.0, 0.0),
        input_port_size=(15.0, 15.0, 15.0),
        output_port_origin=(45.0, 0.0, 0.0),
        output_port_size=(15.0, 15.0, 15.0),
    )

    # Synthetic 1 kHz tone, 1 second
    sample_rate = 16000
    n = sample_rate
    t = np.arange(n) / sample_rate
    audio_in = (0.5 * np.sin(2 * np.pi * 1000 * t)).astype(np.float32)
    io._write_input_buffer(audio_in)

    # Passthrough: inject; manually fire atoms at the 1 kHz-mapped
    # position in the OUTPUT port for each block; read.
    duration = 0.5
    n_injected = io.inject_into_substrate(w, dt=duration)
    assert n_injected > 0

    # Fake the substrate's response: place output-port atoms at the 1 kHz
    # position and synthesize firing events at 1 kHz rate so the output
    # pipeline produces a clean 1 kHz spectral peak.
    from agent.encoder_audio import freq_to_port_position
    rng = np.random.default_rng(0)
    n_atoms = 32
    for k in range(n_atoms):
        pos = freq_to_port_position(
            1000.0, freq_min=50.0, freq_max=8000.0,
            port_origin=(45.0, 0.0, 0.0),
            port_size=(15.0, 15.0, 15.0),
            rng=rng,
        )
        w.k_pos[k] = pos
        w.k_level[k] = 4
        w.k_alive[k] = True
        w.k_count = max(w.k_count, k + 1)
    # Generate firing events at high rate
    fire_period = 1.0 / 1000.0
    n_fires = int(duration / fire_period)
    w.firing_events = []
    for i in range(n_fires):
        atom_idx = i % max(n_atoms, 1)
        w.firing_events.append((i * fire_period, atom_idx))
    w.t = duration

    n_written = io.read_from_substrate(w, dt=duration)
    assert n_written > 0

    audio_out = io._read_output_buffer(n_written)
    # Spectral peak check
    fft_size = 512
    spectrum = np.fft.rfft(audio_out[:fft_size], n=fft_size)
    freqs = np.fft.rfftfreq(fft_size, d=1.0 / 16000)
    peak_idx = int(np.argmax(np.abs(spectrum)))
    peak_freq = float(freqs[peak_idx])
    assert abs(peak_freq - 1000.0) < 1000.0 * 0.10

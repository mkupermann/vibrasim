"""Tests for AudioIO.read_from_substrate (AC7)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO


def test_AC7_read_from_substrate_produces_audio_from_firings():
    """Manually fire atoms inside output port at 1 kHz position; read produces
    audio with spectral peak near 1 kHz."""
    w = World(WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=512, n_nodes_max=64,
        box_size=(60.0, 60.0, 60.0),
        audio_io_enabled=True,
        audio_output_port_origin=(45.0, 0.0, 0.0),
        audio_output_port_size=(15.0, 15.0, 15.0),
    ))
    io = AudioIO(
        sample_rate=16000, block_size=256, buffer_seconds=1.0,
        output_port_origin=(45.0, 0.0, 0.0),
        output_port_size=(15.0, 15.0, 15.0),
    )

    # Fake firings: place atoms at the 1 kHz-mapped position inside the
    # output port and fill firing_events.
    from agent.encoder_audio import freq_to_port_position
    rng = np.random.default_rng(0)
    n_atoms = 8
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

    # Synthesize firing events at 1 kHz rate over 0.5 sim-sec
    duration = 0.5
    fire_period = 1.0 / 1000.0
    n_fires = int(duration / fire_period)
    for i in range(n_fires):
        atom_idx = i % n_atoms
        w.firing_events.append((i * fire_period, atom_idx))
    w.t = duration

    n_written = io.read_from_substrate(w, dt=duration)
    assert n_written > 0, "AC7: no audio samples written"

    # Drain output buffer and check spectral peak
    audio = io._read_output_buffer(n_written)
    assert len(audio) > 256
    # Take the first FFT-size window and check peak
    fft_size = 512
    spectrum = np.fft.rfft(audio[:fft_size], n=fft_size)
    freqs = np.fft.rfftfreq(fft_size, d=1.0 / 16000)
    peak_idx = int(np.argmax(np.abs(spectrum)))
    peak_freq = float(freqs[peak_idx])
    assert abs(peak_freq - 1000.0) < 1000.0 * 0.10, (
        f"AC7: decoded peak at {peak_freq} Hz, expected near 1000 Hz"
    )

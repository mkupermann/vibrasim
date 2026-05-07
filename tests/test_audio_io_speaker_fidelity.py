"""Headline integration test I2 — speaker fidelity."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO
from agent.encoder_audio import freq_to_port_position


def test_I2_speaker_fidelity():
    """Manually fire atoms at the 440 Hz-mapped position in the output port for
    5 sim-sec; output audio has spectral peak at 440 Hz ±5%."""
    w = World(WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=128, n_nodes_max=64,
        box_size=(60.0, 60.0, 60.0),
        audio_io_enabled=True,
        audio_output_port_origin=(45.0, 0.0, 0.0),
        audio_output_port_size=(15.0, 15.0, 15.0),
        rng_seed=42,
    ))
    io = AudioIO(
        sample_rate=16000, block_size=256, buffer_seconds=10.0,
        output_port_origin=(45.0, 0.0, 0.0),
        output_port_size=(15.0, 15.0, 15.0),
        rng=np.random.default_rng(42),
    )

    # Place 16 atoms at 440 Hz-mapped position
    rng = np.random.default_rng(42)
    n_atoms = 16
    for k in range(n_atoms):
        pos = freq_to_port_position(
            440.0, freq_min=50.0, freq_max=8000.0,
            port_origin=(45.0, 0.0, 0.0), port_size=(15.0, 15.0, 15.0),
            rng=rng,
        )
        w.k_pos[k] = pos
        w.k_level[k] = 4
        w.k_alive[k] = True
        w.k_count = max(w.k_count, k + 1)

    # Synthesize firing events at 440 Hz over 5 sim-sec
    duration = 5.0
    fire_period = 1.0 / 440.0
    n_fires = int(duration / fire_period)
    w.firing_events = []
    for i in range(n_fires):
        atom_idx = i % n_atoms
        w.firing_events.append((i * fire_period, atom_idx))
    w.t = duration

    n_written = io.read_from_substrate(w, dt=duration)
    assert n_written > 0

    audio = io._read_output_buffer(n_written)
    # Take a chunk near the middle to avoid block-boundary artifacts
    chunk = audio[len(audio) // 4 : len(audio) // 4 + 2048]
    if len(chunk) < 1024:
        chunk = audio[:2048]
    fft_size = 2048
    spectrum = np.fft.rfft(chunk[:fft_size], n=fft_size)
    freqs = np.fft.rfftfreq(fft_size, d=1.0 / 16000)
    peak_idx = int(np.argmax(np.abs(spectrum)))
    peak_freq = float(freqs[peak_idx])
    assert abs(peak_freq - 440.0) < 440.0 * 0.05, (
        f"I2: peak at {peak_freq:.1f} Hz, expected 440 Hz ±5%"
    )

"""Headline integration test I1 — tonotopic correctness."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO


def test_I1_tonotopic_correctness():
    """Inject a 440 Hz tone for 5 sim-sec; verify vibration positions are
    localised within ±5% of the 440 Hz-mapped position along the tonotopic
    axis."""
    w = World(WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=8192,
        box_size=(60.0, 60.0, 60.0),
        audio_io_enabled=True,
        audio_input_port_origin=(0.0, 0.0, 0.0),
        audio_input_port_size=(15.0, 15.0, 15.0),
        rng_seed=42,
    ))
    io = AudioIO(
        sample_rate=16000, block_size=256, buffer_seconds=10.0,
        input_port_origin=(0.0, 0.0, 0.0),
        input_port_size=(15.0, 15.0, 15.0),
        rng=np.random.default_rng(42),
    )

    # 5 sim-seconds of 440 Hz tone
    sample_rate = 16000
    duration = 5.0
    n = int(sample_rate * duration)
    t = np.arange(n) / sample_rate
    audio = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    io._write_input_buffer(audio)

    n_injected = io.inject_into_substrate(w, dt=duration)
    assert n_injected > 0

    # Compute expected 440 Hz x-position
    log_440 = np.log(440.0)
    log_min = np.log(50.0)
    log_max = np.log(8000.0)
    expected_x = (log_440 - log_min) / (log_max - log_min) * 15.0  # port_size_x = 15

    alive = np.where(w.s_alive)[0]
    xs = w.s_pos[alive, 0]
    median_x = float(np.median(xs))
    assert abs(median_x - expected_x) < 0.05 * 15.0, (
        f"I1: median x={median_x:.2f}, expected ~{expected_x:.2f} (±5%)"
    )

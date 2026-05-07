"""Plumbing test — inject + tick + read loop does not crash or saturate
buffers under sustained synthetic input. Slow.

Final-review note: this test was originally framed as "I3 — closed-loop
stability under live audio" but the quiet 0.1×normal noise produces no
emissions above amplitude_threshold (encode_block normalises by fft_size
so per-bin amplitudes land below 0.01). The substrate therefore never
fires; this test only verifies that the inject + tick + read pipeline
itself is structurally sound and does not blow up.

A genuine closed-loop stability test (where the substrate fires
continuously under live audio) requires substrate read-out tuning
beyond Plan C's scope and lands as a Plan C.5 follow-up."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO


@pytest.mark.slow
def test_I3_inject_tick_read_plumbing_does_not_crash():
    """30 sim-sec of quiet synthetic noise through inject + tick + read.
    Substrate vibration buffer must not saturate; circular buffer fill
    stays under 80%."""
    w = World(WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=4096, n_nodes_max=128,
        box_size=(60.0, 60.0, 60.0),
        audio_io_enabled=True,
        rng_seed=42,
        # Disable ambient gen so the test is scoped to audio drive only.
        # (Without this, ambient regen exhausts node slots in <1 sim-sec
        # regardless of n_nodes_max.)
        lambda_gen=0.0,
        lambda_dec=0.0,
    ))
    io = AudioIO(
        sample_rate=16000, block_size=256, buffer_seconds=4.0,
        input_port_origin=(0.0, 0.0, 0.0), input_port_size=(15.0, 15.0, 15.0),
        output_port_origin=(45.0, 0.0, 0.0), output_port_size=(15.0, 15.0, 15.0),
        rng=np.random.default_rng(42),
    )

    sample_rate = 16000
    duration = 30.0
    rng = np.random.default_rng(0)
    audio = (0.1 * rng.standard_normal(int(sample_rate * duration))).astype(np.float32)

    from world.physics import tick
    dt_chunk = 1.0
    samples_per_chunk = int(sample_rate * dt_chunk)
    max_alive = 0
    max_buffer_pct = 0.0
    for chunk in range(int(duration / dt_chunk)):
        start = chunk * samples_per_chunk
        end = min(start + samples_per_chunk, len(audio))
        io._write_input_buffer(audio[start:end])

        io.inject_into_substrate(w, dt=dt_chunk)
        n_ticks = int(dt_chunk / w.config.dt)
        for _ in range(n_ticks):
            tick(w, w.config.dt)
        n_out = io.read_from_substrate(w, dt=dt_chunk)
        # Drain output buffer to simulate the playback callback;
        # otherwise it fills with silent blocks every tick.
        if n_out > 0:
            io._read_output_buffer(n_out)

        max_alive = max(max_alive, int(w.s_alive.sum()))
        with io._input_lock:
            in_fill = (io._input_write_pos - io._input_read_pos) % len(io._input_buffer)
        with io._output_lock:
            out_fill = (io._output_write_pos - io._output_read_pos) % len(io._output_buffer)
        in_pct = in_fill / len(io._input_buffer)
        out_pct = out_fill / len(io._output_buffer)
        max_buffer_pct = max(max_buffer_pct, in_pct, out_pct)

    print(f"I3 plumbing: max alive vibrations = {max_alive}, max buffer fill = {max_buffer_pct:.2%}")
    assert max_alive < w.config.n_vibrations_max, "Plumbing test: vibration buffer saturated"
    assert max_buffer_pct < 0.80, f"Plumbing test: max buffer fill {max_buffer_pct:.2%} exceeds 80%"

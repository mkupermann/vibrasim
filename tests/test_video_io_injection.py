"""Tests for VideoIO.inject_into_substrate (VC7)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from agent.video_io import VideoIO


def _world_for_video():
    return World(WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=2048,
        box_size=(60.0, 60.0, 60.0),
        video_io_enabled=True,
        video_input_port_origin=(0.0, 0.0, 45.0),
        video_input_port_size=(15.0, 15.0, 15.0),
    ))


def test_VC7_inject_creates_vibrations_in_video_port():
    """Synthetic frame with a vertical bright bar → injected vibrations
    cluster on that column inside the video port."""
    w = _world_for_video()
    io = VideoIO(
        fps=30, buffer_seconds=1.0,
        patch_grid=(16, 16), n_orientations=8,
        amplitude_threshold=0.05,
        video_port_origin=(0.0, 0.0, 45.0),
        video_port_size=(15.0, 15.0, 15.0),
    )
    # Synthetic 640×480 frame: vertical bright bar in the right half
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:, 320:, :] = 255
    io._write_frame_buffer(frame)

    n_alive_before = int(w.s_alive.sum())
    n_injected = io.inject_into_substrate(w, dt=1.0 / 30)
    n_alive_after = int(w.s_alive.sum())

    assert n_injected > 0, "VC7: no vibrations injected from a bright-bar frame"
    assert n_alive_after > n_alive_before
    # All injected vibrations within the video port box
    new_indices = np.where(w.s_alive)[0]
    pos = w.s_pos[new_indices]
    assert ((pos[:, 0] >= 0.0) & (pos[:, 0] <= 15.0)).all()
    assert ((pos[:, 1] >= 0.0) & (pos[:, 1] <= 15.0)).all()
    assert ((pos[:, 2] >= 45.0) & (pos[:, 2] <= 60.0)).all()

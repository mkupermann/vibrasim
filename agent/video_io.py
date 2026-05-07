"""Plan D — live webcam capture into the substrate's video input port."""
import threading
from collections import deque
from typing import Optional
import numpy as np

from agent.encoder_video import (
    downsample_frame,
    build_oriented_filter_bank,
    encode_frame,
    patch_to_port_position,
    feature_magnitude_to_frequency,
)


class VideoIO:
    """Live webcam → vibration injections into the video input port.

    One background thread (capture) and one circular frame buffer. The
    main substrate thread calls inject_into_substrate() once per tick;
    VideoIO does not run the substrate.
    """

    def __init__(
        self,
        fps: int = 30,
        buffer_seconds: float = 5.0,
        patch_grid: tuple[int, int] = (16, 16),
        n_orientations: int = 8,
        amplitude_threshold: float = 0.05,
        video_port_origin: tuple[float, float, float] = (0.0, 0.0, 45.0),
        video_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
        freq_min: float = 1000.0,
        freq_max: float = 12000.0,
        webcam_index: int = 0,
        rng: Optional[np.random.Generator] = None,
    ):
        self.fps = fps
        self.buffer_seconds = buffer_seconds
        self.patch_grid = patch_grid
        self.n_orientations = n_orientations
        self.amplitude_threshold = amplitude_threshold
        self.video_port_origin = video_port_origin
        self.video_port_size = video_port_size
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.webcam_index = webcam_index
        self.rng = rng if rng is not None else np.random.default_rng()

        self._filter_bank = build_oriented_filter_bank(
            kernel_size=5, orientations_deg=None,
        )

        max_frames = int(fps * buffer_seconds)
        self._frame_buffer: deque[np.ndarray] = deque(maxlen=max_frames)
        self._frame_lock = threading.Lock()

        self._capture_thread: Optional[threading.Thread] = None
        self._capture_running = False

    def _write_frame_buffer(self, frame: np.ndarray) -> None:
        """Direct write — used by tests and by the capture thread."""
        with self._frame_lock:
            self._frame_buffer.append(frame)

    def _read_latest_frame(self) -> Optional[np.ndarray]:
        """Read the most-recent frame; returns None if buffer is empty."""
        with self._frame_lock:
            if len(self._frame_buffer) == 0:
                return None
            return self._frame_buffer[-1]

    def inject_into_substrate(self, world, dt: float) -> int:
        """Read the most-recent buffered frame; encode features; inject one
        vibration per feature at its retinotopic port position."""
        frame = self._read_latest_frame()
        if frame is None:
            return 0
        downsampled = downsample_frame(frame, output_size=(128, 128))
        features = encode_frame(
            downsampled,
            patch_grid=self.patch_grid,
            filter_bank=self._filter_bank,
            amplitude_threshold=self.amplitude_threshold,
        )
        n_injected = 0
        for px, py, o, magnitude, sign in features:
            pos = patch_to_port_position(
                px, py, o,
                patch_grid=self.patch_grid,
                n_orientations=self.n_orientations,
                port_origin=self.video_port_origin,
                port_size=self.video_port_size,
            )
            f = feature_magnitude_to_frequency(
                magnitude, freq_min=self.freq_min, freq_max=self.freq_max,
            )
            free_idx = np.where(~world.s_alive)[0]
            if len(free_idx) == 0:
                break
            i = int(free_idx[0])
            world.s_pos[i] = pos
            world.s_vel[i] = 0.0
            world.s_freq[i] = float(f)
            world.s_pol[i] = bool(sign)
            world.s_alive[i] = True
            world.n_alive = max(world.n_alive, i + 1)
            n_injected += 1
        return n_injected

    def start(self) -> None:
        """Open webcam; start capture thread.

        Lazy-imports cv2 so substrate-only users don't need OpenCV.
        """
        if self._capture_running:
            return
        import cv2

        cap = cv2.VideoCapture(self.webcam_index)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open webcam at index {self.webcam_index}")

        self._capture_running = True

        def _loop():
            while self._capture_running:
                ok, frame = cap.read()
                if not ok:
                    break
                # cv2 returns BGR; convert to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self._write_frame_buffer(frame_rgb)

        self._capture_thread = threading.Thread(target=_loop, daemon=True)
        self._capture_thread.start()
        self._cap = cap

    def stop(self) -> None:
        if not self._capture_running:
            return
        self._capture_running = False
        if self._capture_thread is not None:
            self._capture_thread.join(timeout=2.0)
            self._capture_thread = None
        if hasattr(self, "_cap"):
            self._cap.release()
            del self._cap

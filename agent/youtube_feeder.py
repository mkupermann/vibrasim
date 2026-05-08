"""YouTube → substrate ingestion.

Downloads a YouTube video, extracts audio + video frames, and feeds them
into a running AudioIO / VideoIO at real-time rate so the substrate
trains on the content.

Usage:
    feeder = YouTubeFeeder(
        url="https://www.youtube.com/watch?v=...",
        audio_io=audio_io,
        video_io=video_io,
        duration_seconds=60.0,    # 0 = play to end
    )
    feeder.start()                # spawns a daemon feeder thread
    # ... substrate runs ...
    feeder.stop()                 # cooperative cancel

Requires the `agent` optional extra (yt-dlp + opencv-python-headless) and
ffmpeg on PATH.
"""
from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional

import numpy as np


def _have_ytdlp() -> bool:
    try:
        import yt_dlp  # noqa: F401
        return True
    except ImportError:
        return False


def _have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


class YouTubeFeeder:
    """Download a YouTube video + stream its audio + video frames into an
    AudioIO and a VideoIO at real-time playback rate.

    The substrate side already runs in real-time mode (AgentLoop's
    `start_realtime`); this feeder just keeps the input buffers full at
    the same rate so the substrate gets continuous audio + video input
    as if from a real mic + webcam.
    """

    def __init__(self, url: str, audio_io, video_io,
                 duration_seconds: float = 60.0,
                 audio_sample_rate: int = 16000,
                 cache_dir: Optional[Path] = None,
                 progress_callback=None):
        if not _have_ytdlp():
            raise RuntimeError(
                "yt-dlp is required. Install with: "
                "uv sync --extra agent  (or: uv pip install yt-dlp)"
            )
        if not _have_ffmpeg():
            raise RuntimeError(
                "ffmpeg is required on PATH for audio extraction. "
                "macOS: brew install ffmpeg. Linux: apt install ffmpeg."
            )
        self.url = url
        self.audio_io = audio_io
        self.video_io = video_io
        self.duration_seconds = float(duration_seconds)
        self.audio_sample_rate = audio_sample_rate
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "eqmod-yt-cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.progress_callback = progress_callback

        self._video_path: Optional[Path] = None
        self._audio_path: Optional[Path] = None
        self._title: str = ""
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._error: Optional[str] = None
        self._progress: dict = {"phase": "idle", "frac": 0.0, "msg": ""}

    # ---------- public API ------------------------------------------------

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._error = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    @property
    def progress(self) -> dict:
        return dict(self._progress)

    @property
    def error(self) -> Optional[str]:
        return self._error

    @property
    def title(self) -> str:
        return self._title

    @property
    def is_running(self) -> bool:
        return self._running

    # ---------- thread ----------------------------------------------------

    def _set_progress(self, phase: str, frac: float = 0.0, msg: str = "") -> None:
        self._progress = {"phase": phase, "frac": frac, "msg": msg}
        if self.progress_callback is not None:
            try:
                self.progress_callback(self._progress)
            except Exception:
                pass

    def _run(self) -> None:
        try:
            self._set_progress("download", 0.0, "fetching URL info")
            self._download()
            self._set_progress("extract", 0.0, "extracting audio")
            self._extract_audio()
            self._set_progress("stream", 0.0, "streaming to substrate")
            self._stream()
            self._set_progress("done", 1.0, "complete")
        except Exception as exc:  # pragma: no cover — IO-dependent
            self._error = str(exc)
            self._set_progress("error", 0.0, str(exc))
        finally:
            self._running = False

    def _download(self) -> None:
        import yt_dlp
        ydl_opts = {
            "format": "best[height<=360][ext=mp4]/best[ext=mp4]/best",
            "outtmpl": str(self.cache_dir / "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=True)
            self._title = info.get("title", "")
            video_path = Path(info["requested_downloads"][0]["filepath"])
            self._video_path = video_path

    def _extract_audio(self) -> None:
        if self._video_path is None:
            raise RuntimeError("video not downloaded")
        self._audio_path = self._video_path.with_suffix(".f32.raw")
        # Single-channel 16 kHz float32 PCM — matches AudioIO's input format
        cmd = [
            "ffmpeg", "-y",
            "-i", str(self._video_path),
            "-ac", "1",
            "-ar", str(self.audio_sample_rate),
            "-f", "f32le",
            "-loglevel", "error",
            str(self._audio_path),
        ]
        subprocess.run(cmd, check=True)

    def _stream(self) -> None:
        import cv2
        if self._video_path is None or self._audio_path is None:
            raise RuntimeError("artefacts missing")

        # Open both streams
        cap = cv2.VideoCapture(str(self._video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        if fps <= 0:
            fps = 30.0
        frame_dt = 1.0 / fps

        audio_data = np.fromfile(str(self._audio_path), dtype=np.float32)
        audio_block_size = int(self.audio_sample_rate * frame_dt)
        n_audio_blocks = len(audio_data) // audio_block_size

        if self.duration_seconds > 0:
            max_blocks = int(self.duration_seconds * fps)
            n_audio_blocks = min(n_audio_blocks, max_blocks)

        t_start = time.perf_counter()
        for block_idx in range(n_audio_blocks):
            if not self._running:
                break
            # Audio: write the block
            a0 = block_idx * audio_block_size
            a1 = a0 + audio_block_size
            self.audio_io._write_input_buffer(audio_data[a0:a1])

            # Video: read a frame and convert BGR → RGB
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.video_io._write_frame_buffer(frame_rgb)

            # Real-time pacing
            target_t = t_start + (block_idx + 1) * frame_dt
            now = time.perf_counter()
            sleep_remaining = target_t - now
            if sleep_remaining > 0:
                time.sleep(min(sleep_remaining, 0.1))

            if block_idx % 30 == 0:
                self._set_progress(
                    "stream",
                    (block_idx + 1) / max(n_audio_blocks, 1),
                    f"frame {block_idx+1}/{n_audio_blocks} of '{self._title[:30]}'",
                )

        cap.release()

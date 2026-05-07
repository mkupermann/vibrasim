"""Plan E — closed-loop orchestrator.

Mode 1 (stepped, Task 6): tests call AgentLoop.step(dt) directly.
Mode 2 (real-time, Task 9): start_realtime spawns a substrate thread.
Mode 3 (demo, Task 10): python -m agent.demo CLI entry point.
"""
import time
from typing import Optional
from world.physics import tick


class AgentLoop:
    """Closed-loop orchestrator. Stepped mode for tests; real-time mode for
    live operation. Audio/video capture+playback threads run independently;
    the loop's substrate path consumes their buffers each tick."""

    def __init__(
        self,
        world,
        audio_io=None,
        video_io=None,
        reward=None,
    ):
        self.world = world
        self.audio_io = audio_io
        self.video_io = video_io
        self.reward = reward
        self._realtime_thread = None
        self._realtime_running = False

    def step(self, dt: float) -> None:
        """One substrate tick + I/O sync. Inject from audio + video first,
        then tick, then read audio output. Reward is fired explicitly by
        the caller (e.g. M5's reward dispenser); the loop doesn't auto-fire."""
        if self.audio_io is not None:
            self.audio_io.inject_into_substrate(self.world, dt)
        if self.video_io is not None:
            self.video_io.inject_into_substrate(self.world, dt)
        tick(self.world, dt)
        if self.audio_io is not None:
            self.audio_io.read_from_substrate(self.world, dt)

    def start_realtime(self) -> None:
        """Spawn a daemon substrate thread that calls step(dt) on a
        target cadence of agent_dt_realtime_ms milliseconds, using
        overshoot-compensated sleep to stay on schedule."""
        if self._realtime_running:
            return
        import threading
        dt = self.world.config.dt
        sleep_s = self.world.config.agent_dt_realtime_ms / 1000.0
        self._realtime_running = True

        def _loop():
            while self._realtime_running:
                t0 = time.perf_counter()
                self.step(dt)
                elapsed = time.perf_counter() - t0
                remaining = sleep_s - elapsed
                if remaining > 0:
                    time.sleep(remaining)

        self._realtime_thread = threading.Thread(target=_loop, daemon=True)
        self._realtime_thread.start()

    def stop_realtime(self) -> None:
        """Signal the substrate thread to stop and join with a 2-second
        timeout."""
        self._realtime_running = False
        if self._realtime_thread is not None:
            self._realtime_thread.join(timeout=2.0)
            self._realtime_thread = None

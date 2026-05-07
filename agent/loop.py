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
        """Spawn substrate thread. Filled in Task 9."""
        raise NotImplementedError("AgentLoop.start_realtime — Task 9")

    def stop_realtime(self) -> None:
        raise NotImplementedError("AgentLoop.stop_realtime — Task 9")

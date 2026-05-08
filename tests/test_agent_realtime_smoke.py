"""AL3 — real-time mode smoke test (slow)."""
import time
import pytest
import numpy as np
from world.config import WorldConfig
from world.state import World
from agent.loop import AgentLoop


@pytest.mark.slow
def test_AL3_realtime_smoke():
    """start_realtime → 5 wall-sec → stop_realtime cleanly. Substrate
    thread joined; vibration count > 0 (something happened); no exceptions."""
    w = World(WorldConfig(
        n_initial_vibrations=80, n_vibrations_max=512,
        box_size=(60.0, 60.0, 60.0),
        agent_dt_realtime_ms=17,
        rng_seed=42,
    ))
    loop = AgentLoop(w)
    loop.start_realtime()
    try:
        time.sleep(5.0)
    finally:
        loop.stop_realtime()
    assert w.t > 0.0, "AL3: substrate thread did not advance world time"
    assert int(w.s_alive.sum()) > 0, "AL3: no vibrations alive after run"

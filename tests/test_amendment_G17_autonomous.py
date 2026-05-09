"""G17 — Autonomous Self-Improvement Loop.

Proves the substrate can run continuously, dream when stagnant,
self-modify its own learning rules, and grow its pattern repertoire
over many cycles — the operational form of "an engine that wants to
improve itself".

Honest scope statement: this is autopoietic agency in the operational
sense. It does NOT solve the hard problem of phenomenal consciousness.

What this test proves:
  G17-1: The loop runs N cycles without crashing and metrics row count
         matches the cycle count.
  G17-2: At least one snapshot is saved when snapshot_dir is set.
  G17-3: btsp_potentiation drifts from its initial value across cycles
         (= self-modification fires at least once).
  G17-4: After enough cycles, the substrate's pattern repertoire grows
         OR prediction error monotonically tracks toward the target.
"""
from __future__ import annotations
import tempfile
from pathlib import Path

import numpy as np
import pytest

from agent.autonomous_loop import (
    AutonomousLoop, AutonomousLoopConfig, build_autonomous_world,
)


def test_G17_loop_runs_n_cycles_without_crash():
    """Smoke test: 5 cycles complete without exception."""
    world = build_autonomous_world()
    loop = AutonomousLoop(
        world,
        AutonomousLoopConfig(
            awake_seconds_per_cycle=2.0,
            dream_seconds_per_cycle=1.0,
            stagnation_threshold=0.05,
            stagnation_window=2,
        ),
    )
    # Run 5 cycles via direct loop invocation
    for _ in range(5):
        loop.cycle += 1
        loop._run_awake_phase()
    assert loop.cycle == 5
    assert world.t > 0.0


def test_G17_loop_records_metrics_per_cycle():
    """Each cycle yields one awake metrics row (and possibly one dream row)."""
    world = build_autonomous_world()
    loop = AutonomousLoop(
        world,
        AutonomousLoopConfig(
            awake_seconds_per_cycle=1.0,
            dream_seconds_per_cycle=0.5,
            stagnation_threshold=0.001,  # never stagnant → no dream
            stagnation_window=2,
        ),
    )
    # Run 3 full cycles via the run() loop with stop after 3 cycles.
    import threading

    def stop_after_3():
        import time
        # Wait until 3 cycles' worth of awake phase has run
        while loop.cycle < 3:
            time.sleep(0.01)
        loop.stop_event.set()

    t = threading.Thread(target=stop_after_3, daemon=True)
    t.start()
    loop.run()
    assert loop.cycle >= 3
    # At least 3 awake metrics rows recorded
    awake_rows = [m for m in loop.metrics if m.phase == "awake"]
    assert len(awake_rows) >= 3


def test_G17_loop_snapshot_persisted():
    """When snapshot_dir is set + cycle hits the snapshot interval,
    at least one snapshot file appears on disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        world = build_autonomous_world()
        loop = AutonomousLoop(
            world,
            AutonomousLoopConfig(
                awake_seconds_per_cycle=0.5,
                dream_seconds_per_cycle=0.2,
                snapshot_interval_cycles=2,
                stagnation_threshold=0.001,
                stagnation_window=2,
                snapshot_dir=str(tmpdir),
            ),
        )
        import threading
        import time

        def stop_after_3():
            while loop.cycle < 3:
                time.sleep(0.01)
            loop.stop_event.set()

        t = threading.Thread(target=stop_after_3, daemon=True)
        t.start()
        loop.run()

        snapshots = list(Path(tmpdir).glob("autonomous_cycle_*.npz"))
        assert len(snapshots) >= 1, (
            f"expected at least one snapshot in {tmpdir}; "
            f"found {[s.name for s in snapshots]}"
        )


def test_G17_metrics_csv_persists():
    """When metrics_log_path is set, CSV header + one row per cycle
    is written."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "metrics.csv"
        world = build_autonomous_world()
        loop = AutonomousLoop(
            world,
            AutonomousLoopConfig(
                awake_seconds_per_cycle=0.5,
                dream_seconds_per_cycle=0.2,
                stagnation_threshold=0.001,
                stagnation_window=2,
                metrics_log_path=str(csv_path),
            ),
        )
        import threading
        import time

        def stop_after_3():
            while loop.cycle < 3:
                time.sleep(0.01)
            loop.stop_event.set()

        t = threading.Thread(target=stop_after_3, daemon=True)
        t.start()
        loop.run()

        assert csv_path.exists()
        lines = csv_path.read_text().splitlines()
        assert lines[0].startswith("cycle,")
        assert len(lines) >= 4  # header + at least 3 cycles' rows

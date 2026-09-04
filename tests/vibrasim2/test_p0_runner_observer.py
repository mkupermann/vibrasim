from queue import Queue
from types import SimpleNamespace

import numpy as np

from vibrasim2.observation import ObservationStatus
from vibrasim2.observation_transport import LatestOnlyPublisher
from vibrasim2.p0.types import ChannelMode, P0Config, P0State, P0StateSnapshot, RunCell, RunPurpose, Topology
from vibrasim2.viewer_process import (
    P0ObservationSink,
    ViewerHandle,
    ViewerProcessConfig,
    shutdown_viewer,
    start_viewer,
)


def tiny_cell() -> RunCell:
    return RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.PRIMARY, (4, 16), 0.05, 10)


def tiny_snapshot() -> P0StateSnapshot:
    config = P0Config.registered()
    return P0StateSnapshot(
        10, 0.5,
        P0State(
            np.zeros(config.grid_shape), np.zeros(config.grid_shape),
            np.zeros(6), np.zeros(6),
        ),
    )


def fake_handle(queue):
    return ViewerHandle(None, queue, None, LatestOnlyPublisher(queue),
                        SimpleNamespace(display_scale=4.0))


def test_sink_publishes_only_after_supplied_snapshot_call(tmp_path):
    queue = Queue(maxsize=1)
    sink = P0ObservationSink(fake_handle(queue), tmp_path, "r1")
    calls = ["snapshot:10:persisted"]
    sink.after_snapshot_persisted("A", tiny_cell(), tiny_snapshot(), tmp_path)
    envelope = queue.get_nowait()
    calls.append("snapshot:10:published")
    assert calls.index("snapshot:10:persisted") < calls.index("snapshot:10:published")
    assert envelope.tick == 10
    assert envelope.status is ObservationStatus.RUNNING


def test_sink_close_true_publishes_complete_once_and_false_does_not(tmp_path, monkeypatch):
    import vibrasim2.viewer_process as viewer_process

    shutdowns = []
    monkeypatch.setattr(viewer_process, "shutdown_viewer", lambda handle: shutdowns.append(handle))
    queue = Queue(maxsize=1)
    sink = P0ObservationSink(fake_handle(queue), tmp_path, "r1")
    sink.after_snapshot_persisted("A", tiny_cell(), tiny_snapshot(), tmp_path)
    sink.close(True)
    complete = queue.get_nowait()
    assert complete.status is ObservationStatus.COMPLETE
    assert complete.sequence == 2
    sink.close(True)
    assert len(shutdowns) == 1

    queue2 = Queue(maxsize=1)
    sink2 = P0ObservationSink(fake_handle(queue2), tmp_path / "false", "r1")
    sink2.after_snapshot_persisted("A", tiny_cell(), tiny_snapshot(), tmp_path)
    sink2.close(False)
    assert queue2.get_nowait().status is ObservationStatus.RUNNING


def test_shutdown_terminates_only_an_unresponsive_viewer_and_is_idempotent():
    calls = []

    class StopEvent:
        def set(self):
            calls.append("stop")

    class Process:
        def join(self, timeout):
            calls.append(("join", timeout))

        def is_alive(self):
            calls.append("alive")
            return True

        def terminate(self):
            calls.append("terminate")

    class Queue:
        def cancel_join_thread(self):
            calls.append("cancel")

        def close(self):
            calls.append("close")

    handle = ViewerHandle(Process(), Queue(), StopEvent(), None, ViewerProcessConfig())
    shutdown_viewer(handle)
    shutdown_viewer(handle)
    assert calls == [
        "stop", ("join", 2.0), "alive", "terminate", ("join", 2.0), "cancel", "close"
    ]


def test_start_failure_returns_disabled_handle_and_logs_event(tmp_path, monkeypatch):
    import vibrasim2.viewer_process as viewer_process

    monkeypatch.setattr(viewer_process.multiprocessing, "get_context", lambda name: (_ for _ in ()).throw(OSError("no spawn")))
    handle = start_viewer(tmp_path, ViewerProcessConfig())
    assert handle.process is None
    assert '"event":"viewer_start_failed"' in (tmp_path / "view-events.jsonl").read_text()

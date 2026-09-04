from multiprocessing import get_context
from queue import Empty

import numpy as np


def envelope_worker(frame_queue, report_queue, stop_event, ready_event, drain_event):
    try:
        envelope = frame_queue.get(timeout=2.0)
        report_queue.put(("received", envelope.tick))
        ready_event.set()
        drain_event.wait(1.0)
        deadline = __import__("time").monotonic() + 0.25
        while __import__("time").monotonic() < deadline:
            try:
                envelope = frame_queue.get_nowait()
            except Empty:
                break
            report_queue.put(("final", envelope.tick, envelope.status.value))
        stop_event.set()
    except Exception as exc:
        report_queue.put(("error", type(exc).__name__))


def test_spawn_worker_receives_envelope_and_exits_bounded():
    from vibrasim2.observation import EdgeState, ObservationEnvelope, ObservationStatus, WireframeFrame

    context = get_context("spawn")
    frame_queue = context.Queue(maxsize=1)
    report_queue = context.Queue()
    stop_event = context.Event()
    ready_event = context.Event()
    drain_event = context.Event()
    frame = WireframeFrame(np.zeros((1, 3)), np.empty((0, 2), dtype=np.int32), (), ())
    envelope = ObservationEnvelope(
        1, "r1", "A", "cycle", (0, 0), 10, 0.5, 1, 1,
        ObservationStatus.RUNNING, 4.0, frame,
    )
    frame_queue.put(envelope)
    process = context.Process(
        target=envelope_worker,
        args=(frame_queue, report_queue, stop_event, ready_event, drain_event),
    )
    process.start()
    try:
        assert report_queue.get(timeout=1.0) == ("received", 10)
        assert ready_event.wait(1.0)
        frame_queue.put(
            ObservationEnvelope(
                1, "r1", "A", "cycle", (0, 0), 20, 1.0, 2, 2,
                ObservationStatus.COMPLETE, 4.0, frame,
            )
        )
        drain_event.set()
        process.join(5.0)
        assert not process.is_alive()
        assert report_queue.get(timeout=1.0) == ("final", 20, "complete")
        assert stop_event.is_set()
    finally:
        frame_queue.cancel_join_thread()
        frame_queue.close()
        report_queue.cancel_join_thread()
        report_queue.close()


def _replay_tree(root):
    from vibrasim2.p0.artifacts import CellJournal, write_run_manifest
    from vibrasim2.p0.types import (
        ChannelMode,
        P0Config,
        P0State,
        P0StateSnapshot,
        RunCell,
        RunPurpose,
        Topology,
    )

    config = P0Config((2, 2), 1.0, 0.5, 1.0, 0.05, 2.0, 20, 10, ((0, 0),))
    cell = RunCell(Topology.CYCLE, ChannelMode.FULL, RunPurpose.PRIMARY, (0, 0), 0.05, 20)
    write_run_manifest(root, run_id="replay-001", config=config, cells=(cell,), scientific_core_sha256="a" * 64)
    journal = CellJournal(
        root / cell.slug,
        stage="A",
        cell=cell,
        config=config,
        coupling_sites=np.array(((0, 0),), dtype=np.int64),
        supplied_edges=np.empty((0, 2), dtype=np.int64),
    )
    state = P0State(np.zeros((2, 2)), np.zeros((2, 2)), np.zeros(1), np.zeros(1))
    for tick in (10, 20):
        journal.append_snapshot(P0StateSnapshot(tick, tick * 0.05, state))


def test_replay_reads_persisted_snapshots_and_validates_result_digest(tmp_path):
    from vibrasim2.p0.artifacts import atomic_write_json, scientific_digest
    from vibrasim2.viewer_process import iter_replay_envelopes

    _replay_tree(tmp_path)
    running = tuple(iter_replay_envelopes(tmp_path))
    assert [envelope.tick for envelope in running] == [10, 20]
    assert all(envelope.status.value == "running" for envelope in running)
    assert all(envelope.arm == "cycle" for envelope in running)
    assert running[-1].display_scale == 4.0
    assert running[-1].frame.positions.shape == (5, 3)

    atomic_write_json(tmp_path / "result.json", {"scientific_digest": scientific_digest(tmp_path)})
    complete = tuple(iter_replay_envelopes(tmp_path))
    assert [envelope.tick for envelope in complete] == [10, 20]
    assert complete[-1].status.value == "complete"
    assert complete[0].status.value == "running"

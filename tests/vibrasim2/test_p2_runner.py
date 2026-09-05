from dataclasses import replace

from vibrasim2.p2.artifacts import read_json, scientific_digest
from vibrasim2.p2.runner import run_execution
from vibrasim2.p2.trajectory import run_trajectory
from vibrasim2.p2.types import P2Config, Verdict


class RecordingObserver:
    def __init__(self):
        self.frames = []
        self.closed_with = None

    def after_snapshot_persisted(self, stage, cell, snapshot, cell_dir):
        assert (cell_dir / "snapshots" / f"{snapshot.tick:08d}.npz").is_file()
        self.frames.append((stage, cell.slug, snapshot.tick))

    def close(self, result_recorded):
        self.closed_with = result_recorded


def test_execution_persists_before_observing_and_records_readback_result(tmp_path):
    config = replace(P2Config.registered(), steps=4, frame_stride=2)
    observer = RecordingObserver()

    result = run_execution(
        tmp_path,
        config,
        trajectory_executor=run_trajectory,
        observer_factory=lambda _run_id: observer,
        run_id="v2-p2-fixture",
    )

    assert result.verdict in {Verdict.NULL, Verdict.INCONCLUSIVE}
    # 12 primary/reproduction cells emit ticks 0,2,4; six half-step cells emit
    # ticks 0,2,4,6,8.
    assert len(observer.frames) == 12 * 3 + 6 * 5
    assert observer.closed_with is True
    recorded = read_json(tmp_path / "result.json")
    assert recorded["verdict"] == result.verdict.value
    assert recorded["scientific_digest"] == scientific_digest(tmp_path)


def test_execution_refuses_existing_run_manifest(tmp_path):
    config = replace(P2Config.registered(), steps=1, frame_stride=1)
    run_execution(tmp_path, config, run_id="v2-p2-first")

    try:
        run_execution(tmp_path, config, run_id="v2-p2-second")
    except Exception as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("second execution unexpectedly overwrote evidence")

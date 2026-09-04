import hashlib
import json
import shutil
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from vibrasim2.p0.artifacts import (
    PREREGISTRATION_SHA256,
    ArtifactError,
    atomic_write_json,
    iter_energy_records,
    iter_snapshots,
    read_json,
    scientific_digest,
)
from vibrasim2.p0.budget import BUDGETED_PATHS, BudgetError, load_budget_ledger
from vibrasim2.p0.energy import EnergyRecord, Trajectory
from vibrasim2.p0.runner import (
    ExecutionMatrix,
    NullObservationSink,
    P0RunResult,
    PostRunBudgetError,
    _run_execution,
    _run_registered_p0,
)
from vibrasim2.p0.types import (
    ChannelMode,
    P0Config,
    P0StateSnapshot,
    RunCell,
    RunPurpose,
    Topology,
    Verdict,
)
from vibrasim2.p0.verdict import P0Evidence, StageAGate

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def passing_evidence(**changes: bool) -> P0Evidence:
    values = {name: True for name in P0Evidence.__dataclass_fields__}
    values.update(changes)
    return P0Evidence(**values)


def short_trajectory(cell, config, initial) -> Trajectory:
    records = (
        EnergyRecord(0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, True),
        EnergyRecord(1, cell.dt, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, True),
    )
    return Trajectory(cell, records, (P0StateSnapshot(0, 0.0, initial),))


def tiny_execution(*, include_reproduction: bool = False) -> ExecutionMatrix:
    config = replace(P0Config.registered(), steps=1, source_centres=((4, 16),))
    primary = RunCell(
        Topology.CYCLE,
        ChannelMode.FULL,
        RunPurpose.PRIMARY,
        (4, 16),
        0.05,
        1,
    )
    reproduction = RunCell(
        Topology.CYCLE,
        ChannelMode.FULL,
        RunPurpose.REPRODUCTION,
        (4, 16),
        0.05,
        1,
    )
    return ExecutionMatrix(
        config,
        (primary,),
        (reproduction,) if include_reproduction else (),
        short_trajectory,
    )


def stage_a_fail_result(*args, **kwargs) -> StageAGate:
    return StageAGate(False, Verdict.FAIL, ("forced Stage-A test failure",))


class RecordingSink(NullObservationSink):
    def __init__(self):
        self.events: list[tuple[str, str, int]] = []
        self.closed: list[bool] = []

    def after_snapshot_persisted(self, stage, cell, snapshot, cell_dir):
        assert (cell_dir / "snapshots" / f"snapshot-{snapshot.tick:010d}.npz").is_file()
        self.events.append((stage, cell.slug, snapshot.tick))

    def close(self, result_recorded: bool):
        self.closed.append(result_recorded)


def install_stage_a_result(monkeypatch, gate: StageAGate) -> None:
    monkeypatch.setattr(
        "vibrasim2.p0.runner.build_evidence", lambda *args, **kwargs: passing_evidence()
    )
    monkeypatch.setattr("vibrasim2.p0.runner.evaluate_stage_a", lambda evidence: gate)


@pytest.mark.parametrize("verdict", (Verdict.FAIL, Verdict.INCONCLUSIVE))
def test_closed_stage_a_uses_common_result_finalization(tmp_path, monkeypatch, verdict):
    install_stage_a_result(
        monkeypatch, StageAGate(False, verdict, (f"forced {verdict.value}",))
    )
    sink = RecordingSink()

    result = _run_execution(
        tmp_path,
        tiny_execution(),
        observer_factory=lambda run_id: sink,
        run_id="tiny-run",
        scientific_core_sha256="a" * 64,
    )

    assert result.verdict is verdict
    assert read_json(tmp_path / "result.json")["verdict"] == verdict.value
    assert sink.closed == [True]


def test_stage_b_never_starts_after_failed_stage_a(tmp_path, monkeypatch):
    install_stage_a_result(monkeypatch, stage_a_fail_result())
    monkeypatch.setattr(
        "vibrasim2.p0.runner.run_reproduction_cells",
        lambda *args, **kwargs: pytest.fail("Stage B started after a closed Stage A"),
    )
    result = _run_execution(tmp_path, tiny_execution())
    assert result.verdict.value == "FAIL"


def test_raw_artifacts_are_reloaded_before_evidence(tmp_path, monkeypatch):
    checked = []

    def reload_and_build(output_dir, *, include_reproduction):
        cell = tiny_execution().stage_a_cells[0]
        checked.append(tuple(iter_energy_records(output_dir / cell.slug)))
        checked.append(tuple(iter_snapshots(output_dir / cell.slug)))
        return passing_evidence()

    monkeypatch.setattr("vibrasim2.p0.runner.build_evidence", reload_and_build)
    monkeypatch.setattr(
        "vibrasim2.p0.runner.evaluate_stage_a",
        lambda evidence: StageAGate(False, Verdict.FAIL, ("closed",)),
    )
    _run_execution(tmp_path, tiny_execution())
    assert [len(values) for values in checked] == [2, 1]


def test_stage_b_runs_only_after_stage_a_proceeds(tmp_path, monkeypatch):
    calls = []

    def executor(cell, config, initial):
        calls.append(cell.purpose)
        return short_trajectory(cell, config, initial)

    matrix = replace(
        tiny_execution(include_reproduction=True), trajectory_executor=executor
    )
    monkeypatch.setattr(
        "vibrasim2.p0.runner.build_evidence",
        lambda *args, **kwargs: passing_evidence(),
    )
    monkeypatch.setattr(
        "vibrasim2.p0.runner.evaluate_stage_a",
        lambda evidence: StageAGate(True, None, ()),
    )
    monkeypatch.setattr(
        "vibrasim2.p0.runner.decide_verdict", lambda evidence: Verdict.NULL
    )

    result = _run_execution(tmp_path, matrix)

    assert calls == [RunPurpose.PRIMARY, RunPurpose.REPRODUCTION]
    assert result.verdict is Verdict.NULL


def test_observer_factory_and_callback_follow_persistence(tmp_path, monkeypatch):
    install_stage_a_result(monkeypatch, stage_a_fail_result())
    sink = RecordingSink()

    def factory(run_id):
        assert read_json(tmp_path / "run.json")["run_id"] == run_id
        return sink

    _run_execution(
        tmp_path, tiny_execution(), observer_factory=factory, run_id="ordered"
    )
    assert sink.events == [("A", tiny_execution().stage_a_cells[0].slug, 0)]


def test_observer_failure_cannot_stop_science(tmp_path, monkeypatch):
    install_stage_a_result(monkeypatch, stage_a_fail_result())

    class FailingSink(RecordingSink):
        def after_snapshot_persisted(self, *args):
            raise RuntimeError("viewer gone")

    sink = FailingSink()
    result = _run_execution(
        tmp_path, tiny_execution(), observer_factory=lambda run_id: sink
    )
    assert result.verdict is Verdict.FAIL
    assert sink.closed == [False]
    assert "observer_failed" in (tmp_path / "view-events.jsonl").read_text()


def test_artifact_failure_produces_no_scientific_verdict(tmp_path, monkeypatch):
    install_stage_a_result(monkeypatch, stage_a_fail_result())
    real_atomic_write_json = atomic_write_json

    def fail_result_only(path, value):
        if path.name == "result.json":
            raise ArtifactError("readback mismatch")
        return real_atomic_write_json(path, value)

    monkeypatch.setattr("vibrasim2.p0.runner.atomic_write_json", fail_result_only)
    with pytest.raises(ArtifactError, match="readback mismatch"):
        _run_execution(tmp_path, tiny_execution())
    assert not (tmp_path / "result.json").exists()


def test_result_readback_precedes_result_object(tmp_path, monkeypatch):
    install_stage_a_result(monkeypatch, stage_a_fail_result())
    real_read_json = read_json

    def fail_result_read(path):
        if path.name == "result.json":
            raise ArtifactError("independent result readback failed")
        return real_read_json(path)

    monkeypatch.setattr("vibrasim2.p0.runner.read_json", fail_result_read)
    with pytest.raises(ArtifactError, match="independent result readback"):
        _run_execution(tmp_path, tiny_execution())


def test_core_digest_is_bound_through_manifest_result_and_digest(tmp_path, monkeypatch):
    install_stage_a_result(monkeypatch, stage_a_fail_result())
    core = "b" * 64
    result = _run_execution(
        tmp_path,
        tiny_execution(),
        run_id="core-bound",
        scientific_core_sha256=core,
    )
    manifest = read_json(tmp_path / "run.json")
    recorded = read_json(tmp_path / "result.json")
    assert manifest["scientific_core_sha256"] == core
    assert recorded["scientific_core_sha256"] == core
    assert recorded["scientific_digest"] == scientific_digest(tmp_path)
    assert result.scientific_digest == recorded["scientific_digest"]


def _core_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for index, relative in enumerate(BUDGETED_PATHS):
        data = f"fixture {index}\n".encode()
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(str(len(data)).encode())
        digest.update(b"\0")
        digest.update(data)
    return digest.hexdigest()


def write_registered_repository_fixture(
    root: Path, *, elapsed: int = 100, status: str = "within_cap"
) -> tuple[Path, str]:
    for relative in (
        "docs/amendments/v2_p0_reciprocal_channel.md",
        "docs/amendments/v2_p0_scope_addendum.md",
    ):
        source = REPOSITORY_ROOT / relative
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    core = _core_digest(root)
    start = datetime(2026, 9, 4, 8, tzinfo=UTC)
    end = start + timedelta(seconds=elapsed)
    ledger = root / "docs/vibrasim2/P0_BUDGET_LEDGER.json"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "registration_sha256": PREREGISTRATION_SHA256,
                "hard_ceiling_seconds": 19800,
                "status": status,
                "cumulative_elapsed_seconds": elapsed,
                "scientific_core_sha256": core,
                "budgeted_paths": list(BUDGETED_PATHS),
                "intervals": [
                    {
                        "started_at_utc": start.isoformat().replace("+00:00", "Z"),
                        "ended_at_utc": end.isoformat().replace("+00:00", "Z"),
                        "elapsed_seconds": elapsed,
                        "phase": "implementation",
                        "owner": "work/vibrasim2-research-reset",
                        "outcome": "completed",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return ledger, core


def clock(*values: datetime):
    moments = iter(values)
    return lambda: next(moments)


def test_budget_guard_precedes_directory_creation_and_execution(tmp_path, monkeypatch):
    write_registered_repository_fixture(
        tmp_path, elapsed=19800, status="overrun_registration_required"
    )
    output = tmp_path / "archive/run-logs/v2-p0/blocked"
    monkeypatch.setattr(
        "vibrasim2.p0.runner._run_execution",
        lambda *args, **kwargs: pytest.fail("execution started before budget guard"),
    )
    with pytest.raises(BudgetError):
        _run_registered_p0(output, repository_root=tmp_path)
    assert not output.exists()


def test_scientific_run_owns_and_closes_one_budget_interval(tmp_path, monkeypatch):
    ledger, core = write_registered_repository_fixture(tmp_path)
    output = tmp_path / "archive/run-logs/v2-p0/aborted"
    start = datetime(2026, 9, 4, 9, tzinfo=UTC)

    def fail_execution(*args, **kwargs):
        active = load_budget_ledger(ledger)
        assert active.intervals[-1].phase == "scientific_run"
        assert active.intervals[-1].owner == "run-001"
        assert kwargs["scientific_core_sha256"] == core
        raise RuntimeError("sentinel operational failure")

    monkeypatch.setattr("vibrasim2.p0.runner._new_run_id", lambda: "run-001")
    monkeypatch.setattr("vibrasim2.p0.runner._run_execution", fail_execution)
    with pytest.raises(RuntimeError, match="sentinel"):
        _run_registered_p0(
            output,
            repository_root=tmp_path,
            utc_now=clock(start, start + timedelta(seconds=1.2)),
        )
    closed = load_budget_ledger(ledger)
    assert len(closed.intervals) == 2
    assert closed.intervals[-1].outcome == "aborted"
    assert closed.intervals[-1].elapsed_seconds == 2


def _recorded_result(output: Path, core: str) -> P0RunResult:
    evidence = passing_evidence()
    atomic_write_json(
        output / "result.json",
        {
            "schema_version": 1,
            "verdict": "NULL",
            "scientific_core_sha256": core,
            "scientific_digest": "fixture-digest",
        },
    )
    return P0RunResult(Verdict.NULL, evidence, output, "fixture-digest")


@pytest.mark.parametrize(
    ("implementation_elapsed", "run_elapsed", "expected_status"),
    (
        (100, 900, "phase_reserve_breached"),
        (17100, 2700, "overrun_registration_required"),
    ),
)
def test_post_run_budget_stop_preserves_recorded_result(
    tmp_path,
    monkeypatch,
    implementation_elapsed,
    run_elapsed,
    expected_status,
):
    _, core = write_registered_repository_fixture(
        tmp_path, elapsed=implementation_elapsed
    )
    output = tmp_path / "archive/run-logs/v2-p0/completed"
    start = datetime(2026, 9, 4, 13, tzinfo=UTC)
    monkeypatch.setattr("vibrasim2.p0.runner._new_run_id", lambda: "run-stop")
    monkeypatch.setattr(
        "vibrasim2.p0.runner._run_execution",
        lambda path, *args, **kwargs: _recorded_result(path, core),
    )
    with pytest.raises(PostRunBudgetError) as stopped:
        _run_registered_p0(
            output,
            repository_root=tmp_path,
            utc_now=clock(start, start + timedelta(seconds=run_elapsed)),
        )
    assert stopped.value.result_path == output / "result.json"
    assert stopped.value.verdict is Verdict.NULL
    assert stopped.value.ledger_status == expected_status
    assert (output / "result.json").is_file()


def test_post_run_core_change_keeps_leased_identity(tmp_path, monkeypatch):
    _, core = write_registered_repository_fixture(tmp_path)
    output = tmp_path / "archive/run-logs/v2-p0/core-change"
    start = datetime(2026, 9, 4, 13, tzinfo=UTC)

    def mutate_after_lease(path, *args, **kwargs):
        (tmp_path / BUDGETED_PATHS[0]).write_text("changed\n", encoding="utf-8")
        return _recorded_result(path, kwargs["scientific_core_sha256"])

    monkeypatch.setattr("vibrasim2.p0.runner._run_execution", mutate_after_lease)
    with pytest.raises(PostRunBudgetError) as stopped:
        _run_registered_p0(
            output,
            repository_root=tmp_path,
            utc_now=clock(start, start + timedelta(seconds=1)),
        )
    assert stopped.value.verdict is Verdict.NULL
    assert read_json(output / "result.json")["scientific_core_sha256"] == core

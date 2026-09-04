"""Registered P0 stage orchestration with budget and artifact guards."""

from __future__ import annotations

import hashlib
import json
import math
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

import numpy as np

from .artifacts import (
    ADDENDUM_GIT_BLOB,
    ADDENDUM_SHA256,
    PREREGISTRATION_GIT_BLOB,
    PREREGISTRATION_SHA256,
    ArtifactError,
    CellJournal,
    atomic_write_json,
    iter_energy_records,
    iter_snapshots,
    read_json,
    scientific_digest,
    write_run_manifest,
)
from .budget import (
    BudgetError,
    assert_budget_allows_run,
    finish_budget_interval,
    start_budget_interval,
)
from .energy import (
    Trajectory,
    a_b,
    coupling_identity_residual,
    max_material_energy_ratio,
    max_relative_energy_drift,
    run_trajectory,
)
from .fixtures import (
    coupling_sites,
    edges_for,
    initial_state,
    registered_stage_a_cells,
    reproduction_cells,
)
from .types import P0Config, P0State, P0StateSnapshot, RunCell, Verdict
from .verdict import (
    P0Evidence,
    build_evidence,
    decide_verdict,
    evaluate_stage_a,
)

_FIXTURE_CORE_SHA256 = "0" * 64
_PREREGISTRATION_PATH = Path("docs/amendments/v2_p0_reciprocal_channel.md")
_ADDENDUM_PATH = Path("docs/amendments/v2_p0_scope_addendum.md")
_BUDGET_LEDGER_PATH = Path("docs/vibrasim2/P0_BUDGET_LEDGER.json")
_RUN_ROOT = Path("archive/run-logs/v2-p0")


class RegistrationError(RuntimeError):
    """Raised before data when frozen registration or output scope is invalid."""


class ObservationSink(Protocol):
    def after_snapshot_persisted(
        self, stage: str, cell: RunCell, snapshot: P0StateSnapshot, cell_dir: Path
    ) -> None:
        raise NotImplementedError

    def close(self, result_recorded: bool) -> None:
        raise NotImplementedError


class NullObservationSink:
    def after_snapshot_persisted(self, stage, cell, snapshot, cell_dir):
        return None

    def close(self, result_recorded: bool):
        return None


TrajectoryExecutor = Callable[[RunCell, P0Config, P0State], Trajectory]
ObservationSinkFactory = Callable[[str], ObservationSink]


@dataclass(frozen=True)
class ExecutionMatrix:
    config: P0Config
    stage_a_cells: tuple[RunCell, ...]
    reproduction_cells: tuple[RunCell, ...]
    trajectory_executor: TrajectoryExecutor


@dataclass(frozen=True)
class P0RunResult:
    verdict: Verdict
    evidence: P0Evidence
    output_dir: Path
    scientific_digest: str


class PostRunBudgetError(BudgetError):
    """A durable scientific verdict exists, but the budget requires a stop."""

    def __init__(
        self,
        result_path: Path,
        verdict: Verdict,
        ledger_status: str,
        *,
        cause: Exception | None = None,
    ) -> None:
        self.result_path = Path(result_path)
        self.verdict = verdict
        self.ledger_status = ledger_status
        self.cause = cause
        super().__init__(
            f"scientific verdict {verdict.value} recorded at {self.result_path}; "
            f"budget stop: {ledger_status}"
        )


def _new_run_id() -> str:
    return f"v2-p0-{uuid.uuid4().hex}"


def _append_view_event_best_effort(output_dir: Path, value: dict[str, object]) -> None:
    try:
        with (output_dir / "view-events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")))
            stream.write("\n")
    except Exception:  # noqa: BLE001 - a view-event logger may never affect science
        return


def _close_observer_best_effort(
    observer: ObservationSink, result_recorded: bool, output_dir: Path
) -> None:
    try:
        observer.close(result_recorded)
    except Exception as error:  # noqa: BLE001 - observer failures are isolated
        _append_view_event_best_effort(
            output_dir,
            {"event": "observer_close_failed", "error": type(error).__name__},
        )


def _persist_cells(
    output_dir: Path,
    *,
    stage: str,
    cells: tuple[RunCell, ...],
    config: P0Config,
    trajectory_executor: TrajectoryExecutor,
    observer: ObservationSink,
) -> ObservationSink:
    active_observer = observer
    for cell in cells:
        state = initial_state(config, cell.source_centre)
        trajectory = trajectory_executor(cell, config, state)
        if trajectory.cell != cell:
            raise ArtifactError("trajectory executor returned the wrong cell")
        journal = CellJournal(
            output_dir / cell.slug,
            stage=stage,
            cell=cell,
            config=config,
            coupling_sites=coupling_sites(),
            supplied_edges=edges_for(cell.topology),
        )
        for record in trajectory.records:
            journal.append_energy(record)
        for snapshot in trajectory.snapshots:
            journal.append_snapshot(snapshot)
            try:
                active_observer.after_snapshot_persisted(
                    stage, cell, snapshot, journal.cell_dir
                )
            except Exception as error:  # noqa: BLE001 - observer failures are isolated
                _append_view_event_best_effort(
                    output_dir,
                    {
                        "event": "observer_failed",
                        "error": type(error).__name__,
                        "stage": stage,
                        "cell": cell.slug,
                        "tick": snapshot.tick,
                    },
                )
                _close_observer_best_effort(active_observer, False, output_dir)
                active_observer = NullObservationSink()
    return active_observer


def run_stage_a(
    output_dir: Path,
    matrix: ExecutionMatrix,
    observer: ObservationSink,
) -> ObservationSink:
    return _persist_cells(
        output_dir,
        stage="A",
        cells=matrix.stage_a_cells,
        config=matrix.config,
        trajectory_executor=matrix.trajectory_executor,
        observer=observer,
    )


def run_reproduction_cells(
    output_dir: Path,
    matrix: ExecutionMatrix,
    observer: ObservationSink,
) -> ObservationSink:
    return _persist_cells(
        output_dir,
        stage="B",
        cells=matrix.reproduction_cells,
        config=matrix.config,
        trajectory_executor=matrix.trajectory_executor,
        observer=observer,
    )


def _fixture_evidence(
    output_dir: Path, matrix: ExecutionMatrix, *, include_reproduction: bool
) -> P0Evidence:
    cells = matrix.stage_a_cells + (
        matrix.reproduction_cells if include_reproduction else ()
    )
    for cell in cells:
        if not tuple(iter_energy_records(output_dir / cell.slug)):
            raise ArtifactError(f"missing fixture energy records: {cell.slug}")
        if not tuple(iter_snapshots(output_dir / cell.slug)):
            raise ArtifactError(f"missing fixture snapshots: {cell.slug}")
    return P0Evidence(*(False for _ in P0Evidence.__dataclass_fields__))


def _build_evidence(
    output_dir: Path,
    matrix: ExecutionMatrix,
    *,
    include_reproduction: bool,
    fixture_mode: bool,
) -> P0Evidence:
    try:
        return build_evidence(output_dir, include_reproduction=include_reproduction)
    except ArtifactError:
        if not fixture_mode:
            raise
        return _fixture_evidence(
            output_dir, matrix, include_reproduction=include_reproduction
        )


def _json_number(value: float) -> float | None:
    number = float(value)
    return number if math.isfinite(number) else None


def _cell_metrics(output_dir: Path) -> dict[str, dict[str, object]]:
    manifest = read_json(output_dir / "run.json")
    metrics: dict[str, dict[str, object]] = {}
    for slug in manifest["cell_order"]:
        cell_dir = output_dir / slug
        if not cell_dir.is_dir():
            continue
        records = tuple(iter_energy_records(cell_dir))
        snapshots = tuple(iter_snapshots(cell_dir))
        finite = bool(
            records
            and snapshots
            and all(record.finite for record in records)
            and all(
                all(
                    bool(getattr(snapshot.state, name).size)
                    and bool(getattr(snapshot.state, name).dtype.kind == "f")
                    and bool(np.isfinite(getattr(snapshot.state, name)).all())
                    for name in ("u", "p", "q", "r")
                )
                for snapshot in snapshots
            )
        )
        values: dict[str, object] = {
            "finite": finite,
            "energy_record_count": len(records),
            "snapshot_count": len(snapshots),
        }
        if finite:
            try:
                values.update(
                    a_b=_json_number(a_b(records)),
                    max_relative_energy_drift=_json_number(
                        max_relative_energy_drift(records)
                    ),
                    coupling_identity_residual=_json_number(
                        coupling_identity_residual(records)
                    ),
                    max_material_energy_ratio=_json_number(
                        max_material_energy_ratio(records)
                    ),
                )
            except ValueError:
                values.update(
                    a_b=None,
                    max_relative_energy_drift=None,
                    coupling_identity_residual=None,
                    max_material_energy_ratio=None,
                )
        else:
            values.update(
                a_b=None,
                max_relative_energy_drift=None,
                coupling_identity_residual=None,
                max_material_energy_ratio=None,
            )
        metrics[slug] = values
    return metrics


def _failed_evidence_reasons(evidence: P0Evidence) -> tuple[str, ...]:
    return tuple(
        name for name in P0Evidence.__dataclass_fields__ if not getattr(evidence, name)
    )


def finalize_scientific_result(
    output_dir: Path,
    evidence: P0Evidence,
    verdict: Verdict,
    observer: ObservationSink,
    *,
    scientific_core_sha256: str,
    reasons: tuple[str, ...] = (),
) -> P0RunResult:
    try:
        manifest = read_json(output_dir / "run.json")
        if manifest.get("scientific_core_sha256") != scientific_core_sha256:
            raise ArtifactError("execution core digest does not match run manifest")
        digest = scientific_digest(output_dir)
        result_path = output_dir / "result.json"
        atomic_write_json(
            result_path,
            {
                "schema_version": 1,
                "preregistration_sha256": PREREGISTRATION_SHA256,
                "preregistration_git_blob": PREREGISTRATION_GIT_BLOB,
                "addendum_sha256": ADDENDUM_SHA256,
                "addendum_git_blob": ADDENDUM_GIT_BLOB,
                "scientific_core_sha256": scientific_core_sha256,
                "verdict": verdict.value,
                "reasons": list(reasons or _failed_evidence_reasons(evidence)),
                "registered_constants": manifest["config"],
                "evidence": asdict(evidence),
                "cell_metrics": _cell_metrics(output_dir),
                "scientific_digest": digest,
            },
        )
        recorded = read_json(result_path)
        if (
            recorded.get("scientific_core_sha256") != scientific_core_sha256
            or recorded.get("scientific_digest") != digest
        ):
            raise ArtifactError("result readback does not match the execution identity")
        recorded_evidence = P0Evidence(**recorded["evidence"])
        recorded_verdict = Verdict(recorded["verdict"])
        result = P0RunResult(
            recorded_verdict,
            recorded_evidence,
            output_dir,
            recorded["scientific_digest"],
        )
    except ArtifactError:
        _close_observer_best_effort(observer, False, output_dir)
        raise
    _close_observer_best_effort(observer, True, output_dir)
    return result


def _run_execution(
    output_dir: str | Path,
    matrix: ExecutionMatrix,
    observer_factory: ObservationSinkFactory | None = None,
    run_id: str | None = None,
    scientific_core_sha256: str | None = None,
) -> P0RunResult:
    output = Path(output_dir)
    execution_run_id = run_id or "fixture-run"
    execution_core = scientific_core_sha256 or _FIXTURE_CORE_SHA256
    all_cells = matrix.stage_a_cells + matrix.reproduction_cells
    write_run_manifest(
        output,
        run_id=execution_run_id,
        config=matrix.config,
        cells=all_cells,
        scientific_core_sha256=execution_core,
    )
    verified_manifest = read_json(output / "run.json")
    if (
        verified_manifest.get("run_id") != execution_run_id
        or verified_manifest.get("scientific_core_sha256") != execution_core
    ):
        raise ArtifactError("run manifest readback does not match execution identity")
    observer = (
        observer_factory(verified_manifest["run_id"])
        if observer_factory is not None
        else NullObservationSink()
    )
    fixture_mode = scientific_core_sha256 is None
    observer = run_stage_a(output, matrix, observer)
    evidence = _build_evidence(
        output,
        matrix,
        include_reproduction=False,
        fixture_mode=fixture_mode,
    )
    gate = evaluate_stage_a(evidence)
    if not gate.proceed:
        if gate.provisional_verdict is None:
            raise ArtifactError("closed Stage A has no provisional verdict")
        return finalize_scientific_result(
            output,
            evidence,
            gate.provisional_verdict,
            observer,
            scientific_core_sha256=execution_core,
            reasons=gate.reasons,
        )

    observer = run_reproduction_cells(output, matrix, observer)
    evidence = _build_evidence(
        output,
        matrix,
        include_reproduction=True,
        fixture_mode=fixture_mode,
    )
    verdict = decide_verdict(evidence)
    return finalize_scientific_result(
        output,
        evidence,
        verdict,
        observer,
        scientific_core_sha256=execution_core,
    )


def _canonical_lf_bytes(path: Path) -> bytes:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise RegistrationError(
            f"missing frozen registration document: {path}"
        ) from error
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _validate_frozen_document(
    path: Path, expected_sha256: str, expected_blob: str
) -> None:
    data = _canonical_lf_bytes(path)
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise RegistrationError(f"frozen document SHA-256 mismatch: {path}")
    blob_header = f"blob {len(data)}\0".encode()
    if hashlib.sha1(blob_header + data).hexdigest() != expected_blob:
        raise RegistrationError(f"frozen document Git blob mismatch: {path}")


def _validate_output_path(output_dir: Path, repository_root: Path) -> Path:
    run_root = (repository_root / _RUN_ROOT).resolve()
    output = output_dir.resolve()
    if output == run_root or output.parent != run_root:
        raise RegistrationError(
            "output directory must be one fresh direct child of archive/run-logs/v2-p0"
        )
    if output.exists():
        raise RegistrationError("output directory already exists")
    return output


def _registered_matrix() -> ExecutionMatrix:
    config = P0Config.registered()
    config.assert_registered()
    return ExecutionMatrix(
        config,
        registered_stage_a_cells(config),
        reproduction_cells(config),
        run_trajectory,
    )


def _run_registered_p0(
    output_dir: str | Path,
    *,
    repository_root: str | Path,
    observer_factory: ObservationSinkFactory | None = None,
    utc_now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> P0RunResult:
    repository = Path(repository_root).resolve()
    output = _validate_output_path(Path(output_dir), repository)
    _validate_frozen_document(
        repository / _PREREGISTRATION_PATH,
        PREREGISTRATION_SHA256,
        PREREGISTRATION_GIT_BLOB,
    )
    _validate_frozen_document(
        repository / _ADDENDUM_PATH, ADDENDUM_SHA256, ADDENDUM_GIT_BLOB
    )
    matrix = _registered_matrix()
    ledger_path = repository / _BUDGET_LEDGER_PATH
    assert_budget_allows_run(ledger_path, PREREGISTRATION_SHA256, repository)
    run_id = _new_run_id()
    lease = start_budget_interval(
        ledger_path,
        PREREGISTRATION_SHA256,
        repository,
        phase="scientific_run",
        owner=run_id,
        started_at_utc=utc_now(),
    )

    result: P0RunResult | None = None
    execution_error: BaseException | None = None
    try:
        run_root = (repository / _RUN_ROOT).resolve()
        run_root.mkdir(parents=True, exist_ok=True)
        output.mkdir(exist_ok=False)
        result = _run_execution(
            output,
            matrix,
            observer_factory=observer_factory,
            run_id=run_id,
            scientific_core_sha256=lease.scientific_core_sha256,
        )
    except BaseException as error:  # noqa: BLE001 - lease closure must run on every exit
        execution_error = error

    try:
        closed = finish_budget_interval(
            lease,
            ended_at_utc=utc_now(),
            outcome="completed" if result is not None else "aborted",
        )
    except Exception as close_error:
        if result is not None:
            raise PostRunBudgetError(
                output / "result.json",
                result.verdict,
                "lease_close_failed",
                cause=close_error,
            ) from close_error
        if execution_error is not None:
            raise close_error from execution_error
        raise

    if execution_error is not None:
        raise execution_error
    if result is None:
        raise ArtifactError("scientific execution returned no result")
    if closed.status != "within_cap":
        raise PostRunBudgetError(output / "result.json", result.verdict, closed.status)
    return result


def run_registered_p0(
    output_dir: str | Path,
    observer_factory: ObservationSinkFactory | None = None,
) -> P0RunResult:
    repository_root = Path(__file__).resolve().parents[2]
    return _run_registered_p0(
        output_dir,
        repository_root=repository_root,
        observer_factory=observer_factory,
    )

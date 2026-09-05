"""Guarded persistence pipeline for the V2-P2 registered matrix."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Protocol

from .artifacts import (
    P2ArtifactError,
    P2CellJournal,
    atomic_write_json,
    read_json,
    scientific_digest,
    write_run_manifest,
)
from .dynamics import initial_state
from .fixtures import registered_cells
from .registration import P2_REGISTRATION_SHA256
from .trajectory import P2Trajectory, run_trajectory
from .types import P2Cell, P2Config, Verdict
from .verdict import CellOutcome, P2Evidence, build_evidence, decide_verdict


class ObservationSink(Protocol):
    def after_snapshot_persisted(self, stage, cell, snapshot, cell_dir) -> None: ...
    def close(self, result_recorded: bool) -> None: ...


class NullObservationSink:
    def after_snapshot_persisted(self, stage, cell, snapshot, cell_dir) -> None:
        return None

    def close(self, result_recorded: bool) -> None:
        return None


TrajectoryExecutor = Callable[[P2Cell, P2Config, object], P2Trajectory]


@dataclass(frozen=True)
class P2RunResult:
    verdict: Verdict
    evidence: P2Evidence
    output_dir: Path
    scientific_digest: str


def _outcome(trajectory: P2Trajectory) -> CellOutcome:
    final = trajectory.records[-1]
    drifts = [
        record.absolute_energy_drift
        for record in trajectory.records
        if record.absolute_energy_drift is not None
    ]
    return CellOutcome(
        cell=trajectory.cell,
        bond_time=float(final.bond_time or 0.0),
        max_absolute_energy_drift=max(drifts, default=float("inf")),
        finite=bool(trajectory.records and all(record.finite for record in trajectory.records)),
        events=trajectory.events,
    )


def _reasons(evidence: P2Evidence) -> list[str]:
    return [
        name
        for name in P2Evidence.__dataclass_fields__
        if name.endswith("_holds") and not getattr(evidence, name)
    ] + (["all_values_finite"] if not evidence.all_values_finite else [])


def run_execution(
    output_dir: Path,
    config: P2Config,
    *,
    trajectory_executor: TrajectoryExecutor = run_trajectory,
    observer_factory=None,
    run_id: str | None = None,
) -> P2RunResult:
    """Execute a declared matrix; callers guard registered authority separately."""
    output = Path(output_dir)
    cells = registered_cells(config)
    execution_run_id = run_id or f"v2-p2-{uuid.uuid4().hex}"
    write_run_manifest(output, execution_run_id, config, cells)
    manifest = read_json(output / "run.json")
    if manifest.get("run_id") != execution_run_id:
        raise P2ArtifactError("run manifest identity readback failed")
    observer: ObservationSink = NullObservationSink()
    if observer_factory is not None:
        try:
            observer = observer_factory(execution_run_id)
        except Exception:
            observer = NullObservationSink()
    outcomes: list[CellOutcome] = []
    try:
        for cell in cells:
            trajectory = trajectory_executor(
                cell, config, initial_state(config, cell.source_centre)
            )
            if trajectory.cell != cell:
                raise P2ArtifactError("trajectory executor returned the wrong cell")
            journal = P2CellJournal(output / cell.slug, cell, config)
            for record in trajectory.records:
                journal.append_energy(record)
            for event in trajectory.events:
                journal.append_event(event)
            for snapshot in trajectory.snapshots:
                journal.append_snapshot(snapshot)
                try:
                    observer.after_snapshot_persisted("P2", cell, snapshot, journal.path)
                except Exception:
                    observer.close(False)
                    observer = NullObservationSink()
            outcomes.append(_outcome(trajectory))
        evidence = build_evidence(tuple(outcomes), config)
        verdict = decide_verdict(evidence)
        digest = scientific_digest(output)
        metrics = {
            outcome.cell.slug: {
                "bond_time": outcome.bond_time,
                "max_absolute_energy_drift": outcome.max_absolute_energy_drift,
                "finite": outcome.finite,
                "event_count": len(outcome.events),
            }
            for outcome in outcomes
        }
        atomic_write_json(
            output / "result.json",
            {
                "schema_version": 1,
                "experiment": "P2",
                "registration_sha256": P2_REGISTRATION_SHA256,
                "verdict": verdict.value,
                "reasons": _reasons(evidence),
                "evidence": asdict(evidence),
                "cell_metrics": metrics,
                "scientific_digest": digest,
            },
            create_only=True,
        )
        recorded = read_json(output / "result.json")
        if recorded.get("scientific_digest") != digest or recorded.get("verdict") != verdict.value:
            raise P2ArtifactError("result readback identity failed")
    except Exception:
        observer.close(False)
        raise
    observer.close(True)
    return P2RunResult(verdict, evidence, output, digest)


def run_registered_p2(output_dir: Path, *, observer_factory=None) -> P2RunResult:
    config = P2Config.registered()
    config.assert_registered()
    return run_execution(output_dir, config, observer_factory=observer_factory)


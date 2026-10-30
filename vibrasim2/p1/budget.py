"""Wall-clock budget leases for P1 implementation and audit execution."""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .registration import P1_DESIGN_SHA256

_PHASES = {"implementation", "implementation_correction", "scientific_audit"}


class P1BudgetError(RuntimeError):
    """Raised when the frozen P1 wall-clock contract is not satisfied."""


@dataclass(frozen=True)
class P1BudgetLease:
    started_at_utc: str
    phase: str
    owner: str
    registration_sha256: str


def _utc(value: datetime | None) -> datetime:
    current = datetime.now(UTC) if value is None else value
    if current.tzinfo is None:
        raise P1BudgetError("budget timestamps must be timezone-aware")
    return current.astimezone(UTC)


def _stamp(value: datetime) -> str:
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise P1BudgetError(f"cannot read P1 budget ledger: {path}") from error
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise P1BudgetError("invalid P1 budget ledger schema")
    if value.get("registration_sha256") != P1_DESIGN_SHA256:
        raise P1BudgetError("P1 registration digest mismatch")
    ceiling = value.get("hard_ceiling_seconds")
    cumulative = value.get("cumulative_elapsed_seconds")
    intervals = value.get("intervals")
    if (
        not isinstance(ceiling, int)
        or ceiling <= 0
        or not isinstance(cumulative, int)
        or cumulative < 0
        or not isinstance(intervals, list)
    ):
        raise P1BudgetError("invalid P1 budget values")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8") + b"\n"
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_bytes(encoded)
        os.replace(temporary, path)
        if json.loads(path.read_text(encoding="utf-8")) != value:
            raise P1BudgetError("P1 budget readback mismatch")
    except OSError as error:
        raise P1BudgetError(f"cannot write P1 budget ledger: {path}") from error
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def _open_intervals(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in value["intervals"] if item.get("ended_at_utc") is None]


def assert_p1_budget_allows_audit(path: str | Path) -> dict[str, Any]:
    value = _load(Path(path))
    if _open_intervals(value):
        raise P1BudgetError("P1 budget contains an open interval")
    if value["cumulative_elapsed_seconds"] >= value["hard_ceiling_seconds"]:
        raise P1BudgetError("P1 hard ceiling reached")
    if value.get("status") != "within_cap":
        raise P1BudgetError("P1 budget is not closed within cap")
    return value


def start_p1_interval(
    path: str | Path,
    phase: str,
    owner: str,
    *,
    now: datetime | None = None,
) -> P1BudgetLease:
    target = Path(path)
    value = _load(target)
    if phase not in _PHASES:
        raise P1BudgetError(f"unrecognized P1 budget phase: {phase}")
    if not owner or _open_intervals(value):
        raise P1BudgetError("P1 budget already has an open interval")
    if value["cumulative_elapsed_seconds"] >= value["hard_ceiling_seconds"]:
        raise P1BudgetError("P1 hard ceiling reached")
    lease = P1BudgetLease(
        _stamp(_utc(now)), phase, owner, value["registration_sha256"]
    )
    value["intervals"].append(
        {
            "started_at_utc": lease.started_at_utc,
            "ended_at_utc": None,
            "elapsed_seconds": None,
            "phase": phase,
            "owner": owner,
            "outcome": None,
        }
    )
    value["status"] = "in_progress"
    _write(target, value)
    return lease


def finish_p1_interval(
    path: str | Path,
    lease: P1BudgetLease,
    outcome: str,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    target = Path(path)
    value = _load(target)
    opened = _open_intervals(value)
    if len(opened) != 1:
        raise P1BudgetError("expected exactly one open P1 interval")
    interval = opened[0]
    if (
        lease.registration_sha256 != value["registration_sha256"]
        or interval.get("started_at_utc") != lease.started_at_utc
        or interval.get("phase") != lease.phase
        or interval.get("owner") != lease.owner
    ):
        raise P1BudgetError("P1 budget lease mismatch")
    started = datetime.fromisoformat(lease.started_at_utc.replace("Z", "+00:00"))
    ended = _utc(now)
    elapsed = math.ceil((ended - started).total_seconds())
    if elapsed < 0:
        raise P1BudgetError("P1 budget interval ended before it started")
    interval.update(
        ended_at_utc=_stamp(ended), elapsed_seconds=elapsed, outcome=outcome
    )
    value["cumulative_elapsed_seconds"] += elapsed
    value["status"] = (
        "within_cap"
        if value["cumulative_elapsed_seconds"] < value["hard_ceiling_seconds"]
        else "hard_ceiling_reached"
    )
    _write(target, value)
    return value

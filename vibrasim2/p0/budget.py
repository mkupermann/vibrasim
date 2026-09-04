"""Validated, atomic wall-clock budget ledger for the registered P0 route."""

from __future__ import annotations

import hashlib
import json
import math
import os
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


HARD_CEILING_SECONDS = 19_800
RUN_REVIEW_RESERVE_SECONDS = 2_700
REVIEW_RESERVE_SECONDS = 1_801
RUN_LIMIT_SECONDS = 900
IMPLEMENTATION_OWNER = "work/vibrasim2-research-reset"
ALLOWED_PHASES = frozenset(("implementation", "implementation_correction", "scientific_run", "review"))
ALLOWED_OUTCOMES = frozenset(("completed", "aborted"))
ALLOWED_STATUSES = frozenset(("active", "within_cap", "phase_reserve_breached", "overrun_registration_required"))
BUDGETED_PATHS = (
    "tests/vibrasim2/test_p0_artifacts.py",
    "tests/vibrasim2/test_p0_budget.py",
    "tests/vibrasim2/test_p0_cli.py",
    "tests/vibrasim2/test_p0_dynamics.py",
    "tests/vibrasim2/test_p0_energy.py",
    "tests/vibrasim2/test_p0_fixtures.py",
    "tests/vibrasim2/test_p0_runner.py",
    "tests/vibrasim2/test_p0_types.py",
    "tests/vibrasim2/test_p0_verdict.py",
    "vibrasim2/p0/__init__.py",
    "vibrasim2/p0/artifacts.py",
    "vibrasim2/p0/budget.py",
    "vibrasim2/p0/cli.py",
    "vibrasim2/p0/dynamics.py",
    "vibrasim2/p0/energy.py",
    "vibrasim2/p0/fixtures.py",
    "vibrasim2/p0/runner.py",
    "vibrasim2/p0/types.py",
    "vibrasim2/p0/verdict.py",
)
_LEDGER_KEYS = frozenset(
    (
        "schema_version",
        "registration_sha256",
        "hard_ceiling_seconds",
        "status",
        "cumulative_elapsed_seconds",
        "scientific_core_sha256",
        "budgeted_paths",
        "intervals",
    )
)
_INTERVAL_KEYS = frozenset(
    ("started_at_utc", "ended_at_utc", "elapsed_seconds", "phase", "owner", "outcome")
)


class BudgetError(RuntimeError):
    """The ledger is malformed, blocked, or cannot authorize its next phase."""


@dataclass(frozen=True)
class BudgetInterval:
    started_at_utc: datetime
    ended_at_utc: datetime | None
    elapsed_seconds: int | None
    phase: str
    owner: str
    outcome: str | None

    @property
    def is_open(self) -> bool:
        return self.ended_at_utc is None


@dataclass(frozen=True)
class BudgetLedger:
    schema_version: int
    registration_sha256: str
    hard_ceiling_seconds: int
    status: str
    cumulative_elapsed_seconds: int
    scientific_core_sha256: str | None
    budgeted_paths: tuple[str, ...]
    intervals: tuple[BudgetInterval, ...]


@dataclass(frozen=True)
class BudgetLease:
    ledger_path: Path
    expected_registration_sha256: str
    repository_root: Path
    phase: str
    owner: str
    started_at_utc: datetime


def _require_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise BudgetError(f"{name} must be an integer")
    return value


def _parse_utc(value: object, name: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise BudgetError(f"{name} must be an RFC3339 UTC timestamp") from exc
    else:
        raise BudgetError(f"{name} must be an RFC3339 UTC timestamp")
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise BudgetError(f"{name} must be timezone-aware UTC")
    return parsed.astimezone(timezone.utc)


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_digest(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise BudgetError("scientific_core_sha256 must be a lowercase SHA-256 hex digest or null")
    return value


def _parse_interval(raw: object, index: int) -> BudgetInterval:
    if not isinstance(raw, dict) or frozenset(raw) != _INTERVAL_KEYS:
        raise BudgetError(f"interval {index} has unknown or missing keys")
    started = _parse_utc(raw["started_at_utc"], f"interval {index} start")
    phase = raw["phase"]
    owner = raw["owner"]
    if phase not in ALLOWED_PHASES:
        raise BudgetError(f"interval {index} has an invalid phase")
    if not isinstance(owner, str) or not owner:
        raise BudgetError(f"interval {index} owner must be a non-empty string")

    end_raw = raw["ended_at_utc"]
    elapsed_raw = raw["elapsed_seconds"]
    outcome = raw["outcome"]
    open_values = (end_raw is None, elapsed_raw is None, outcome is None)
    if any(open_values) and not all(open_values):
        raise BudgetError(f"interval {index} has inconsistent open/closed fields")
    if all(open_values):
        return BudgetInterval(started, None, None, phase, owner, None)

    ended = _parse_utc(end_raw, f"interval {index} end")
    if ended < started:
        raise BudgetError(f"interval {index} end timestamp precedes its start timestamp")
    elapsed = _require_int(elapsed_raw, f"interval {index} elapsed_seconds")
    expected_elapsed = math.ceil((ended - started).total_seconds())
    if elapsed != expected_elapsed:
        raise BudgetError(f"interval {index} elapsed_seconds does not match its timestamps")
    if outcome not in ALLOWED_OUTCOMES:
        raise BudgetError(f"interval {index} has an invalid outcome")
    return BudgetInterval(started, ended, elapsed, phase, owner, outcome)


def _validate_phase_order(intervals: tuple[BudgetInterval, ...]) -> None:
    first = intervals[0]
    if first.phase != "implementation" or first.owner != IMPLEMENTATION_OWNER:
        raise BudgetError("the first interval must be the registered implementation interval")
    seen_scientific = False
    seen_review = False
    scientific: BudgetInterval | None = None
    for index, interval in enumerate(intervals[1:], start=1):
        if interval.phase == "implementation":
            raise BudgetError("implementation may occur only in the first interval")
        if interval.phase == "implementation_correction":
            if seen_scientific or seen_review:
                raise BudgetError("implementation corrections must precede scientific data")
        elif interval.phase == "scientific_run":
            if seen_scientific or seen_review:
                raise BudgetError("at most one scientific run is registered")
            seen_scientific = True
            scientific = interval
        elif interval.phase == "review":
            if seen_review or scientific is None or scientific.outcome != "completed":
                raise BudgetError("review requires exactly one completed scientific run")
            seen_review = True

        if any(previous.outcome == "aborted" for previous in intervals[:index]):
            raise BudgetError("an aborted interval blocks every later phase pending audit")


def _expected_closed_status(ledger: BudgetLedger) -> str:
    if ledger.cumulative_elapsed_seconds >= HARD_CEILING_SECONDS:
        return "overrun_registration_required"
    if any(interval.outcome == "aborted" for interval in ledger.intervals):
        return "phase_reserve_breached"
    remaining = HARD_CEILING_SECONDS - ledger.cumulative_elapsed_seconds
    last = ledger.intervals[-1]
    if last.phase in {"implementation", "implementation_correction"} and remaining < RUN_REVIEW_RESERVE_SECONDS:
        return "phase_reserve_breached"
    scientific_index = next(
        (index for index, interval in enumerate(ledger.intervals) if interval.phase == "scientific_run"),
        None,
    )
    scientific = ledger.intervals[scientific_index] if scientific_index is not None else None
    elapsed_through_scientific = (
        sum(interval.elapsed_seconds or 0 for interval in ledger.intervals[: scientific_index + 1])
        if scientific_index is not None
        else 0
    )
    remaining_after_scientific = HARD_CEILING_SECONDS - elapsed_through_scientific
    if scientific is not None and scientific.elapsed_seconds is not None and (
        scientific.elapsed_seconds >= RUN_LIMIT_SECONDS
        or remaining_after_scientific < REVIEW_RESERVE_SECONDS
    ):
        return "phase_reserve_breached"
    review = next((interval for interval in ledger.intervals if interval.phase == "review"), None)
    if review is not None and review.elapsed_seconds is not None and review.elapsed_seconds > 1_800:
        return "phase_reserve_breached"
    return "within_cap"


def _parse_ledger(raw: object) -> BudgetLedger:
    if not isinstance(raw, dict) or frozenset(raw) != _LEDGER_KEYS:
        raise BudgetError("budget ledger has unknown or missing keys")
    schema_version = _require_int(raw["schema_version"], "schema_version")
    hard_ceiling = _require_int(raw["hard_ceiling_seconds"], "hard_ceiling_seconds")
    cumulative = _require_int(raw["cumulative_elapsed_seconds"], "cumulative_elapsed_seconds")
    registration = raw["registration_sha256"]
    status = raw["status"]
    paths = raw["budgeted_paths"]
    intervals_raw = raw["intervals"]
    if schema_version != 1:
        raise BudgetError("unsupported budget ledger schema version")
    if hard_ceiling != HARD_CEILING_SECONDS:
        raise BudgetError("hard ceiling must remain exactly 19800 seconds")
    if not isinstance(registration, str) or len(registration) != 64:
        raise BudgetError("registration_sha256 must be a SHA-256 digest")
    if status not in ALLOWED_STATUSES:
        raise BudgetError("budget ledger has an invalid status")
    if not isinstance(paths, list) or tuple(paths) != BUDGETED_PATHS:
        raise BudgetError("budgeted path inventory does not match the registered inventory")
    if not isinstance(intervals_raw, list) or not intervals_raw:
        raise BudgetError("budget ledger must contain at least one interval")
    intervals = tuple(_parse_interval(value, index) for index, value in enumerate(intervals_raw))
    if sum(interval.is_open for interval in intervals) > 1 or any(interval.is_open for interval in intervals[:-1]):
        raise BudgetError("only the last interval may be open")
    previous_end: datetime | None = None
    for interval in intervals:
        if previous_end is not None and interval.started_at_utc < previous_end:
            raise BudgetError("budget intervals overlap or have non-monotonic ordering")
        previous_end = interval.ended_at_utc
    _validate_phase_order(intervals)

    computed_sum = sum(interval.elapsed_seconds or 0 for interval in intervals)
    if cumulative != computed_sum:
        raise BudgetError("cumulative_elapsed_seconds is inconsistent with interval durations")
    if cumulative < 0:
        raise BudgetError("cumulative_elapsed_seconds cannot be negative")
    core_digest = _validate_digest(raw["scientific_core_sha256"])
    ledger = BudgetLedger(
        schema_version,
        registration,
        hard_ceiling,
        status,
        cumulative,
        core_digest,
        tuple(paths),
        intervals,
    )
    if intervals[-1].is_open:
        if status != "active":
            raise BudgetError("an open interval requires active status")
        if len(intervals) == 1 and core_digest is not None:
            raise BudgetError("the initial open implementation ledger cannot have a core digest")
    else:
        expected_status = _expected_closed_status(ledger)
        if status != expected_status:
            raise BudgetError(f"closed ledger status must be {expected_status}")
        if core_digest is None:
            raise BudgetError("a closed implementation ledger requires a scientific core digest")
    return ledger


def load_budget_ledger(path: Path) -> BudgetLedger:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BudgetError(f"cannot read budget ledger: {exc}") from exc
    return _parse_ledger(raw)


def _canonical_lf_bytes(path: Path) -> bytes:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BudgetError(f"missing or unreadable budgeted file: {path}") from exc
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _scientific_core_digest(repository_root: Path) -> str:
    digest = hashlib.sha256()
    for relative in BUDGETED_PATHS:
        data = _canonical_lf_bytes(repository_root / relative)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
    return digest.hexdigest()


def _lock_path(ledger_path: Path) -> Path:
    return ledger_path.with_name(ledger_path.name + ".lock")


def _validate_core_and_registration(
    ledger: BudgetLedger,
    expected_registration_sha256: str,
    repository_root: Path,
) -> None:
    if ledger.registration_sha256 != expected_registration_sha256:
        raise BudgetError("budget ledger registration identity does not match")
    actual_digest = _scientific_core_digest(repository_root)
    if ledger.scientific_core_sha256 != actual_digest:
        raise BudgetError("scientific core digest changed after budget closure")


def assert_budget_allows_run(
    ledger_path: Path,
    expected_registration_sha256: str,
    repository_root: Path,
) -> BudgetLedger:
    ledger_path = Path(ledger_path).resolve()
    if _lock_path(ledger_path).exists():
        raise BudgetError("budget ledger lock exists and requires manual audit")
    ledger = load_budget_ledger(ledger_path)
    _validate_core_and_registration(ledger, expected_registration_sha256, Path(repository_root).resolve())
    if ledger.status != "within_cap" or ledger.intervals[-1].is_open:
        raise BudgetError(f"budget ledger status {ledger.status!r} does not allow a run")
    if any(interval.phase == "scientific_run" for interval in ledger.intervals):
        raise BudgetError("the registered scientific run has already been attempted")
    if ledger.intervals[0].outcome != "completed":
        raise BudgetError("the registered implementation interval is not complete")
    remaining = HARD_CEILING_SECONDS - ledger.cumulative_elapsed_seconds
    if remaining < RUN_REVIEW_RESERVE_SECONDS:
        raise BudgetError("registered run-plus-review reserve is not available")
    return ledger


@contextmanager
def _exclusive_lock(ledger_path: Path) -> Iterator[None]:
    lock = _lock_path(ledger_path)
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise BudgetError("budget ledger lock exists and requires manual audit") from exc
    try:
        os.write(descriptor, str(os.getpid()).encode("ascii"))
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        yield
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def _ledger_to_json(ledger: BudgetLedger) -> dict[str, object]:
    intervals = []
    for interval in ledger.intervals:
        value = asdict(interval)
        value["started_at_utc"] = _format_utc(interval.started_at_utc)
        value["ended_at_utc"] = _format_utc(interval.ended_at_utc) if interval.ended_at_utc else None
        intervals.append(value)
    return {
        "schema_version": ledger.schema_version,
        "registration_sha256": ledger.registration_sha256,
        "hard_ceiling_seconds": ledger.hard_ceiling_seconds,
        "status": ledger.status,
        "cumulative_elapsed_seconds": ledger.cumulative_elapsed_seconds,
        "scientific_core_sha256": ledger.scientific_core_sha256,
        "budgeted_paths": list(ledger.budgeted_paths),
        "intervals": intervals,
    }


def _atomic_write(ledger_path: Path, ledger: BudgetLedger) -> BudgetLedger:
    temporary = ledger_path.with_name(f".{ledger_path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(_ledger_to_json(ledger), handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, ledger_path)
        return load_budget_ledger(ledger_path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def start_budget_interval(
    ledger_path: Path,
    expected_registration_sha256: str,
    repository_root: Path,
    *,
    phase: str,
    owner: str,
    started_at_utc: datetime,
) -> BudgetLease:
    ledger_path = Path(ledger_path).resolve()
    repository_root = Path(repository_root).resolve()
    started = _parse_utc(started_at_utc, "interval start")
    if phase not in {"implementation_correction", "scientific_run", "review"}:
        raise BudgetError("invalid phase for a new budget interval")
    if not isinstance(owner, str) or not owner:
        raise BudgetError("budget lease owner must be a non-empty string")

    with _exclusive_lock(ledger_path):
        ledger = load_budget_ledger(ledger_path)
        _validate_core_and_registration(ledger, expected_registration_sha256, repository_root)
        if ledger.status != "within_cap" or ledger.intervals[-1].is_open:
            raise BudgetError(f"budget ledger status {ledger.status!r} does not allow another interval")
        if started < ledger.intervals[-1].ended_at_utc:
            raise BudgetError("new interval start timestamp is non-monotonic")
        remaining = HARD_CEILING_SECONDS - ledger.cumulative_elapsed_seconds
        scientific = [interval for interval in ledger.intervals if interval.phase == "scientific_run"]
        reviews = [interval for interval in ledger.intervals if interval.phase == "review"]
        if phase == "implementation_correction":
            if scientific or reviews or remaining <= 0:
                raise BudgetError("implementation correction is not permitted in this phase state")
        elif phase == "scientific_run":
            if scientific or reviews or remaining < RUN_REVIEW_RESERVE_SECONDS:
                raise BudgetError("registered scientific run phase or reserve is unavailable")
        else:
            if len(scientific) != 1 or scientific[0].outcome != "completed" or reviews:
                raise BudgetError("review requires exactly one completed scientific run and no prior review")
            if remaining < REVIEW_RESERVE_SECONDS:
                raise BudgetError("registered review reserve is unavailable")
        interval = BudgetInterval(started, None, None, phase, owner, None)
        active = replace(ledger, status="active", intervals=ledger.intervals + (interval,))
        _atomic_write(ledger_path, active)
    return BudgetLease(ledger_path, expected_registration_sha256, repository_root, phase, owner, started)


def finish_budget_interval(
    lease: BudgetLease,
    *,
    ended_at_utc: datetime,
    outcome: str,
) -> BudgetLedger:
    if outcome not in ALLOWED_OUTCOMES:
        raise BudgetError("budget interval outcome must be completed or aborted")
    ended = _parse_utc(ended_at_utc, "interval end")
    with _exclusive_lock(lease.ledger_path):
        ledger = load_budget_ledger(lease.ledger_path)
        if ledger.registration_sha256 != lease.expected_registration_sha256:
            raise BudgetError("budget lease registration identity does not match")
        if ledger.status != "active" or not ledger.intervals[-1].is_open:
            raise BudgetError("budget lease does not identify the active interval")
        current = ledger.intervals[-1]
        if (
            current.phase != lease.phase
            or current.owner != lease.owner
            or current.started_at_utc != lease.started_at_utc
        ):
            raise BudgetError("budget lease owner or interval identity does not match")
        if ended < current.started_at_utc:
            raise BudgetError("interval end timestamp precedes its start timestamp")
        if current.phase != "implementation_correction":
            _validate_core_and_registration(ledger, lease.expected_registration_sha256, lease.repository_root)
        elapsed = math.ceil((ended - current.started_at_utc).total_seconds())
        closed_interval = replace(current, ended_at_utc=ended, elapsed_seconds=elapsed, outcome=outcome)
        core_digest = ledger.scientific_core_sha256
        if current.phase == "implementation_correction":
            core_digest = _scientific_core_digest(lease.repository_root)
        closed = replace(
            ledger,
            cumulative_elapsed_seconds=ledger.cumulative_elapsed_seconds + elapsed,
            scientific_core_sha256=core_digest,
            intervals=ledger.intervals[:-1] + (closed_interval,),
        )
        closed = replace(closed, status=_expected_closed_status(closed))
        return _atomic_write(lease.ledger_path, closed)

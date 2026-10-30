"""Single-run authority and scientific-core identity for registered V2-P2."""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .artifacts import atomic_write_json
from .registration import P2_REGISTRATION_SHA256


CORE_PATHS = (
    "docs/amendments/v2_p2_dynamic_maintenance.md",
    "vibrasim2/p2/registration.py",
    "vibrasim2/p2/types.py",
    "vibrasim2/p2/fixtures.py",
    "vibrasim2/p2/bonds.py",
    "vibrasim2/p2/dynamics.py",
    "vibrasim2/p2/trajectory.py",
    "vibrasim2/p2/verdict.py",
    "vibrasim2/p2/artifacts.py",
    "vibrasim2/p2/runner.py",
    "vibrasim2/p2/budget.py",
)
HARD_CEILING_SECONDS = 18_000


class P2BudgetError(RuntimeError):
    pass


@dataclass(frozen=True)
class P2BudgetLease:
    ledger_path: Path
    repository_root: Path
    run_id: str
    started_monotonic: float


def scientific_core_digest(repository_root: Path) -> str:
    root = Path(repository_root).resolve()
    hasher = hashlib.sha256()
    for relative_text in CORE_PATHS:
        relative = Path(relative_text)
        path = root / relative
        if not path.is_file():
            raise P2BudgetError(f"missing scientific core path: {relative_text}")
        name = relative.as_posix().encode()
        payload = path.read_bytes()
        hasher.update(len(name).to_bytes(8, "big"))
        hasher.update(name)
        hasher.update(len(payload).to_bytes(8, "big"))
        hasher.update(payload)
    return hasher.hexdigest()


def _read(path: Path) -> dict[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise P2BudgetError(f"invalid P2 budget ledger: {path}") from exc
    if not isinstance(value, dict):
        raise P2BudgetError("P2 budget ledger must be an object")
    return value


def assert_ready(ledger_path: Path, repository_root: Path) -> dict[str, object]:
    ledger = _read(ledger_path)
    required = {
        "schema_version", "experiment", "status", "registration_sha256",
        "scientific_core_sha256", "hard_ceiling_seconds", "run_id",
        "started_at_utc", "elapsed_seconds",
    }
    if set(ledger) != required or ledger.get("schema_version") != 1 or ledger.get("experiment") != "P2":
        raise P2BudgetError("P2 budget ledger schema is invalid")
    if ledger.get("status") != "ready" or ledger.get("run_id") is not None:
        raise P2BudgetError(f"P2 budget status {ledger.get('status')!r} does not authorize a run")
    if ledger.get("registration_sha256") != P2_REGISTRATION_SHA256:
        raise P2BudgetError("P2 registration identity mismatch")
    if ledger.get("hard_ceiling_seconds") != HARD_CEILING_SECONDS:
        raise P2BudgetError("P2 hard ceiling mismatch")
    if ledger.get("scientific_core_sha256") != scientific_core_digest(repository_root):
        raise P2BudgetError("P2 scientific core identity mismatch")
    return ledger


def start_run(ledger_path: Path, repository_root: Path, run_id: str) -> P2BudgetLease:
    path = Path(ledger_path).resolve()
    lock = path.with_name(path.name + ".lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(descriptor)
    except FileExistsError as exc:
        raise P2BudgetError("P2 budget lock requires audit") from exc
    try:
        ledger = assert_ready(path, repository_root)
        ledger.update(
            status="active",
            run_id=run_id,
            started_at_utc=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        )
        atomic_write_json(path, ledger)
    finally:
        lock.unlink(missing_ok=True)
    return P2BudgetLease(path, Path(repository_root).resolve(), run_id, time.monotonic())


def finish_run(lease: P2BudgetLease, *, completed: bool) -> dict[str, object]:
    ledger = _read(lease.ledger_path)
    if ledger.get("status") != "active" or ledger.get("run_id") != lease.run_id:
        raise P2BudgetError("P2 active lease identity mismatch")
    elapsed = max(0, int(round(time.monotonic() - lease.started_monotonic)))
    ledger["elapsed_seconds"] = elapsed
    if elapsed >= HARD_CEILING_SECONDS:
        ledger["status"] = "ceiling_exceeded"
    else:
        ledger["status"] = "used" if completed else "aborted"
    atomic_write_json(lease.ledger_path, ledger)
    return _read(lease.ledger_path)

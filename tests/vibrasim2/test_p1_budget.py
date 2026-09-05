import json
from datetime import UTC, datetime, timedelta

import pytest

from vibrasim2.p1.budget import (
    P1BudgetError,
    assert_p1_budget_allows_audit,
    finish_p1_interval,
    start_p1_interval,
)
from vibrasim2.p1.registration import P1_DESIGN_SHA256


def ledger(*, ceiling=100, cumulative=0, status="not_started", intervals=None):
    return {
        "schema_version": 1,
        "registration_sha256": P1_DESIGN_SHA256,
        "registration_git_blob": "8" * 40,
        "hard_ceiling_seconds": ceiling,
        "status": status,
        "cumulative_elapsed_seconds": cumulative,
        "budgeted_paths": ["vibrasim2/p1/budget.py"],
        "intervals": [] if intervals is None else intervals,
    }


def write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_budget_rejects_elapsed_hard_ceiling(tmp_path):
    path = write(tmp_path / "ledger.json", ledger(ceiling=10, cumulative=10))
    with pytest.raises(P1BudgetError, match="hard ceiling"):
        assert_p1_budget_allows_audit(path)


def test_budget_rejects_registration_mismatch(tmp_path):
    value = ledger()
    value["registration_sha256"] = "0" * 64
    path = write(tmp_path / "ledger.json", value)
    with pytest.raises(P1BudgetError, match="registration"):
        assert_p1_budget_allows_audit(path)


def test_interval_uses_ceiling_rounded_seconds(tmp_path):
    path = write(tmp_path / "ledger.json", ledger())
    start = datetime(2026, 9, 5, 12, 0, 0, tzinfo=UTC)
    lease = start_p1_interval(path, "implementation", "test", now=start)
    finish_p1_interval(path, lease, "completed", now=start + timedelta(seconds=1.01))
    closed = json.loads(path.read_text(encoding="utf-8"))
    assert closed["cumulative_elapsed_seconds"] == 2
    assert closed["intervals"][-1]["elapsed_seconds"] == 2
    assert closed["status"] == "within_cap"

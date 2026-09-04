import hashlib
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from vibrasim2.p0.budget import (
    BudgetError,
    assert_budget_allows_run,
    finish_budget_interval,
    load_budget_ledger,
    start_budget_interval,
)


REGISTRATION = "28992a8b131100ed4eb2cd9147ddea7b3251921777211a63bb4b64e5524ca9e1"
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
UTC = timezone.utc


def write_core(root: Path) -> str:
    digest = hashlib.sha256()
    for index, relative in enumerate(BUDGETED_PATHS):
        data = f"fixture {index}\n".encode()
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        encoded_path = relative.encode("utf-8")
        digest.update(encoded_path)
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
    return digest.hexdigest()


def timestamp(seconds: int) -> str:
    value = datetime(2026, 9, 4, 8, tzinfo=UTC) + timedelta(seconds=seconds)
    return value.isoformat().replace("+00:00", "Z")


def implementation_interval(elapsed: int, *, outcome: str = "completed") -> dict[str, object]:
    return {
        "started_at_utc": timestamp(0),
        "ended_at_utc": timestamp(elapsed),
        "elapsed_seconds": elapsed,
        "phase": "implementation",
        "owner": "work/vibrasim2-research-reset",
        "outcome": outcome,
    }


def write_ledger(
    root: Path,
    *,
    elapsed: int = 100,
    status: str = "within_cap",
    registration: str = REGISTRATION,
    intervals: list[dict[str, object]] | None = None,
    cumulative: int | None = None,
) -> Path:
    core_digest = write_core(root)
    ledger = root / "docs/vibrasim2/P0_BUDGET_LEDGER.json"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    records = intervals if intervals is not None else [implementation_interval(elapsed)]
    ledger.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "registration_sha256": registration,
                "hard_ceiling_seconds": 19800,
                "status": status,
                "cumulative_elapsed_seconds": elapsed if cumulative is None else cumulative,
                "scientific_core_sha256": core_digest,
                "budgeted_paths": list(BUDGETED_PATHS),
                "intervals": records,
            }
        ),
        encoding="utf-8",
    )
    return ledger


def rewrite(ledger: Path, **changes: object) -> None:
    value = json.loads(ledger.read_text(encoding="utf-8"))
    value.update(changes)
    ledger.write_text(json.dumps(value), encoding="utf-8")


def test_closed_consistent_ledger_allows_first_registered_run(tmp_path):
    ledger = write_ledger(tmp_path)

    parsed = assert_budget_allows_run(ledger, REGISTRATION, tmp_path)

    assert parsed.cumulative_elapsed_seconds == 100
    assert parsed.status == "within_cap"


def test_active_ledger_is_rejected(tmp_path):
    interval = implementation_interval(100)
    interval.update(ended_at_utc=None, elapsed_seconds=None, outcome=None)
    ledger = write_ledger(tmp_path, status="active", intervals=[interval], cumulative=0)

    with pytest.raises(BudgetError, match="open|active"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_exact_hard_ceiling_is_rejected(tmp_path):
    ledger = write_ledger(tmp_path, elapsed=19800, status="overrun_registration_required")

    with pytest.raises(BudgetError, match="overrun|ceiling"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_phase_reserve_breach_is_rejected(tmp_path):
    ledger = write_ledger(tmp_path, elapsed=17101, status="phase_reserve_breached")

    with pytest.raises(BudgetError, match="reserve|status"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_overrun_status_is_rejected(tmp_path):
    ledger = write_ledger(tmp_path, elapsed=19801, status="overrun_registration_required")

    with pytest.raises(BudgetError, match="overrun|ceiling|status"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_wrong_registration_identity_is_rejected(tmp_path):
    ledger = write_ledger(tmp_path, registration="0" * 64)

    with pytest.raises(BudgetError, match="registration"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_backward_timestamps_are_rejected(tmp_path):
    interval = implementation_interval(100)
    interval["ended_at_utc"] = timestamp(-1)
    ledger = write_ledger(tmp_path, intervals=[interval])

    with pytest.raises(BudgetError, match="timestamp|end"):
        load_budget_ledger(ledger)


def test_inconsistent_arithmetic_is_rejected(tmp_path):
    ledger = write_ledger(tmp_path, elapsed=100, cumulative=99)

    with pytest.raises(BudgetError, match="cumulative"):
        load_budget_ledger(ledger)


def test_stale_sibling_lock_is_rejected(tmp_path):
    ledger = write_ledger(tmp_path)
    ledger.with_name(ledger.name + ".lock").write_text("stale", encoding="utf-8")

    with pytest.raises(BudgetError, match="lock"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_fewer_than_registered_reserve_seconds_is_rejected(tmp_path):
    ledger = write_ledger(tmp_path, elapsed=17101, status="within_cap")

    with pytest.raises(BudgetError, match="reserve|status"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_aborted_implementation_correction_is_rejected(tmp_path):
    intervals = [
        implementation_interval(100),
        {
            "started_at_utc": timestamp(100),
            "ended_at_utc": timestamp(110),
            "elapsed_seconds": 10,
            "phase": "implementation_correction",
            "owner": "fix-1",
            "outcome": "aborted",
        },
    ]
    ledger = write_ledger(
        tmp_path,
        elapsed=110,
        status="phase_reserve_breached",
        intervals=intervals,
    )

    with pytest.raises(BudgetError, match="aborted|reserve|status"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_changed_budgeted_file_is_rejected(tmp_path):
    ledger = write_ledger(tmp_path)
    (tmp_path / BUDGETED_PATHS[0]).write_text("changed\n", encoding="utf-8")

    with pytest.raises(BudgetError, match="digest|changed"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_mismatched_path_inventory_is_rejected(tmp_path):
    ledger = write_ledger(tmp_path)
    value = json.loads(ledger.read_text(encoding="utf-8"))
    value["budgeted_paths"] = value["budgeted_paths"][:-1]
    ledger.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(BudgetError, match="path inventory"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_unknown_keys_and_boolean_integers_are_rejected(tmp_path):
    ledger = write_ledger(tmp_path)
    rewrite(ledger, unexpected=True)
    with pytest.raises(BudgetError, match="keys"):
        load_budget_ledger(ledger)

    ledger = write_ledger(tmp_path)
    rewrite(ledger, cumulative_elapsed_seconds=True)
    with pytest.raises(BudgetError, match="integer"):
        load_budget_ledger(ledger)


def test_start_and_finish_correction_are_atomic_and_update_digest(tmp_path):
    ledger = write_ledger(tmp_path)
    lease = start_budget_interval(
        ledger,
        REGISTRATION,
        tmp_path,
        phase="implementation_correction",
        owner="fix-2",
        started_at_utc=datetime(2026, 9, 4, 8, 2, tzinfo=UTC),
    )
    active = load_budget_ledger(ledger)
    assert active.status == "active"
    assert active.intervals[-1].owner == "fix-2"
    assert not ledger.with_name(ledger.name + ".lock").exists()

    (tmp_path / BUDGETED_PATHS[0]).write_text("corrected\n", encoding="utf-8")
    closed = finish_budget_interval(
        lease,
        ended_at_utc=datetime(2026, 9, 4, 8, 2, 1, 200_000, tzinfo=UTC),
        outcome="completed",
    )

    assert closed.status == "within_cap"
    assert closed.cumulative_elapsed_seconds == 102
    assert closed.intervals[-1].elapsed_seconds == 2
    assert closed.scientific_core_sha256 != active.scientific_core_sha256
    assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_second_or_concurrent_start_is_rejected(tmp_path):
    ledger = write_ledger(tmp_path)
    start_budget_interval(
        ledger,
        REGISTRATION,
        tmp_path,
        phase="implementation_correction",
        owner="fix-3",
        started_at_utc=datetime(2026, 9, 4, 8, 2, tzinfo=UTC),
    )
    with pytest.raises(BudgetError, match="open|active"):
        start_budget_interval(
            ledger,
            REGISTRATION,
            tmp_path,
            phase="implementation_correction",
            owner="fix-4",
            started_at_utc=datetime(2026, 9, 4, 8, 3, tzinfo=UTC),
        )


def test_finish_requires_the_exact_lease_owner(tmp_path):
    ledger = write_ledger(tmp_path)
    lease = start_budget_interval(
        ledger,
        REGISTRATION,
        tmp_path,
        phase="implementation_correction",
        owner="fix-5",
        started_at_utc=datetime(2026, 9, 4, 8, 2, tzinfo=UTC),
    )

    with pytest.raises(BudgetError, match="lease|owner"):
        finish_budget_interval(
            replace(lease, owner="not-the-owner"),
            ended_at_utc=datetime(2026, 9, 4, 8, 3, tzinfo=UTC),
            outcome="completed",
        )


def test_completed_900_second_scientific_run_breaches_phase_reserve(tmp_path):
    ledger = write_ledger(tmp_path, elapsed=17100)
    lease = start_budget_interval(
        ledger,
        REGISTRATION,
        tmp_path,
        phase="scientific_run",
        owner="run-1",
        started_at_utc=datetime(2026, 9, 4, 13, tzinfo=UTC),
    )
    closed = finish_budget_interval(
        lease,
        ended_at_utc=datetime(2026, 9, 4, 13, 15, tzinfo=UTC),
        outcome="completed",
    )

    assert closed.status == "phase_reserve_breached"
    with pytest.raises(BudgetError, match="reserve|status"):
        assert_budget_allows_run(ledger, REGISTRATION, tmp_path)


def test_completed_review_does_not_require_a_second_review_reserve(tmp_path):
    ledger = write_ledger(tmp_path, elapsed=17100)
    run_lease = start_budget_interval(
        ledger,
        REGISTRATION,
        tmp_path,
        phase="scientific_run",
        owner="run-2",
        started_at_utc=datetime(2026, 9, 4, 13, tzinfo=UTC),
    )
    run_closed = finish_budget_interval(
        run_lease,
        ended_at_utc=datetime(2026, 9, 4, 13, 14, 59, tzinfo=UTC),
        outcome="completed",
    )
    assert run_closed.status == "within_cap"

    review_lease = start_budget_interval(
        ledger,
        REGISTRATION,
        tmp_path,
        phase="review",
        owner="review-1",
        started_at_utc=datetime(2026, 9, 4, 13, 15, tzinfo=UTC),
    )
    review_closed = finish_budget_interval(
        review_lease,
        ended_at_utc=datetime(2026, 9, 4, 13, 45, tzinfo=UTC),
        outcome="completed",
    )

    assert review_closed.cumulative_elapsed_seconds == 19799
    assert review_closed.status == "within_cap"

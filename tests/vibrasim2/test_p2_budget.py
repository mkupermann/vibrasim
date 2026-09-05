import json
from pathlib import Path

import pytest

from vibrasim2.p2.budget import (
    P2BudgetError,
    assert_ready,
    finish_run,
    scientific_core_digest,
    start_run,
)
from vibrasim2.p2.registration import P2_BUDGET_PATH


ROOT = Path(__file__).resolve().parents[2]


def test_committed_budget_records_the_used_run_and_exact_current_core():
    ledger = json.loads((ROOT / P2_BUDGET_PATH).read_text())

    assert ledger["status"] == "used"
    assert ledger["run_id"] == "v2-p2-848c7cccbc764c29bf45fa7b1805d604"
    assert ledger["elapsed_seconds"] == 366
    assert ledger["scientific_core_sha256"] == scientific_core_digest(ROOT)
    with pytest.raises(P2BudgetError, match="does not authorize"):
        assert_ready(ROOT / P2_BUDGET_PATH, ROOT)


def test_started_lease_blocks_second_run_and_closes_used(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(
        json.dumps(
            {
                "elapsed_seconds": 0,
                "experiment": "P2",
                "hard_ceiling_seconds": 18000,
                "registration_sha256": (
                    "d2f975305d3a5ff49bcf3ef1e2cdbc9e9b3430eca2f70a695b2368df40151255"
                ),
                "run_id": None,
                "schema_version": 1,
                "scientific_core_sha256": scientific_core_digest(ROOT),
                "started_at_utc": None,
                "status": "ready",
            }
        )
    )

    lease = start_run(ledger_path, ROOT, "v2-p2-test")
    with pytest.raises(P2BudgetError, match="does not authorize"):
        start_run(ledger_path, ROOT, "v2-p2-other")
    closed = finish_run(lease, completed=True)

    assert closed["status"] == "used"
    assert closed["run_id"] == "v2-p2-test"
    assert json.loads(ledger_path.read_text())["status"] == "used"

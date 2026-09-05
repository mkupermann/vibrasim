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


def test_committed_budget_authorizes_exact_current_core_once():
    ledger = assert_ready(ROOT / P2_BUDGET_PATH, ROOT)

    assert ledger["scientific_core_sha256"] == scientific_core_digest(ROOT)


def test_started_lease_blocks_second_run_and_closes_used(tmp_path):
    source = ROOT / P2_BUDGET_PATH
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_bytes(source.read_bytes())

    lease = start_run(ledger_path, ROOT, "v2-p2-test")
    with pytest.raises(P2BudgetError, match="does not authorize"):
        start_run(ledger_path, ROOT, "v2-p2-other")
    closed = finish_run(lease, completed=True)

    assert closed["status"] == "used"
    assert closed["run_id"] == "v2-p2-test"
    assert json.loads(ledger_path.read_text())["status"] == "used"

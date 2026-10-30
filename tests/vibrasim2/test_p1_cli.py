import json
from pathlib import Path

from vibrasim2.p1.audit import AuditOutcome, AuditResult
from vibrasim2.p1.cli import main
from vibrasim2.p1.registration import P1_DESIGN_SHA256


def budget(path):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "registration_sha256": P1_DESIGN_SHA256,
                "registration_git_blob": "8" * 40,
                "hard_ceiling_seconds": 100,
                "status": "within_cap",
                "cumulative_elapsed_seconds": 0,
                "budgeted_paths": [],
                "intervals": [],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_cli_rejects_existing_output_before_input_read(tmp_path, monkeypatch, capsys):
    root = tmp_path / "v2-p1"
    root.mkdir()
    output = root / "existing"
    output.mkdir()
    monkeypatch.setattr("vibrasim2.p1.cli.P1_OUTPUT_ROOT", root)
    code = main(["audit", "--input-dir", str(tmp_path / "missing"), "--output-dir", str(output)])
    assert code == 1
    assert "output" in capsys.readouterr().err.lower()


def test_cli_writes_audited_result_under_fixed_root(tmp_path, monkeypatch, capsys):
    root = tmp_path / "v2-p1"
    root.mkdir()
    ledger = budget(tmp_path / "ledger.json")
    monkeypatch.setattr("vibrasim2.p1.cli.P1_OUTPUT_ROOT", root)
    monkeypatch.setattr("vibrasim2.p1.cli.P1_BUDGET_PATH", ledger)
    monkeypatch.setattr(
        "vibrasim2.p1.cli.audit_registered_run",
        lambda _: AuditResult(AuditOutcome.UNRESOLVED, ()),
    )
    output = root / "audit-001"
    code = main(["audit", "--input-dir", str(tmp_path), "--output-dir", str(output)])
    assert code == 0
    assert json.loads((output / "audit.json").read_text())["outcome"] == "UNRESOLVED"
    assert "UNRESOLVED" in capsys.readouterr().out
    closed = json.loads(Path(ledger).read_text())
    assert closed["intervals"][-1]["outcome"] == "completed"

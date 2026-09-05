from pathlib import Path
from types import SimpleNamespace

import pytest

from vibrasim2.p2.cli import main
from vibrasim2.p2.types import Verdict


def test_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_run_uses_budget_and_observer(monkeypatch, tmp_path, capsys):
    calls = []
    lease = object()
    monkeypatch.setattr("vibrasim2.p2.cli.start_run", lambda *args: calls.append("start") or lease)
    monkeypatch.setattr("vibrasim2.p2.cli.make_p2_observer_factory", lambda path: ("observer", path))
    monkeypatch.setattr(
        "vibrasim2.p2.cli.run_registered_p2",
        lambda output, **kwargs: calls.append((output, kwargs)) or SimpleNamespace(
            verdict=Verdict.NULL, scientific_digest="a" * 64, output_dir=output
        ),
    )
    monkeypatch.setattr(
        "vibrasim2.p2.cli.finish_run",
        lambda actual, completed: calls.append((actual, completed)),
    )

    assert main(["run", "--output-dir", str(tmp_path), "--observe"]) == 0
    assert calls[0] == "start"
    assert calls[-1] == (lease, True)
    assert calls[1][0] == tmp_path
    assert calls[1][1]["observer_factory"] == ("observer", tmp_path)
    assert "V2-P2 NULL" in capsys.readouterr().out


def test_budget_failure_returns_nonzero(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(
        "vibrasim2.p2.cli.start_run",
        lambda *args: (_ for _ in ()).throw(RuntimeError("blocked")),
    )

    assert main(["run", "--output-dir", str(tmp_path)]) == 1
    assert "blocked" in capsys.readouterr().err

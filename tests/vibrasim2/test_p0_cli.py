from pathlib import Path
from types import SimpleNamespace

import pytest

from vibrasim2.p0.artifacts import ArtifactError
from vibrasim2.p0.cli import main
from vibrasim2.p0.runner import PostRunBudgetError
from vibrasim2.p0.types import Verdict

RUN_PATH = Path("archive/run-logs/v2-p0/cli-boundary-test")


def test_help_is_safe(capsys):
    with pytest.raises(SystemExit) as stopped:
        main(["--help"])
    assert stopped.value.code == 0
    assert "registered V2-P0" in capsys.readouterr().out


def test_output_directory_is_explicit(capsys):
    with pytest.raises(SystemExit) as stopped:
        main(["run"])
    assert stopped.value.code == 2
    assert "--output-dir" in capsys.readouterr().err


def test_unregistered_axes_are_rejected(capsys):
    for option in ("--seed", "--dt", "--steps", "--g", "--k-b", "--source-centre"):
        with pytest.raises(SystemExit) as stopped:
            main(["run", "--output-dir", str(RUN_PATH), option, "1"])
        assert stopped.value.code == 2


def test_run_delegates_once_without_a_seed(monkeypatch, capsys):
    calls = []
    fake = SimpleNamespace(
        verdict=SimpleNamespace(value="NULL"),
        scientific_digest="abc123",
        output_dir=RUN_PATH,
    )
    monkeypatch.setattr(
        "vibrasim2.p0.cli.run_registered_p0", lambda path: calls.append(path) or fake
    )
    assert main(["run", "--output-dir", str(RUN_PATH)]) == 0
    assert calls == [RUN_PATH.resolve()]
    assert "NULL" in capsys.readouterr().out


def test_observe_changes_only_the_sink_factory(monkeypatch):
    calls = []
    factory = object()
    fake = SimpleNamespace(
        verdict=SimpleNamespace(value="NULL"),
        scientific_digest="abc123",
        output_dir=RUN_PATH,
    )
    monkeypatch.setattr(
        "vibrasim2.p0.cli.resolve_observer_factory",
        lambda observe, path: factory if observe else None,
    )
    monkeypatch.setattr(
        "vibrasim2.p0.cli.run_registered_p0",
        lambda path, observer_factory=None: (
            calls.append((path, observer_factory)) or fake
        ),
    )
    assert main(["run", "--output-dir", str(RUN_PATH), "--observe"]) == 0
    assert calls == [(RUN_PATH.resolve(), factory)]


def test_pre_result_failure_is_reported_without_a_verdict(monkeypatch, capsys):
    monkeypatch.setattr(
        "vibrasim2.p0.cli.run_registered_p0",
        lambda *args, **kwargs: (_ for _ in ()).throw(ArtifactError("disk failed")),
    )
    assert main(["run", "--output-dir", str(RUN_PATH)]) == 1
    captured = capsys.readouterr()
    assert "NO SCIENTIFIC VERDICT" in captured.err
    assert "disk failed" in captured.err


def test_observer_setup_failure_is_reported_without_a_verdict(monkeypatch, capsys):
    monkeypatch.setattr(
        "vibrasim2.p0.cli.resolve_observer_factory",
        lambda *args: (_ for _ in ()).throw(RuntimeError("viewer unavailable")),
    )
    assert main(["run", "--output-dir", str(RUN_PATH), "--observe"]) == 1
    captured = capsys.readouterr()
    assert "NO SCIENTIFIC VERDICT" in captured.err
    assert "viewer unavailable" in captured.err


def test_post_run_budget_stop_reports_the_durable_verdict(monkeypatch, capsys):
    result_path = RUN_PATH / "result.json"
    monkeypatch.setattr(
        "vibrasim2.p0.cli.run_registered_p0",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            PostRunBudgetError(result_path, Verdict.NULL, "phase_reserve_breached")
        ),
    )
    assert main(["run", "--output-dir", str(RUN_PATH)]) == 1
    captured = capsys.readouterr()
    assert "SCIENTIFIC VERDICT RECORDED" in captured.err
    assert str(result_path) in captured.err
    assert "NULL" in captured.err


def test_observer_factory_is_resolved_lazily(monkeypatch):
    factory = object()
    monkeypatch.setattr(
        "vibrasim2.viewer_process.make_registered_observer_factory",
        lambda output_dir: factory,
    )
    from vibrasim2.p0.cli import resolve_observer_factory

    assert resolve_observer_factory(False, RUN_PATH) is None
    assert resolve_observer_factory(True, RUN_PATH) is factory

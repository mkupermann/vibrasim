"""Tiny technical fixtures for frozen execution and tamper detection."""
import importlib.util
import json

import pytest

from vibrasim2.l0 import evaluation as ev


def runner():
    assert importlib.util.find_spec('vibrasim2.l0.run') is not None, 'runner missing'
    from vibrasim2.l0 import run
    return run


def test_manifest_detects_changed_code_and_environment(tmp_path):
    run = runner()
    manifest = run.manifest()
    run.validate_manifest(manifest)
    assert manifest['seeds'] == list(range(30))
    assert manifest['hard_seconds'] == 7140
    manifest['source_sha256']['vibrasim2/l0/core.py'] = '0' * 64
    with pytest.raises(ValueError):
        run.validate_manifest(manifest)
    manifest = run.manifest()
    manifest['numpy'] = 'wrong'
    with pytest.raises(ValueError):
        run.validate_manifest(manifest)


def test_exact_replay_accepts_original_and_detects_changed_trace(tmp_path, monkeypatch):
    run = runner()
    monkeypatch.setattr(ev, 'TRAIN_COUNT', 20)
    monkeypatch.setattr(ev, 'EVAL_COUNT', 4)
    folder = tmp_path / 'seed'
    ev.run_repetition(1003, folder)
    counts = run.verify_repetition(1003, folder, lambda: None)
    assert counts['files_verified'] == 22
    path = folder / 'full-training.jsonl'
    lines = path.read_text().splitlines()
    row = json.loads(lines[0])
    row['feedback'] = .12345
    lines[0] = json.dumps(row)
    path.write_text('\n'.join(lines) + '\n')
    with pytest.raises(ValueError, match='artifact mismatch'):
        run.verify_repetition(1003, folder, lambda: None)


def test_inventory_detects_added_removed_and_changed_files(tmp_path):
    run = runner()
    (tmp_path / 'a.txt').write_text('evidence')
    recorded = run.inventory(tmp_path)
    run.validate_inventory(tmp_path, recorded)
    (tmp_path / 'b.txt').write_text('unexpected')
    with pytest.raises(ValueError):
        run.validate_inventory(tmp_path, recorded)
    (tmp_path / 'b.txt').unlink()
    (tmp_path / 'a.txt').write_text('altered')
    with pytest.raises(ValueError):
        run.validate_inventory(tmp_path, recorded)


def test_run_directory_cannot_be_overwritten(tmp_path):
    with pytest.raises(FileExistsError):
        runner().execute(tmp_path)


def test_execute_records_resource_failure_before_any_seed(tmp_path, monkeypatch):
    run = runner()
    def expired(*args):
        raise TimeoutError('technical deadline fixture')
    monkeypatch.setattr(run, 'check_limits', expired)
    folder = tmp_path / 'failed'
    result = run.execute(folder)
    assert result['verdict'] == 'FAIL'
    assert result['completed_seeds'] == []
    assert 'TimeoutError' in result['reasons'][0]
    assert json.loads((folder / 'result.json').read_text())['verdict'] == 'FAIL'
    assert run.assess(folder)['verified_complete'] is False


def test_readback_rejects_missing_or_changed_result(tmp_path):
    assert runner().assess(tmp_path)['verdict'] == 'FAIL'

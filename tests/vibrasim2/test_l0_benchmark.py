"""Small fixtures for resource accounting; no research task or target."""
import importlib.util
import json

import pytest


def benchmark():
    assert importlib.util.find_spec('vibrasim2.l0.benchmark') is not None, 'benchmark missing'
    from vibrasim2.l0 import benchmark as module
    return module


def test_resource_probe_measures_real_process_and_records_limits(tmp_path):
    module = benchmark()
    assert module.peak_memory_bytes() > 0
    report = module.measure(tmp_path, fill=4, count=3)
    assert report['kind'] == 'technical-non-target-benchmark'
    assert report['research_run'] is False
    assert report['full_capacity'] is False
    assert report['memory_entries'] == 7
    assert report['state_bytes'] > 0
    assert len(report['action_seconds']) == 3
    assert report['limits_passed'] is True
    assert report['proposed_research_hard_seconds'] is None
    assert set(report['source_sha256']) == {'core.py', 'evaluation.py', 'benchmark.py'}
    json.dumps(report, allow_nan=False)


def test_resource_probe_rejects_invalid_workload_before_writing(tmp_path):
    for fill, count in [(0, 2), (4097, 2), (4, 0)]:
        with pytest.raises(ValueError):
            benchmark().measure(tmp_path, fill=fill, count=count)
    assert list(tmp_path.iterdir()) == []


def test_resource_guard_rejects_time_and_memory_limit():
    module = benchmark()
    with pytest.raises(TimeoutError):
        module.check_limits(0, 2**31)
    with pytest.raises(MemoryError):
        module.check_limits(float('inf'), 1)

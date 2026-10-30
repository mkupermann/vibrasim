"""Resource probe using random contexts and unrelated random feedback, never targets."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import tempfile
import time

import numpy as np

from .core import CONSTANTS, Learner, MAX_STATE_BYTES


MEMORY_LIMIT = 2 * 1024 ** 3


def peak_memory_bytes():
    if sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('faults', wintypes.DWORD)] + [
                (name, ctypes.c_size_t) for name in
                ('peak_working', 'working', 'peak_paged', 'paged',
                 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile')]

        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        psapi = ctypes.WinDLL('psapi', use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(counters.peak_working)
    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == 'darwin' else peak * 1024)


def check_limits(deadline, memory_limit=MEMORY_LIMIT):
    if time.perf_counter() > deadline:
        raise TimeoutError('fixed wall-clock budget exceeded')
    if peak_memory_bytes() > memory_limit:
        raise MemoryError('process peak memory exceeded budget')


def measure(directory, *, fill=4096, count=64):
    if (type(fill) is not int or not 1 <= fill <= CONSTANTS['capacity']
            or type(count) is not int or not 1 <= count <= 1024):
        raise ValueError('invalid benchmark workload')
    started = time.perf_counter()
    deadline = started + 120
    learner = Learner(58097)
    rng = np.random.Generator(np.random.PCG64(58098))
    for index in range(fill):
        if index % 32 == 0:
            check_limits(deadline)
        attempt = learner.attempt(float(rng.random()), index)
        learner.feedback(attempt.id, float(rng.uniform(-1, 1)), index)
    measurements = []
    for index in range(count):
        check_limits(deadline)
        context = float(rng.random())
        begin = time.perf_counter()
        attempt = learner.attempt(context, fill + index)
        learner.feedback(attempt.id, float(rng.uniform(-1, 1)), fill + index)
        measurements.append(time.perf_counter() - begin)
    path = Path(directory) / 'benchmark-state.json'
    if path.exists():
        raise FileExistsError(path)
    learner.save(path)
    begin = time.perf_counter()
    learner.evaluate(rng.random(count), 58099)
    evaluation_seconds = time.perf_counter() - begin
    check_limits(deadline)
    full = fill == CONSTANTS['capacity']
    # 30 seeds * 5 arms * (2400 training + 6 * 200 evaluation actions).
    # Charge every arm/action the slow full-memory K1 cost, plus 10 min I/O margin.
    action_budget = 540_000
    unit_seconds = max(float(np.percentile(measurements, 95)), evaluation_seconds / count)
    estimated = action_budget * unit_seconds + 600
    hard_limit = int(math.ceil(2 * estimated / 60) * 60) if full else None
    source = Path(__file__).parent
    return dict(kind='technical-non-target-benchmark', research_run=False,
                recorded_utc=datetime.now(timezone.utc).isoformat(),
                python=sys.version, numpy=np.__version__, platform=platform.platform(),
                full_capacity=full, memory_entries=learner.memory_size,
                fill_attempts=fill, measured_attempts=count, action_seconds=measurements,
                p95_action_seconds=float(np.percentile(measurements, 95)),
                evaluation_seconds=evaluation_seconds, evaluation_actions=count,
                elapsed_seconds=time.perf_counter() - started,
                peak_memory_bytes=peak_memory_bytes(), state_bytes=path.stat().st_size,
                limits_passed=peak_memory_bytes() <= MEMORY_LIMIT and path.stat().st_size <= MAX_STATE_BYTES,
                proposed_research_estimate_seconds=estimated if full else None,
                proposed_research_hard_seconds=hard_limit,
                estimate_basis=dict(actions=action_budget, charged_seconds_per_action=unit_seconds,
                                    io_margin_seconds=600, hard_multiplier=2),
                source_sha256={name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                               for name in ('core.py', 'evaluation.py', 'benchmark.py')})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='new JSON report; never overwritten')
    args = parser.parse_args(argv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents concurrent runs from replacing evidence.
    with args.output.open('x', encoding='utf-8') as output:
        try:
            with tempfile.TemporaryDirectory(prefix='l0-benchmark-') as temporary:
                report = measure(temporary)
        except Exception as exc:
            json.dump(dict(kind='technical-non-target-benchmark', status='FAIL',
                           error=f'{type(exc).__name__}: {exc}'), output, indent=2)
            raise
        json.dump(report, output, indent=2, allow_nan=False)
    print(json.dumps({key: report[key] for key in (
        'limits_passed', 'elapsed_seconds', 'peak_memory_bytes', 'state_bytes',
        'proposed_research_hard_seconds')}, indent=2))
    return 0 if report['limits_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

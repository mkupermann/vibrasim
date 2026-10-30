"""Frozen G176/G177 execution, exact replay and artifact consistency checks."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import tempfile
import time

import numpy as np

from . import evaluation as ev
from .benchmark import MEMORY_LIMIT, check_limits, peak_memory_bytes
from .core import CONSTANTS, MAX_STATE_BYTES

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ('vibrasim2/__init__.py', 'vibrasim2/l0/__init__.py',
           'vibrasim2/l0/core.py', 'vibrasim2/l0/evaluation.py',
           'vibrasim2/l0/benchmark.py', 'vibrasim2/l0/run.py',
           'docs/amendments/G176_l0_continuous_experience_learning.md',
           'docs/amendments/G177_l0_frozen_run.md',
           'docs/validation/l0-20260916-resource.json')


def digest(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def manifest():
    return dict(schema=1, programme='G176/G177-L0', seeds=list(range(30)),
                python=sys.version, numpy=np.__version__, platform=platform.platform(),
                constants=CONSTANTS.copy(), streams=ev.STREAMS.copy(), arms=ev.ARMS.copy(),
                train_per_phase=ev.TRAIN_COUNT, held_per_task=ev.EVAL_COUNT,
                block_size=ev.BLOCK_SIZE, hard_seconds=7140,
                memory_bytes=MEMORY_LIMIT, state_bytes=MAX_STATE_BYTES,
                source_sha256={name: digest(ROOT / name) for name in SOURCES})


def validate_manifest(record):
    if record != manifest():
        raise ValueError('frozen manifest differs from current code/environment/configuration')


def inventory(directory):
    directory = Path(directory)
    return {path.relative_to(directory).as_posix(): digest(path)
            for path in sorted(directory.rglob('*')) if path.is_file()}


def validate_inventory(directory, expected):
    if inventory(directory) != expected:
        raise ValueError('artifact inventory changed')


def verify_repetition(seed, directory, guard):
    directory = Path(directory)
    guard()
    with tempfile.TemporaryDirectory(prefix='l0-replay-') as temporary:
        replay = Path(temporary) / 'replay'
        ev.run_repetition(seed, replay, guard=guard)
        original_files, replay_files = inventory(directory), inventory(replay)
        if original_files.keys() != replay_files.keys():
            raise ValueError('artifact mismatch: seed file inventory')
        for name in original_files:
            guard()
            if name == 'dataset.npz':
                with np.load(directory / name, allow_pickle=False) as original, np.load(replay / name, allow_pickle=False) as copy:
                    if set(original.files) != set(copy.files) or any(
                            not np.array_equal(original[key], copy[key]) for key in original.files):
                        raise ValueError('artifact mismatch: dataset')
            elif original_files[name] != replay_files[name]:
                raise ValueError(f'artifact mismatch: {name}')
    guard()
    return dict(files_verified=len(original_files), exact_replay=True)


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)


def execute(directory):
    started = time.perf_counter()
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    record = manifest()
    manifest_path = directory / 'manifest.json'
    write_json(manifest_path, record)
    manifest_hash = digest(manifest_path)
    deadline = started + record['hard_seconds']
    rows, audits, hashes = [], {}, {}

    def guard():
        check_limits(deadline, record['memory_bytes'])

    try:
        validate_manifest(record)
        for seed in record['seeds']:
            guard()
            validate_manifest(record)
            folder = directory / f'seed-{seed:02d}'
            ev.run_repetition(seed, folder, guard=guard)
            audits[str(seed)] = verify_repetition(seed, folder, guard)
            # Consume the file that was just independently replayed and compared.
            rows.append(json.loads((folder / 'metrics.json').read_text(encoding='utf-8')))
            hashes[str(seed)] = inventory(folder)
            print(json.dumps(dict(seed=seed, verified=len(rows), elapsed_seconds=time.perf_counter()-started)), flush=True)
        guard()
        validate_manifest(record)
        if digest(manifest_path) != manifest_hash:
            raise ValueError('frozen manifest file changed')
        for seed in record['seeds']:
            guard()
            validate_inventory(directory / f'seed-{seed:02d}', hashes[str(seed)])
        result = ev.summarize(rows)
        guard()
    except KeyboardInterrupt:
        result = ev.summarize(rows, external_abort=True)
        result['interruption'] = 'KeyboardInterrupt'
    except Exception as exc:
        result = dict(verdict='FAIL', reasons=[f'{type(exc).__name__}: {exc}'])
    elapsed = time.perf_counter() - started
    peak = peak_memory_bytes()
    if elapsed > record['hard_seconds'] or peak > record['memory_bytes']:
        result = dict(verdict='FAIL', reasons=['fixed time or memory limit exceeded'])
    result.update(manifest_sha256=manifest_hash, completed_seeds=[r['seed'] for r in rows],
                  elapsed_seconds=elapsed, peak_memory_bytes=peak,
                  seed_audits=audits, artifact_sha256=hashes,
                  finished_utc=datetime.now(timezone.utc).isoformat())
    write_json(directory / 'result.json', result)
    print(json.dumps(dict(verdict=result['verdict'], elapsed_seconds=elapsed, peak_memory_bytes=peak)), flush=True)
    return result


def assess(directory):
    """Read-only source/inventory/metric check; no new scientific run or replay."""
    directory = Path(directory)
    try:
        record = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        saved = json.loads((directory / 'result.json').read_text(encoding='utf-8'))
        validate_manifest(record)
        if digest(directory / 'manifest.json') != saved['manifest_sha256']:
            raise ValueError('manifest hash mismatch')
        if saved['verdict'] in ('FAIL', 'INCONCLUSIVE'):
            return dict(verdict=saved['verdict'], verified_complete=False, reasons=saved.get('reasons', []))
        if saved['completed_seeds'] != record['seeds'] or saved['elapsed_seconds'] > record['hard_seconds'] or saved['peak_memory_bytes'] > record['memory_bytes']:
            raise ValueError('completion or resource evidence invalid')
        rows = []
        for seed in record['seeds']:
            folder = directory / f'seed-{seed:02d}'
            validate_inventory(folder, saved['artifact_sha256'][str(seed)])
            if saved['seed_audits'][str(seed)] != dict(files_verified=22, exact_replay=True):
                raise ValueError('missing replay evidence')
            rows.append(json.loads((folder / 'metrics.json').read_text(encoding='utf-8')))
        calculated = ev.summarize(rows)
        if any(saved.get(key) != value for key, value in calculated.items()):
            raise ValueError('saved verdict or metrics differ from raw artifacts')
        return dict(verdict=calculated['verdict'], verified_complete=True, seeds=30)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        return dict(verdict='FAIL', verified_complete=False, reasons=[str(exc)])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['execute', 'assess'])
    parser.add_argument('directory', type=Path)
    args = parser.parse_args(argv)
    result = execute(args.directory) if args.operation == 'execute' else assess(args.directory)
    if args.operation == 'assess':
        print(json.dumps(result, indent=2))
    return 1 if result['verdict'] == 'FAIL' else 0


if __name__ == '__main__':
    raise SystemExit(main())

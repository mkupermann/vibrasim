"""Read-only independent scoring audit; imports no L0 learner/evaluator code."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

import numpy as np


ARMS = ('full', 'frozen', 'shuffled', 'uniform', 'nearest')
LABELS = dict(initial_a='A', a='A', restart_a='A', b_before='B', a_after_b='A', b='B')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same(actual, expected):
    require(math.isfinite(actual) and math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12),
            f'numeric mismatch: {actual} versus {expected}')


def rating(x, action, phase):
    require(0 <= x <= 1 and 0 <= action <= 1, 'context or action outside bounds')
    wanted = (1 + 3*x)/5 if phase == 'A' else (4 - 3*x)/5
    return max(-1., 1. - 8. * abs(action - wanted))


def audit(directory):
    directory = Path(directory)
    result_path = directory / 'result.json'
    result = json.loads(result_path.read_text(encoding='utf-8'))
    require(result['verdict'] in ('PASS-LERNEN', 'NULL'), 'no completed scientific verdict')
    scores = {arm: {label: [] for label in LABELS if label != 'restart_a'} for arm in ARMS}
    training_events = evaluation_actions = 0
    for seed in range(30):
        folder = directory / f'seed-{seed:02d}'
        with np.load(folder / 'dataset.npz', allow_pickle=False) as data:
            train_values = set(data['train_a']) | set(data['train_b'])
            held_values = set(data['held_a']) | set(data['held_b'])
            require(not train_values & held_values, 'train/test leakage')
            for arm in ARMS:
                rows = [json.loads(line) for line in (folder / f'{arm}-training.jsonl').read_text().splitlines()]
                require(len(rows) == 2400, 'wrong training event count')
                require({r['id'] for r in rows} == set(range(1, 2401)), 'duplicate/missing attempt')
                for phase_index, phase in enumerate(('A', 'B')):
                    created = 0.
                    phase_rows = rows[phase_index*1200:(phase_index+1)*1200]
                    contexts, delays = data[f'train_{phase.lower()}'], data[f'delay_{phase.lower()}']
                    for offset in range(0, 1200, 20):
                        block = phase_rows[offset:offset+20]
                        by_id = {r['id']: r for r in block}
                        require({r['source_id'] for r in block} == set(by_id), 'feedback not a permutation')
                        require(block == sorted(block, key=lambda r: (r['delay'], r['id'])), 'wrong delivery order')
                        for row in block:
                            index = row['id'] - phase_index*1200 - 1
                            require(offset <= index < offset+20 and row['phase'] == phase, 'wrong block/phase')
                            same(row['context'], float(contexts[index]))
                            same(row['created'], created)
                            same(row['delay'], float(delays[index]))
                            same(row['own_reward'], rating(row['context'], row['action'], phase))
                            source = by_id[row['source_id']]
                            same(row['feedback'], rating(source['context'], source['action'], phase))
                            require((row['source_id'] != row['id']) == (arm == 'shuffled'), 'wrong feedback assignment')
                        created += max(r['delay'] for r in block) + 1
                training_events += len(rows)
                evidence = json.loads((folder / f'{arm}-evaluation.json').read_text())
                require(set(evidence) == set(LABELS), 'missing evaluation stage')
                require(evidence['a'] == evidence['restart_a'], 'restart is not exact')
                for label, phase in LABELS.items():
                    values = evidence[label]
                    require(len(values['actions']) == len(values['rewards']) == 200, 'wrong held-out count')
                    independent = [rating(float(x), a, phase) for x, a in
                                   zip(data[f'held_{phase.lower()}'], values['actions'])]
                    for actual, expected in zip(values['rewards'], independent):
                        same(actual, expected)
                    if label != 'restart_a':
                        scores[arm][label].append(statistics.mean(independent))
                    evaluation_actions += 200
    for arm in ARMS:
        for label, values in scores[arm].items():
            reported = result['descriptive'][arm][label]
            same(reported['mean'], statistics.mean(values))
            same(reported['sd'], statistics.stdev(values))
            require(len(reported['values']) == 30, 'missing individual seed scores')
            for actual, expected in zip(reported['values'], values):
                same(actual, expected)
    for arm in ARMS[1:]:
        differences = [a-b for a, b in zip(scores['full']['a'], scores[arm]['a'])]
        mean, sd = statistics.mean(differences), statistics.stdev(differences)
        reported = result['contrasts'][arm]
        same(reported['mean'], mean)
        same(reported['sd'], sd)
        half = 2.045229642 * sd / math.sqrt(30)
        same(reported['ci95'][0], mean-half)
        same(reported['ci95'][1], mean+half)
    return dict(status='PASS', seeds=30, arms=5, training_events=training_events,
                evaluation_actions=evaluation_actions, score_tolerance=1e-12,
                result_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest(),
                audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='Independent rewards, feedback assignment, splits, restart, per-seed means, SD and paired intervals; policy reproduced by frozen runner.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.directory), indent=2))

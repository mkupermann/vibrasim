"""G176 evaluator. Only this module knows targets; importing never runs a trial.

Before research use, freeze this file, core.py, NumPy version, G176 and a measured
runtime budget. Short tests of plumbing are not a registered research result.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from .core import Learner, bounded, vector


TRAIN_COUNT = 1200
EVAL_COUNT = 200
BLOCK_SIZE = 20
ARMS = dict(full='k1', frozen='frozen', shuffled='k1', uniform='uniform', nearest='nearest')
# Stable names -> SeedSequence spawn_key. Identical streams per arm are intentional.
STREAMS = {name: index for index, name in enumerate((
    'train_a', 'train_b', 'held_a', 'held_b', 'delay_a', 'delay_b',
    'actions', 'shuffle_a', 'shuffle_b', 'initial_a', 'eval_a', 'b_before',
    'a_after_b', 'eval_b'))}
METRICS = ('initial_a', 'a', 'b_before', 'a_after_b', 'b')


def sequence(seed, name):
    if type(seed) is not int or seed < 0:
        raise ValueError('master seed must be a nonnegative integer')
    return np.random.SeedSequence(seed, spawn_key=(STREAMS[name],))


def stream(seed, name):
    return np.random.Generator(np.random.PCG64(sequence(seed, name)))


def dataset(seed):
    data = {name: stream(seed, name).random(TRAIN_COUNT if name.startswith('train') else EVAL_COUNT)
            for name in ('train_a', 'train_b', 'held_a', 'held_b')}
    training = np.concatenate((data['train_a'], data['train_b']))
    held = np.concatenate((data['held_a'], data['held_b']))
    if np.intersect1d(training, held).size:
        raise ValueError('held-out/training overlap')
    for name in ('delay_a', 'delay_b'):
        data[name] = stream(seed, name).uniform(0, 10, TRAIN_COUNT)
    for array in data.values():
        array.flags.writeable = False
    return data


def rewards(contexts, actions, phase):
    contexts, actions = vector(contexts, 'contexts'), vector(actions, 'actions')
    if contexts.shape != actions.shape or phase not in ('A', 'B'):
        raise ValueError('invalid phase or action/context pairing')
    target = .2 + .6 * contexts if phase == 'A' else .8 - .6 * contexts
    return 1 - 2 * np.minimum(abs(actions - target) / .25, 1)


def derangement(rng, count):
    if type(count) is not int or count < 2:
        raise ValueError('derangement needs at least two items')
    indices = np.arange(count)
    # Rejection sampling is uniform over derangements, expected ~e attempts.
    for _ in range(1000):
        candidate = rng.permutation(count)
        if np.all(candidate != indices):
            return candidate
    raise RuntimeError('derangement sampling exceeded its safety bound')


def train_block(learner, contexts, delays, phase, start, shuffle_rng=None):
    contexts = vector(contexts, 'contexts')
    delays = np.asarray(delays, dtype=np.float64)
    start = bounded(start, 0., math.inf, 'block start')
    if (len(contexts) != BLOCK_SIZE or delays.shape != contexts.shape
            or not np.isfinite(delays).all() or (delays < 0).any() or (delays > 10).any()
            or learner.pending_count or phase not in ('A', 'B')):
        raise ValueError('invalid feedback block')
    attempts = [learner.attempt(float(x), start) for x in contexts]
    ratings = rewards(contexts, [a.action for a in attempts], phase)
    source = (np.arange(BLOCK_SIZE) if shuffle_rng is None
              else derangement(shuffle_rng, BLOCK_SIZE))
    rows = []
    for index in np.argsort(delays, kind='stable'):
        attempt = attempts[index]
        assigned = int(source[index])
        reward = float(ratings[assigned])
        delay = float(delays[index])
        learner.feedback(attempt.id, reward, start + delay)
        rows.append(dict(id=attempt.id, context=attempt.context, action=attempt.action,
                         phase=phase, created=start, delay=delay,
                         own_reward=float(ratings[index]), feedback=reward,
                         source_id=attempts[assigned].id))
    return rows, start + float(delays.max()) + 1.


def run_repetition(seed, directory, *, guard=None):
    """One full fixed-budget repetition, preserving raw evidence and checkpoints.

    No CLI launches this implicitly. Research orchestration must supply a resource/
    deadline guard and a frozen manifest. A missing guard is for technical fixtures.
    Existing output is never overwritten. Errors propagate; partial files remain.
    """
    if TRAIN_COUNT % BLOCK_SIZE:
        raise ValueError('training budget must contain complete blocks')
    data = dataset(seed)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    np.savez(directory / 'dataset.npz', **data)
    result = dict(seed=seed, arms={})
    for arm, mode in ARMS.items():
        learner = Learner(sequence(seed, 'actions'), mode)
        evidence = {}

        def check():
            if guard is not None:
                guard()

        def evaluate(label, phase, rng_name):
            check()
            x = data['held_a' if phase == 'A' else 'held_b']
            before = learner.snapshot()
            actions = learner.evaluate(x, sequence(seed, rng_name))
            if learner.snapshot() != before:
                raise ValueError('evaluation mutated training state')
            values = rewards(x, actions, phase)
            evidence[label] = dict(actions=actions.tolist(), rewards=values.tolist())
            check()
            return float(values.mean())

        def train(phase, handle):
            name = phase.lower()
            shuffle = stream(seed, f'shuffle_{name}') if arm == 'shuffled' else None
            start = 0.
            for offset in range(0, TRAIN_COUNT, BLOCK_SIZE):
                check()
                part = slice(offset, offset + BLOCK_SIZE)
                rows, start = train_block(learner, data[f'train_{name}'][part],
                                          data[f'delay_{name}'][part], phase, start, shuffle)
                for row in rows:
                    handle.write(json.dumps(row, allow_nan=False) + '\n')
                handle.flush()
            check()

        metrics = dict(initial_a=evaluate('initial_a', 'A', 'initial_a'))
        with (directory / f'{arm}-training.jsonl').open('x', encoding='utf-8') as handle:
            train('A', handle)
            metrics['a'] = evaluate('a', 'A', 'eval_a')
            metrics['b_before'] = evaluate('b_before', 'B', 'b_before')
            checkpoint = directory / f'{arm}-after-a.json'
            learner.save(checkpoint)
            original = learner.snapshot()
            learner = Learner.load(checkpoint)
            if learner.snapshot() != original:
                raise ValueError('restart changed stored state')
            evaluate('restart_a', 'A', 'eval_a')
            metrics['restart_equal'] = evidence['restart_a'] == evidence['a']
            if not metrics['restart_equal']:
                raise ValueError('restart changed behavior')
            train('B', handle)
        metrics['a_after_b'] = evaluate('a_after_b', 'A', 'a_after_b')
        metrics['b'] = evaluate('b', 'B', 'eval_b')
        learner.save(directory / f'{arm}-after-b.json')
        (directory / f'{arm}-evaluation.json').write_text(
            json.dumps(evidence, allow_nan=False, indent=2), encoding='utf-8')
        result['arms'][arm] = metrics
    (directory / 'metrics.json').write_text(json.dumps(result, allow_nan=False, indent=2), encoding='utf-8')
    return result


def _statistics(values, interval=False):
    values = np.asarray(values, dtype=np.float64)
    mean, sd = float(values.mean()), float(values.std(ddof=1))
    result = dict(mean=mean, sd=sd, values=values.tolist())
    if interval:
        half = 2.045229642 * sd / math.sqrt(30)
        result['ci95'] = [mean - half, mean + half]
    return result


def summarize(rows, *, external_abort=False, violations=()):
    """Numerical verdict; artifact provenance must be verified separately.

    Complete synthetic fixtures can exercise this function. Its output alone is
    not evidence that a registered experiment actually took place.
    """
    if violations:
        return dict(verdict='FAIL', reasons=list(violations))
    try:
        seeds = []
        for row in rows:
            seed = row['seed']
            if type(seed) is not int or not 0 <= seed < 30 or seed in seeds:
                raise ValueError('invalid or duplicate master seed')
            seeds.append(seed)
            if set(row['arms']) != set(ARMS):
                raise ValueError('missing or unknown arm')
            for metrics in row['arms'].values():
                if set(metrics) != set(METRICS) | {'restart_equal'}:
                    raise ValueError('missing or unknown metric')
                if metrics['restart_equal'] is not True:
                    raise ValueError('restart behavior not reproduced')
                for name in METRICS:
                    bounded(metrics[name], -1., 1., name)
        if len(seeds) != 30:
            return dict(verdict='INCONCLUSIVE' if external_abort else 'FAIL',
                        reasons=['incomplete 30-seed dataset'], completed_seeds=seeds)
    except (ValueError, KeyError, TypeError) as exc:
        return dict(verdict='FAIL', reasons=[str(exc)])
    rows = sorted(rows, key=lambda row: row['seed'])
    scores = {arm: {name: np.asarray([row['arms'][arm][name] for row in rows])
                    for name in METRICS} for arm in ARMS}
    descriptions = {arm: {name: _statistics(values) for name, values in metrics.items()}
                    for arm, metrics in scores.items()}
    full = scores['full']['a']
    contrasts = {arm: _statistics(full - scores[arm]['a'], interval=True)
                 for arm in ARMS if arm != 'full'}
    controls_below_bar = all(scores[arm]['a'].mean() < .50 for arm in ('frozen', 'shuffled'))
    passed = (full.mean() >= .50 and controls_below_bar and all(
        contrasts[arm]['mean'] >= .10 and contrasts[arm]['ci95'][0] > 0
        for arm in ('frozen', 'shuffled')))
    alternative = contrasts['nearest']
    gain = _statistics(scores['full']['b'] - scores['full']['b_before'], interval=True)
    loss = _statistics(scores['full']['a'] - scores['full']['a_after_b'], interval=True)
    return dict(verdict='PASS-LERNEN' if passed else 'NULL', descriptive=descriptions,
                contrasts=contrasts, controls_below_bar=controls_below_bar,
                advantage=bool(alternative['mean'] >= .05 and alternative['ci95'][0] > 0),
                adaptation=bool(scores['full']['b'].mean() >= .50 and gain['mean'] >= .10),
                retention=bool(loss['mean'] <= .10), adaptation_gain=gain, retention_loss=loss)

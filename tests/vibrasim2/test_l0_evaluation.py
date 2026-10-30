"""Hand-built fixtures verify the evaluator, not scientific learning efficacy."""
import importlib.util
import json

import numpy as np
import pytest

from vibrasim2.l0.core import Learner


def evaluator():
    assert importlib.util.find_spec('vibrasim2.l0.evaluation') is not None, 'evaluator missing'
    from vibrasim2.l0 import evaluation
    return evaluation


def synthetic_rows():
    arms = ('full', 'frozen', 'shuffled', 'uniform', 'nearest')
    rows = []
    for seed in range(30):
        scores = (.7, -.2, -.1, -.3, .6)
        rows.append(dict(seed=seed, arms={
            arm: dict(initial_a=-.3, a=score, b_before=-.4, a_after_b=score-.2,
                      b=.65, restart_equal=True)
            for arm, score in zip(arms, scores)}))
    return rows


def test_evaluator_scores_known_actions_and_rejects_bad_phase():
    ev = evaluator()
    assert ev.rewards([0, .5, 1], [.2, .5, .8], 'A').tolist() == [1, 1, 1]
    assert ev.rewards([0], [.45], 'A')[0] == -1
    assert ev.rewards([0, 1], [.8, .2], 'B') == pytest.approx([1, 1])
    with pytest.raises(ValueError):
        ev.rewards([0], [.2], 'typo')


def test_splits_are_repeatable_disjoint_and_not_shared_random_state():
    ev = evaluator()
    first, second = ev.dataset(11), ev.dataset(11)
    for name in first:
        assert np.array_equal(first[name], second[name])
    training = np.concatenate([first['train_a'], first['train_b']])
    held = np.concatenate([first['held_a'], first['held_b']])
    assert np.intersect1d(training, held).size == 0
    assert len(first['train_a']) == 1200
    assert len(first['held_a']) == 200
    assert not np.array_equal(first['train_a'], ev.dataset(12)['train_a'])
    ev.stream(11, 'actions').random(100)
    assert np.array_equal(ev.dataset(11)['train_a'], first['train_a'])


def test_derangement_has_no_fixed_points_and_preserves_all_ratings():
    ev = evaluator()
    rng = ev.stream(5, 'shuffle_a')
    for _ in range(10):
        permutation = ev.derangement(rng, 20)
        assert sorted(permutation) == list(range(20))
        assert np.all(permutation != np.arange(20))
    with pytest.raises(ValueError):
        ev.derangement(rng, 1)


def test_block_defers_learning_sorts_delivery_and_shuffles_only_feedback():
    ev = evaluator()
    contexts = np.linspace(0, 1, 20)
    delays = np.arange(20)[::-1] / 2
    full, shuffled = Learner(90), Learner(90)
    untouched = Learner(90)
    expected_actions = [untouched.attempt(x, 0).action for x in contexts]
    full_rows, end = ev.train_block(full, contexts, delays, 'A', 0)
    shuffled_rows, other_end = ev.train_block(
        shuffled, contexts, delays, 'A', 0, ev.stream(4, 'shuffle_a'))
    assert end == other_end == 10.5
    assert [row['id'] for row in full_rows] == list(range(20, 0, -1))
    assert [row['action'] for row in sorted(full_rows, key=lambda r: r['id'])] == expected_actions
    original = {r['id']: r for r in full_rows}
    for row in shuffled_rows:
        assert row['action'] == original[row['id']]['action']
        assert row['delay'] == original[row['id']]['delay']
        assert row['source_id'] != row['id']
        assert row['feedback'] == original[row['source_id']]['feedback']
    assert full.memory_size == shuffled.memory_size == 20
    assert full.pending_count == shuffled.pending_count == 0


def test_block_rejects_invalid_delay_before_mutation():
    ev = evaluator()
    learner = Learner(0)
    before = learner.snapshot()
    with pytest.raises(ValueError):
        ev.train_block(learner, [.2] * 20, [31] * 20, 'A', 0)
    assert learner.snapshot() == before


def test_paired_verdict_and_retention_are_separate():
    result = evaluator().summarize(synthetic_rows())
    assert result['verdict'] == 'PASS-LERNEN'
    assert result['advantage'] is True
    assert result['adaptation'] is True
    assert result['retention'] is False
    assert result['contrasts']['frozen']['mean'] == pytest.approx(.9)
    assert result['contrasts']['frozen']['ci95'][0] == pytest.approx(.9)


def test_successful_shuffled_control_prevents_causal_learning_claim():
    rows = synthetic_rows()
    for row in rows:
        row['arms']['shuffled']['a'] = .55
    result = evaluator().summarize(rows)
    assert result['verdict'] == 'NULL'
    assert result['controls_below_bar'] is False


def test_no_baseline_advantage_does_not_erase_learning():
    rows = synthetic_rows()
    for row in rows:
        row['arms']['nearest']['a'] = .8
    result = evaluator().summarize(rows)
    assert result['verdict'] == 'PASS-LERNEN'
    assert result['advantage'] is False


@pytest.mark.parametrize('damage', ['nan', 'duplicate', 'missing', 'restart', 'range'])
def test_bad_evidence_is_fail_not_null(damage):
    rows = synthetic_rows()
    if damage == 'nan':
        rows[0]['arms']['full']['a'] = float('nan')
    elif damage == 'duplicate':
        rows[1]['seed'] = 0
    elif damage == 'missing':
        del rows[0]['arms']['frozen']
    elif damage == 'range':
        rows[0]['arms']['full']['a'] = 2
    else:
        rows[0]['arms']['full']['restart_equal'] = False
    assert evaluator().summarize(rows)['verdict'] == 'FAIL'


def test_external_abort_is_inconclusive_but_unexplained_missing_data_fails():
    rows = synthetic_rows()[:3]
    assert evaluator().summarize(rows, external_abort=True)['verdict'] == 'INCONCLUSIVE'
    assert evaluator().summarize(rows)['verdict'] == 'FAIL'
    assert evaluator().summarize(rows, external_abort=True,
                                 violations=['resource limit'])['verdict'] == 'FAIL'


def test_short_orchestration_preserves_evidence_and_restart(tmp_path, monkeypatch):
    ev = evaluator()
    monkeypatch.setattr(ev, 'TRAIN_COUNT', 20)
    monkeypatch.setattr(ev, 'EVAL_COUNT', 4)
    result = ev.run_repetition(1001, tmp_path / 'seed-1001')
    assert set(result['arms']) == {'full', 'frozen', 'shuffled', 'uniform', 'nearest'}
    for arm in result['arms']:
        assert result['arms'][arm]['restart_equal'] is True
        evidence = json.loads((tmp_path / 'seed-1001' / f'{arm}-evaluation.json').read_text())
        assert set(evidence) == {'initial_a', 'a', 'b_before', 'a_after_b', 'b', 'restart_a'}
        assert evidence['a'] == evidence['restart_a']
        trace = [json.loads(line) for line in
                 (tmp_path / 'seed-1001' / f'{arm}-training.jsonl').read_text().splitlines()]
        assert len(trace) == 40
        assert len({r['id'] for r in trace}) == 40
    with pytest.raises(FileExistsError):
        ev.run_repetition(1001, tmp_path / 'seed-1001')


def test_variable_paired_interval_uses_seed_differences():
    rows = synthetic_rows()
    # Differences are fifteen 0.1 and fifteen 0.3; mean .2, sample sd sqrt(.3/29).
    for index, row in enumerate(rows):
        row['arms']['full']['a'] = .6 if index < 15 else .8
        row['arms']['frozen']['a'] = .5
    contrast = evaluator().summarize(rows)['contrasts']['frozen']
    half = 2.045229642 * (.3 / 29 / 30) ** .5
    assert contrast['mean'] == pytest.approx(.2)
    assert contrast['ci95'] == pytest.approx([.2 - half, .2 + half])


def test_runtime_guard_stops_orchestration_without_completed_result(tmp_path, monkeypatch):
    ev = evaluator()
    monkeypatch.setattr(ev, 'TRAIN_COUNT', 20)
    monkeypatch.setattr(ev, 'EVAL_COUNT', 4)
    def stopped():
        raise TimeoutError('test deadline')
    with pytest.raises(TimeoutError):
        ev.run_repetition(1002, tmp_path / 'stopped', guard=stopped)
    assert not (tmp_path / 'stopped' / 'metrics.json').exists()

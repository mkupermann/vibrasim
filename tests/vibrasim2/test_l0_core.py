"""Technical contract tests only; no target task is trained here."""
import importlib.util
import json
import math

import numpy as np
import pytest


def core():
    assert importlib.util.find_spec('vibrasim2.l0') is not None, 'L0 kernel missing'
    from vibrasim2.l0 import core as module
    return module


@pytest.mark.parametrize('reward,delay,want', [(1, 0, .25), (-1, 0, -.25),
                                              (1, 10, .09196986029286058)])
def test_feedback_matches_hand_calculation(reward, delay, want):
    learner = core().Learner(17)
    attempt = learner.attempt(.4, 0)
    learner.feedback(attempt.id, reward, delay)
    assert learner.values(.4, [attempt.action])[0] == pytest.approx(want)


def test_absence_expires_without_learning_but_neutral_is_recorded():
    learner = core().Learner(17)
    attempt = learner.attempt(.4, 0)
    assert learner.expire(30) == []
    assert learner.expire(30.01) == [attempt.id]
    assert learner.memory_size == 0
    neutral = learner.attempt(.4, 31)
    learner.feedback(neutral.id, 0, 31)
    assert learner.memory_size == 1
    assert learner.values(.4, [neutral.action])[0] == 0


def test_feedback_rejects_duplicate_unknown_future_and_expired(caplog):
    learner = core().Learner(1)
    attempt = learner.attempt(.5, 10)
    for identity, now in [(attempt.id, 9), (999, 10)]:
        with pytest.raises(ValueError):
            learner.feedback(identity, 1, now)
    learner.feedback(attempt.id, 1, 10)
    with pytest.raises(ValueError):
        learner.feedback(attempt.id, 1, 10)
    expired = learner.attempt(.5, 11)
    with pytest.raises(ValueError):
        learner.feedback(expired.id, 1, 42)
    assert learner.memory_size == 1
    assert 'rejected' in caplog.text


@pytest.mark.parametrize('bad', [-.01, 1.01, float('nan'), float('inf')])
def test_invalid_context_does_not_consume_rng_or_id(bad):
    learner = core().Learner(8)
    before = learner.snapshot()
    with pytest.raises(ValueError):
        learner.attempt(bad, 0)
    assert learner.snapshot() == before


def test_pending_capacity_blocks_without_silent_overwrite():
    learner = core().Learner(2)
    attempts = [learner.attempt(.2, 0) for _ in range(64)]
    before = learner.snapshot()
    with pytest.raises(OverflowError):
        learner.attempt(.2, 0)
    assert learner.snapshot() == before
    learner.feedback(attempts[0].id, 1, 0)
    assert learner.attempt(.2, 0).id == 65


def test_fifo_removes_oldest_experience_and_keeps_bounded_memory():
    learner = core().Learner(3, mode='nearest')
    for index in range(4097):
        attempt = learner.attempt(.3, index)
        learner.feedback(attempt.id, 1 if index == 0 else 0, index)
    saved = learner.snapshot()['memory']
    assert len(saved) == 4096
    assert all(row[2] == 0 for row in saved)


def test_frozen_control_consumes_feedback_without_memory():
    learner = core().Learner(4, mode='frozen')
    attempt = learner.attempt(.2, 0)
    learner.feedback(attempt.id, 1, 0)
    assert learner.memory_size == 0
    assert learner.pending_count == 0


def test_restart_preserves_behavior_and_discards_pending(tmp_path, caplog):
    learner = core().Learner(5)
    attempt = learner.attempt(.5, 100)
    learner.feedback(attempt.id, 1, 101)
    pending = learner.attempt(.6, 102)
    path = tmp_path / 'state.json'
    learner.save(path)
    restored = core().Learner.load(path)
    assert restored.pending_count == 0
    assert str(pending.id) in caplog.text
    # A new process clock may start at zero; training RNG and IDs must continue.
    assert restored.attempt(.6, 0).action == learner.attempt(.6, 102).action
    assert restored.snapshot()['next_id'] == learner.snapshot()['next_id']
    learner.expire(133)
    restored.expire(31)
    assert np.array_equal(learner.evaluate([.1, .5, .9], 91),
                          restored.evaluate([.1, .5, .9], 91))


def test_evaluation_does_not_consume_training_rng_or_store_feedback():
    learner = core().Learner(6)
    attempt = learner.attempt(.5, 0)
    learner.feedback(attempt.id, 1, 0)
    before = learner.snapshot()
    first = learner.evaluate(np.linspace(0, 1, 12), 77)
    assert np.array_equal(first, learner.evaluate(np.linspace(0, 1, 12), 77))
    assert learner.snapshot() == before
    assert len(set(first)) > 3
    assert core().frequency(0) == 200
    assert core().frequency(1) == 1600


def test_corrupt_or_changed_configuration_cannot_load(tmp_path):
    path = tmp_path / 'state.json'
    learner = core().Learner(7)
    learner.save(path)
    data = json.loads(path.read_text())
    data['constants']['eta'] = .9
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        core().Learner.load(path)


def test_invalid_reward_and_time_leave_experience_unchanged():
    learner = core().Learner(7)
    attempt = learner.attempt(.5, 10)
    before = learner.snapshot()
    for reward, now in [(2, 10), (math.nan, 10), (1, math.inf), (1, -1)]:
        with pytest.raises(ValueError):
            learner.feedback(attempt.id, reward, now)
        assert learner.snapshot() == before


def test_conflicting_experiences_cancel_instead_of_overwriting():
    learner = core().Learner(11, mode='nearest')
    positive = learner.attempt(.5, 0)
    learner.feedback(positive.id, 1, 0)
    negative = learner.attempt(.5, 1)
    assert negative.action == positive.action
    learner.feedback(negative.id, -1, 1)
    assert learner.memory_size == 2
    assert learner.values(.5, [positive.action])[0] == 0


def test_k1_uses_reward_to_select_best_new_proposal():
    learner = core().Learner(12)
    random = np.random.Generator(np.random.PCG64(12))
    initial = random.random(64)[0]
    random.random()
    attempt = learner.attempt(.5, 0)
    assert attempt.action == initial
    learner.feedback(attempt.id, 1, 0)
    proposals = random.random(64)
    explore = random.random() < .2
    # With one positive experience at the same x, Q increases towards its action.
    expected = proposals[0] if explore else min(proposals, key=lambda a: abs(a - initial))
    assert learner.attempt(.5, 1).action == expected


def test_evaluation_rejects_pending_and_does_not_hide_clock_rollback():
    learner = core().Learner(13)
    attempt = learner.attempt(.5, 10)
    with pytest.raises(ValueError):
        learner.evaluate([.5], 1)
    learner.feedback(attempt.id, 1, 10)
    with pytest.raises(ValueError):
        learner.attempt(.5, 9)


@pytest.mark.parametrize('damage', ['nan', 'large_q', 'dimensions', 'next_id', 'rng', 'mode'])
def test_corrupt_memory_and_rng_fail_closed(damage):
    learner = core().Learner(15)
    attempt = learner.attempt(.5, 0)
    learner.feedback(attempt.id, 1, 0)
    data = learner.snapshot()
    if damage == 'nan':
        data['memory'][0][0] = math.nan
    elif damage == 'large_q':
        data['memory'][0][2] = 99
    elif damage == 'dimensions':
        data['memory'][0].append(0)
    elif damage == 'next_id':
        data['next_id'] = 1
    elif damage == 'rng':
        data['rng']['bit_generator'] = 'MT19937'
    else:
        data['mode'] = 'frozen'
    with pytest.raises(ValueError):
        core().Learner.from_snapshot(data)

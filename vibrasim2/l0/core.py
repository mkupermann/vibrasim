"""Bounded own-experience kernel. No targets, task labels, audio or training data."""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass
import json
import logging
import math
import os
from pathlib import Path
import tempfile

import numpy as np


CONSTANTS = dict(h_x=.15, h_a=.10, eta=.5, tau=10., alpha=1., epsilon=.20,
                 proposals=64, capacity=4096, pending_capacity=64, max_delay=30.)
MODES = ('k1', 'frozen', 'uniform', 'nearest')
MAX_STATE_BYTES = 100 * 1024 * 1024
LOG = logging.getLogger(__name__)


def bounded(value, low, high, name):
    if isinstance(value, (bool, str, bytes)) or not np.isscalar(value):
        raise ValueError(f'{name} must be a finite number')
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f'{name} must be a finite number') from exc
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{name} outside [{low}, {high}]')
    return value


def frequency(action):
    return 200. * 8. ** bounded(action, 0., 1., 'action')


def vector(values, name):
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 1 or not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError(f'{name} must be a finite vector in [0, 1]')
    return values


@dataclass(frozen=True)
class Attempt:
    id: int
    context: float
    action: float
    created: float


class Learner:
    """Single-threaded kernel; callers supply a monotonic clock in seconds.

    `frozen` consumes exactly the K1 proposal stream but stores no experiences.
    `nearest` is G176's simple positive-experience reference, not another K1.
    """

    def __init__(self, seed, mode='k1'):
        if mode not in MODES:
            raise ValueError(f'unknown mode: {mode}')
        self.mode = mode
        self._rng = np.random.Generator(np.random.PCG64(seed))
        self._memory = deque(maxlen=CONSTANTS['capacity'])
        self._pending = {}
        self._next_id = 1
        self._clock = 0.

    @property
    def memory_size(self):
        return len(self._memory)

    @property
    def pending_count(self):
        return len(self._pending)

    def _time(self, now):
        now = bounded(now, 0., math.inf, 'time')
        if now < self._clock:
            raise ValueError('clock moved backwards')
        return now

    def values(self, context, actions):
        context = bounded(context, 0., 1., 'context')
        actions = vector(actions, 'actions')
        if not self._memory:
            return np.zeros(len(actions), dtype=np.float64)
        memory = np.asarray(self._memory, dtype=np.float64)
        with np.errstate(under='ignore', over='raise', invalid='raise'):
            weights = np.exp(-.5 * ((context - memory[:, 0]) / CONSTANTS['h_x']) ** 2
                             - .5 * ((actions[:, None] - memory[:, 1]) / CONSTANTS['h_a']) ** 2)
            result = (weights * memory[:, 2]).sum(axis=1) / (CONSTANTS['alpha'] + weights.sum(axis=1))
        if not np.isfinite(result).all():
            raise ValueError('nonfinite value estimate')
        return result

    def _choose(self, context, rng):
        if self.mode == 'uniform':
            return float(rng.random())
        if self.mode == 'nearest':
            positive = [row for row in self._memory if row[2] > 0]
            if positive:
                return min(positive, key=lambda row: abs(context - row[0]))[1]
            return float(rng.random())
        proposals = rng.random(CONSTANTS['proposals'])
        explore = rng.random() < CONSTANTS['epsilon']
        if explore:
            return float(proposals[0])
        return float(proposals[np.argmax(self.values(context, proposals))])

    def attempt(self, context, now):
        context = bounded(context, 0., 1., 'context')
        now = self._time(now)
        self.expire(now)
        if len(self._pending) >= CONSTANTS['pending_capacity']:
            raise OverflowError('64 attempts are still awaiting feedback')
        attempt = Attempt(self._next_id, context, self._choose(context, self._rng), now)
        self._pending[attempt.id] = attempt
        self._next_id += 1
        return attempt

    def expire(self, now):
        now = self._time(now)
        expired = [identity for identity, attempt in self._pending.items()
                   if now - attempt.created > CONSTANTS['max_delay']]
        for identity in expired:
            del self._pending[identity]
            LOG.warning('expired attempt %s without feedback', identity)
        self._clock = now
        return expired

    def feedback(self, identity, reward, now):
        try:
            reward = bounded(reward, -1., 1., 'reward')
            now = self._time(now)
            if type(identity) is not int or identity not in self._pending:
                raise ValueError('unknown, duplicate or expired attempt ID')
            attempt = self._pending[identity]
            delay = now - attempt.created
            if not 0 <= delay <= CONSTANTS['max_delay']:
                if delay > CONSTANTS['max_delay']:
                    del self._pending[identity]
                    self._clock = now
                raise ValueError('feedback outside the 30-second window')
        except ValueError:
            LOG.warning('rejected feedback for attempt %s', identity)
            raise
        if self.mode in ('k1', 'nearest'):
            quality = CONSTANTS['eta'] * math.exp(-delay / CONSTANTS['tau']) * reward
            self._memory.append((attempt.context, attempt.action, quality))
        del self._pending[identity]
        self._clock = now

    def evaluate(self, contexts, seed):
        contexts = vector(contexts, 'contexts')
        if self._pending:
            raise ValueError('finish pending feedback before evaluation')
        # A detached memory and RNG make evaluation observational, including IDs.
        copy = Learner.from_snapshot(self.snapshot())
        rng = np.random.Generator(np.random.PCG64(seed))
        return np.asarray([copy._choose(float(x), rng) for x in contexts])

    def snapshot(self):
        return dict(schema=1, constants=CONSTANTS.copy(), mode=self.mode,
                    memory=[list(row) for row in self._memory], next_id=self._next_id,
                    rng=deepcopy(self._rng.bit_generator.state),
                    pending_ids=list(self._pending))

    @classmethod
    def from_snapshot(cls, data):
        try:
            if set(data) != {'schema', 'constants', 'mode', 'memory', 'next_id', 'rng', 'pending_ids'}:
                raise ValueError('unexpected state fields')
            if data['schema'] != 1 or data['constants'] != CONSTANTS:
                raise ValueError('unsupported state schema or constants')
            next_id = data['next_id']
            if type(next_id) is not int or next_id < 1:
                raise ValueError('invalid next attempt ID')
            memory = np.asarray(data['memory'], dtype=np.float64)
            if len(memory) == 0:
                memory = np.empty((0, 3))
            if memory.ndim != 2 or memory.shape[1] != 3 or len(memory) > CONSTANTS['capacity']:
                raise ValueError('invalid memory dimensions')
            if (not np.isfinite(memory).all() or (memory[:, :2] < 0).any()
                    or (memory[:, :2] > 1).any() or (abs(memory[:, 2]) > CONSTANTS['eta']).any()
                    or len(memory) >= next_id):
                raise ValueError('invalid experience values or IDs')
            pending = data['pending_ids']
            if (not isinstance(pending, list) or len(pending) > CONSTANTS['pending_capacity']
                    or any(type(i) is not int or not 0 < i < next_id for i in pending)
                    or len(set(pending)) != len(pending)):
                raise ValueError('invalid pending IDs')
            instance = cls(0, data['mode'])
            if instance.mode in ('frozen', 'uniform') and len(memory):
                raise ValueError('non-learning control contains memory')
            instance._memory.extend(tuple(float(v) for v in row) for row in memory)
            instance._next_id = next_id
            instance._rng.bit_generator.state = deepcopy(data['rng'])
            if instance._rng.bit_generator.state != data['rng']:
                raise ValueError('RNG state was not restored exactly')
            if pending:
                LOG.warning('restart discarded pending attempts %s', pending)
            return instance
        except (KeyError, TypeError, OverflowError) as exc:
            raise ValueError('invalid persisted learner state') from exc

    def save(self, path):
        path = Path(path)
        encoded = json.dumps(self.snapshot(), allow_nan=False, sort_keys=True).encode('utf-8')
        if len(encoded) > MAX_STATE_BYTES:
            raise ValueError('state exceeds 100 MiB')
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()

    @classmethod
    def load(cls, path):
        path = Path(path)
        if path.stat().st_size > MAX_STATE_BYTES:
            raise ValueError('state exceeds 100 MiB')
        return cls.from_snapshot(json.loads(path.read_text(encoding='utf-8')))

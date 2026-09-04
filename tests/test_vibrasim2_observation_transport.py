from queue import Empty, Full

from vibrasim2.observation_transport import LatestOnlyPublisher


class ScriptedQueue:
    def __init__(self, puts, current=None):
        self.puts = iter(puts)
        self.current = current
        self.seen = []

    def put_nowait(self, item):
        self.seen.append(item)
        outcome = next(self.puts)
        if outcome == "full":
            raise Full

    def get_nowait(self):
        value, self.current = self.current, None
        if value is None:
            raise Empty
        return value


def test_full_queue_evicts_one_old_frame_and_retries_once():
    queue = ScriptedQueue(["full", "ok"], current="old")
    outcome = LatestOnlyPublisher(queue).publish("new")
    assert outcome.published
    assert outcome.evicted_previous
    assert len(queue.seen) == 2


def test_second_full_drops_only_new_frame():
    queue = ScriptedQueue(["full", "full"], current="old")
    outcome = LatestOnlyPublisher(queue).publish("new")
    assert outcome.dropped_new
    assert not outcome.published


def test_empty_eviction_and_broken_queue_are_non_raising_drops():
    empty = ScriptedQueue(["full"], current=None)
    assert LatestOnlyPublisher(empty).publish("new").dropped_new

    class BrokenQueue:
        def put_nowait(self, item):
            raise OSError("closed")

    outcome = LatestOnlyPublisher(BrokenQueue()).publish("new")
    assert outcome.dropped_new
    assert not outcome.published

"""Non-blocking latest-only transport for observer frames."""
from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Full
from typing import Any


@dataclass(frozen=True)
class PublishOutcome:
    published: bool = False
    evicted_previous: bool = False
    dropped_new: bool = False


class LatestOnlyPublisher:
    """Publish at most the newest item without ever waiting on the consumer."""

    def __init__(self, queue: Any) -> None:
        self.queue = queue

    def publish(self, item: Any) -> PublishOutcome:
        try:
            self.queue.put_nowait(item)
            return PublishOutcome(published=True)
        except Full:
            pass
        except Exception:
            return PublishOutcome(dropped_new=True)

        try:
            self.queue.get_nowait()
        except (Empty, Exception):
            return PublishOutcome(dropped_new=True)

        try:
            self.queue.put_nowait(item)
            return PublishOutcome(published=True, evicted_previous=True)
        except Exception:
            return PublishOutcome(evicted_previous=True, dropped_new=True)


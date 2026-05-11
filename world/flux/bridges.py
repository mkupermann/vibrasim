"""Bridges — SoA container for node-to-node directed weighted edges.

A bridge connects a source node to a destination node and carries a
scalar weight that grows with through-flux and decays without it
(spec §5.5). Bridges are directed: bridge(a→b) is distinct from
bridge(b→a). Nodes survive while they have at least one alive bridge;
when their last bridge breaks they dissociate (handled in plasticity).
"""
from __future__ import annotations
import numpy as np


class Bridges:
    """Pre-allocated SoA container for bridges between nodes.

    Slot reuse identical to `Quanta` / `Nodes`: lowest-index free slot
    wins on `add`; `_next_search` cursor advances past the just-filled
    slot.

    Each bridge carries (src_slot, dst_slot, weight, last_flux_tick).
    `last_flux_tick` is the most recent tick at which flux through the
    bridge was nonzero — used by the F1b plasticity rule.
    """

    def __init__(self, max_bridges: int):
        self.max_bridges = int(max_bridges)
        N = self.max_bridges
        self.src = np.zeros(N, dtype=np.int64)
        self.dst = np.zeros(N, dtype=np.int64)
        self.weight = np.zeros(N, dtype=np.float64)
        self.last_flux_tick = np.zeros(N, dtype=np.int64)
        self.alive = np.zeros(N, dtype=np.bool_)
        self._next_search = 0

    def n_alive(self) -> int:
        return int(self.alive.sum())

    def add(self, src: int, dst: int, weight: float,
            born_tick: int) -> int:
        N = self.max_bridges
        for i in range(N):
            j = (self._next_search + i) % N
            if not self.alive[j]:
                self.src[j] = int(src)
                self.dst[j] = int(dst)
                self.weight[j] = float(weight)
                self.last_flux_tick[j] = int(born_tick)
                self.alive[j] = True
                self._next_search = (j + 1) % N
                return j
        return -1

    def remove(self, slot: int) -> None:
        if not self.alive[slot]:
            return
        self.alive[slot] = False
        self.weight[slot] = 0.0
        self._next_search = min(self._next_search, slot)

    def find(self, src: int, dst: int) -> int:
        """Return the alive bridge slot with (src, dst) or -1.

        Directed: bridge(a→b) and bridge(b→a) are distinct.
        """
        mask = self.alive & (self.src == src) & (self.dst == dst)
        idx = np.where(mask)[0]
        if idx.size == 0:
            return -1
        return int(idx[0])

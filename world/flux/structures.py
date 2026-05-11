"""Nodes — SoA container for bound structures.

A Node is a bound configuration of one or more vibrations. It carries
the summed energy of its constituent vibrations (minus the η heat
exported during binding). Nodes persist while flux passes through them
(F1b mechanic; F1a nodes just accumulate).

Bridges (node-to-node weighted edges) are added in F1b. F1a stores
nodes only.
"""
from __future__ import annotations
from typing import Sequence
import numpy as np


class Nodes:
    """Pre-allocated SoA container for bound nodes.

    Slot reuse identical to `Quanta`: lowest-index free slot wins on
    `add`; `_next_search` cursor advances past the just-filled slot.

    Each node carries position, energy, dominant frequency, and the
    tick at which it was born (for F1b decay accounting).
    """

    def __init__(self, max_nodes: int):
        self.max_nodes = int(max_nodes)
        N = self.max_nodes
        self.pos = np.zeros((N, 3), dtype=np.float64)
        self.energy = np.zeros(N, dtype=np.float64)
        self.freq = np.zeros(N, dtype=np.float64)
        self.born_tick = np.zeros(N, dtype=np.int64)
        self.alive = np.zeros(N, dtype=np.bool_)
        self._next_search = 0

    def n_alive(self) -> int:
        return int(self.alive.sum())

    def total_energy(self) -> float:
        return float(self.energy[self.alive].sum())

    def add(self, pos: Sequence[float], energy: float, freq: float,
            born_tick: int) -> int:
        N = self.max_nodes
        for i in range(N):
            j = (self._next_search + i) % N
            if not self.alive[j]:
                self.pos[j] = pos
                self.energy[j] = float(energy)
                self.freq[j] = float(freq)
                self.born_tick[j] = int(born_tick)
                self.alive[j] = True
                self._next_search = (j + 1) % N
                return j
        return -1

    def remove(self, slot: int) -> float:
        if not self.alive[slot]:
            return 0.0
        e = float(self.energy[slot])
        self.alive[slot] = False
        self.energy[slot] = 0.0
        self._next_search = min(self._next_search, slot)
        return e

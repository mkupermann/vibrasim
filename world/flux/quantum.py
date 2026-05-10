"""Quanta — struct-of-arrays container for energy-carrying vibrations.

Each vibration carries a discrete energy quantum. Bound vibrations live
in the Structures graph (added in F1); free vibrations live here.
"""
from __future__ import annotations
from typing import Sequence
import numpy as np


class Quanta:
    """Pre-allocated SoA container for free vibrations.

    Slots are reused on remove: `add` finds the lowest-index free slot.
    Energy is float64 for clean conservation arithmetic; positions and
    velocities are float64 to match legacy EQMOD's `world/state.py`.
    """

    def __init__(self, max_quanta: int):
        self.max_quanta = int(max_quanta)
        N = self.max_quanta
        self.pos = np.zeros((N, 3), dtype=np.float64)
        self.vel = np.zeros((N, 3), dtype=np.float64)
        self.freq = np.zeros(N, dtype=np.float64)
        self.polarity = np.zeros(N, dtype=np.int8)
        self.energy = np.zeros(N, dtype=np.float64)
        self.alive = np.zeros(N, dtype=np.bool_)
        self._next_search = 0  # cursor for free-slot search

    def n_alive(self) -> int:
        return int(self.alive.sum())

    def total_energy(self) -> float:
        return float(self.energy[self.alive].sum())

    def add(self, pos: Sequence[float], vel: Sequence[float],
            freq: float, polarity: int, energy: float) -> int:
        """Add a vibration, returning its slot index or -1 if full."""
        N = self.max_quanta
        # Search from _next_search forward, wrap around once
        for i in range(N):
            j = (self._next_search + i) % N
            if not self.alive[j]:
                self.pos[j] = pos
                self.vel[j] = vel
                self.freq[j] = freq
                self.polarity[j] = polarity
                self.energy[j] = energy
                self.alive[j] = True
                self._next_search = (j + 1) % N  # advance past just-filled slot
                return j
        return -1

    def remove(self, slot: int) -> float:
        """Mark slot dead; return the released energy quantum."""
        if not self.alive[slot]:
            return 0.0
        e = float(self.energy[slot])
        self.alive[slot] = False
        self.energy[slot] = 0.0
        # Reset search cursor so this slot is reused first
        self._next_search = min(self._next_search, slot)
        return e

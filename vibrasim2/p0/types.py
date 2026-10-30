"""Immutable domain values for the registered Vibrasim-II P0 experiment."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray


class Topology(str, Enum):
    CYCLE = "cycle"
    BRANCH = "branch"


class ChannelMode(str, Enum):
    FULL = "full"
    NO_BONDS = "no_bonds"
    DECOUPLED = "decoupled"
    BROKEN_PAIR = "broken_pair"


class RunPurpose(str, Enum):
    PRIMARY = "primary"
    CONVERGENCE = "convergence"
    SENSITIVITY = "sensitivity"
    REPRODUCTION = "reproduction"


class Verdict(str, Enum):
    PASS = "PASS"
    NULL = "NULL"
    INCONCLUSIVE = "INCONCLUSIVE"
    FAIL = "FAIL"


@dataclass(frozen=True)
class P0Config:
    grid_shape: tuple[int, int]
    c: float
    k_b: float
    g: float
    dt: float
    sigma: float
    steps: int
    frame_stride: int
    source_centres: tuple[tuple[int, int], ...]

    @classmethod
    def registered(cls) -> "P0Config":
        return cls(
            grid_shape=(32, 32),
            c=1.0,
            k_b=0.5,
            g=1.0,
            dt=0.05,
            sigma=2.0,
            steps=2000,
            frame_stride=10,
            source_centres=((4, 16), (16, 4), (4, 4)),
        )

    def assert_registered(self) -> None:
        if self != type(self).registered():
            raise ValueError("registered P0 configuration is immutable")


@dataclass(frozen=True)
class RunCell:
    topology: Topology
    mode: ChannelMode
    purpose: RunPurpose
    source_centre: tuple[int, int]
    dt: float
    steps: int

    @property
    def slug(self) -> str:
        x, y = self.source_centre
        return f"{self.purpose.value}-{self.mode.value}-{self.topology.value}-x{x}-y{y}-dt{self.dt:g}"

    @property
    def arm_label(self) -> str:
        if self.mode is ChannelMode.FULL:
            return self.topology.value
        if self.mode is ChannelMode.BROKEN_PAIR:
            return f"{self.topology.value}:broken_pair"
        return self.mode.value


@dataclass(frozen=True)
class P0State:
    u: NDArray[np.float64]
    p: NDArray[np.float64]
    q: NDArray[np.float64]
    r: NDArray[np.float64]

    def __post_init__(self) -> None:
        arrays = tuple(np.array(value, dtype=np.float64, copy=True) for value in (self.u, self.p, self.q, self.r))
        u, p, q, r = arrays
        if u.ndim != 2 or p.ndim != 2 or u.shape != p.shape:
            raise ValueError("u and p must have matching two-dimensional shapes")
        if q.ndim != 1 or r.ndim != 1 or q.shape != r.shape:
            raise ValueError("q and r must have matching one-dimensional shapes")
        if any(value.size == 0 for value in arrays):
            raise ValueError("P0 state arrays must be non-empty")
        for value in arrays:
            value.setflags(write=False)
        for name, value in zip(("u", "p", "q", "r"), arrays, strict=True):
            object.__setattr__(self, name, value)


@dataclass(frozen=True)
class P0StateSnapshot:
    tick: int
    simulation_time: float
    state: P0State

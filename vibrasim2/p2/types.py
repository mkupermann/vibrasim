"""Immutable domain values for registered Vibrasim-II P2 cells."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray


class P2Arm(str, Enum):
    FULL = "full"
    NO_CAPTURE = "no_capture"
    NO_FIELD_FEEDBACK = "no_field_feedback"


class P2Purpose(str, Enum):
    PRIMARY = "primary"
    CONVERGENCE = "convergence"
    REPRODUCTION = "reproduction"


@dataclass(frozen=True)
class P2Config:
    grid_shape: tuple[int, int]
    candidate_radius: float
    c: float
    g: float
    k_m: float
    k_f: float
    capture_fraction: float
    formation_cost: float
    bond_lifetime: float
    max_valence: int
    dt: float
    steps: int
    sigma: float
    frame_stride: int
    source_centres: tuple[tuple[int, int], ...]
    energy_tolerance: float

    @classmethod
    def registered(cls) -> "P2Config":
        return cls(
            grid_shape=(32, 32), candidate_radius=4.5,
            c=1.0, g=1.0, k_m=0.5, k_f=0.25,
            capture_fraction=0.25, formation_cost=0.02,
            bond_lifetime=10.0, max_valence=2,
            dt=0.025, steps=4000, sigma=2.0, frame_stride=10,
            source_centres=((4, 16), (16, 4), (4, 4)),
            energy_tolerance=2e-4,
        )

    def assert_registered(self) -> None:
        if self != type(self).registered():
            raise ValueError("registered P2 configuration is immutable")


@dataclass(frozen=True)
class P2Cell:
    arm: P2Arm
    purpose: P2Purpose
    source_centre: tuple[int, int]
    dt: float
    steps: int

    @property
    def slug(self) -> str:
        x, y = self.source_centre
        return f"{self.purpose.value}-{self.arm.value}-x{x}-y{y}-dt{self.dt:g}"


@dataclass(frozen=True, order=True)
class Bond:
    left: int
    right: int
    age: float
    matter_rest: float
    field_rest: float

    def __post_init__(self) -> None:
        if self.left < 0 or self.right <= self.left:
            raise ValueError("bond requires ordered distinct endpoints")
        if not math.isfinite(self.age) or self.age < 0:
            raise ValueError("bond requires non-negative finite age")
        if not math.isfinite(self.matter_rest) or not math.isfinite(self.field_rest):
            raise ValueError("bond rest offsets must be finite")


@dataclass(frozen=True)
class P2State:
    u: NDArray[np.float64]
    p: NDArray[np.float64]
    q: NDArray[np.float64]
    r: NDArray[np.float64]
    reservoirs: NDArray[np.float64]
    bonds: tuple[Bond, ...]
    formation_sink: float
    bond_time: float

    def __post_init__(self) -> None:
        arrays = tuple(
            np.array(value, dtype=np.float64, copy=True)
            for value in (self.u, self.p, self.q, self.r, self.reservoirs)
        )
        u, p, q, r, reservoirs = arrays
        if u.ndim != 2 or p.shape != u.shape:
            raise ValueError("u and p must have matching two-dimensional shapes")
        if q.ndim != 1 or r.shape != q.shape or reservoirs.shape != q.shape:
            raise ValueError("q, r, and reservoirs must have matching one-dimensional shapes")
        if any(value.size == 0 or not np.all(np.isfinite(value)) for value in arrays):
            raise ValueError("P2 state arrays must be non-empty and finite")
        if np.any(reservoirs < 0):
            raise ValueError("reservoirs must be non-negative")
        if not math.isfinite(self.formation_sink) or self.formation_sink < 0:
            raise ValueError("formation_sink must be non-negative and finite")
        if not math.isfinite(self.bond_time) or self.bond_time < 0:
            raise ValueError("bond_time must be non-negative and finite")
        keys = tuple((bond.left, bond.right) for bond in self.bonds)
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate bond")
        if any(bond.right >= len(q) for bond in self.bonds):
            raise ValueError("bond endpoint exceeds matter state")
        for value in arrays:
            value.setflags(write=False)
        for name, value in zip(("u", "p", "q", "r", "reservoirs"), arrays, strict=True):
            object.__setattr__(self, name, value)
        object.__setattr__(self, "bonds", tuple(sorted(self.bonds)))


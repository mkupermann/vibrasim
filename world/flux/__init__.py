"""Flux Substrate — thermodynamically grounded learning substrate.

See docs/superpowers/specs/2026-05-10-flux-substrate-design.md for the
design rationale and falsifier contract.

This module is under active development. Public API stabilises after F1.
"""
from __future__ import annotations

from world.flux.audit import ConservationViolation, EnergyAuditor
from world.flux.boundary import absorb_cold_faces, inject_hot_floor
from world.flux.dynamics import Injector, tick
from world.flux.grid import Grid
from world.flux.quantum import Quanta

__all__ = [
    "ConservationViolation",
    "EnergyAuditor",
    "Grid",
    "Injector",
    "Quanta",
    "absorb_cold_faces",
    "inject_hot_floor",
    "tick",
]

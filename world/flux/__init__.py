"""Flux Substrate — thermodynamically grounded learning substrate.

See docs/superpowers/specs/2026-05-10-flux-substrate-design.md for the
design rationale and falsifier contract.

This module is under active development. Public API stabilises after F1.
"""
from __future__ import annotations

from world.flux.audit import ConservationViolation, EnergyAuditor
from world.flux.binding import (
    BindingConfig,
    attempt_binding,
    binding_probability,
    find_pairs_within,
    pred_coherence,
)
from world.flux.boundary import absorb_cold_faces, inject_hot_floor
from world.flux.decay import (
    DecayConfig,
    attempt_decay,
    decay_probability,
)
from world.flux.dynamics import Injector, tick
from world.flux.grid import Grid
from world.flux.quantum import Quanta
from world.flux.structures import Nodes

__all__ = [
    "BindingConfig",
    "ConservationViolation",
    "DecayConfig",
    "EnergyAuditor",
    "Grid",
    "Injector",
    "Nodes",
    "Quanta",
    "absorb_cold_faces",
    "attempt_binding",
    "attempt_decay",
    "binding_probability",
    "decay_probability",
    "find_pairs_within",
    "inject_hot_floor",
    "pred_coherence",
    "tick",
]

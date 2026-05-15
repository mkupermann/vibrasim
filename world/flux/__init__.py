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
from world.flux.boundary import (
    absorb_cold_faces,
    inject_cold_ceiling,
    inject_hot_floor,
)
from world.flux.bridges import Bridges
from world.flux.decay import (
    DecayConfig,
    attempt_decay,
    decay_probability,
)
from world.flux.dynamics import Injector, tick
from world.flux.grid import Grid
from world.flux.plasticity import (
    PlasticityConfig,
    apply_plasticity,
    count_flux_through,
    prune_bridges_and_nodes,
)
from world.flux.pressure import apply_pressure_gradient_force
from world.flux.quantum import Quanta
from world.flux.structures import Nodes
from world.flux.thermal import (
    ThermalConfig,
    apply_buoyancy_and_damping,
    enforce_thermal_boundaries,
)

__all__ = [
    "BindingConfig",
    "Bridges",
    "ConservationViolation",
    "DecayConfig",
    "EnergyAuditor",
    "Grid",
    "Injector",
    "Nodes",
    "PlasticityConfig",
    "Quanta",
    "ThermalConfig",
    "absorb_cold_faces",
    "apply_buoyancy_and_damping",
    "apply_plasticity",
    "apply_pressure_gradient_force",
    "attempt_binding",
    "attempt_decay",
    "binding_probability",
    "count_flux_through",
    "decay_probability",
    "enforce_thermal_boundaries",
    "find_pairs_within",
    "inject_cold_ceiling",
    "inject_hot_floor",
    "pred_coherence",
    "prune_bridges_and_nodes",
    "tick",
]

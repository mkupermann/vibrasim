"""Energy-transfer and finite bond-lifecycle primitives for V2-P2."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np
from numpy.typing import NDArray

from vibrasim2.p0.fixtures import coupling_sites

from .fixtures import candidate_edges
from .types import Bond, P2Arm, P2Config, P2State


@dataclass(frozen=True)
class BondEvent:
    kind: str
    left: int
    right: int

    def __post_init__(self) -> None:
        if self.kind not in {"formed", "expired"}:
            raise ValueError("unknown bond event kind")


def capture_positive_work(
    state: P2State,
    coupling_force: NDArray[np.float64],
    *,
    dt: float,
    fraction: float,
) -> tuple[P2State, float]:
    """Move a bounded fraction of positive coupling work from kinetic energy."""
    forces = np.asarray(coupling_force, dtype=np.float64)
    if forces.shape != state.r.shape or not np.all(np.isfinite(forces)):
        raise ValueError("coupling_force must be finite and match matter velocity")
    if not math.isfinite(dt) or dt <= 0 or not math.isfinite(fraction) or not 0 <= fraction <= 1:
        raise ValueError("capture dt and fraction are invalid")
    requested = fraction * np.maximum(forces * state.r * dt, 0.0)
    available = 0.5 * np.square(state.r)
    debit = np.minimum(requested, available)
    remaining_twice_ke = np.maximum(np.square(state.r) - 2.0 * debit, 0.0)
    next_r = np.copysign(np.sqrt(remaining_twice_ke), state.r)
    next_r[remaining_twice_ke == 0.0] = 0.0
    captured = float(debit.sum())
    return replace(state, r=next_r, reservoirs=state.reservoirs + debit), captured


def bond_spring_energy(
    state: P2State,
    bond: Bond,
    config: P2Config,
    arm: P2Arm = P2Arm.FULL,
) -> float:
    sites = coupling_sites()
    matter_extension = state.q[bond.left] - state.q[bond.right] - bond.matter_rest
    left_site = tuple(sites[bond.left])
    right_site = tuple(sites[bond.right])
    field_extension = state.u[left_site] - state.u[right_site] - bond.field_rest
    field_energy = (
        0.0
        if arm is P2Arm.NO_FIELD_FEEDBACK
        else 0.5 * config.k_f * field_extension**2
    )
    return float(0.5 * config.k_m * matter_extension**2 + field_energy)


def bond_forces(
    state: P2State, arm: P2Arm, config: P2Config
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return universal live-bond force terms for field and matter."""
    field = np.zeros(config.grid_shape, dtype=np.float64)
    matter = np.zeros_like(state.q)
    sites = coupling_sites()
    for bond in state.bonds:
        matter_extension = state.q[bond.left] - state.q[bond.right] - bond.matter_rest
        matter_force = config.k_m * matter_extension
        matter[bond.left] -= matter_force
        matter[bond.right] += matter_force
        if arm is not P2Arm.NO_FIELD_FEEDBACK:
            left_site = tuple(sites[bond.left])
            right_site = tuple(sites[bond.right])
            field_extension = state.u[left_site] - state.u[right_site] - bond.field_rest
            field_force = config.k_f * field_extension
            field[left_site] -= field_force
            field[right_site] += field_force
    return field, matter


def age_and_expire_bonds(
    state: P2State,
    config: P2Config,
    *,
    dt: float,
    arm: P2Arm = P2Arm.FULL,
) -> tuple[P2State, tuple[BondEvent, ...]]:
    """Age bonds, returning spring potential locally when lifetime is reached."""
    reservoirs = state.reservoirs.copy()
    survivors: list[Bond] = []
    events: list[BondEvent] = []
    for bond in state.bonds:
        aged = replace(bond, age=bond.age + dt)
        if aged.age >= config.bond_lifetime:
            returned = bond_spring_energy(state, bond, config, arm) / 2.0
            reservoirs[bond.left] += returned
            reservoirs[bond.right] += returned
            events.append(BondEvent("expired", bond.left, bond.right))
        else:
            survivors.append(aged)
    return (
        replace(
            state,
            reservoirs=reservoirs,
            bonds=tuple(survivors),
            bond_time=state.bond_time + len(state.bonds) * dt,
        ),
        tuple(events),
    )


def form_eligible_bonds(
    state: P2State, config: P2Config
) -> tuple[P2State, tuple[BondEvent, ...]]:
    """Form every locally funded candidate permitted by deterministic priority."""
    active = {(bond.left, bond.right) for bond in state.bonds}
    degree = np.zeros(len(state.q), dtype=np.int64)
    for left, right in active:
        degree[left] += 1
        degree[right] += 1
    reservoirs = state.reservoirs.copy()
    sites = coupling_sites()
    formed: list[Bond] = []
    half_cost = config.formation_cost / 2.0
    for left, right in candidate_edges(config):
        if (left, right) in active:
            continue
        if degree[left] >= config.max_valence or degree[right] >= config.max_valence:
            continue
        if reservoirs[left] < half_cost or reservoirs[right] < half_cost:
            continue
        reservoirs[left] -= half_cost
        reservoirs[right] -= half_cost
        degree[left] += 1
        degree[right] += 1
        left_site = tuple(sites[left])
        right_site = tuple(sites[right])
        formed.append(
            Bond(
                left,
                right,
                age=0.0,
                matter_rest=float(state.q[left] - state.q[right]),
                field_rest=float(state.u[left_site] - state.u[right_site]),
            )
        )
    events = tuple(BondEvent("formed", bond.left, bond.right) for bond in formed)
    return (
        replace(
            state,
            reservoirs=reservoirs,
            bonds=state.bonds + tuple(formed),
            formation_sink=state.formation_sink + config.formation_cost * len(formed),
        ),
        events,
    )

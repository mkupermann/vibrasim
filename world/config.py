from __future__ import annotations
import tomllib
from dataclasses import dataclass, replace, fields
from pathlib import Path


@dataclass(frozen=True)
class WorldConfig:
    # Seeding (3D)
    n_initial_vibrations: int = 1000
    box_size: tuple[float, float, float] = (1000.0, 1000.0, 1000.0)
    freq_min: float = 100.0
    freq_max: float = 10000.0
    freq_distribution: str = "log"
    speed_min: float = 10.0
    speed_max: float = 50.0
    polarity_split: float = 0.5

    # Binding
    r_1: float = 5.0
    r_2: float = 10.0
    freq_ratio: float = 0.08
    freq_tolerance: float = 0.005

    # Decay (mean exponential lifetimes, seconds)
    pair_decay_time: float = 5.0
    triad_decay_time: float = 30.0

    # Scale separation through repulsion (§4.6)
    repulsion_k: float = 100.0
    repulsion_cell_size: float = 100.0
    repulsion_threshold_ratio: float = 1000.0

    # Ambient regeneration (§4.7)
    lambda_gen: float = 0.0001
    lambda_dec: float = 0.001

    # Simulation
    dt: float = 1.0 / 60.0
    rng_seed: int | None = 42

    # Capacity
    n_vibrations_max: int = 4096
    n_nodes_max: int = 1024

    # Neuron dynamics — PHASE4-R1/R2/R3 amendments. Off by default so legacy
    # configurations behave exactly as before. When enabled, level-4 atoms
    # accumulate charge from nearby vibrations, fire when charge ≥ theta_fire,
    # and lock for t_refractory seconds after each firing.
    neuron_dynamics_enabled: bool = False
    tau_membrane: float = 0.5            # charge decay time constant (s)
    theta_fire: float = 4.0              # firing threshold (integrated count)
    n_emit: int = 8                      # vibrations emitted per firing
    t_refractory: float = 0.05           # refractory window after firing (s)
    r_integrate: float = 5.0             # radius around atom to count incoming vibrations
    emit_speed: float = 30.0             # speed magnitude of emitted vibrations
    emit_freq: float = 30000.0           # nominal frequency of emitted vibrations

    # Plan A — substrate growth amendments
    lambda_dec_mol: float = 0.0           # baseline decay rate for level-5+ molecules
    r_strengthen: float = 5.0             # radius around firings for level-5+ strengthening
    emit_band_ratios: tuple[float, float, float] = (0.08, 1.0, 12.5)  # PHASE4 emission band multipliers
    mol_fusion_enabled: bool = False      # PHASE3-R1: allow molecule + molecule binding

    # Plan A.5 — substrate performance
    slot_recycling_enabled: bool = True   # World.allocate_node reuses dead slots before extending k_count
    numba_jit_enabled: bool = True        # @njit cores for hot loops


INITIAL_CONFIG = WorldConfig()


def load_config(path: Path | str | None) -> WorldConfig:
    if path is None:
        return WorldConfig()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    valid_field_names = {f.name for f in fields(WorldConfig)}
    overrides = {k: v for k, v in data.items() if k in valid_field_names}
    if "box_size" in overrides and isinstance(overrides["box_size"], list):
        overrides["box_size"] = tuple(overrides["box_size"])
    return replace(WorldConfig(), **overrides)

from __future__ import annotations
import tomllib
from dataclasses import dataclass, replace, fields
from pathlib import Path


@dataclass(frozen=True)
class WorldConfig:
    # Seeding
    n_initial_vibrations: int = 1000
    box_size: tuple[float, float] = (1000.0, 1000.0)
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

    # Simulation
    dt: float = 1.0 / 60.0
    rng_seed: int | None = 42

    # Capacity
    n_vibrations_max: int = 4096
    n_nodes_max: int = 1024


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

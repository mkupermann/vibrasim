import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World


@pytest.fixture
def default_config() -> WorldConfig:
    return WorldConfig()


@pytest.fixture
def empty_world() -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(100.0, 100.0, 100.0),
        n_vibrations_max=64,
        n_nodes_max=32,
        rng_seed=42,
    )
    return World(cfg)

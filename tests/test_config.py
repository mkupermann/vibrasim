import pytest
import tomllib
from pathlib import Path
from world.config import WorldConfig, INITIAL_CONFIG, load_config


def test_default_config_matches_spec():
    cfg = WorldConfig()
    assert cfg.n_initial_vibrations == 1000
    assert cfg.box_size == (1000.0, 1000.0)
    assert cfg.freq_min == 100.0
    assert cfg.freq_max == 10000.0
    assert cfg.freq_distribution == "log"
    assert cfg.r_1 == 5.0
    assert cfg.r_2 == 10.0
    assert cfg.freq_ratio == 0.08
    assert cfg.freq_tolerance == 0.005
    assert cfg.pair_decay_time == 5.0
    assert cfg.triad_decay_time == 30.0
    assert cfg.dt == pytest.approx(1.0 / 60.0)
    assert cfg.rng_seed == 42
    assert cfg.n_vibrations_max == 4096
    assert cfg.n_nodes_max == 1024


def test_initial_config_singleton():
    assert INITIAL_CONFIG == WorldConfig()


def test_config_is_frozen():
    cfg = WorldConfig()
    with pytest.raises(Exception):
        cfg.r_1 = 99.0  # type: ignore[misc]


def test_toml_override(tmp_path: Path):
    toml = tmp_path / "override.toml"
    toml.write_text('r_1 = 7.5\nrng_seed = 123\n')
    cfg = load_config(toml)
    assert cfg.r_1 == 7.5
    assert cfg.rng_seed == 123
    assert cfg.r_2 == 10.0
    assert cfg.n_initial_vibrations == 1000


def test_load_config_with_no_path_returns_defaults():
    assert load_config(None) == WorldConfig()

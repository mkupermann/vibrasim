import pytest
import tomllib
from pathlib import Path
from world.config import WorldConfig, INITIAL_CONFIG, load_config


def test_default_config_matches_spec():
    cfg = WorldConfig()
    assert cfg.n_initial_vibrations == 1000
    assert cfg.box_size == (1000.0, 1000.0, 1000.0)         # CHANGED: 3-tuple
    assert cfg.r_1 == 5.0
    assert cfg.r_2 == 10.0
    assert cfg.repulsion_k == 100.0                         # NEW
    assert cfg.repulsion_cell_size == 100.0                 # NEW
    assert cfg.repulsion_threshold_ratio == 1000.0          # NEW
    assert cfg.lambda_gen == 0.0001                         # NEW
    assert cfg.lambda_dec == 0.001                          # NEW
    assert cfg.dt == pytest.approx(1.0 / 60.0)
    assert cfg.rng_seed == 42
    assert cfg.n_vibrations_max == 4096
    assert cfg.n_nodes_max == 1024


def test_box_size_is_three_tuple():
    cfg = WorldConfig()
    assert len(cfg.box_size) == 3
    for d in cfg.box_size:
        assert isinstance(d, float)


def test_toml_box_size_list_to_tuple():
    """Three-element list in TOML coerces to 3-tuple."""
    import tempfile, pathlib
    from world.config import load_config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write('box_size = [500.0, 500.0, 500.0]\n')
        path = pathlib.Path(f.name)
    cfg = load_config(path)
    assert cfg.box_size == (500.0, 500.0, 500.0)


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

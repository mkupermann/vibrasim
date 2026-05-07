import pytest
import tomllib
from pathlib import Path
from world.config import WorldConfig, INITIAL_CONFIG, load_config


def test_default_config_matches_spec():
    cfg = WorldConfig()
    assert cfg.n_initial_vibrations == 1000
    assert cfg.box_size == (60.0, 60.0, 60.0)               # CHANGED: 3-tuple, matches calibration TOMLs
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
        f.write('box_size = [50.0, 50.0, 50.0]\n')
        path = pathlib.Path(f.name)
    cfg = load_config(path)
    assert cfg.box_size == (50.0, 50.0, 50.0)


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


def test_growth_amendment_fields_have_safe_defaults():
    """Plan A new fields must default off so legacy configs are unaffected."""
    cfg = WorldConfig()
    assert cfg.lambda_dec_mol == 0.0
    assert cfg.r_strengthen == 5.0
    assert cfg.emit_band_ratios == (0.08, 1.0, 12.5)  # freq_ratio, 1, 1/freq_ratio
    assert cfg.mol_fusion_enabled is False


def test_AP_perf_flags_slot_recycling_default_true():
    """Plan A.5 slot_recycling_enabled defaults ON."""
    cfg = WorldConfig(numba_jit_enabled=False)
    assert cfg.slot_recycling_enabled is True


def test_AP_jit_guard_requires_valid_cell_to_enable():
    """numba_jit_enabled=True with cell >= max(box_size) does not raise.

    The default box_size=(60,60,60) and repulsion_cell_size=100 already
    satisfy this; here we also verify an explicit oversized cell works.
    """
    cfg = WorldConfig(repulsion_cell_size=1000.0, numba_jit_enabled=True)
    assert cfg.numba_jit_enabled is True
    assert cfg.slot_recycling_enabled is True


def test_jit_guard_fires_when_cell_lt_box():
    """numba_jit_enabled=True with cell < box raises AssertionError.

    The JIT core in apply_scale_repulsion does an unconditional O(K²)
    all-pairs loop; the Python path uses a spatial grid keyed on
    repulsion_cell_size. When cell < box the two paths diverge.
    """
    with pytest.raises(AssertionError, match="repulsion_cell_size"):
        WorldConfig(
            numba_jit_enabled=True,
            box_size=(1000.0, 1000.0, 1000.0),
            repulsion_cell_size=100.0,
        )


def test_jit_guard_silent_when_jit_disabled():
    """numba_jit_enabled=False with cell < box does NOT raise.

    The Python spatial-grid path is always correct; the guard only
    protects the JIT path.
    """
    cfg = WorldConfig(
        numba_jit_enabled=False,
        box_size=(1000.0, 1000.0, 1000.0),
        repulsion_cell_size=100.0,
    )
    assert cfg.numba_jit_enabled is False


def test_default_worldconfig_constructs_without_raising():
    """Regression: bare WorldConfig() must not raise.

    With box_size=(60,60,60) and repulsion_cell_size=100, the JIT guard
    condition (cell >= max(box)) is satisfied even when numba_jit_enabled
    defaults to True.
    """
    cfg = WorldConfig()
    assert cfg.numba_jit_enabled is True
    assert cfg.box_size == (60.0, 60.0, 60.0)
    assert cfg.repulsion_cell_size >= max(cfg.box_size)


def test_stdp_amendment_fields_have_safe_defaults():
    """Plan B new fields must default off so legacy configs are unaffected."""
    cfg = WorldConfig()
    assert cfg.stdp_enabled is False
    assert cfg.tau_LTP == 0.020
    assert cfg.tau_LTD == 0.020
    assert cfg.delta_LTP == 1.0
    assert cfg.delta_LTD == 0.5
    assert cfg.r_bridge == 5.0
    assert cfg.synaptic_transmission_strength == 0.5
    assert cfg.synaptic_transmission_threshold == 5.0


def test_plan_C_audio_fields_have_safe_defaults():
    """Plan C audio fields default off so legacy configs are unaffected."""
    cfg = WorldConfig()
    assert cfg.audio_io_enabled is False
    assert cfg.audio_sample_rate == 16000
    assert cfg.audio_block_size == 256
    assert cfg.audio_fft_size == 512
    assert cfg.audio_buffer_seconds == 30.0
    assert cfg.audio_amplitude_threshold == 0.01
    assert cfg.audio_freq_min == 50.0
    assert cfg.audio_freq_max == 8000.0
    assert cfg.audio_input_port_origin == (0.0, 0.0, 0.0)
    assert cfg.audio_input_port_size == (15.0, 15.0, 15.0)
    assert cfg.audio_output_port_origin == (45.0, 0.0, 0.0)
    assert cfg.audio_output_port_size == (15.0, 15.0, 15.0)


def test_plan_D_video_fields_have_safe_defaults():
    """Plan D video fields default off so legacy configs are unaffected."""
    cfg = WorldConfig()
    assert cfg.video_io_enabled is False
    assert cfg.video_fps == 30
    assert cfg.video_buffer_seconds == 5.0
    assert cfg.video_patch_grid == (16, 16)
    assert cfg.video_n_orientations == 8
    assert cfg.video_amplitude_threshold == 0.05
    assert cfg.video_freq_min == 1000.0
    assert cfg.video_freq_max == 12000.0
    assert cfg.video_input_port_origin == (0.0, 0.0, 45.0)
    assert cfg.video_input_port_size == (15.0, 15.0, 15.0)
    assert cfg.video_webcam_index == 0

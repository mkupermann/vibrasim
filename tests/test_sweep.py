import json
import pytest
from pathlib import Path
from tools.sweep import grid_configs, run_one_trial


def test_grid_enumeration():
    configs = list(grid_configs({"r_2": [10, 20, 30], "freq_tolerance": [0.005, 0.01]}))
    assert len(configs) == 6
    assert {"r_2": 10, "freq_tolerance": 0.005} in configs


def test_run_one_trial_returns_objective(tmp_path):
    """A short trial returns a finite objective value."""
    params = {"box_size": [200.0, 200.0, 200.0], "repulsion_cell_size": 200.0,
              "duration": 5.0, "objective": "time_to_first_atom"}
    result = run_one_trial(params, snapshot_dir=tmp_path)
    assert "objective" in result
    assert "params" in result
    assert "wall_s" in result

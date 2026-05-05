from pathlib import Path
import pytest
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot
from tools.histogram import compute_histogram_text


def test_text_output_lists_levels(tmp_path):
    cfg = WorldConfig(rng_seed=42)
    w = World(cfg)
    path = tmp_path / "snap.npz"
    save_snapshot(w, path)
    text = compute_histogram_text(path)
    assert "vibrations" in text.lower()
    assert "electrons" in text.lower() or "e-" in text


def test_empty_world_no_crash(tmp_path):
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100., 100., 100.),
                      rng_seed=42)
    w = World(cfg)
    path = tmp_path / "snap.npz"
    save_snapshot(w, path)
    text = compute_histogram_text(path)
    assert isinstance(text, str)

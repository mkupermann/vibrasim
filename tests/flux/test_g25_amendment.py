"""R-21 unit tests for G25 — content-driven xy-position injection.

Acceptance per ``.eqmod/autopilot/QUEUE.yaml::R-21`` rows 1-4 and
``docs/amendments/G25-content-driven-injection.md`` §3.

These are mechanical tests on the helper function and the env-var
routing. The 10k-tick substrate verification lives in
``test_g25_verification.py``.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pytest

from agent.flux.audio_raw import (
    inject_raw_audio_sample,
    position_hash,
    position_hash_content_driven,
)
from world.flux.grid import Grid
from world.flux.quantum import Quanta


# Locked fixtures: legacy ``position_hash`` numerical output for four
# (sample_index, Lx, Ly, voxel_size, seed) tuples, captured on
# autopilot/R-21 at 2026-05-21 before G25 changes. These pin the legacy
# path so the content-driven sibling cannot accidentally regress it.
_LEGACY_FIXTURES = [
    # (sample_index, Lx, Ly, voxel_size, seed, expected_x, expected_y)
    (12345, 30, 15, 1.0, 0,
     3.99239005520939827e+00, 9.95019581168889999e+00),
    (0, 30, 15, 1.0, 0,
     2.64993242430500686e+01, 7.21385271870531142e+00),
    (1, 30, 15, 1.0, 0,
     1.69968472514301538e+01, 8.02788444212637842e+00),
    (999999, 80, 40, 1.0, 0,
     3.56213346868753433e+01, 1.08743475098162889e+01),
]


def test_content_driven_position_hash_returns_different_xy_for_different_sample_values():
    """G25 §3 row 1: same sample_index, different sample_value → different xy.

    Threshold: Euclidean distance > 0.5 * voxel_size. Higher than 0
    so a near-miss collision in the hash output also fails — the
    content channel must move the quantum at least half a voxel.
    """
    Lx, Ly, voxel_size = 30, 15, 1.0
    x1, y1 = position_hash_content_driven(
        12345, 0.1, Lx, Ly, voxel_size, seed=0,
    )
    x2, y2 = position_hash_content_driven(
        12345, 0.8, Lx, Ly, voxel_size, seed=0,
    )
    distance = math.hypot(x1 - x2, y1 - y2)
    assert distance > 0.5 * voxel_size, (
        f"content-driven position collapsed to nearly the same xy: "
        f"sample_value=0.1 -> ({x1}, {y1}); "
        f"sample_value=0.8 -> ({x2}, {y2}); dist={distance}"
    )


def test_content_driven_position_hash_deterministic():
    """G25 §3 row 2: identical inputs → bit-identical xy across calls."""
    Lx, Ly, voxel_size = 30, 15, 1.0
    inputs = [
        (12345, 0.1, 0),
        (12345, 0.8, 0),
        (0, -0.5, 7),
        (4242, 0.0, 42),
        (1_000_001, 1.0, 1),
    ]
    for sample_index, sample_value, seed in inputs:
        x1, y1 = position_hash_content_driven(
            sample_index, sample_value, Lx, Ly, voxel_size, seed=seed,
        )
        x2, y2 = position_hash_content_driven(
            sample_index, sample_value, Lx, Ly, voxel_size, seed=seed,
        )
        assert x1 == x2 and y1 == y2, (
            f"non-deterministic at "
            f"(sample_index={sample_index}, sample_value={sample_value}, "
            f"seed={seed}): ({x1}, {y1}) != ({x2}, {y2})"
        )


def test_legacy_position_hash_unchanged():
    """G25 §3 row 3: legacy ``position_hash`` numerical output preserved.

    Four pinned fixtures: each must reproduce the captured xy values
    bit-for-bit. If this fails, G25's implementation accidentally
    perturbed the legacy code path and the R-13/R-14-era acceptance
    of those upstream items is invalidated.
    """
    for (sample_index, Lx, Ly, voxel_size, seed,
         expected_x, expected_y) in _LEGACY_FIXTURES:
        x, y = position_hash(
            sample_index, Lx, Ly, voxel_size, seed=seed,
        )
        assert x == expected_x and y == expected_y, (
            f"legacy position_hash drift at "
            f"(sample_index={sample_index}, Lx={Lx}, Ly={Ly}, "
            f"voxel_size={voxel_size}, seed={seed}): "
            f"got ({x}, {y}), expected ({expected_x}, {expected_y})"
        )


def test_env_var_routes_to_content_driven_path(monkeypatch):
    """G25 §3 row 4: with the env var set, inject_raw_audio_sample calls
    position_hash_content_driven, NOT position_hash.

    Verified via two monkey-patched counters on the module-level
    references. The injection function must invoke the content-driven
    helper when ``EQMOD_USE_CONTENT_DRIVEN_POSITION=1`` and the legacy
    helper when the env var is absent or set to ``"0"``.
    """
    import agent.flux.audio_raw as raw_mod

    legacy_calls = []
    content_calls = []

    def legacy_spy(sample_index, Lx, Ly, voxel_size, *, seed=0):
        legacy_calls.append((sample_index, Lx, Ly, voxel_size, seed))
        return (0.0, 0.0)

    def content_spy(sample_index, sample_value, Lx, Ly, voxel_size, *, seed=0):
        content_calls.append(
            (sample_index, sample_value, Lx, Ly, voxel_size, seed)
        )
        return (0.0, 0.0)

    monkeypatch.setattr(raw_mod, "position_hash", legacy_spy)
    monkeypatch.setattr(
        raw_mod, "position_hash_content_driven", content_spy,
    )

    grid = Grid(dims=(30, 15, 8), voxel_size=1.0, T_smoothing=0.1)
    quanta = Quanta(max_quanta=64)
    rng = np.random.default_rng(0)

    # Without env var: legacy path.
    monkeypatch.delenv("EQMOD_USE_CONTENT_DRIVEN_POSITION", raising=False)
    inject_raw_audio_sample(
        quanta, grid, sample_value=0.3, sample_index=42, rng=rng,
    )
    assert len(legacy_calls) == 1 and len(content_calls) == 0, (
        f"legacy path not taken: "
        f"legacy_calls={legacy_calls}, content_calls={content_calls}"
    )

    # With env var = "0": still legacy.
    monkeypatch.setenv("EQMOD_USE_CONTENT_DRIVEN_POSITION", "0")
    inject_raw_audio_sample(
        quanta, grid, sample_value=0.3, sample_index=43, rng=rng,
    )
    assert len(legacy_calls) == 2 and len(content_calls) == 0

    # With env var = "1": content-driven path.
    monkeypatch.setenv("EQMOD_USE_CONTENT_DRIVEN_POSITION", "1")
    inject_raw_audio_sample(
        quanta, grid, sample_value=0.3, sample_index=44, rng=rng,
    )
    assert len(legacy_calls) == 2 and len(content_calls) == 1, (
        f"content-driven path not taken under env var: "
        f"legacy_calls={legacy_calls}, content_calls={content_calls}"
    )
    # The recorded call must include the sample_value 0.3.
    assert content_calls[0][1] == pytest.approx(0.3)

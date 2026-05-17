"""Shared fixtures for the flux test layer.

Session-scoped R-11 encoder-free runs: the no-input control is consumed
by both ``test_encoder_free_training_run.py`` and
``test_encoder_free_negative_control.py``. Computing it once per pytest
invocation saves roughly the wallclock of one no-input run when both
files are executed in the same postflight pass.
"""
from __future__ import annotations

import os

import pytest


def _encoder_free_cfg_for_session():
    """Locked R-11 config with ``EQMOD_R11_N_TICKS`` override.

    The R-9 plan's target is ~1.8M ticks (~30 min audio at the assumed
    1 kHz tick rate). The actual encoder-free tick rate on this Mac
    under the full F1b/F1c stack is far below 1 kHz, so the plan target
    is unreachable inside the postflight 30-min pytest timeout. The
    default value here is sized to fit a single postflight run for
    BOTH gates combined; any deviation from the plan target is
    documented in the R-11 phase-log entry.
    """
    from agent.flux.encoder_free_training import EncoderFreeTrainingConfig
    n_ticks = int(os.environ.get("EQMOD_R11_N_TICKS", "5000"))
    return EncoderFreeTrainingConfig(n_ticks_train=n_ticks)


@pytest.fixture(scope="session")
def encoder_free_cfg():
    return _encoder_free_cfg_for_session()


@pytest.fixture(scope="session")
def encoder_free_trained_result(encoder_free_cfg):
    from agent.flux.encoder_free_training import run_encoder_free_training
    return run_encoder_free_training(encoder_free_cfg, input_kind="audio")


@pytest.fixture(scope="session")
def encoder_free_control_result(encoder_free_cfg):
    from agent.flux.encoder_free_training import run_encoder_free_training
    return run_encoder_free_training(encoder_free_cfg, input_kind="no_input")

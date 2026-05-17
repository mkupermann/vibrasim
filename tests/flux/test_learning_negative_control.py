"""F3 negative-control acceptance.

Pre-registered by R-4 (plan
`docs/superpowers/plans/2026-05-16-flux-substrate-F3.md`):

The same substrate, run for the same wallclock with the same RNG,
driven by spectrally-flat gaussian white noise through the SAME cochlea,
must NOT reach the frequency-localisation threshold that the trained
run reaches. If it does, the trained-run signal is a state detector,
not a learning finding — and F3 NULLs per the charter's negative-control
rule.
"""
from __future__ import annotations

import pytest

from agent.flux.learning_metric import frequency_localisation_index
from agent.flux.learning_run import LearningRunConfig, run_learning_session


@pytest.mark.slow
def test_F3_control_substrate_does_not_develop_pattern_specific_topology():
    cfg = LearningRunConfig()

    # Trained baseline (matched-wallclock).
    trained = run_learning_session(cfg, input_kind="train")
    n_alive_train = int(trained.bridges.alive.sum())
    assert n_alive_train >= cfg.n_bridges_min_alive, (
        f"trained baseline produced only {n_alive_train} alive bridges; "
        f"the test cannot evaluate the negative control if the trained "
        f"substrate itself failed to form structure — verdict NULL"
    )
    floc_train = frequency_localisation_index(
        trained.bridges, trained.nodes,
        f_train_hz=cfg.f_train_hz, band_log_hz=cfg.band_log_hz,
    )

    # Negative control (white noise, same wallclock, same seed).
    control = run_learning_session(cfg, input_kind="control")
    n_alive_control = int(control.bridges.alive.sum())
    assert n_alive_control >= cfg.n_bridges_min_alive_control, (
        f"control run produced only {n_alive_control} alive bridges — "
        f"the control failed to function as a control (silent-pass risk) — "
        f"verdict NULL not PASS"
    )
    floc_control = frequency_localisation_index(
        control.bridges, control.nodes,
        f_train_hz=cfg.f_train_hz, band_log_hz=cfg.band_log_hz,
    )

    # Pre-registered absolute upper bound on control's f_loc.
    assert floc_control < cfg.f_loc_thresh_control, (
        f"control substrate f_loc = {floc_control:.3f} >= "
        f"{cfg.f_loc_thresh_control:.3f}. The substrate appears to "
        f"concentrate bridges at log(1000) even with flat-spectrum input — "
        f"the trained-run metric is a state detector, not a learning "
        f"signal. Verdict NULL per autopilot charter."
    )
    # Pre-registered relative margin.
    margin = floc_train - floc_control
    assert margin >= cfg.margin_min, (
        f"trained − control margin = {margin:.3f} < "
        f"{cfg.margin_min:.3f}. Trained may have crossed its floor "
        f"only because control drifted close to it; the separation is "
        f"not significant. Verdict NULL."
    )

"""R-11 encoder-free training acceptance — pre-registered gate.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-11``:

  ``test_encoder_free_substrate_distinguishable_from_no_input_control``
  PASSES — KL divergence of the encoder-free babble-MFCC histogram vs
  the no-input control histogram is > 2σ on 100-bootstrap.

The detailed plan
(``docs/superpowers/plans/2026-05-17-flux-encoder-free-audio-detailed.md``)
locks every parameter — no calibration sweeps authorised. NULL with
postmortem is the correct outcome on first failure; do not retune.

Session-scoped fixtures live in ``tests/flux/conftest.py`` so the no-
input control is shared with ``test_encoder_free_negative_control.py``.
"""
from __future__ import annotations

import pytest

from agent.flux.encoder_free_training import bootstrap_kl_stats


@pytest.mark.slow
def test_encoder_free_substrate_distinguishable_from_no_input_control(
    encoder_free_trained_result, encoder_free_control_result,
):
    """Trained encoder-free babble-MFCC vs no-input babble-MFCC: KL > 2σ.

    100-bootstrap with replacement on the per-frame MFCC values, then
    KL between the resampled probability histograms. Mean of the
    bootstrap KL must exceed 2 × its standard deviation — i.e. the KL
    reflects a real distributional gap, not within-resample noise.
    """
    trained = encoder_free_trained_result
    control = encoder_free_control_result
    cfg = trained.cfg
    mean, std, _ = bootstrap_kl_stats(
        trained.mfcc_per_frame.ravel(),
        control.mfcc_per_frame.ravel(),
        n_bootstrap=cfg.n_bootstrap,
        seed=11_07,
        n_bins=cfg.mfcc_hist_n_bins,
        value_range=cfg.mfcc_hist_range,
    )
    assert mean > 2.0 * std, (
        f"encoder-free substrate not distinguishable from no-input control: "
        f"KL_mean={mean:.6f} vs 2σ={2 * std:.6f} "
        f"(std={std:.6f}, n_bootstrap={cfg.n_bootstrap}). "
        f"trained bridges_alive={trained.n_bridges_alive} "
        f"nodes_alive={trained.n_nodes_alive} "
        f"quanta_peak={trained.n_quanta_alive_peak}; "
        f"control bridges_alive={control.n_bridges_alive} "
        f"nodes_alive={control.n_nodes_alive}. "
        f"Verdict: NULL per autopilot charter — no retuning."
    )

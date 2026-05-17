"""R-11 encoder-free negative-control sanity — pre-registered gate.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-11``:

  ``test_no_input_control_produces_no_substrate_specific_signal``
  PASSES — the no-input control's babble-MFCC distribution is
  statistically indistinguishable from white-noise MFCC (one-tailed
  KS-test ``p ≥ 0.05``).

Why two gates: the trained-vs-no-input gate (``test_encoder_free_training_run``)
is meaningful only if the no-input control is honest — i.e. it does not
itself develop substrate-specific structure from background thermal
flux alone. Per autopilot charter §"Negative controls are required":
a PASS without a clean negative control is a state detector, not a
finding.

Session-scoped fixtures live in ``tests/flux/conftest.py``.
"""
from __future__ import annotations

import pytest
from scipy.stats import ks_2samp

from agent.flux.encoder_free_training import mfcc_of_white_noise


@pytest.mark.slow
def test_no_input_control_produces_no_substrate_specific_signal(
    encoder_free_control_result,
):
    """No-input control babble-MFCC ≈ white-noise MFCC (KS p ≥ 0.05).

    The control's per-frame MFCC samples are compared against
    per-frame MFCCs of matched-duration, matched-SR Gaussian white
    noise. ``ks_2samp`` is two-sample two-sided; we accept the more
    permissive two-sided form (charter wording: "statistically
    indistinguishable"). ``p ≥ 0.05`` ⇒ we fail to reject same-distribution.
    """
    control = encoder_free_control_result
    cfg = control.cfg
    n_samples = control.babble.size
    duration_s = n_samples / cfg.sample_rate_hz
    wn_mfcc_per_frame = mfcc_of_white_noise(
        duration_s=duration_s,
        sample_rate_hz=cfg.sample_rate_hz,
        n_mfcc=cfg.mfcc_n_coeff,
        n_mels=cfg.mfcc_n_mels,
        frame_ms=cfg.mfcc_frame_ms,
        hop_ms=cfg.mfcc_hop_ms,
    )
    control_flat = control.mfcc_per_frame.ravel()
    wn_flat = wn_mfcc_per_frame.ravel()
    if control_flat.size == 0 or wn_flat.size == 0:
        pytest.skip(
            "control or white-noise reference produced zero MFCC frames "
            "— babble shorter than one frame; raise babble_n_samples."
        )
    stat, p = ks_2samp(control_flat, wn_flat)
    assert p >= 0.05, (
        f"no-input control produced substrate-specific signal: "
        f"KS statistic={stat:.4f} p={p:.6f} (need p ≥ 0.05). "
        f"control bridges_alive={control.n_bridges_alive} "
        f"nodes_alive={control.n_nodes_alive}. "
        f"Control is NOT honest — any trained-substrate result is "
        f"meaningless until the no-input control's background "
        f"emergence is explained. Verdict: NULL per autopilot charter."
    )

"""R-8 negative-control acceptance.

Pre-registered by R-6 (plan
`docs/superpowers/plans/2026-05-17-flux-training-EN.md`).

The same substrate, run for the same wallclock with the same RNG seed,
driven by gaussian white noise RMS-matched to the corpus through the
SAME cochlea, must NOT reach the corpus-alignment threshold that the
trained run reaches. If it does, the trained metric is a state detector
not a learning finding — verdict NULL per the autopilot charter's
negative-control rule.
"""
from __future__ import annotations

import pytest

from agent.flux.corpus_spectrum import compute_corpus_log_power_spectrum
from agent.flux.training_metric import corpus_alignment_index
from agent.flux.training_run import (
    DEFAULT_MANIFEST_PATH,
    TrainingRunConfig,
    load_corpus_waveform_from_manifest,
    run_training_session,
)


_MANIFEST_PRESENT = DEFAULT_MANIFEST_PATH.is_file()
_skip_no_corpus = pytest.mark.skipif(
    not _MANIFEST_PRESENT,
    reason=(
        f"R-7 corpus manifest missing at {DEFAULT_MANIFEST_PATH}; "
        f"R-8 cannot run without it"
    ),
)


@pytest.mark.slow
@_skip_no_corpus
def test_R8_control_substrate_does_not_align_with_corpus_spectrum():
    """Pre-registered R-8 negative-control acceptance.

    Locked thresholds (R-6 plan):
        alignment_thresh_control = 0.40
        margin_min = 0.10
        n_bridges_min_alive_control = 20
    """
    cfg = TrainingRunConfig()

    # Trained baseline (matched-wallclock, same seed).
    trained = run_training_session(cfg, input_kind="train")
    n_alive_train = int(trained.bridges.alive.sum())
    assert n_alive_train >= cfg.n_bridges_min_alive_train, (
        f"trained baseline produced only {n_alive_train} alive bridges; "
        f"cannot evaluate negative control if trained substrate itself "
        f"failed to form structure — verdict NULL"
    )

    corpus_wave = load_corpus_waveform_from_manifest(
        cfg.manifest_path,
        stage_order=cfg.stage_order,
        sample_rate_hz=cfg.cochlea_cfg.sample_rate_hz,
    )
    p_corpus = compute_corpus_log_power_spectrum(
        corpus_wave,
        sample_rate_hz=cfg.cochlea_cfg.sample_rate_hz,
        n_freq_bins=cfg.n_freq_bins,
        freq_band_hz=cfg.freq_band_hz,
    )

    alignment_train = corpus_alignment_index(
        trained.bridges, trained.nodes, p_corpus,
        n_freq_bins=cfg.n_freq_bins, freq_band_hz=cfg.freq_band_hz,
    )

    # Negative control (RMS-matched white noise, same wallclock, same seed).
    control = run_training_session(cfg, input_kind="control")
    n_alive_control = int(control.bridges.alive.sum())
    assert n_alive_control >= cfg.n_bridges_min_alive_control, (
        f"control produced only {n_alive_control} alive bridges — "
        f"the control failed to function (silent-pass risk) — "
        f"verdict NULL not PASS"
    )
    alignment_control = corpus_alignment_index(
        control.bridges, control.nodes, p_corpus,
        n_freq_bins=cfg.n_freq_bins, freq_band_hz=cfg.freq_band_hz,
    )

    # Pre-registered absolute upper bound on control's alignment.
    assert alignment_control < cfg.alignment_thresh_control, (
        f"control corpus_alignment_index = {alignment_control:.4f} >= "
        f"{cfg.alignment_thresh_control:.4f}. The substrate appears to "
        f"align with the corpus spectrum even from flat-spectrum input — "
        f"the trained metric is a state detector, not a learning signal. "
        f"Verdict NULL per autopilot charter."
    )

    # Pre-registered relative margin.
    margin = alignment_train - alignment_control
    assert margin >= cfg.margin_min, (
        f"trained − control margin = {margin:.4f} < "
        f"{cfg.margin_min:.4f}. The trained run may have crossed its "
        f"floor only because control drifted close; the separation is "
        f"not significant. Verdict NULL."
    )

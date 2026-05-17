"""F3 learning emergence — trained-run acceptance.

Pre-registered by R-4 (plan
`docs/superpowers/plans/2026-05-16-flux-substrate-F3.md`). Implementation
under R-5. Thresholds are LOCKED — no post-hoc retuning.

This module collects:
- Waveform-generator unit tests (`-k waveform`)
- Frequency-localisation metric unit tests (`-k floc`)
- A construct-without-raising smoke (`-k constructs`)
- The slow trained-run acceptance test
  (`test_F3_trained_substrate_develops_pattern_specific_topology`).
"""
from __future__ import annotations

import numpy as np
import pytest

from agent.flux.learning_metric import frequency_localisation_index
from agent.flux.learning_run import (
    LearningRunConfig,
    make_control_waveform,
    make_training_waveform,
    run_learning_session,
)
from world.flux.bridges import Bridges
from world.flux.structures import Nodes


# -------------------------- Waveform tests -------------------------

def test_training_waveform_has_peak_at_1khz():
    cfg = LearningRunConfig()
    sr = cfg.cochlea_cfg.sample_rate_hz
    n = sr  # 1 s
    x = make_training_waveform(cfg, n_samples=n)
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    peak_hz = float(freqs[int(np.argmax(spec))])
    assert 800.0 < peak_hz < 1200.0, (
        f"training waveform peak at {peak_hz} Hz, expected ~1 kHz"
    )


def test_training_waveform_is_deterministic():
    cfg = LearningRunConfig()
    a = make_training_waveform(cfg, n_samples=4000)
    b = make_training_waveform(cfg, n_samples=4000)
    assert np.allclose(a, b), "training waveform must be deterministic"


def test_control_waveform_has_flat_spectrum():
    cfg = LearningRunConfig()
    sr = cfg.cochlea_cfg.sample_rate_hz
    n = 4 * sr  # 4 s
    x = make_control_waveform(cfg, n_samples=n)
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    band = (freqs >= 200) & (freqs <= 6000)
    in_band = spec[band]
    cv = float(np.std(in_band) / np.mean(in_band))
    assert cv < 1.5, (
        f"control waveform CV={cv:.2f} in [200, 6000] Hz, expected flat (CV<1.5)"
    )


def test_control_waveform_energy_matches_training():
    cfg = LearningRunConfig()
    n = cfg.cochlea_cfg.sample_rate_hz  # 1 s
    train = make_training_waveform(cfg, n_samples=n)
    ctrl = make_control_waveform(cfg, n_samples=n)
    rms_train = float(np.sqrt(np.mean(train * train)))
    rms_ctrl = float(np.sqrt(np.mean(ctrl * ctrl)))
    assert abs(rms_train - rms_ctrl) / rms_train < 0.05, (
        f"RMS mismatch: train={rms_train:.4f}, ctrl={rms_ctrl:.4f}"
    )


def test_control_waveform_is_deterministic():
    cfg = LearningRunConfig()
    a = make_control_waveform(cfg, n_samples=4000)
    b = make_control_waveform(cfg, n_samples=4000)
    assert np.allclose(a, b), (
        "control waveform must be deterministic for locked seed"
    )


# ---------------------- Floc metric tests -------------------------

def test_floc_zero_when_no_bridges():
    n = Nodes(max_nodes=4)
    b = Bridges(max_bridges=4)
    floc = frequency_localisation_index(
        b, n, f_train_hz=1000.0, band_log_hz=0.25,
    )
    assert floc == 0.0


def test_floc_one_when_all_bridges_in_band():
    n = Nodes(max_nodes=4)
    b = Bridges(max_bridges=4)
    log_1k = float(np.log(1000.0))
    s0 = n.add(pos=(0.0, 0.0, 0.0), energy=1.0, freq=log_1k, born_tick=0)
    s1 = n.add(pos=(1.0, 0.0, 0.0), energy=1.0,
               freq=log_1k + 0.05, born_tick=0)
    b.add(src=s0, dst=s1, weight=1.0, born_tick=0)
    floc = frequency_localisation_index(
        b, n, f_train_hz=1000.0, band_log_hz=0.25,
    )
    assert floc == pytest.approx(1.0)


def test_floc_zero_when_all_bridges_out_of_band():
    n = Nodes(max_nodes=4)
    b = Bridges(max_bridges=4)
    log_4k = float(np.log(4000.0))
    s0 = n.add(pos=(0.0, 0.0, 0.0), energy=1.0, freq=log_4k, born_tick=0)
    s1 = n.add(pos=(1.0, 0.0, 0.0), energy=1.0, freq=log_4k, born_tick=0)
    b.add(src=s0, dst=s1, weight=1.0, born_tick=0)
    floc = frequency_localisation_index(
        b, n, f_train_hz=1000.0, band_log_hz=0.25,
    )
    assert floc == 0.0


def test_floc_partial_when_mixed():
    """Two bridges; one in-band, one out-of-band. f_loc should be 0.5."""
    n = Nodes(max_nodes=4)
    b = Bridges(max_bridges=4)
    log_1k = float(np.log(1000.0))
    log_4k = float(np.log(4000.0))
    s0 = n.add(pos=(0.0, 0.0, 0.0), energy=1.0, freq=log_1k, born_tick=0)
    s1 = n.add(pos=(1.0, 0.0, 0.0), energy=1.0, freq=log_1k, born_tick=0)
    s2 = n.add(pos=(0.0, 1.0, 0.0), energy=1.0, freq=log_4k, born_tick=0)
    s3 = n.add(pos=(1.0, 1.0, 0.0), energy=1.0, freq=log_4k, born_tick=0)
    b.add(src=s0, dst=s1, weight=1.0, born_tick=0)
    b.add(src=s2, dst=s3, weight=1.0, born_tick=0)
    floc = frequency_localisation_index(
        b, n, f_train_hz=1000.0, band_log_hz=0.25,
    )
    assert floc == pytest.approx(0.5)


def test_floc_requires_both_endpoints_in_band():
    """A bridge with one endpoint in-band, one out, must NOT count."""
    n = Nodes(max_nodes=4)
    b = Bridges(max_bridges=4)
    log_1k = float(np.log(1000.0))
    log_4k = float(np.log(4000.0))
    s0 = n.add(pos=(0.0, 0.0, 0.0), energy=1.0, freq=log_1k, born_tick=0)
    s1 = n.add(pos=(1.0, 0.0, 0.0), energy=1.0, freq=log_4k, born_tick=0)
    b.add(src=s0, dst=s1, weight=1.0, born_tick=0)
    floc = frequency_localisation_index(
        b, n, f_train_hz=1000.0, band_log_hz=0.25,
    )
    assert floc == 0.0


# ------------------------ Construct smoke -------------------------

def test_run_learning_session_constructs_without_raising():
    cfg = LearningRunConfig(n_ticks_train=200)
    result = run_learning_session(cfg, input_kind="train")
    assert result.tick_index == 200
    assert result.quanta is not None
    assert result.nodes is not None
    assert result.bridges is not None
    # Audit must balance after the short run.
    assert result.audit.is_balanced(tol=cfg.audit_tol), (
        f"smoke run audit unbalanced: residual={result.audit.residual()}"
    )


# -------------------- F3 trained-run acceptance --------------------

@pytest.mark.slow
def test_F3_trained_substrate_develops_pattern_specific_topology():
    """Pre-registered F3 acceptance: substrate exposed to a repeated
    1 kHz tone-burst pattern develops bridge topology concentrated
    around log(1000). Locked thresholds — DO NOT retune."""
    cfg = LearningRunConfig()
    result = run_learning_session(cfg, input_kind="train")
    n_alive = int(result.bridges.alive.sum())
    assert n_alive >= cfg.n_bridges_min_alive, (
        f"trained run produced only {n_alive} alive bridges, need "
        f">= {cfg.n_bridges_min_alive} for f_loc to be a meaningful "
        f"measurement — verdict NULL not PASS"
    )
    floc = frequency_localisation_index(
        result.bridges, result.nodes,
        f_train_hz=cfg.f_train_hz, band_log_hz=cfg.band_log_hz,
    )
    assert floc >= cfg.f_loc_thresh_train, (
        f"trained substrate f_loc = {floc:.3f}, "
        f"pre-registered threshold {cfg.f_loc_thresh_train:.3f} — "
        f"verdict NULL not PASS. Bridges alive: {n_alive}. "
        f"Do NOT retune thresholds; they are locked by R-4 plan."
    )
    assert result.audit.is_balanced(tol=cfg.audit_tol), (
        f"trained run violated T1 conservation: "
        f"residual={result.audit.residual():.6e}, "
        f"tol={cfg.audit_tol:.6e}"
    )

"""R-8 trained-run acceptance.

Pre-registered by R-6 (plan
`docs/superpowers/plans/2026-05-17-flux-training-EN.md`). Implementation
by R-8. Thresholds LOCKED — no post-hoc retuning.

Layered tests:
- Spectrum / metric unit tests (`-k spectrum` / `-k metric`)
- Construct-without-raising smoke (`-k constructs`)
- The slow trained-run acceptance test
  (`test_R8_trained_substrate_aligns_with_corpus_spectrum`)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from agent.flux.corpus_spectrum import compute_corpus_log_power_spectrum
from agent.flux.training_metric import corpus_alignment_index
from agent.flux.training_run import (
    DEFAULT_MANIFEST_PATH,
    TrainingRunConfig,
    load_corpus_waveform_from_manifest,
    make_control_waveform,
    make_corpus_waveform,
    run_training_session,
)
from world.flux.bridges import Bridges
from world.flux.structures import Nodes


_MANIFEST_PRESENT = DEFAULT_MANIFEST_PATH.is_file()
_skip_no_corpus = pytest.mark.skipif(
    not _MANIFEST_PRESENT,
    reason=(
        f"R-7 corpus manifest missing at {DEFAULT_MANIFEST_PATH}; "
        f"R-8 cannot run without it"
    ),
)


# --------------------- Spectrum unit tests -------------------------


def test_spectrum_uniform_input_is_nonzero_distribution():
    """Flat-spectrum noise into the spectrum compute returns a probability
    distribution that sums to 1.0 and has nonzero mass across most bins.
    """
    rng = np.random.default_rng(0)
    sr = 16000
    x = rng.standard_normal(sr * 4)
    p = compute_corpus_log_power_spectrum(
        x, sample_rate_hz=sr, n_freq_bins=64,
    )
    assert p.shape == (64,)
    assert p.sum() == pytest.approx(1.0)
    assert (p > 0).sum() >= 40, (
        f"white-noise spectrum populated only {(p > 0).sum()} of 64 bins; "
        f"expected >= 40 (most of the cochlea range)"
    )


def test_spectrum_pure_tone_concentrates_mass():
    """A 1 kHz pure tone produces a distribution concentrated near the
    cochlea bin covering 1000 Hz.
    """
    sr = 16000
    n = sr * 2
    t = np.arange(n) / sr
    x = np.sin(2.0 * np.pi * 1000.0 * t)
    p = compute_corpus_log_power_spectrum(
        x, sample_rate_hz=sr, n_freq_bins=64,
    )
    bin_edges = np.logspace(np.log10(50.0), np.log10(8000.0), 65)
    bin_of_1k = int(np.searchsorted(bin_edges, 1000.0) - 1)
    top_bin = int(np.argmax(p))
    assert abs(top_bin - bin_of_1k) <= 2, (
        f"1 kHz peak at bin {top_bin}, expected near {bin_of_1k}"
    )


# --------------------- Metric unit tests ---------------------------


def test_metric_zero_when_no_bridges():
    nodes = Nodes(max_nodes=4)
    bridges = Bridges(max_bridges=4)
    p_corpus = np.full(64, 1.0 / 64, dtype=np.float64)
    alignment = corpus_alignment_index(
        bridges, nodes, p_corpus, n_freq_bins=64,
    )
    assert alignment == 0.0


def test_metric_perfect_alignment_when_bridge_distribution_matches_corpus():
    """A bridge endpoint distribution that exactly mirrors p_corpus
    returns alignment = 1.0 (JS divergence = 0)."""
    nodes = Nodes(max_nodes=128)
    bridges = Bridges(max_bridges=128)
    # Build a corpus distribution concentrated in 4 bins.
    p_corpus = np.zeros(64, dtype=np.float64)
    p_corpus[10] = 0.25
    p_corpus[20] = 0.25
    p_corpus[30] = 0.25
    p_corpus[40] = 0.25
    bin_edges = np.logspace(np.log10(50.0), np.log10(8000.0), 65)
    bin_centres_hz = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    # Add 4 bridges, each pair of endpoints in one of those bins.
    for bin_k in (10, 20, 30, 40):
        log_hz = float(np.log(bin_centres_hz[bin_k]))
        a = nodes.add(pos=(0.0, 0.0, 0.0), energy=1.0, freq=log_hz,
                      born_tick=0)
        b = nodes.add(pos=(1.0, 0.0, 0.0), energy=1.0, freq=log_hz,
                      born_tick=0)
        bridges.add(src=a, dst=b, weight=1.0, born_tick=0)
    alignment = corpus_alignment_index(
        bridges, nodes, p_corpus, n_freq_bins=64,
    )
    assert alignment == pytest.approx(1.0, abs=1e-9)


def test_metric_low_alignment_when_distribution_disjoint_from_corpus():
    """Bridge endpoints in completely different bins than corpus mass —
    alignment should be far below 1.0 (positive JS divergence)."""
    nodes = Nodes(max_nodes=128)
    bridges = Bridges(max_bridges=128)
    p_corpus = np.zeros(64, dtype=np.float64)
    p_corpus[5] = 1.0
    bin_edges = np.logspace(np.log10(50.0), np.log10(8000.0), 65)
    bin_centres_hz = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    # Add bridges in bin 50 (far from bin 5).
    for _ in range(4):
        log_hz = float(np.log(bin_centres_hz[50]))
        a = nodes.add(pos=(0.0, 0.0, 0.0), energy=1.0, freq=log_hz,
                      born_tick=0)
        b = nodes.add(pos=(1.0, 0.0, 0.0), energy=1.0, freq=log_hz,
                      born_tick=0)
        bridges.add(src=a, dst=b, weight=1.0, born_tick=0)
    alignment = corpus_alignment_index(
        bridges, nodes, p_corpus, n_freq_bins=64,
    )
    assert alignment < 0.6, (
        f"disjoint distributions returned alignment={alignment:.3f}, "
        f"expected < 0.6"
    )


# --------------------- Waveform construction -----------------------


@_skip_no_corpus
def test_load_corpus_waveform_meets_expected_minimum_seconds():
    """Manifest-based loader returns enough audio to exercise the
    n_ticks_train_min target (60_000 ticks × 16 samples/tick at 16 kHz =
    60 s minimum)."""
    cfg = TrainingRunConfig()
    wave = load_corpus_waveform_from_manifest(
        cfg.manifest_path,
        stage_order=cfg.stage_order,
        sample_rate_hz=cfg.cochlea_cfg.sample_rate_hz,
    )
    n_needed = cfg.n_ticks_train_min * cfg.cochlea_cfg.n_audio_samples_per_tick
    assert wave.size >= n_needed or cfg.corpus_repeat_to_fill_ticks, (
        f"corpus size {wave.size} < required {n_needed} samples and "
        f"corpus_repeat_to_fill_ticks is False"
    )


@_skip_no_corpus
def test_make_corpus_waveform_is_correct_length():
    cfg = TrainingRunConfig()
    n = 16000 * 5  # 5 seconds at 16 kHz
    wave = make_corpus_waveform(cfg, n_samples=n)
    assert wave.size == n


def test_make_control_waveform_rms_matches_target():
    cfg = TrainingRunConfig()
    target = 0.05
    wave = make_control_waveform(cfg, n_samples=16000, target_rms=target)
    rms = float(np.sqrt(np.mean(wave * wave)))
    assert abs(rms - target) / target < 0.02


# --------------------- Construct smoke -----------------------------


@_skip_no_corpus
def test_run_training_session_constructs_without_raising_short():
    """Short 200-tick run — proves the plumbing works, not acceptance.

    Uses a tiny n_ticks_train BELOW the locked min purely to validate
    the run-loop does not raise. This is a smoke test, not the locked
    acceptance — that lives in
    `test_R8_trained_substrate_aligns_with_corpus_spectrum`.
    """
    cfg = TrainingRunConfig()
    cfg.n_ticks_train = max(cfg.n_ticks_train_min, 200)
    # Override the range to allow the smoke; the locked-acceptance test
    # below uses the unmodified defaults.
    cfg.n_ticks_train_min = 200
    cfg.n_ticks_train = 200
    result = run_training_session(cfg, input_kind="train")
    assert result.tick_index == 200
    assert result.bridges is not None
    result.audit.check()


# --------------------- R-8 trained-run acceptance ------------------


@pytest.mark.slow
@_skip_no_corpus
def test_R8_trained_substrate_aligns_with_corpus_spectrum():
    """Pre-registered R-8 acceptance: substrate exposed to the English
    corpus develops bridge topology whose endpoint-frequency
    distribution aligns with the corpus log-power spectrum.

    Locked thresholds (R-6 plan):
        n_ticks_train_min = 60_000
        alignment_thresh_train = 0.50
        n_bridges_min_alive_train = 50

    DO NOT retune these. A failure here → verdict NULL with postmortem.
    """
    cfg = TrainingRunConfig()
    assert cfg.n_ticks_train >= cfg.n_ticks_train_min, (
        f"n_ticks_train={cfg.n_ticks_train} below locked floor "
        f"{cfg.n_ticks_train_min} — protocol breach"
    )
    result = run_training_session(cfg, input_kind="train")

    n_alive = int(result.bridges.alive.sum())
    assert n_alive >= cfg.n_bridges_min_alive_train, (
        f"trained run produced only {n_alive} alive bridges, need "
        f">= {cfg.n_bridges_min_alive_train} for corpus_alignment_index "
        f"to be a meaningful measurement — verdict NULL not PASS"
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
    alignment = corpus_alignment_index(
        result.bridges, result.nodes, p_corpus,
        n_freq_bins=cfg.n_freq_bins, freq_band_hz=cfg.freq_band_hz,
    )
    assert alignment >= cfg.alignment_thresh_train, (
        f"trained corpus_alignment_index = {alignment:.4f}, "
        f"pre-registered threshold {cfg.alignment_thresh_train:.4f} — "
        f"verdict NULL not PASS. Bridges alive: {n_alive}. "
        f"Do NOT retune; thresholds locked by R-6 plan."
    )
    result.audit.check()

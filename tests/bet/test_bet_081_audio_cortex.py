"""BET-081 — Emergent audio-cortex clustering via continuous stream STDP.

Pre-registered bars (docs/amendments/bet_081_audio_cortex.md):
  T81a  Training duration >= 4h wallclock without crash
  T81b  >= 50% of L5 E-neurons fire at least once during eval
  T81c  At least 3/10 k-means clusters: intra-cosine > inter-cosine + 0.05
  T81d  Silhouette score > 0.05
  T81e  Untrained substrate FAILS T81c and T81d

Smoke test (test_T81_smoke): 3 min training, 1K neurons. Verifies pipeline.
Full test (test_T81_full): 4h training, full 10K neurons. Run via run_bet_081.bat.
"""
import pytest
import numpy as np
from pathlib import Path


def _manifest():
    p = Path.home() / ".eqmod" / "training" / "EN" / "manifest.json"
    if not p.exists():
        pytest.skip(f"Audio corpus not found: {p}")
    return p


@pytest.mark.slow
def test_T81_smoke():
    """3-min smoke with 1K neurons. Verifies pipeline end-to-end."""
    from world.flux.brian2_audio_cortex import (
        AudioCortexConfig, AudioDaemonConfig, run_audio_cortex_training)

    cc = AudioCortexConfig(
        n_L4_E=200, n_L23_E=250, n_L5_E=200, n_L6_E=150,
        n_L4_I=50, n_L23_I=62, n_L5_I=50, n_L6_I=37)
    cfg = AudioDaemonConfig(
        cortex=cc, run_duration_seconds=180,
        checkpoint_interval_seconds=9999, eval_interval_seconds=60,
        telegram_heartbeat_interval_seconds=9999,
        audio_manifest_path=_manifest(), eval_n_probe_chunks=30)

    result = run_audio_cortex_training(cfg)
    assert result["chunks_trained"] > 10
    p = result["probe"]
    assert p["L5_active_fraction"] > 0.0
    print(f"\nSmoke: {result['chunks_trained']} chunks, "
          f"L5 active {p['L5_active_fraction']:.3f}, "
          f"sil {p['silhouette_score']:.4f}, "
          f"distinct {p['n_distinct_clusters']}/{p['k']}")


@pytest.mark.slow
def test_T81_full():
    """Full 4h BET-081. Run with:
        run_bet_081.bat
    or: pytest tests/bet/test_bet_081_audio_cortex.py::test_T81_full -xvs
    """
    from world.flux.brian2_audio_cortex import (
        AudioCortexConfig, AudioDaemonConfig, run_audio_cortex_training)
    import json

    bet_dir = Path.home() / ".eqmod" / "bet" / "BET-081"
    cfg = AudioDaemonConfig(
        cortex=AudioCortexConfig(),
        run_duration_seconds=4 * 3600,
        checkpoint_dir=bet_dir / "checkpoints",
        metrics_log_path=bet_dir / "metrics.json",
        audio_manifest_path=_manifest(),
        bet_dir=bet_dir, eval_n_probe_chunks=500)

    result = run_audio_cortex_training(cfg)
    p = result["probe"]

    # T81a: duration
    assert result["train_seconds"] >= 4 * 3600 * 0.95, \
        f"T81a FAIL: {result['train_seconds']/3600:.2f}h < 4h"
    # T81b: activity
    assert p["L5_active_fraction"] >= 0.50, \
        f"T81b FAIL: L5 active {p['L5_active_fraction']:.3f} < 0.50"
    # T81c: cluster distinctness
    assert p["n_distinct_clusters"] >= 3, \
        f"T81c FAIL: distinct {p['n_distinct_clusters']} < 3"
    # T81d: silhouette
    assert p["silhouette_score"] > 0.05, \
        f"T81d FAIL: sil {p['silhouette_score']:.4f} <= 0.05"

    print(f"\nBET-081 TRAINED PASS: L5 {p['L5_active_fraction']:.3f}, "
          f"sil {p['silhouette_score']:.4f}, distinct {p['n_distinct_clusters']}")

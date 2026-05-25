"""BET-081 launcher.

Run via run_bet_081.bat (sets up MSVC env for Cython backend).
Or directly: BRIAN2_BACKEND=numpy python -m world.flux.run_bet_081
"""
from pathlib import Path
from world.flux.brian2_audio_cortex import (
    AudioCortexConfig, AudioDaemonConfig, run_audio_cortex_training)

bet_dir = Path.home() / ".eqmod" / "bet" / "BET-081"

cfg = AudioDaemonConfig(
    cortex=AudioCortexConfig(),  # full 10K
    run_duration_seconds=4 * 3600,
    checkpoint_dir=bet_dir / "checkpoints",
    metrics_log_path=bet_dir / "metrics.json",
    notify_config_path=Path.home() / ".eqmod" / "autopilot" / "notify_config.json",
    audio_manifest_path=Path.home() / ".eqmod" / "training" / "EN" / "manifest.json",
    bet_dir=bet_dir,
    eval_n_probe_chunks=500,
)

if __name__ == "__main__":
    result = run_audio_cortex_training(cfg)
    p = result.get("probe", {})
    print(f"\n{'='*60}")
    print(f"BET-081 RESULT:")
    print(f"  Training: {result['chunks_trained']} chunks in {result['train_seconds']/3600:.2f}h")
    print(f"  L5 active: {p.get('L5_active_fraction', '?')}")
    print(f"  Silhouette: {p.get('silhouette_score', '?')}")
    print(f"  Distinct clusters: {p.get('n_distinct_clusters', '?')}/{p.get('k', '?')}")
    print(f"{'='*60}")

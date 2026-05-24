"""BET-080 — T66 Brian2 cortical 12h continuous training.

Phase B: extend BET-079 (4h PASS) to 12h. Daemon now supports resume
from latest checkpoint, so a crash mid-run does not lose progress.

T66 bars (LOCKED, all must pass):
  T66a — Total elapsed (cumulative across resumes if any) ≥ 11h
  T66b — ≥ 10 hourly checkpoints exist on disk
  T66c — Final L5 prototype acc > 0.7 (substrate still discriminating)
  T66d — Positive trajectory: final L5 acc ≥ pre-eval L5 acc - 0.05
         (no significant degradation from baseline)
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import pytest

warnings.filterwarnings('ignore')

RUN_DURATION_SECONDS = 12 * 3600.0  # 12 hours
T66A_MIN_ELAPSED = 11 * 3600.0
T66B_MIN_CHECKPOINTS = 10
T66C_FINAL_L5_ACC_MIN = 0.7
T66D_MAX_DEGRADATION = 0.05

OUT_DIR = Path.home() / ".eqmod/bet/BET-080"
CKPT_DIR = OUT_DIR / "checkpoints"
METRICS_LOG = OUT_DIR / "metrics.json"
NOTIFY_CONFIG = Path.home() / ".eqmod/autopilot/notify_config.json"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


@pytest.fixture(scope="module")
def daemon_result():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CKPT_DIR.mkdir(parents=True, exist_ok=True)

    from world.flux.brian2_cortical_daemon import DaemonConfig, run_long_training

    cfg = DaemonConfig(
        run_duration_seconds=RUN_DURATION_SECONDS,
        chunk_duration_ms=100.0,
        checkpoint_interval_seconds=3600.0,
        eval_interval_seconds=3600.0,
        telegram_heartbeat_interval_seconds=3600.0,
        checkpoint_dir=CKPT_DIR,
        metrics_log_path=METRICS_LOG,
        notify_config_path=NOTIFY_CONFIG if NOTIFY_CONFIG.exists() else None,
        audio_manifest_path=MANIFEST_PATH,
        eval_n_chunks_per_class=20,
    )

    return run_long_training(cfg)


def _verdict(s, n_checkpoints, n_metrics_entries, baseline_l5_acc):
    elapsed = s["elapsed_seconds"]
    final_l5 = s["final_eval"]["L5_acc"]
    ran_enough = elapsed >= T66A_MIN_ELAPSED
    enough_ckpts = n_checkpoints >= T66B_MIN_CHECKPOINTS
    final_ok = final_l5 > T66C_FINAL_L5_ACC_MIN
    not_degraded = final_l5 >= (baseline_l5_acc - T66D_MAX_DEGRADATION)
    return {
        "elapsed_seconds": elapsed,
        "chunks_trained": s["chunks_trained"],
        "pre_eval": s["pre_eval"],
        "final_eval": s["final_eval"],
        "n_checkpoints": n_checkpoints,
        "n_metrics_entries": n_metrics_entries,
        "baseline_l5_acc": baseline_l5_acc,
        "T66a_duration_ok": ran_enough,
        "T66b_checkpoints_ok": enough_ckpts,
        "T66c_final_acc_ok": final_ok,
        "T66d_no_degradation_ok": not_degraded,
        "T66_pass": ran_enough and enough_ckpts and final_ok and not_degraded,
    }


def test_T66(daemon_result):
    ckpt_files = list(CKPT_DIR.glob("checkpoint_h*.pkl"))
    metrics = json.loads(METRICS_LOG.read_text()) if METRICS_LOG.exists() else []
    baseline_l5 = daemon_result["pre_eval"]["L5_acc"]
    m = _verdict(daemon_result, len(ckpt_files), len(metrics), baseline_l5)

    if not m["T66_pass"]:
        pytest.fail(
            f"BET-080 NULL T66 12h continuous.\n"
            f"  elapsed: {m['elapsed_seconds']/3600:.2f}h (need >= {T66A_MIN_ELAPSED/3600:.1f}h)\n"
            f"  chunks trained: {m['chunks_trained']}\n"
            f"  checkpoints: {m['n_checkpoints']} (need >= {T66B_MIN_CHECKPOINTS})\n"
            f"  pre  L5 acc: {m['pre_eval']['L5_acc']:.3f}\n"
            f"  final L5 acc: {m['final_eval']['L5_acc']:.3f} "
            f"(need > {T66C_FINAL_L5_ACC_MIN}; "
            f"need >= {m['baseline_l5_acc'] - T66D_MAX_DEGRADATION:.3f} for no-degradation)\n"
            f"  pre  L6 KL: {m['pre_eval']['L6_kl']:.3e}\n"
            f"  final L6 KL: {m['final_eval']['L6_kl']:.3e}\n"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(daemon_result):
    yield
    ckpt_files = list(CKPT_DIR.glob("checkpoint_h*.pkl"))
    metrics = json.loads(METRICS_LOG.read_text()) if METRICS_LOG.exists() else []
    baseline_l5 = daemon_result["pre_eval"]["L5_acc"]
    m = _verdict(daemon_result, len(ckpt_files), len(metrics), baseline_l5)
    verdict = "passed" if m["T66_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-080",
        "verdict": verdict,
        "hypothesis": "T66 Brian2 cortical 25K, 12h continuous (resume-capable). Bars: >=11h elapsed, >=10 ckpts, final L5 acc > 0.7, final L5 >= pre L5 - 0.05.",
        "thresholds": {
            "T66a_min_elapsed_h": T66A_MIN_ELAPSED / 3600,
            "T66b_min_checkpoints": T66B_MIN_CHECKPOINTS,
            "T66c_final_acc_min": T66C_FINAL_L5_ACC_MIN,
            "T66d_max_degradation": T66D_MAX_DEGRADATION,
        },
        "measurements": m,
        "checkpoint_files": [str(p) for p in ckpt_files],
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

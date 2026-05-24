"""BET-079 — T65 Brian2 cortical 4h continuous training.

Phase B Validierung der Long-Training-Daemon-Infrastruktur. Cortical
25K substrate (BET-077c-balanced) wird 4h continuous auf gemischtem
EN/WN audio trainiert. Stündliche checkpoints + Telegram heartbeats.

T65 bars (LOCKED, all must pass):
  T65a — Daemon läuft ≥ 3.5h ohne crash
  T65b — Mindestens 3 checkpoints geschrieben
  T65c — Final L5 prototype acc > 0.7 (Substrate diskriminiert noch)
  T65d — Metrics-Log enthält pre_eval + mind. 3 hourly_eval + final_eval
"""
from __future__ import annotations

import json
import shutil
import time
import warnings
from pathlib import Path

import pytest

warnings.filterwarnings('ignore')

RUN_DURATION_SECONDS = 4 * 3600.0  # 4 hours
T65A_MIN_ELAPSED = 3.5 * 3600.0
T65B_MIN_CHECKPOINTS = 3
T65C_FINAL_L5_ACC_MIN = 0.7
T65D_MIN_METRICS_ENTRIES = 5  # pre + 3 hourly + final

OUT_DIR = Path.home() / ".eqmod/bet/BET-079"
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


def _verdict(s, n_checkpoints, n_metrics_entries):
    ran_enough = s["elapsed_seconds"] >= T65A_MIN_ELAPSED
    enough_ckpts = n_checkpoints >= T65B_MIN_CHECKPOINTS
    final_ok = s["final_eval"]["L5_acc"] > T65C_FINAL_L5_ACC_MIN
    enough_metrics = n_metrics_entries >= T65D_MIN_METRICS_ENTRIES
    return {
        "elapsed_seconds": s["elapsed_seconds"],
        "chunks_trained": s["chunks_trained"],
        "pre_eval": s["pre_eval"],
        "final_eval": s["final_eval"],
        "n_checkpoints": n_checkpoints,
        "n_metrics_entries": n_metrics_entries,
        "T65a_duration_ok": ran_enough,
        "T65b_checkpoints_ok": enough_ckpts,
        "T65c_final_acc_ok": final_ok,
        "T65d_metrics_log_ok": enough_metrics,
        "T65_pass": ran_enough and enough_ckpts and final_ok and enough_metrics,
    }


def test_T65(daemon_result):
    ckpt_files = list(CKPT_DIR.glob("checkpoint_h*.pkl"))
    metrics = json.loads(METRICS_LOG.read_text()) if METRICS_LOG.exists() else []
    m = _verdict(daemon_result, len(ckpt_files), len(metrics))

    if not m["T65_pass"]:
        pytest.fail(
            f"BET-079 NULL T65 long-training daemon.\n"
            f"  elapsed: {m['elapsed_seconds']/3600:.2f}h (need >= {T65A_MIN_ELAPSED/3600:.1f}h)\n"
            f"  chunks trained: {m['chunks_trained']}\n"
            f"  checkpoints: {m['n_checkpoints']} (need >= {T65B_MIN_CHECKPOINTS})\n"
            f"  metrics entries: {m['n_metrics_entries']} (need >= {T65D_MIN_METRICS_ENTRIES})\n"
            f"  pre  L5 acc: {m['pre_eval']['L5_acc']:.3f}, L6 KL: {m['pre_eval']['L6_kl']:.3e}\n"
            f"  final L5 acc: {m['final_eval']['L5_acc']:.3f} "
            f"(need > {T65C_FINAL_L5_ACC_MIN}), L6 KL: {m['final_eval']['L6_kl']:.3e}\n"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(daemon_result):
    yield
    ckpt_files = list(CKPT_DIR.glob("checkpoint_h*.pkl"))
    metrics = json.loads(METRICS_LOG.read_text()) if METRICS_LOG.exists() else []
    m = _verdict(daemon_result, len(ckpt_files), len(metrics))
    verdict = "passed" if m["T65_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-079",
        "verdict": verdict,
        "hypothesis": "T65 Brian2 cortical 25K, 4h continuous training, hourly checkpoint+eval+telegram. Bars: ran >=3.5h, >=3 ckpts, final L5 acc>0.7, >=5 metrics entries.",
        "thresholds": {
            "T65a_min_elapsed_h": T65A_MIN_ELAPSED / 3600,
            "T65b_min_checkpoints": T65B_MIN_CHECKPOINTS,
            "T65c_final_acc_min": T65C_FINAL_L5_ACC_MIN,
            "T65d_min_metrics_entries": T65D_MIN_METRICS_ENTRIES,
        },
        "measurements": m,
        "checkpoint_files": [str(p) for p in ckpt_files],
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

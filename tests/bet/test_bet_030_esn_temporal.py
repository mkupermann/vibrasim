"""BET-030 — Echo State Network temporal substrate tests.

After honest AI-researcher review of BET-028: SOM+replay is non-temporal
(bag-of-chunks). Substantive AI claim "lernt temporal" requires a
substrate with temporal dynamics. ESN (Jaeger 2001) has temporal
dynamics by construction.

Pre-registered tests (NEW class, not retrocompatible with T0-T17):

  T18 Temporal-order sensitivity:
    Train ESN on EN-chunks in forward time order.
    Train fresh ESN on EN-chunks in reverse time order.
    Compare final reservoir states.
    Bar: ||u_fwd - u_rev|| / max(||u_fwd||, ||u_rev||) > 0.1
    (same content, different order → measurably different state)

    Negative control: SOM cell weights should NOT depend on order
    (cell-weights converge to running mean, permutation-invariant).
    Predict: SOM-fwd ≈ SOM-rev with ratio < 0.05.

  T19 Temporal prediction with linear readout:
    Train ESN on EN. Collect (state_t, features_t+1) pairs.
    Fit linear W_out via pseudoinverse least-squares.
    On held-out: MSE(ESN prediction) < MSE(persistence baseline).
    Bar: MSE_ESN / MSE_persistence < 0.9 (ESN beats "predict last")
    Persistence baseline: predict features_t+1 = features_t.

If T18 + T19 PASS: ESN is the first substrate in this bet programme
with demonstrable temporal learning. If NULL: even reservoir computing
doesn't learn meaningful temporal structure on the R-7 corpus at
this scale.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.reservoir import (
    ReservoirConfig, initialise as esn_init, run as esn_run,
)
from world.flux.som_replay import (
    SOMReplayConfig, initialise as som_init, run as som_run,
)
from world.flux.cognitive_map import encode_sensor

N_TICKS = 5_000  # Smaller scale — ESN compute is heavy (1000x1000 matvec per tick)
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
TARGET_RMS = 0.25

T18_RATIO_MIN = 0.1
T18_SOM_RATIO_MAX = 0.05  # negative control bar
T19_RATIO_MAX = 0.9

OUT_DIR = Path.home() / ".eqmod/bet/BET-030"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _reverse_chunks_in_time(audio, chunk_size):
    """Reverse the ORDER of chunks (not samples within chunks)."""
    n_chunks = audio.size // chunk_size
    out = np.empty(n_chunks * chunk_size, dtype=audio.dtype)
    for k in range(n_chunks):
        out[k * chunk_size:(k + 1) * chunk_size] = (
            audio[(n_chunks - 1 - k) * chunk_size:(n_chunks - k) * chunk_size]
        )
    return out


def _collect_state_features(state_history, audio, cfg):
    """Build (state_t, features_t+1) pairs for readout training."""
    n = state_history.shape[0] - 1  # last tick has no t+1
    features = np.zeros((state_history.shape[0], cfg.n_features), dtype=np.float64)
    for k in range(state_history.shape[0]):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size > 0:
            features[k] = encode_sensor(chunk, cfg)
    X = state_history[:n]
    Y = features[1:n + 1]
    return X, Y, features


def _fit_readout(X, Y, ridge=1e-4):
    """Ridge regression: W_out = (X^T X + ridge I)^-1 X^T Y."""
    XtX = X.T @ X
    XtX += ridge * np.eye(XtX.shape[0])
    XtY = X.T @ Y
    W_out = np.linalg.solve(XtX, XtY)
    return W_out


def _mse(pred, true):
    return float(np.mean((pred - true) ** 2))


@pytest.fixture(scope="module")
def substrates():
    cfg = ReservoirConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if 2 * n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)
    eng_held = full[n_audio:2 * n_audio].astype(np.float64)
    eng_reverse = _reverse_chunks_in_time(eng_train, SAMPLES_PER_TICK)

    # --- T18: temporal order sensitivity ---
    state_fwd = esn_run(cfg, N_TICKS, eng_train)
    state_rev = esn_run(cfg, N_TICKS, eng_reverse)
    diff = float(np.linalg.norm(state_fwd["u"] - state_rev["u"]))
    norm_fwd = float(np.linalg.norm(state_fwd["u"]))
    norm_rev = float(np.linalg.norm(state_rev["u"]))
    t18_ratio = diff / max(norm_fwd, norm_rev, 1e-9)

    # SOM negative control
    som_cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    som_fwd = som_run(som_cfg, N_TICKS, eng_train)
    som_rev = som_run(som_cfg, N_TICKS, eng_reverse)
    som_diff = float(np.linalg.norm(som_fwd["w"].ravel() - som_rev["w"].ravel()))
    som_norm = float(np.linalg.norm(som_fwd["w"].ravel())) + float(np.linalg.norm(som_rev["w"].ravel()))
    t18_som_ratio = 2 * som_diff / max(som_norm, 1e-9)

    # --- T19: temporal prediction ---
    # Re-run on EN with state_history capture for readout training
    state_history_run = esn_run(cfg, N_TICKS, eng_train, return_state_history=True)
    history = state_history_run["state_history_recent"]
    X_train, Y_train, _ = _collect_state_features(history, eng_train, cfg)
    W_out = _fit_readout(X_train, Y_train)

    # Test on held-out data
    state_held = esn_run(cfg, N_TICKS, eng_held, return_state_history=True)
    held_history = state_held["state_history_recent"]
    X_held, Y_held, all_features = _collect_state_features(held_history, eng_held, cfg)
    Y_pred = X_held @ W_out
    mse_esn = _mse(Y_pred, Y_held)

    # Persistence baseline: predict features_t+1 = features_t
    feat_persistence = all_features[:-1]
    Y_persistence_pred = feat_persistence
    mse_persistence = _mse(Y_persistence_pred, Y_held)

    # Constant-mean baseline (informational)
    mean_feature = Y_train.mean(axis=0)
    Y_mean_pred = np.broadcast_to(mean_feature, Y_held.shape)
    mse_mean = _mse(Y_mean_pred, Y_held)

    t19_ratio = mse_esn / max(mse_persistence, 1e-12)

    return dict(
        cfg=cfg, n_ticks=N_TICKS,
        t18_ratio=t18_ratio, t18_som_ratio=t18_som_ratio,
        norm_fwd=norm_fwd, norm_rev=norm_rev,
        mse_esn=mse_esn, mse_persistence=mse_persistence, mse_mean=mse_mean,
        t19_ratio=t19_ratio,
    )


def _verdict(s):
    t18_pass = s["t18_ratio"] > T18_RATIO_MIN
    t18_neg_ok = s["t18_som_ratio"] < T18_SOM_RATIO_MAX
    t19_pass = s["t19_ratio"] < T19_RATIO_MAX
    return {
        "T18_ratio": s["t18_ratio"], "T18_ratio_min": T18_RATIO_MIN, "T18_pass": t18_pass,
        "T18_som_ratio": s["t18_som_ratio"], "T18_som_max": T18_SOM_RATIO_MAX,
        "T18_neg_control_ok": t18_neg_ok,
        "T18_overall_pass": t18_pass and t18_neg_ok,
        "T19_mse_esn": s["mse_esn"], "T19_mse_persistence": s["mse_persistence"],
        "T19_mse_mean_baseline": s["mse_mean"], "T19_ratio_esn_over_persist": s["t19_ratio"],
        "T19_ratio_max": T19_RATIO_MAX, "T19_pass": t19_pass,
        "T18_T19_pass": (t18_pass and t18_neg_ok) and t19_pass,
        "n_ticks": s["n_ticks"],
    }


def test_T18_T19(substrates):
    m = _verdict(substrates)
    if not m["T18_T19_pass"]:
        pytest.fail(
            f"BET-030 NULL on temporal tests.\n"
            f"  T18 ESN ratio (fwd vs rev): {m['T18_ratio']:.4f} (need > {T18_RATIO_MIN}) "
            f"pass={m['T18_pass']}\n"
            f"  T18 SOM neg control: {m['T18_som_ratio']:.4f} (need < {T18_SOM_RATIO_MAX}) "
            f"pass={m['T18_neg_control_ok']}\n"
            f"  T19 MSE ESN={m['T19_mse_esn']:.6f}, persistence={m['T19_mse_persistence']:.6f}, "
            f"ratio={m['T19_ratio_esn_over_persist']:.4f} (need < {T19_RATIO_MAX}) "
            f"pass={m['T19_pass']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T18_T19_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-030",
        "verdict": verdict,
        "hypothesis": "Echo State Network (Jaeger 2001) tested on T18 (temporal-order sensitivity) + T19 (temporal next-step prediction beating persistence baseline). First temporal-substrate test in bet programme.",
        "thresholds": {
            "T18_esn_ratio_min": T18_RATIO_MIN,
            "T18_som_neg_control_max": T18_SOM_RATIO_MAX,
            "T19_ratio_max": T19_RATIO_MAX,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

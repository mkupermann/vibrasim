"""BET-031 — ESN at coarser time granularity (samples_per_tick=160 = 10ms).

BET-030 NULL: at samples_per_tick=16 (1ms), audio features were too
smooth for ESN to beat persistence baseline (3.5x WORSE in MSE).

At 10x coarser granularity, features change more between consecutive
chunks. Persistence baseline weakens. Reservoir's temporal modeling
gets a fair chance to demonstrate prediction advantage.

Same T18/T19 bars as BET-030 (locked):
  T18 ESN ratio > 0.10 AND SOM neg-control < 0.05
  T19 MSE(ESN) / MSE(persistence) < 0.9
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

N_TICKS = 5_000
SAMPLES_PER_TICK = 160   # 10ms at 16kHz (10x BET-030)
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
TARGET_RMS = 0.25

T18_RATIO_MIN = 0.1
T18_SOM_RATIO_MAX = 0.05
T19_RATIO_MAX = 0.9

OUT_DIR = Path.home() / ".eqmod/bet/BET-031"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _reverse_chunks(audio, chunk_size):
    n_chunks = audio.size // chunk_size
    out = np.empty(n_chunks * chunk_size, dtype=audio.dtype)
    for k in range(n_chunks):
        out[k * chunk_size:(k + 1) * chunk_size] = (
            audio[(n_chunks - 1 - k) * chunk_size:(n_chunks - k) * chunk_size]
        )
    return out


def _collect(history, audio, cfg):
    n_history = history.shape[0]
    features = np.zeros((n_history, cfg.n_features), dtype=np.float64)
    for k in range(n_history):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size > 0:
            features[k] = encode_sensor(chunk, cfg)
    X = history[:n_history - 1]
    Y = features[1:n_history]
    return X, Y, features


def _fit(X, Y, ridge=1e-4):
    XtX = X.T @ X + ridge * np.eye(X.shape[1])
    return np.linalg.solve(XtX, X.T @ Y)


def _mse(a, b):
    return float(np.mean((a - b) ** 2))


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
    eng_rev = _reverse_chunks(eng_train, SAMPLES_PER_TICK)

    state_fwd = esn_run(cfg, N_TICKS, eng_train)
    state_rev = esn_run(cfg, N_TICKS, eng_rev)
    diff = float(np.linalg.norm(state_fwd["u"] - state_rev["u"]))
    norm_fwd = float(np.linalg.norm(state_fwd["u"]))
    norm_rev = float(np.linalg.norm(state_rev["u"]))
    t18_ratio = diff / max(norm_fwd, norm_rev, 1e-9)

    som_cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    som_fwd = som_run(som_cfg, N_TICKS, eng_train)
    som_rev = som_run(som_cfg, N_TICKS, eng_rev)
    som_diff = float(np.linalg.norm(som_fwd["w"].ravel() - som_rev["w"].ravel()))
    som_norm = float(np.linalg.norm(som_fwd["w"].ravel())) + float(np.linalg.norm(som_rev["w"].ravel()))
    t18_som = 2 * som_diff / max(som_norm, 1e-9)

    state_history = esn_run(cfg, N_TICKS, eng_train, return_state_history=True)
    history = state_history["state_history_recent"]
    X_train, Y_train, _ = _collect(history, eng_train, cfg)
    W_out = _fit(X_train, Y_train)

    state_held = esn_run(cfg, N_TICKS, eng_held, return_state_history=True)
    held_history = state_held["state_history_recent"]
    X_held, Y_held, all_features = _collect(held_history, eng_held, cfg)
    Y_pred = X_held @ W_out
    mse_esn = _mse(Y_pred, Y_held)
    mse_persistence = _mse(all_features[:-1], Y_held)
    mse_mean = _mse(np.broadcast_to(Y_train.mean(axis=0), Y_held.shape), Y_held)
    t19_ratio = mse_esn / max(mse_persistence, 1e-12)

    return dict(
        t18_ratio=t18_ratio, t18_som_ratio=t18_som,
        mse_esn=mse_esn, mse_persistence=mse_persistence, mse_mean=mse_mean,
        t19_ratio=t19_ratio,
    )


def _verdict(s):
    t18_pass = s["t18_ratio"] > T18_RATIO_MIN
    t18_neg = s["t18_som_ratio"] < T18_SOM_RATIO_MAX
    t19_pass = s["t19_ratio"] < T19_RATIO_MAX
    return {
        "T18_ratio": s["t18_ratio"], "T18_pass": t18_pass,
        "T18_som_ratio": s["t18_som_ratio"], "T18_neg_ok": t18_neg,
        "T18_overall_pass": t18_pass and t18_neg,
        "T19_mse_esn": s["mse_esn"], "T19_mse_persistence": s["mse_persistence"],
        "T19_mse_mean": s["mse_mean"], "T19_ratio": s["t19_ratio"], "T19_pass": t19_pass,
        "all_pass": (t18_pass and t18_neg) and t19_pass,
    }


def test_T18_T19_coarse(substrates):
    m = _verdict(substrates)
    if not m["all_pass"]:
        pytest.fail(
            f"BET-031 NULL coarse-granularity ESN.\n"
            f"  T18 ESN={m['T18_ratio']:.4f} SOM_neg={m['T18_som_ratio']:.4f} "
            f"overall_pass={m['T18_overall_pass']}\n"
            f"  T19 MSE_ESN={m['T19_mse_esn']:.6f} MSE_persist={m['T19_mse_persistence']:.6f} "
            f"ratio={m['T19_ratio']:.4f} pass={m['T19_pass']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["all_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-031",
        "verdict": verdict,
        "hypothesis": "ESN at 10ms granularity. BET-030 NULL because 1ms-features too smooth for ESN to beat persistence. 10ms gives features room to vary between chunks.",
        "thresholds": {
            "T18_ratio_min": T18_RATIO_MIN, "T18_som_max": T18_SOM_RATIO_MAX,
            "T19_ratio_max": T19_RATIO_MAX,
        },
        "measurements": {
            "samples_per_tick": SAMPLES_PER_TICK,
            **m,
        },
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

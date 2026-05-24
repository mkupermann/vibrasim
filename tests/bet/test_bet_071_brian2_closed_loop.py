"""BET-071 — T55 Brian2 closed-loop sensorimotor (Stufe 6 Phase A).

Brian2 hierarchical substrate + motor neurons. Motor activity selects
next input chunk. Active inference minimum.

T55 bars (LOCKED, both must pass):
  T55a — Motor selectivity: at least one motor neuron's firing differs
         by > 1.5x between classes (motor[i] fires class-dependently).
  T55b — Closed-loop stability deviates from chance: |dwell - 0.5| > 0.15
         OR stability > 0.6 (substrate's behavior is non-random — it
         either settles on one class or follows reproducible pattern).
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pytest

warnings.filterwarnings('ignore')

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.brian2_closed_loop import Brian2ClosedLoopConfig, train_and_run_closed_loop

N_TRAIN_PER_CLASS = 80
N_CLOSED_LOOP_TICKS = 100
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T55_MOTOR_SELECTIVITY_MIN = 1.5
T55_DWELL_DEVIATION_MIN = 0.15
T55_STABILITY_MIN = 0.6

OUT_DIR = Path.home() / ".eqmod/bet/BET-071"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


@pytest.fixture(scope="module")
def substrates():
    class _Cfg:
        n_features = N_FEATURES
        fft_bands = FFT_BANDS
        samples_per_tick = SAMPLES_PER_TICK
    encoder_cfg = _Cfg()

    n_train = N_TRAIN_PER_CLASS * SAMPLES_PER_TICK
    n_test = 50 * SAMPLES_PER_TICK  # test chunk pool

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_train + n_test > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_train].astype(np.float64)
    eng_test = full[n_train:n_train + n_test].astype(np.float64)
    wn_train = _make_wn(n_train, TARGET_RMS, WN_SEED)
    wn_test = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)

    def chunks(audio, n):
        return [audio[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK] for k in range(n)]

    train_dict = {0: chunks(eng_train, N_TRAIN_PER_CLASS),
                  1: chunks(wn_train, N_TRAIN_PER_CLASS)}
    test_dict = {0: chunks(eng_test, 50), 1: chunks(wn_test, 50)}

    cfg = Brian2ClosedLoopConfig(chunk_duration_ms=100.0)
    result = train_and_run_closed_loop(
        train_dict, test_dict, encoder_cfg,
        N_TRAIN_PER_CLASS, N_CLOSED_LOOP_TICKS, cfg,
    )

    motor_class_means = result["motor_class_means"]
    # Compute motor selectivity: max ratio of (class-A firing / class-B firing)
    max_ratio = 0.0
    if 0 in motor_class_means and 1 in motor_class_means:
        m0 = motor_class_means[0]
        m1 = motor_class_means[1]
        for i in range(len(m0)):
            r1 = (m0[i] + 0.1) / (m1[i] + 0.1)
            r2 = (m1[i] + 0.1) / (m0[i] + 0.1)
            max_ratio = max(max_ratio, r1, r2)

    dwell_0 = result["dwell"].get(0, 0)
    dwell_deviation = abs(dwell_0 - 0.5)
    stability = result["stability"]

    return dict(
        motor_selectivity_max_ratio=float(max_ratio),
        motor_class0_means=motor_class_means.get(0, np.zeros(2)).tolist(),
        motor_class1_means=motor_class_means.get(1, np.zeros(2)).tolist(),
        closed_loop_dwell_class_0=dwell_0,
        closed_loop_dwell_deviation=dwell_deviation,
        closed_loop_stability=stability,
        n_closed_loop_ticks=N_CLOSED_LOOP_TICKS,
        total_L2_spikes=result["total_L2_spikes"],
        total_motor_spikes=result["total_motor_spikes"],
        final_W_L2_Motor=result["final_W_L2_Motor_mean"],
    )


def _verdict(s):
    selectivity_ok = s["motor_selectivity_max_ratio"] > T55_MOTOR_SELECTIVITY_MIN
    nonrandom_ok = (s["closed_loop_dwell_deviation"] > T55_DWELL_DEVIATION_MIN
                    or s["closed_loop_stability"] > T55_STABILITY_MIN)
    return {**s, "T55a_selectivity_ok": selectivity_ok,
            "T55b_nonrandom_ok": nonrandom_ok,
            "T55_pass": selectivity_ok and nonrandom_ok}


def test_T55(substrates):
    m = _verdict(substrates)
    if not m["T55_pass"]:
        pytest.fail(
            f"BET-071 NULL T55 closed-loop sensorimotor.\n"
            f"  motor selectivity (max ratio): {m['motor_selectivity_max_ratio']:.4f} "
            f"(need > {T55_MOTOR_SELECTIVITY_MIN})\n"
            f"  motor class-0 means: {m['motor_class0_means']}\n"
            f"  motor class-1 means: {m['motor_class1_means']}\n"
            f"  closed-loop dwell class-0: {m['closed_loop_dwell_class_0']:.4f} "
            f"(deviation {m['closed_loop_dwell_deviation']:.4f} need > {T55_DWELL_DEVIATION_MIN})\n"
            f"  closed-loop stability: {m['closed_loop_stability']:.4f} "
            f"(need > {T55_STABILITY_MIN} OR dwell-dev > {T55_DWELL_DEVIATION_MIN})\n"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T55_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-071",
        "verdict": verdict,
        "hypothesis": "T55 Brian2 closed-loop sensorimotor. Stufe 6 Phase A. Motor neurons in L2; motor activity selects next chunk. Bars: motor selectivity > 1.5x AND |dwell-0.5| > 0.15 OR stability > 0.6.",
        "thresholds": {
            "T55_motor_selectivity_min": T55_MOTOR_SELECTIVITY_MIN,
            "T55_dwell_deviation_min": T55_DWELL_DEVIATION_MIN,
            "T55_stability_min": T55_STABILITY_MIN,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

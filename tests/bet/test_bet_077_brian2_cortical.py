"""BET-077 — T61 Brian2 cortical-density 4-layer substrate.

Phase B basis test. 25K neurons in 4 cortical layers (L4, L2/3, L5, L6)
with E:I 4:1, recurrent E→E STDP, feedforward + feedback connectivity.

T61 bars (LOCKED):
  T61a — substrate builds + runs without OOM/crash
  T61b — L5 prototype-classification accuracy on EN-vs-WN > 0.75
         (matches Phase A binary discrimination at cortical-density)
  T61c — Hierarchical KL amplification > 5×:
         max(KL_L4, KL_L23, KL_L5, KL_L6) / KL_L4 > 5
         (deeper layers more class-selective than input layer)
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pytest

warnings.filterwarnings('ignore')

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.brian2_cortical import Brian2CorticalConfig, train_and_collect_layer_patterns
from world.flux.harder_bar_metrics import hist_kl_symmetric

N_TRAIN_PER_CLASS = 80
N_TEST_PER_CLASS = 25
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T61B_ACC_MIN = 0.75
T61C_KL_AMPL_MIN = 5.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-077"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _proto_accuracy(patterns_class0, patterns_class1):
    proto0 = patterns_class0.mean(axis=0)
    proto1 = patterns_class1.mean(axis=0)
    correct, total = 0, 0
    for p in patterns_class0:
        d0 = float(np.linalg.norm(p - proto0))
        d1 = float(np.linalg.norm(p - proto1))
        if d0 < d1: correct += 1
        total += 1
    for p in patterns_class1:
        d0 = float(np.linalg.norm(p - proto0))
        d1 = float(np.linalg.norm(p - proto1))
        if d1 < d0: correct += 1
        total += 1
    return correct / max(total, 1)


@pytest.fixture(scope="module")
def substrates():
    class _Cfg:
        n_features = N_FEATURES
        fft_bands = FFT_BANDS
        samples_per_tick = SAMPLES_PER_TICK
    encoder_cfg = _Cfg()

    n_train = N_TRAIN_PER_CLASS * SAMPLES_PER_TICK
    n_test = N_TEST_PER_CLASS * SAMPLES_PER_TICK

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
    test_dict = {0: chunks(eng_test, N_TEST_PER_CLASS),
                 1: chunks(wn_test, N_TEST_PER_CLASS)}

    cfg = Brian2CorticalConfig(chunk_duration_ms=100.0)
    result = train_and_collect_layer_patterns(
        train_dict, test_dict, encoder_cfg,
        N_TRAIN_PER_CLASS, N_TEST_PER_CLASS, cfg,
    )

    # Accuracies per layer
    L4_acc  = _proto_accuracy(result["L4_patterns"][0],  result["L4_patterns"][1])
    L23_acc = _proto_accuracy(result["L23_patterns"][0], result["L23_patterns"][1])
    L5_acc  = _proto_accuracy(result["L5_patterns"][0],  result["L5_patterns"][1])
    L6_acc  = _proto_accuracy(result["L6_patterns"][0],  result["L6_patterns"][1])

    # KL per layer
    L4_kl  = hist_kl_symmetric(result["L4_patterns"][0].astype(np.float64),
                                result["L4_patterns"][1].astype(np.float64))
    L23_kl = hist_kl_symmetric(result["L23_patterns"][0].astype(np.float64),
                                result["L23_patterns"][1].astype(np.float64))
    L5_kl  = hist_kl_symmetric(result["L5_patterns"][0].astype(np.float64),
                                result["L5_patterns"][1].astype(np.float64))
    L6_kl  = hist_kl_symmetric(result["L6_patterns"][0].astype(np.float64),
                                result["L6_patterns"][1].astype(np.float64))

    max_kl = max(L23_kl, L5_kl, L6_kl)
    kl_amplification = max_kl / L4_kl if L4_kl > 1e-6 else float('inf')

    return dict(
        n_synapses_total=result["n_synapses_total"],
        n_synapses_input=result["n_synapses_input"],
        n_synapses_ff=result["n_synapses_ff"],
        n_synapses_fb=result["n_synapses_fb"],
        n_synapses_rec_EE=result["n_synapses_rec_EE"],
        n_synapses_inhib=result["n_synapses_inhib"],
        L4_accuracy=L4_acc, L23_accuracy=L23_acc, L5_accuracy=L5_acc, L6_accuracy=L6_acc,
        L4_kl=L4_kl, L23_kl=L23_kl, L5_kl=L5_kl, L6_kl=L6_kl,
        kl_amplification=kl_amplification,
        total_L4_spikes=result["total_L4_spikes"],
        total_L23_spikes=result["total_L23_spikes"],
        total_L5_spikes=result["total_L5_spikes"],
        total_L6_spikes=result["total_L6_spikes"],
    )


def _verdict(s):
    acc_ok = s["L5_accuracy"] > T61B_ACC_MIN
    kl_amp_ok = s["kl_amplification"] > T61C_KL_AMPL_MIN
    return {**s, "T61b_acc_ok": acc_ok, "T61c_kl_amp_ok": kl_amp_ok,
            "T61_pass": acc_ok and kl_amp_ok}


def test_T61(substrates):
    m = _verdict(substrates)
    if not m["T61_pass"]:
        pytest.fail(
            f"BET-077 NULL T61 cortical 4-layer.\n"
            f"  total synapses: {m['n_synapses_total']:,}\n"
            f"  per-layer prototype acc: L4 {m['L4_accuracy']:.3f}, L23 {m['L23_accuracy']:.3f}, "
            f"L5 {m['L5_accuracy']:.3f} (need > {T61B_ACC_MIN}), L6 {m['L6_accuracy']:.3f}\n"
            f"  per-layer KL EN-vs-WN: L4 {m['L4_kl']:.3f}, L23 {m['L23_kl']:.3f}, "
            f"L5 {m['L5_kl']:.3f}, L6 {m['L6_kl']:.3f}\n"
            f"  KL amplification: {m['kl_amplification']:.2f}× "
            f"(need > {T61C_KL_AMPL_MIN}×)\n"
            f"  total spikes per layer: L4 {m['total_L4_spikes']:,}, "
            f"L23 {m['total_L23_spikes']:,}, L5 {m['total_L5_spikes']:,}, L6 {m['total_L6_spikes']:,}\n"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T61_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-077",
        "verdict": verdict,
        "hypothesis": "T61 Brian2 cortical-density 4-layer substrate (25K neurons, E:I 4:1, ~25M synapses). Bars: L5 prototype acc > 0.75 AND hierarchical KL amplification > 5x.",
        "thresholds": {"T61b_acc_min": T61B_ACC_MIN, "T61c_kl_amp_min": T61C_KL_AMPL_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

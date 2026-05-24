"""BET-068 — T52 Brian2 hierarchical 2-layer SNN.

Stufe 7 des Proof. Two-layer SNN (L1 local + L2 global) + top-down
plastic feedback. Cortical-style structure. Tests if hierarchy adds
class-discriminability beyond single-layer (BET-065).

T52 bar (LOCKED):
  prototype-classification accuracy on L2 > 0.8 (matches/improves BET-065).
  AND KL between L2 patterns of EN vs WN > 0.1.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pytest

warnings.filterwarnings('ignore')

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.brian2_hierarchical import Brian2HierarchicalConfig, train_and_collect_patterns
from world.flux.harder_bar_metrics import hist_kl_symmetric

N_TRAIN_PER_CLASS = 100
N_TEST_PER_CLASS = 30
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T52_ACCURACY_MIN = 0.8
T52_KL_MIN = 0.1

OUT_DIR = Path.home() / ".eqmod/bet/BET-068"
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

    cfg = Brian2HierarchicalConfig(chunk_duration_ms=100.0)
    result = train_and_collect_patterns(
        train_dict, test_dict, encoder_cfg,
        N_TRAIN_PER_CLASS, N_TEST_PER_CLASS, cfg,
    )

    L2_en = result["L2_patterns_by_class"][0]
    L2_wn = result["L2_patterns_by_class"][1]
    proto_en = L2_en.mean(axis=0)
    proto_wn = L2_wn.mean(axis=0)
    correct = 0
    total = 0
    for p in L2_en:
        d_en = float(np.linalg.norm(p - proto_en))
        d_wn = float(np.linalg.norm(p - proto_wn))
        if d_en < d_wn: correct += 1
        total += 1
    for p in L2_wn:
        d_en = float(np.linalg.norm(p - proto_en))
        d_wn = float(np.linalg.norm(p - proto_wn))
        if d_wn < d_en: correct += 1
        total += 1
    L2_accuracy = correct / max(total, 1)
    L2_kl = hist_kl_symmetric(L2_en.astype(np.float64), L2_wn.astype(np.float64))

    # Also report L1 stats for comparison
    L1_en = result["L1_patterns_by_class"][0]
    L1_wn = result["L1_patterns_by_class"][1]
    L1_kl = hist_kl_symmetric(L1_en.astype(np.float64), L1_wn.astype(np.float64))

    return dict(
        L2_accuracy_prototype=L2_accuracy,
        L2_kl_en_wn=L2_kl,
        L1_kl_en_wn=L1_kl,
        L2_pattern_mean_en=float(L2_en.mean()),
        L2_pattern_mean_wn=float(L2_wn.mean()),
        final_W_in_L1=result["final_W_in_L1_mean"],
        final_W_L1_L2=result["final_W_L1_L2_mean"],
        final_W_L2_L1_topdown=result["final_W_L2_L1_mean"],
        total_L1_spikes=result["total_L1_spikes"],
        total_L2_spikes=result["total_L2_spikes"],
    )


def _verdict(s):
    acc_ok = s["L2_accuracy_prototype"] > T52_ACCURACY_MIN
    kl_ok = s["L2_kl_en_wn"] > T52_KL_MIN
    return {**s, "T52_acc_ok": acc_ok, "T52_kl_ok": kl_ok,
            "T52_pass": acc_ok and kl_ok}


def test_T52(substrates):
    m = _verdict(substrates)
    if not m["T52_pass"]:
        pytest.fail(
            f"BET-068 NULL T52 hierarchical.\n"
            f"  L2 prototype accuracy: {m['L2_accuracy_prototype']:.4f} "
            f"(need > {T52_ACCURACY_MIN})\n"
            f"  L2 KL EN-vs-WN: {m['L2_kl_en_wn']:.4f} (need > {T52_KL_MIN})\n"
            f"  L1 KL: {m['L1_kl_en_wn']:.4f} (info-flow hint)\n"
            f"  W in→L1 mean: {m['final_W_in_L1']:.4f}\n"
            f"  W L1→L2 mean: {m['final_W_L1_L2']:.4f}\n"
            f"  W L2→L1 top-down: {m['final_W_L2_L1_topdown']:.4f}\n"
            f"  L1 spikes: {m['total_L1_spikes']}, L2 spikes: {m['total_L2_spikes']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T52_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-068",
        "verdict": verdict,
        "hypothesis": "T52 Brian2 hierarchical 2-layer SNN (L1+L2 + top-down). Stufe 7 des Proof. Cortical-style structure with bottom-up and top-down plastic synapses. Bar: L2 prototype acc > 0.8 AND L2 KL > 0.1.",
        "thresholds": {"T52_accuracy_min": T52_ACCURACY_MIN, "T52_kl_min": T52_KL_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

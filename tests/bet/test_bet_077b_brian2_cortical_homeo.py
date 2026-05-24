"""BET-077b — T62 Cortical 25K substrate + homeostatic plasticity.

Fixes the L5/L6 collapse seen in BET-077 (saturated firing prevented
class-discrimination). Each E neuron's v_thresh drifts toward target
firing rate of 5 Hz, applied between chunks.

T62 bars (LOCKED, all three must pass):
  T62a — Substrate runs without crash
  T62b — NO layer saturates: spike count per layer < 5× the BET-077
         minimum (which was L6 at 16.7M for 80×2=160 trials × 100ms).
         I.e. spike count per layer < 5e6 per 160 chunks for 5000 E.
         Conservative bar: max layer spike rate per chunk per neuron < 1.0.
  T62c — L5 prototype acc > 0.75 AND KL amplification > 5×
         (the BET-077 bars now ALL must hold, not just L23)
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

T62B_MAX_SPIKES_PER_NEURON_PER_CHUNK = 1.0  # 10 Hz max (5 Hz target × 2)
T62C_ACC_MIN = 0.75
T62C_KL_AMPL_MIN = 5.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-077b"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _proto_accuracy(p0, p1):
    proto0 = p0.mean(axis=0)
    proto1 = p1.mean(axis=0)
    correct, total = 0, 0
    for p in p0:
        if np.linalg.norm(p - proto0) < np.linalg.norm(p - proto1): correct += 1
        total += 1
    for p in p1:
        if np.linalg.norm(p - proto1) < np.linalg.norm(p - proto0): correct += 1
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

    cfg = Brian2CorticalConfig(
        chunk_duration_ms=100.0,
        homeostasis_enabled=True,
        homeostasis_target_rate_hz=5.0,
        homeostasis_eta_mv=0.05,
    )
    result = train_and_collect_layer_patterns(
        train_dict, test_dict, encoder_cfg,
        N_TRAIN_PER_CLASS, N_TEST_PER_CLASS, cfg,
    )

    L4_acc  = _proto_accuracy(result["L4_patterns"][0],  result["L4_patterns"][1])
    L23_acc = _proto_accuracy(result["L23_patterns"][0], result["L23_patterns"][1])
    L5_acc  = _proto_accuracy(result["L5_patterns"][0],  result["L5_patterns"][1])
    L6_acc  = _proto_accuracy(result["L6_patterns"][0],  result["L6_patterns"][1])

    L4_kl  = hist_kl_symmetric(result["L4_patterns"][0].astype(np.float64),
                                result["L4_patterns"][1].astype(np.float64))
    L23_kl = hist_kl_symmetric(result["L23_patterns"][0].astype(np.float64),
                                result["L23_patterns"][1].astype(np.float64))
    L5_kl  = hist_kl_symmetric(result["L5_patterns"][0].astype(np.float64),
                                result["L5_patterns"][1].astype(np.float64))
    L6_kl  = hist_kl_symmetric(result["L6_patterns"][0].astype(np.float64),
                                result["L6_patterns"][1].astype(np.float64))
    max_kl = max(L23_kl, L5_kl, L6_kl)
    kl_ampl = max_kl / L4_kl if L4_kl > 1e-9 else float('inf')

    # Per-chunk firing rates per neuron
    total_chunks = N_TRAIN_PER_CLASS * 2 + N_TEST_PER_CLASS * 2
    n_neurons = {'L4': 5000, 'L23': 6000, 'L5': 5000, 'L6': 4000}
    fire_rate_L4  = result["total_L4_spikes"]  / (total_chunks * n_neurons['L4'])
    fire_rate_L23 = result["total_L23_spikes"] / (total_chunks * n_neurons['L23'])
    fire_rate_L5  = result["total_L5_spikes"]  / (total_chunks * n_neurons['L5'])
    fire_rate_L6  = result["total_L6_spikes"]  / (total_chunks * n_neurons['L6'])
    max_fire_rate = max(fire_rate_L4, fire_rate_L23, fire_rate_L5, fire_rate_L6)

    return dict(
        n_synapses_total=result["n_synapses_total"],
        L4_accuracy=L4_acc, L23_accuracy=L23_acc, L5_accuracy=L5_acc, L6_accuracy=L6_acc,
        L4_kl=L4_kl, L23_kl=L23_kl, L5_kl=L5_kl, L6_kl=L6_kl,
        kl_amplification=kl_ampl,
        fire_rate_per_chunk_L4=fire_rate_L4,
        fire_rate_per_chunk_L23=fire_rate_L23,
        fire_rate_per_chunk_L5=fire_rate_L5,
        fire_rate_per_chunk_L6=fire_rate_L6,
        max_fire_rate=max_fire_rate,
        total_L4_spikes=result["total_L4_spikes"],
        total_L23_spikes=result["total_L23_spikes"],
        total_L5_spikes=result["total_L5_spikes"],
        total_L6_spikes=result["total_L6_spikes"],
    )


def _verdict(s):
    no_saturation = s["max_fire_rate"] < T62B_MAX_SPIKES_PER_NEURON_PER_CHUNK
    acc_ok = s["L5_accuracy"] > T62C_ACC_MIN
    kl_amp_ok = s["kl_amplification"] > T62C_KL_AMPL_MIN
    return {**s, "T62b_no_saturation_ok": no_saturation,
            "T62c_acc_ok": acc_ok, "T62c_kl_amp_ok": kl_amp_ok,
            "T62_pass": no_saturation and acc_ok and kl_amp_ok}


def test_T62(substrates):
    m = _verdict(substrates)
    if not m["T62_pass"]:
        pytest.fail(
            f"BET-077b NULL T62 cortical+homeostatic.\n"
            f"  total synapses: {m['n_synapses_total']:,}\n"
            f"  per-chunk fire rate (target {0.5:.2f}/neuron/chunk = 5 Hz):\n"
            f"    L4 {m['fire_rate_per_chunk_L4']:.3f}, L23 {m['fire_rate_per_chunk_L23']:.3f}, "
            f"L5 {m['fire_rate_per_chunk_L5']:.3f}, L6 {m['fire_rate_per_chunk_L6']:.3f}\n"
            f"    max {m['max_fire_rate']:.3f} (need < {T62B_MAX_SPIKES_PER_NEURON_PER_CHUNK})\n"
            f"  prototype acc: L4 {m['L4_accuracy']:.3f}, L23 {m['L23_accuracy']:.3f}, "
            f"L5 {m['L5_accuracy']:.3f} (need > {T62C_ACC_MIN}), L6 {m['L6_accuracy']:.3f}\n"
            f"  KL: L4 {m['L4_kl']:.3e}, L23 {m['L23_kl']:.3e}, "
            f"L5 {m['L5_kl']:.3e}, L6 {m['L6_kl']:.3e}\n"
            f"  KL amplification: {m['kl_amplification']:.2f}× (need > {T62C_KL_AMPL_MIN}×)\n"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T62_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-077b",
        "verdict": verdict,
        "hypothesis": "T62 Cortical 25K + homeostatic threshold drift (Turrigiano 2008). Fixes BET-077 L5/L6 collapse. Bars: no saturation AND L5 acc > 0.75 AND KL amplification > 5x.",
        "thresholds": {
            "T62b_max_fire_rate": T62B_MAX_SPIKES_PER_NEURON_PER_CHUNK,
            "T62c_acc_min": T62C_ACC_MIN,
            "T62c_kl_amp_min": T62C_KL_AMPL_MIN,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

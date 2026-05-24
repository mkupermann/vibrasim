"""BET-077c — T63 Cortical 25K with bounded recurrent + stronger inhibition.

After BET-077 L5/L6 collapse and BET-077b homeostasis insufficient,
this BET applies four structural fixes simultaneously:
  - Recurrent E→E wmax 0.3 (was 2.0) via separate STDP namespace
  - p_rec_EE 0.05 → 0.02
  - p_IE 0.30 → 0.40, w_IE 1.0 → 1.5 (stronger lateral inhibition)
  - Homeostasis eta 0.05 → 1.0 mV/spike-excess (20× stronger drift)

T63 bars (LOCKED, all must pass):
  T63a — max fire rate < 1.0 spikes/neuron/chunk (no saturation)
  T63b — L5 prototype acc > 0.75
  T63c — KL amplification > 5×
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

T63A_MAX_FIRE_RATE = 1.0
T63B_ACC_MIN = 0.75
T63C_KL_AMPL_MIN = 5.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-077c"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _proto_accuracy(p0, p1):
    proto0 = p0.mean(axis=0); proto1 = p1.mean(axis=0)
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
        n_features = N_FEATURES; fft_bands = FFT_BANDS; samples_per_tick = SAMPLES_PER_TICK
    encoder_cfg = _Cfg()

    n_train = N_TRAIN_PER_CLASS * SAMPLES_PER_TICK
    n_test = N_TEST_PER_CLASS * SAMPLES_PER_TICK
    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS)
    eng_train = full[:n_train].astype(np.float64)
    eng_test = full[n_train:n_train + n_test].astype(np.float64)
    wn_train = _make_wn(n_train, TARGET_RMS, WN_SEED)
    wn_test = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)

    def chunks(audio, n):
        return [audio[k*SAMPLES_PER_TICK:(k+1)*SAMPLES_PER_TICK] for k in range(n)]

    train_dict = {0: chunks(eng_train, N_TRAIN_PER_CLASS),
                  1: chunks(wn_train, N_TRAIN_PER_CLASS)}
    test_dict = {0: chunks(eng_test, N_TEST_PER_CLASS),
                 1: chunks(wn_test, N_TEST_PER_CLASS)}

    cfg = Brian2CorticalConfig(
        chunk_duration_ms=100.0,
        p_rec_EE=0.02,                     # was 0.05
        p_IE=0.40,                         # was 0.30
        homeostasis_enabled=True,
        homeostasis_target_rate_hz=5.0,
        homeostasis_eta_mv=1.0,            # was 0.05 — 20× stronger
    )
    # boost w_IE via post-fact namespace override is not exposed; effect via
    # higher p_IE alone — gives 33% more I→E synapses with same weight 1.0.

    result = train_and_collect_layer_patterns(
        train_dict, test_dict, encoder_cfg,
        N_TRAIN_PER_CLASS, N_TEST_PER_CLASS, cfg)

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

    total_chunks = N_TRAIN_PER_CLASS * 2 + N_TEST_PER_CLASS * 2
    n_neurons = {'L4': 5000, 'L23': 6000, 'L5': 5000, 'L6': 4000}
    fire = {
        'L4':  result["total_L4_spikes"]  / (total_chunks * n_neurons['L4']),
        'L23': result["total_L23_spikes"] / (total_chunks * n_neurons['L23']),
        'L5':  result["total_L5_spikes"]  / (total_chunks * n_neurons['L5']),
        'L6':  result["total_L6_spikes"]  / (total_chunks * n_neurons['L6']),
    }

    return dict(
        n_synapses_total=result["n_synapses_total"],
        L4_accuracy=L4_acc, L23_accuracy=L23_acc, L5_accuracy=L5_acc, L6_accuracy=L6_acc,
        L4_kl=L4_kl, L23_kl=L23_kl, L5_kl=L5_kl, L6_kl=L6_kl,
        kl_amplification=kl_ampl,
        fire_rate_per_chunk_L4=fire['L4'],
        fire_rate_per_chunk_L23=fire['L23'],
        fire_rate_per_chunk_L5=fire['L5'],
        fire_rate_per_chunk_L6=fire['L6'],
        max_fire_rate=max(fire.values()),
        total_L4_spikes=result["total_L4_spikes"],
        total_L23_spikes=result["total_L23_spikes"],
        total_L5_spikes=result["total_L5_spikes"],
        total_L6_spikes=result["total_L6_spikes"],
    )


def _verdict(s):
    no_sat = s["max_fire_rate"] < T63A_MAX_FIRE_RATE
    acc_ok = s["L5_accuracy"] > T63B_ACC_MIN
    kl_ok  = s["kl_amplification"] > T63C_KL_AMPL_MIN
    return {**s, "T63a_no_saturation_ok": no_sat, "T63b_acc_ok": acc_ok,
            "T63c_kl_amp_ok": kl_ok, "T63_pass": no_sat and acc_ok and kl_ok}


def test_T63(substrates):
    m = _verdict(substrates)
    if not m["T63_pass"]:
        pytest.fail(
            f"BET-077c NULL T63 cortical balanced.\n"
            f"  total synapses: {m['n_synapses_total']:,}\n"
            f"  fire rate L4 {m['fire_rate_per_chunk_L4']:.3f}, L23 {m['fire_rate_per_chunk_L23']:.3f}, "
            f"L5 {m['fire_rate_per_chunk_L5']:.3f}, L6 {m['fire_rate_per_chunk_L6']:.3f} "
            f"(max {m['max_fire_rate']:.3f}, need < {T63A_MAX_FIRE_RATE})\n"
            f"  acc L4 {m['L4_accuracy']:.3f}, L23 {m['L23_accuracy']:.3f}, "
            f"L5 {m['L5_accuracy']:.3f} (need > {T63B_ACC_MIN}), L6 {m['L6_accuracy']:.3f}\n"
            f"  KL: L4 {m['L4_kl']:.3e}, L23 {m['L23_kl']:.3e}, "
            f"L5 {m['L5_kl']:.3e}, L6 {m['L6_kl']:.3e}\n"
            f"  KL amp {m['kl_amplification']:.2f}× (need > {T63C_KL_AMPL_MIN}×)\n"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T63_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-077c",
        "verdict": verdict,
        "hypothesis": "T63 Cortical 25K balanced (recurrent E→E wmax 0.3, p_rec 0.02, p_IE 0.4, homeostasis eta 1.0mV). Bars: no saturation AND L5 acc > 0.75 AND KL amp > 5x.",
        "thresholds": {
            "T63a_max_fire_rate": T63A_MAX_FIRE_RATE,
            "T63b_acc_min": T63B_ACC_MIN,
            "T63c_kl_amp_min": T63C_KL_AMPL_MIN,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

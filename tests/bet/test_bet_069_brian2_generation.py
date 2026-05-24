"""BET-069 — T53 Brian2 hierarchical SNN generation test.

Stufe 4 des Proof. After training hierarchical SNN (BET-068 substrate),
test GENERATION: directly activate L2 neurons (substitute for "thought"
or "class concept"). Observe L1 patterns produced via TOP-DOWN
synapses. Compare to L1 patterns observed during normal class
presentation.

If top-down-driven L1 patterns differ between classes AND match the
class-typical bottom-up L1 patterns → substrate has internal generative
model. Brain-faithful generative substrate.

T53 bar (LOCKED):
  Cosine similarity(L1 pattern via top-down EN-L2-trigger,
                    L1 pattern via bottom-up EN-input) > 0.3
  AND
  Generated L1 patterns differ between EN-trigger and WN-trigger
  (KL > 0.05).
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pytest

warnings.filterwarnings('ignore')

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.harder_bar_metrics import hist_kl_symmetric

N_TRAIN_PER_CLASS = 100
N_TEST_PER_CLASS = 20
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
TARGET_RMS = 0.25

T53_COSINE_MIN = 0.3
T53_KL_MIN = 0.05

OUT_DIR = Path.home() / ".eqmod/bet/BET-069"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _cosine(a, b):
    denom = np.linalg.norm(a) * np.linalg.norm(b) + 1e-12
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0


@pytest.fixture(scope="module")
def substrates():
    from brian2 import (NeuronGroup, PoissonGroup, Synapses, SpikeMonitor,
                        Network, Hz, ms, mV, defaultclock, prefs)
    from world.flux.cognitive_map import encode_sensor

    prefs.codegen.target = 'numpy'
    defaultclock.dt = 1.0 * ms

    class _Cfg:
        n_features = N_FEATURES
        fft_bands = FFT_BANDS
        samples_per_tick = SAMPLES_PER_TICK
    encoder_cfg = _Cfg()

    # ----- Build substrate (like BET-068) -----
    n_input, n_L1, n_L2 = 10, 100, 50
    n_inh1, n_inh2 = 25, 12

    eqs_lif = '''
    dv/dt = (-(v - v_rest) + ge*(0*mV - v) + gi*(-80*mV - v)) / tau_m : volt (unless refractory)
    dge/dt = -ge / tau_e : 1
    dgi/dt = -gi / tau_i : 1
    '''
    tau_m = 20 * ms
    tau_e = 5 * ms
    tau_i = 10 * ms
    v_rest = -70 * mV
    v_thresh = -54 * mV
    v_reset = -75 * mV
    tau_ref = 5 * ms

    input_group = PoissonGroup(n_input, rates=0 * Hz)
    L1 = NeuronGroup(n_L1, eqs_lif, threshold='v > v_thresh',
                     reset='v = v_reset', refractory=tau_ref, method='euler')
    L1.v = v_rest
    Inh1 = NeuronGroup(n_inh1, eqs_lif, threshold='v > v_thresh',
                       reset='v = v_reset', refractory=tau_ref, method='euler')
    Inh1.v = v_rest
    L2 = NeuronGroup(n_L2, eqs_lif, threshold='v > v_thresh',
                     reset='v = v_reset', refractory=tau_ref, method='euler')
    L2.v = v_rest
    Inh2 = NeuronGroup(n_inh2, eqs_lif, threshold='v > v_thresh',
                       reset='v = v_reset', refractory=tau_ref, method='euler')
    Inh2.v = v_rest

    # Direct external drive to L2 (for generation phase)
    L2_external_drive = PoissonGroup(n_L2, rates=0 * Hz)

    stdp_eqs = '''
    w : 1
    dApre/dt = -Apre / taupre : 1 (event-driven)
    dApost/dt = -Apost / taupost : 1 (event-driven)
    '''
    on_pre = '''ge += w
                Apre += dApre_val
                w = clip(w + Apost, 0, wmax)'''
    on_post = '''Apost += dApost_val
                 w = clip(w + Apre, 0, wmax)'''
    ns = {'taupre': 20*ms, 'taupost': 20*ms,
          'dApre_val': 0.01, 'dApost_val': -0.012, 'wmax': 2.0}

    rng = np.random.default_rng(0)

    syn_in_L1 = Synapses(input_group, L1, model=stdp_eqs, on_pre=on_pre,
                         on_post=on_post, namespace=ns)
    syn_in_L1.connect(p=0.5)
    syn_in_L1.w = rng.uniform(0.5, 1.5, len(syn_in_L1))

    syn_L1_L2 = Synapses(L1, L2, model=stdp_eqs, on_pre=on_pre,
                         on_post=on_post, namespace=ns)
    syn_L1_L2.connect(p=0.3)
    syn_L1_L2.w = rng.uniform(0.3, 0.7, len(syn_L1_L2))

    syn_L2_L1 = Synapses(L2, L1, model=stdp_eqs, on_pre=on_pre,
                         on_post=on_post, namespace=ns)
    syn_L2_L1.connect(p=0.2)
    syn_L2_L1.w = rng.uniform(0.2, 0.5, len(syn_L2_L1))

    syn_L1_Inh1 = Synapses(L1, Inh1, 'w : 1', on_pre='ge_post += w')
    syn_L1_Inh1.connect(p=0.3); syn_L1_Inh1.w = 0.5
    syn_Inh1_L1 = Synapses(Inh1, L1, 'w : 1', on_pre='gi_post += w')
    syn_Inh1_L1.connect(p=0.4); syn_Inh1_L1.w = 1.0
    syn_L2_Inh2 = Synapses(L2, Inh2, 'w : 1', on_pre='ge_post += w')
    syn_L2_Inh2.connect(p=0.3); syn_L2_Inh2.w = 0.5
    syn_Inh2_L2 = Synapses(Inh2, L2, 'w : 1', on_pre='gi_post += w')
    syn_Inh2_L2.connect(p=0.4); syn_Inh2_L2.w = 1.0

    syn_L2ext_L2 = Synapses(L2_external_drive, L2, 'w : 1', on_pre='ge_post += w')
    syn_L2ext_L2.connect('i==j')
    syn_L2ext_L2.w = 2.0

    mon_L1 = SpikeMonitor(L1)
    mon_L2 = SpikeMonitor(L2)
    net = Network(input_group, L2_external_drive, L1, Inh1, L2, Inh2,
                  syn_in_L1, syn_L1_L2, syn_L2_L1,
                  syn_L1_Inh1, syn_Inh1_L1, syn_L2_Inh2, syn_Inh2_L2,
                  syn_L2ext_L2,
                  mon_L1, mon_L2)

    chunk_dur = 100 * ms

    # ----- Training -----
    n_train = N_TRAIN_PER_CLASS * SAMPLES_PER_TICK
    n_test = N_TEST_PER_CLASS * SAMPLES_PER_TICK
    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS)
    eng_train = full[:n_train]
    eng_test = full[n_train:n_train + n_test]
    wn_train = _make_wn(n_train, TARGET_RMS, WN_SEED)
    wn_test = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)

    def _chunk(audio, k):
        return audio[k*SAMPLES_PER_TICK:(k+1)*SAMPLES_PER_TICK]

    # Disable L2_external_drive during training
    L2_external_drive.rates = 0 * Hz

    for trial in range(N_TRAIN_PER_CLASS):
        for label, audio in [(0, eng_train), (1, wn_train)]:
            features = encode_sensor(_chunk(audio, trial), encoder_cfg)
            input_group.rates = np.clip(features[:n_input], 0, 1) * 100 * Hz
            net.run(chunk_dur)

    # ----- Phase 1: Bottom-up L2 patterns (observation) -----
    L2_test_patterns = {0: [], 1: []}
    L1_test_patterns_bottomup = {0: [], 1: []}
    for k in range(N_TEST_PER_CLASS):
        for label, audio in [(0, eng_test), (1, wn_test)]:
            features = encode_sensor(_chunk(audio, k), encoder_cfg)
            input_group.rates = np.clip(features[:n_input], 0, 1) * 100 * Hz
            l1b, l2b = np.array(mon_L1.count).copy(), np.array(mon_L2.count).copy()
            net.run(chunk_dur)
            L1_test_patterns_bottomup[label].append(np.array(mon_L1.count) - l1b)
            L2_test_patterns[label].append(np.array(mon_L2.count) - l2b)

    # Identify "class-typical" L2 neuron-firing per class
    L2_proto_en = np.mean(L2_test_patterns[0], axis=0)
    L2_proto_wn = np.mean(L2_test_patterns[1], axis=0)

    # Identify EN-typical L2 neurons (fire more for EN than WN)
    L2_en_preference = L2_proto_en - L2_proto_wn  # +ve: prefers EN
    en_specific = L2_en_preference > L2_en_preference.std()
    wn_specific = L2_en_preference < -L2_en_preference.std()

    # ----- Phase 2: Top-down generation -----
    # Activate L2-EN-neurons via external drive; observe L1
    input_group.rates = 0 * Hz  # no bottom-up
    L1_generated_en = []
    L1_generated_wn = []

    # Drive EN-specific L2 neurons
    drive_rates = np.zeros(n_L2)
    drive_rates[en_specific] = 200.0  # Hz
    L2_external_drive.rates = drive_rates * Hz
    for _ in range(N_TEST_PER_CLASS):
        l1b = np.array(mon_L1.count).copy()
        net.run(chunk_dur)
        L1_generated_en.append(np.array(mon_L1.count) - l1b)
    # Reset, drive WN-specific
    drive_rates = np.zeros(n_L2)
    drive_rates[wn_specific] = 200.0
    L2_external_drive.rates = drive_rates * Hz
    for _ in range(N_TEST_PER_CLASS):
        l1b = np.array(mon_L1.count).copy()
        net.run(chunk_dur)
        L1_generated_wn.append(np.array(mon_L1.count) - l1b)

    L1_bu_en = np.mean(L1_test_patterns_bottomup[0], axis=0)
    L1_bu_wn = np.mean(L1_test_patterns_bottomup[1], axis=0)
    L1_gen_en = np.mean(L1_generated_en, axis=0)
    L1_gen_wn = np.mean(L1_generated_wn, axis=0)

    cosine_en_match = _cosine(L1_gen_en, L1_bu_en)
    cosine_wn_match = _cosine(L1_gen_wn, L1_bu_wn)
    cosine_en_to_wn = _cosine(L1_gen_en, L1_bu_wn)  # cross-class confusion check

    kl_gen_classes = hist_kl_symmetric(
        np.array(L1_generated_en).astype(np.float64),
        np.array(L1_generated_wn).astype(np.float64),
    )

    return dict(
        n_en_specific_L2=int(en_specific.sum()),
        n_wn_specific_L2=int(wn_specific.sum()),
        cosine_top_down_EN_to_bottom_up_EN=cosine_en_match,
        cosine_top_down_WN_to_bottom_up_WN=cosine_wn_match,
        cosine_top_down_EN_to_bottom_up_WN=cosine_en_to_wn,
        mean_cosine_match=(cosine_en_match + cosine_wn_match) / 2,
        kl_generated_classes=kl_gen_classes,
        L1_gen_en_mean=float(L1_gen_en.mean()),
        L1_gen_wn_mean=float(L1_gen_wn.mean()),
    )


def _verdict(s):
    cos_ok = s["mean_cosine_match"] > T53_COSINE_MIN
    kl_ok = s["kl_generated_classes"] > T53_KL_MIN
    return {**s, "T53_cos_ok": cos_ok, "T53_kl_ok": kl_ok,
            "T53_pass": cos_ok and kl_ok}


def test_T53(substrates):
    m = _verdict(substrates)
    if not m["T53_pass"]:
        pytest.fail(
            f"BET-069 NULL T53 generation.\n"
            f"  EN-specific L2 neurons: {m['n_en_specific_L2']}\n"
            f"  WN-specific L2 neurons: {m['n_wn_specific_L2']}\n"
            f"  cos(top-down EN, bottom-up EN): {m['cosine_top_down_EN_to_bottom_up_EN']:.4f}\n"
            f"  cos(top-down WN, bottom-up WN): {m['cosine_top_down_WN_to_bottom_up_WN']:.4f}\n"
            f"  mean cosine match: {m['mean_cosine_match']:.4f} (need > {T53_COSINE_MIN})\n"
            f"  KL between generated classes: {m['kl_generated_classes']:.4f} (need > {T53_KL_MIN})"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T53_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-069",
        "verdict": verdict,
        "hypothesis": "T53 Brian2 hierarchical SNN generation. Activate class-specific L2 neurons externally, observe top-down generated L1 pattern. Bar: cosine to bottom-up L1 > 0.3 AND KL between generated classes > 0.05.",
        "thresholds": {"T53_cosine_min": T53_COSINE_MIN, "T53_kl_min": T53_KL_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))

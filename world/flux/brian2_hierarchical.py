"""Brian2 hierarchical multi-layer SNN — cortical-style structure.

Stufe 7 des Proof-Programms. Two layers of LIF neurons with STDP between
them. Layer 1 (local features) gets driven by audio input; Layer 2
(global features) receives from Layer 1 via STDP synapses. Top-down
connections from Layer 2 back to Layer 1 (predictive coding hint).

Brain inspiration:
  - Cortical layers (Layer 4 input → Layer 2/3 processing →
    Layer 5 output) — simplified to 2 layers here
  - Bottom-up driving + top-down predictions (Friston FEP)
  - STDP plasticity at every connection

Reference: Diehl & Cook 2015 Front. Comp. Neurosci. (canonical SNN+STDP
on MNIST with similar architecture)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Brian2HierarchicalConfig:
    n_input: int = 10
    n_layer1: int = 100
    n_layer2: int = 50
    n_inh1: int = 25       # inhibitory in layer 1
    n_inh2: int = 12       # inhibitory in layer 2
    input_rate_max_hz: float = 100.0
    chunk_duration_ms: float = 100.0
    rng_seed: int = 0


def train_and_collect_patterns(train_dict, test_dict, encoder_cfg,
                               n_train_per_class, n_test_per_class,
                               cfg: Brian2HierarchicalConfig):
    from brian2 import (NeuronGroup, PoissonGroup, Synapses, SpikeMonitor,
                        Network, Hz, ms, mV, defaultclock, prefs)
    from world.flux.cognitive_map import encode_sensor

    prefs.codegen.target = 'numpy'
    defaultclock.dt = 1.0 * ms

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

    input_group = PoissonGroup(cfg.n_input, rates=0 * Hz)

    # Layer 1 (local features)
    L1 = NeuronGroup(cfg.n_layer1, eqs_lif, threshold='v > v_thresh',
                     reset='v = v_reset', refractory=tau_ref, method='euler')
    L1.v = v_rest
    Inh1 = NeuronGroup(cfg.n_inh1, eqs_lif, threshold='v > v_thresh',
                       reset='v = v_reset', refractory=tau_ref, method='euler')
    Inh1.v = v_rest

    # Layer 2 (global features)
    L2 = NeuronGroup(cfg.n_layer2, eqs_lif, threshold='v > v_thresh',
                     reset='v = v_reset', refractory=tau_ref, method='euler')
    L2.v = v_rest
    Inh2 = NeuronGroup(cfg.n_inh2, eqs_lif, threshold='v > v_thresh',
                       reset='v = v_reset', refractory=tau_ref, method='euler')
    Inh2.v = v_rest

    stdp_eqs = '''
    w : 1
    dApre/dt = -Apre / taupre : 1 (event-driven)
    dApost/dt = -Apost / taupost : 1 (event-driven)
    '''
    on_pre = '''
    ge += w
    Apre += dApre_val
    w = clip(w + Apost, 0, wmax)
    '''
    on_post = '''
    Apost += dApost_val
    w = clip(w + Apre, 0, wmax)
    '''
    stdp_ns = {'taupre': 20 * ms, 'taupost': 20 * ms,
               'dApre_val': 0.01, 'dApost_val': -0.012, 'wmax': 2.0}

    rng = np.random.default_rng(cfg.rng_seed)

    # input → L1: plastic
    syn_in_L1 = Synapses(input_group, L1, model=stdp_eqs, on_pre=on_pre,
                          on_post=on_post, namespace=stdp_ns)
    syn_in_L1.connect(p=0.5)
    syn_in_L1.w = rng.uniform(0.5, 1.5, len(syn_in_L1))

    # L1 → L2: plastic (the hierarchical step)
    syn_L1_L2 = Synapses(L1, L2, model=stdp_eqs, on_pre=on_pre,
                          on_post=on_post, namespace=stdp_ns)
    syn_L1_L2.connect(p=0.3)
    syn_L1_L2.w = rng.uniform(0.3, 0.7, len(syn_L1_L2))

    # L2 → L1 top-down (predictive feedback, plastic)
    syn_L2_L1 = Synapses(L2, L1, model=stdp_eqs, on_pre=on_pre,
                          on_post=on_post, namespace=stdp_ns)
    syn_L2_L1.connect(p=0.1)  # sparser top-down
    syn_L2_L1.w = rng.uniform(0.1, 0.3, len(syn_L2_L1))

    # L1 → Inh1 → L1 (lateral inhibition for sparsity)
    syn_L1_Inh1 = Synapses(L1, Inh1, 'w : 1', on_pre='ge_post += w')
    syn_L1_Inh1.connect(p=0.3)
    syn_L1_Inh1.w = 0.5
    syn_Inh1_L1 = Synapses(Inh1, L1, 'w : 1', on_pre='gi_post += w')
    syn_Inh1_L1.connect(p=0.4)
    syn_Inh1_L1.w = 1.0

    # L2 → Inh2 → L2
    syn_L2_Inh2 = Synapses(L2, Inh2, 'w : 1', on_pre='ge_post += w')
    syn_L2_Inh2.connect(p=0.3)
    syn_L2_Inh2.w = 0.5
    syn_Inh2_L2 = Synapses(Inh2, L2, 'w : 1', on_pre='gi_post += w')
    syn_Inh2_L2.connect(p=0.4)
    syn_Inh2_L2.w = 1.0

    mon_L1 = SpikeMonitor(L1)
    mon_L2 = SpikeMonitor(L2)
    net = Network(input_group, L1, Inh1, L2, Inh2,
                  syn_in_L1, syn_L1_L2, syn_L2_L1,
                  syn_L1_Inh1, syn_Inh1_L1, syn_L2_Inh2, syn_Inh2_L2,
                  mon_L1, mon_L2)

    chunk_dur = cfg.chunk_duration_ms * ms

    # Training
    train_classes = list(train_dict.keys())
    for trial in range(n_train_per_class):
        for class_label in train_classes:
            chunks = train_dict[class_label]
            if trial >= len(chunks):
                continue
            features = encode_sensor(chunks[trial], encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz
            net.run(chunk_dur)

    # Test: collect L1 and L2 spike patterns per chunk
    test_classes = list(test_dict.keys())
    L1_patterns = {c: [] for c in test_classes}
    L2_patterns = {c: [] for c in test_classes}
    for k in range(n_test_per_class):
        for class_label in test_classes:
            chunks = test_dict[class_label]
            if k >= len(chunks):
                continue
            features = encode_sensor(chunks[k], encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz
            l1_before = np.array(mon_L1.count).copy()
            l2_before = np.array(mon_L2.count).copy()
            net.run(chunk_dur)
            l1_after = np.array(mon_L1.count)
            l2_after = np.array(mon_L2.count)
            L1_patterns[class_label].append(l1_after - l1_before)
            L2_patterns[class_label].append(l2_after - l2_before)

    return {
        "L1_patterns_by_class": {c: np.array(L1_patterns[c]) for c in test_classes},
        "L2_patterns_by_class": {c: np.array(L2_patterns[c]) for c in test_classes},
        "final_W_in_L1_mean": float(np.mean(syn_in_L1.w)),
        "final_W_L1_L2_mean": float(np.mean(syn_L1_L2.w)),
        "final_W_L2_L1_mean": float(np.mean(syn_L2_L1.w)),
        "total_L1_spikes": int(len(mon_L1.i)),
        "total_L2_spikes": int(len(mon_L2.i)),
    }

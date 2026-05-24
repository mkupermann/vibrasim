"""SNN+STDP via Brian2 (proper brain-sim library).

After 6 from-scratch numpy attempts NULLed, use Brian2 (canonical
Python SNN simulator, equations-based with proper integration).

Architecture:
  Input: 10 Poisson neurons (one per audio feature dim)
         rate ∝ feature value
  Hidden: 100 conductance-based LIF excitatory neurons
  Inhibitory: 25 LIF inhibitory (stabilization)
  Synapses:
    input → hidden: plastic, STDP, all-to-all
    hidden → inhibitory: fixed excitatory
    inhibitory → hidden: fixed inhibitory feedback

Equations follow Brian2 standard examples (LIF with exponential
synapses, STDP with pre/post traces).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Brian2SNNConfig:
    n_input: int = 10
    n_hidden: int = 100
    n_inhibitory: int = 25
    input_rate_max_hz: float = 100.0    # max Poisson rate
    chunk_duration_ms: float = 100.0
    rng_seed: int = 0


def run_substrate(train_dict, test_dict, encoder_cfg, n_train_per_class, n_test_per_class,
                  cfg: Brian2SNNConfig):
    """Run Brian2 SNN+STDP training + test.

    train_dict: {class_label: list of audio chunks for training}
    test_dict: {class_label: list of audio chunks for test}
    Returns dict with hidden spike patterns per chunk per class.
    """
    from brian2 import (NeuronGroup, PoissonGroup, Synapses, SpikeMonitor,
                        Network, Hz, ms, mV, second, defaultclock, run, prefs)
    from world.flux.cognitive_map import encode_sensor

    prefs.codegen.target = 'numpy'  # avoid C++ compile delay
    defaultclock.dt = 1.0 * ms

    # LIF dynamics (standard Brian2 example)
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

    # Input: Poisson rate-driven
    input_group = PoissonGroup(cfg.n_input, rates=0 * Hz)

    # Hidden excitatory
    hidden = NeuronGroup(cfg.n_hidden, eqs_lif, threshold='v > v_thresh',
                         reset='v = v_reset', refractory=tau_ref, method='euler')
    hidden.v = v_rest

    # Inhibitory
    inh = NeuronGroup(cfg.n_inhibitory, eqs_lif, threshold='v > v_thresh',
                      reset='v = v_reset', refractory=tau_ref, method='euler')
    inh.v = v_rest

    # input → hidden: plastic STDP
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

    syn_in_hid = Synapses(input_group, hidden, model=stdp_eqs, on_pre=on_pre, on_post=on_post,
                          namespace={'taupre': 20 * ms, 'taupost': 20 * ms,
                                     'dApre_val': 0.01, 'dApost_val': -0.012,
                                     'wmax': 2.0})
    syn_in_hid.connect(p=0.5)  # 50% connection density
    rng = np.random.default_rng(cfg.rng_seed)
    syn_in_hid.w = rng.uniform(0.5, 1.5, len(syn_in_hid))

    # hidden → inhibitory (fixed excitatory)
    syn_hid_inh = Synapses(hidden, inh, 'w : 1', on_pre='ge_post += w')
    syn_hid_inh.connect(p=0.3)
    syn_hid_inh.w = 0.5

    # inhibitory → hidden (fixed inhibitory)
    syn_inh_hid = Synapses(inh, hidden, 'w : 1', on_pre='gi_post += w')
    syn_inh_hid.connect(p=0.4)
    syn_inh_hid.w = 1.0

    monitor = SpikeMonitor(hidden)
    net = Network(input_group, hidden, inh, syn_in_hid, syn_hid_inh, syn_inh_hid, monitor)

    # Training: present each class's chunks alternating
    train_classes = list(train_dict.keys())
    chunk_dur = cfg.chunk_duration_ms * ms

    for trial in range(n_train_per_class):
        for class_label in train_classes:
            chunks = train_dict[class_label]
            if trial >= len(chunks):
                continue
            features = encode_sensor(chunks[trial], encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz
            net.run(chunk_dur)

    # Test patterns
    test_classes = list(test_dict.keys())
    test_patterns_by_class = {c: [] for c in test_classes}
    for k in range(n_test_per_class):
        for class_label in test_classes:
            test_chunks = test_dict[class_label]
            if k >= len(test_chunks):
                continue
            features = encode_sensor(test_chunks[k], encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz
            spike_count_before = np.array(monitor.count)
            net.run(chunk_dur)
            spike_count_after = np.array(monitor.count)
            pattern = spike_count_after - spike_count_before
            test_patterns_by_class[class_label].append(pattern)

    # Aggregate test patterns
    test_arrays = {c: np.array(test_patterns_by_class[c], dtype=np.float64)
                   for c in train_classes}

    return {
        "test_patterns_by_class": test_arrays,
        "final_W_mean": float(np.mean(syn_in_hid.w)),
        "final_W_std": float(np.std(syn_in_hid.w)),
        "total_hidden_spikes": int(len(monitor.i)),
    }

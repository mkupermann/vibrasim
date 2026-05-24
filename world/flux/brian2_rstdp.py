"""Brian2 R-STDP (reward-modulated STDP) — brain-faithful with agency.

After BET-065 Brian2 SNN+STDP PASSED (98% unsupervised), add reward
signal. Substrate's STDP modulated by dopamine-like global signal.

Architecture extension:
  - 10 Poisson input neurons (audio features → rates)
  - 100 conductance-LIF excitatory hidden + 25 inhibitory
  - 2 readout neurons (one per class) — receive from hidden
  - STDP on hidden→readout synapses, MODULATED by dopamine variable
  - Reward signal D(t) gates plasticity: ΔW = D * STDP_kernel

Izhikevich 2007 dopamine-modulated STDP standard form.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Brian2RSTDPConfig:
    n_input: int = 10
    n_hidden: int = 100
    n_inhibitory: int = 25
    n_readout: int = 2
    input_rate_max_hz: float = 100.0
    chunk_duration_ms: float = 100.0
    reward_window_ms: float = 50.0   # how long reward signal stays high
    rng_seed: int = 0


def train_and_test(train_dict, test_dict, encoder_cfg, n_train_per_class, n_test_per_class,
                   cfg: Brian2RSTDPConfig):
    """R-STDP training + test. Substrate learns to fire readout[class] in response to class chunk."""
    from brian2 import (NeuronGroup, PoissonGroup, Synapses, SpikeMonitor,
                        Network, Hz, ms, mV, second, defaultclock, prefs)
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
    hidden = NeuronGroup(cfg.n_hidden, eqs_lif, threshold='v > v_thresh',
                         reset='v = v_reset', refractory=tau_ref, method='euler')
    hidden.v = v_rest
    inh = NeuronGroup(cfg.n_inhibitory, eqs_lif, threshold='v > v_thresh',
                      reset='v = v_reset', refractory=tau_ref, method='euler')
    inh.v = v_rest
    readout = NeuronGroup(cfg.n_readout, eqs_lif, threshold='v > v_thresh',
                          reset='v = v_reset', refractory=tau_ref, method='euler')
    readout.v = v_rest

    # input → hidden: plastic STDP (modest)
    stdp_eqs_simple = '''
    w : 1
    dApre/dt = -Apre / taupre : 1 (event-driven)
    dApost/dt = -Apost / taupost : 1 (event-driven)
    '''
    syn_in_hid = Synapses(input_group, hidden, model=stdp_eqs_simple,
                          on_pre='''ge += w
                                    Apre += dApre_val
                                    w = clip(w + Apost, 0, wmax)''',
                          on_post='''Apost += dApost_val
                                     w = clip(w + Apre, 0, wmax)''',
                          namespace={'taupre': 20 * ms, 'taupost': 20 * ms,
                                     'dApre_val': 0.01, 'dApost_val': -0.012,
                                     'wmax': 2.0})
    syn_in_hid.connect(p=0.5)
    rng = np.random.default_rng(cfg.rng_seed)
    syn_in_hid.w = rng.uniform(0.5, 1.5, len(syn_in_hid))

    # hidden → inhibitory (fixed)
    syn_hid_inh = Synapses(hidden, inh, 'w : 1', on_pre='ge_post += w')
    syn_hid_inh.connect(p=0.3)
    syn_hid_inh.w = 0.5
    syn_inh_hid = Synapses(inh, hidden, 'w : 1', on_pre='gi_post += w')
    syn_inh_hid.connect(p=0.4)
    syn_inh_hid.w = 1.0

    # hidden → readout: R-STDP via eligibility traces
    # Dopamine variable D shared across synapses
    rstdp_eqs = '''
    w : 1
    dApre/dt = -Apre / taupre : 1 (event-driven)
    dApost/dt = -Apost / taupost : 1 (event-driven)
    de/dt = -e / tau_e_elig : 1 (clock-driven)
    '''
    on_pre_rstdp = '''
    ge_post += w
    Apre += dApre_val
    e += Apost
    '''
    on_post_rstdp = '''
    Apost += dApost_val
    e += Apre
    '''
    syn_hid_ro = Synapses(hidden, readout, model=rstdp_eqs,
                          on_pre=on_pre_rstdp, on_post=on_post_rstdp,
                          namespace={'taupre': 20 * ms, 'taupost': 20 * ms,
                                     'dApre_val': 0.01, 'dApost_val': -0.005,
                                     'tau_e_elig': 1000 * ms},
                          method='exact')
    syn_hid_ro.connect(True)  # all-to-all
    syn_hid_ro.w = rng.uniform(0.3, 0.7, len(syn_hid_ro))

    mon_hidden = SpikeMonitor(hidden)
    mon_readout = SpikeMonitor(readout)
    net = Network(input_group, hidden, inh, readout,
                  syn_in_hid, syn_hid_inh, syn_inh_hid, syn_hid_ro,
                  mon_hidden, mon_readout)

    chunk_dur = cfg.chunk_duration_ms * ms

    # Training: present chunks with reward feedback
    train_classes = list(train_dict.keys())
    train_history = []
    for trial in range(n_train_per_class):
        for true_class in train_classes:
            chunks = train_dict[true_class]
            if trial >= len(chunks):
                continue
            features = encode_sensor(chunks[trial], encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz
            # Sample readout spike counts before
            r_before = np.array(mon_readout.count).copy()
            net.run(chunk_dur)
            r_after = np.array(mon_readout.count)
            r_diff = r_after - r_before
            winner = int(np.argmax(r_diff))
            correct = (winner == true_class)
            train_history.append(correct)
            # Apply reward: positive for correct readout, negative for wrong
            # Reward modulates eligibility-based weight update
            reward_value = 1.0 if correct else -0.5
            # Manually apply: w += reward * eligibility (clamped)
            syn_hid_ro.w = np.clip(np.array(syn_hid_ro.w) + reward_value * 0.005 * np.array(syn_hid_ro.e),
                                    0, 2.0)

    # Test (no reward)
    test_classes = list(test_dict.keys())
    accuracies = {}
    for true_class in test_classes:
        correct = 0
        total = 0
        for chunk in test_dict[true_class][:n_test_per_class]:
            features = encode_sensor(chunk, encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz
            r_before = np.array(mon_readout.count).copy()
            net.run(chunk_dur)
            r_after = np.array(mon_readout.count)
            r_diff = r_after - r_before
            winner = int(np.argmax(r_diff))
            if winner == true_class:
                correct += 1
            total += 1
        accuracies[true_class] = correct / max(total, 1)

    train_late_acc = sum(train_history[-50:]) / 50 if len(train_history) >= 50 else 0.0

    return {
        "accuracies": accuracies,
        "train_late_accuracy": train_late_acc,
        "final_W_hidden_readout_mean": float(np.mean(syn_hid_ro.w)),
        "final_W_hidden_readout_std": float(np.std(syn_hid_ro.w)),
        "total_hidden_spikes": int(len(mon_hidden.i)),
        "total_readout_spikes": int(len(mon_readout.i)),
    }

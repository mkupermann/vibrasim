"""Brian2 cortical-density 4-layer substrate — Phase B basis.

After Phase A proved minimal Brian2 SNN (200 neurons) reaches 4 of 7
Stufen, Phase B aims for COMPLETENESS: cortical-style architecture
with realistic E:I balance, recurrent dynamics, layered hierarchy,
and feedback. Mac M-series memory cap forces neuron count compromise.

Architecture (loosely after Markram-Heuvel 2015 cortical microcircuit):
  L4 (input/granular):      5000 E + 1250 I
  L2/3 (local processing):  6000 E + 1500 I
  L5 (output):              5000 E + 1250 I
  L6 (feedback):            4000 E + 1000 I
  Total:                    20 000 E + 5 000 I = 25 000 neurons

Connectivity (~25M synapses total ≈ 2-3GB):
  Within-layer recurrent E→E: 5%
  Within-layer E↔I: 20% / 30% (lat. inhibition)
  Feedforward L4→L2/3, L2/3→L5: 10%
  Feedback L6→L4: 5% (predictive coding)
  STDP on all excitatory pathways

Plasticity:
  STDP everywhere on E→E pathways
  Homeostatic intrinsic plasticity (target firing rate via threshold drift)
  No reward signal (this BET is about hierarchical learning, not agency)

Reference: Diehl & Cook 2015 (SNN+STDP), Markram et al. 2015 (cortical micro-
circuit anatomy), Bono & Clopath 2019 (homeostatic plasticity in SNNs).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Brian2CorticalConfig:
    n_input: int = 10
    # E neurons per layer
    n_L4_E: int = 5000
    n_L23_E: int = 6000
    n_L5_E: int = 5000
    n_L6_E: int = 4000
    # I neurons per layer (E:I = 4:1)
    n_L4_I: int = 1250
    n_L23_I: int = 1500
    n_L5_I: int = 1250
    n_L6_I: int = 1000
    # Connection probabilities
    p_rec_EE: float = 0.05     # within-layer E→E
    p_EI: float = 0.20         # within-layer E→I
    p_IE: float = 0.30         # within-layer I→E
    p_ff: float = 0.10         # feedforward
    p_fb: float = 0.05         # feedback (L6→L4)
    p_input: float = 0.30      # input → L4
    input_rate_max_hz: float = 100.0
    chunk_duration_ms: float = 100.0
    rng_seed: int = 0
    # Homeostatic plasticity (Turrigiano 2008): each E neuron's v_thresh drifts
    # toward target firing rate. 0 disables; typical 0.05 mV per spike-excess.
    homeostasis_enabled: bool = False
    homeostasis_target_rate_hz: float = 5.0
    homeostasis_eta_mv: float = 0.05
    homeostasis_thresh_min_mv: float = -60.0
    homeostasis_thresh_max_mv: float = -48.0


def train_and_collect_layer_patterns(train_dict, test_dict, encoder_cfg,
                                     n_train_per_class, n_test_per_class,
                                     cfg: Brian2CorticalConfig):
    from brian2 import (NeuronGroup, PoissonGroup, Synapses, SpikeMonitor,
                        Network, Hz, ms, mV, defaultclock, prefs)
    from world.flux.cognitive_map import encode_sensor

    prefs.codegen.target = 'cython'
    defaultclock.dt = 1.0 * ms

    tau_m = 20 * ms
    tau_e = 5 * ms
    tau_i = 10 * ms
    v_rest = -70 * mV
    v_thresh_init = -54 * mV
    v_reset = -75 * mV
    tau_ref = 5 * ms

    # v_thresh as per-neuron state variable in both modes — homeostatic mode
    # updates it between chunks, non-homeostatic mode leaves it constant.
    eqs_lif = '''
    dv/dt = (-(v - v_rest) + ge*(0*mV - v) + gi*(-80*mV - v)) / tau_m : volt (unless refractory)
    dge/dt = -ge / tau_e : 1
    dgi/dt = -gi / tau_i : 1
    v_thresh : volt
    '''

    def make_E(n):
        ng = NeuronGroup(n, eqs_lif, threshold='v > v_thresh',
                         reset='v = v_reset', refractory=tau_ref, method='euler')
        ng.v = v_rest
        ng.v_thresh = v_thresh_init
        return ng

    def make_I(n):
        ng = NeuronGroup(n, eqs_lif, threshold='v > v_thresh',
                         reset='v = v_reset', refractory=tau_ref, method='euler')
        ng.v = v_rest
        ng.v_thresh = v_thresh_init
        return ng

    input_group = PoissonGroup(cfg.n_input, rates=0 * Hz)
    L4_E = make_E(cfg.n_L4_E);  L4_I = make_I(cfg.n_L4_I)
    L23_E = make_E(cfg.n_L23_E); L23_I = make_I(cfg.n_L23_I)
    L5_E = make_E(cfg.n_L5_E);  L5_I = make_I(cfg.n_L5_I)
    L6_E = make_E(cfg.n_L6_E);  L6_I = make_I(cfg.n_L6_I)

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

    # Separate namespace for recurrent E→E — lower wmax to prevent runaway
    stdp_ns_rec = {'taupre': 20 * ms, 'taupost': 20 * ms,
                   'dApre_val': 0.005, 'dApost_val': -0.006, 'wmax': 0.3}

    def plastic(src, tgt, p, w_lo, w_hi, ns):
        s = Synapses(src, tgt, model=stdp_eqs, on_pre=on_pre, on_post=on_post,
                     namespace=ns)
        s.connect(p=p)
        s.w = f'rand() * {w_hi - w_lo} + {w_lo}'
        return s

    def static_inh(src, tgt, p, w):
        s = Synapses(src, tgt, 'w : 1', on_pre='gi_post += w')
        s.connect(p=p)
        s.w = w
        return s

    def static_exc(src, tgt, p, w):
        s = Synapses(src, tgt, 'w : 1', on_pre='ge_post += w')
        s.connect(p=p)
        s.w = w
        return s

    # Input → L4
    syn_in_L4 = plastic(input_group, L4_E, cfg.p_input, 0.5, 1.5, stdp_ns)

    # Within-layer recurrent E→E (plastic, lower wmax to prevent runaway)
    syn_L4_rec  = plastic(L4_E,  L4_E,  cfg.p_rec_EE, 0.02, 0.1, stdp_ns_rec)
    syn_L23_rec = plastic(L23_E, L23_E, cfg.p_rec_EE, 0.02, 0.1, stdp_ns_rec)
    syn_L5_rec  = plastic(L5_E,  L5_E,  cfg.p_rec_EE, 0.02, 0.1, stdp_ns_rec)
    syn_L6_rec  = plastic(L6_E,  L6_E,  cfg.p_rec_EE, 0.02, 0.1, stdp_ns_rec)

    # Feedforward (plastic)
    syn_L4_L23  = plastic(L4_E,  L23_E, cfg.p_ff, 0.2, 0.5, stdp_ns)
    syn_L23_L5  = plastic(L23_E, L5_E,  cfg.p_ff, 0.2, 0.5, stdp_ns)
    syn_L5_L6   = plastic(L5_E,  L6_E,  cfg.p_ff, 0.2, 0.5, stdp_ns)

    # Feedback L6 → L4 (plastic, predictive)
    syn_L6_L4   = plastic(L6_E,  L4_E,  cfg.p_fb, 0.05, 0.2, stdp_ns)

    # E→I (static excitation)
    syn_L4_EI  = static_exc(L4_E,  L4_I,  cfg.p_EI, 0.5)
    syn_L23_EI = static_exc(L23_E, L23_I, cfg.p_EI, 0.5)
    syn_L5_EI  = static_exc(L5_E,  L5_I,  cfg.p_EI, 0.5)
    syn_L6_EI  = static_exc(L6_E,  L6_I,  cfg.p_EI, 0.5)

    # I→E (static inhibition; lateral)
    syn_L4_IE  = static_inh(L4_I,  L4_E,  cfg.p_IE, 1.0)
    syn_L23_IE = static_inh(L23_I, L23_E, cfg.p_IE, 1.0)
    syn_L5_IE  = static_inh(L5_I,  L5_E,  cfg.p_IE, 1.0)
    syn_L6_IE  = static_inh(L6_I,  L6_E,  cfg.p_IE, 1.0)

    mon_L4  = SpikeMonitor(L4_E)
    mon_L23 = SpikeMonitor(L23_E)
    mon_L5  = SpikeMonitor(L5_E)
    mon_L6  = SpikeMonitor(L6_E)

    all_synapses = [syn_in_L4,
                    syn_L4_rec, syn_L23_rec, syn_L5_rec, syn_L6_rec,
                    syn_L4_L23, syn_L23_L5, syn_L5_L6, syn_L6_L4,
                    syn_L4_EI, syn_L23_EI, syn_L5_EI, syn_L6_EI,
                    syn_L4_IE, syn_L23_IE, syn_L5_IE, syn_L6_IE]
    all_groups = [input_group,
                  L4_E, L4_I, L23_E, L23_I, L5_E, L5_I, L6_E, L6_I,
                  mon_L4, mon_L23, mon_L5, mon_L6]
    net = Network(*(all_groups + all_synapses))

    chunk_dur = cfg.chunk_duration_ms * ms
    chunk_seconds = cfg.chunk_duration_ms / 1000.0
    target_spikes_per_chunk = cfg.homeostasis_target_rate_hz * chunk_seconds

    excitatory_groups_for_homeo = [L4_E, L23_E, L5_E, L6_E]
    monitors_for_homeo = [mon_L4, mon_L23, mon_L5, mon_L6]

    def _apply_homeostasis(prev_counts):
        if not cfg.homeostasis_enabled:
            return prev_counts
        new_counts = []
        for grp, mon, prev in zip(excitatory_groups_for_homeo, monitors_for_homeo, prev_counts):
            cur = np.array(mon.count)
            diff = cur - prev
            new_counts.append(cur)
            # Excess spikes → raise threshold; deficit → lower
            adj_mv = cfg.homeostasis_eta_mv * (diff - target_spikes_per_chunk)
            new_thresh_mv = (np.array(grp.v_thresh) / 1e-3) + adj_mv
            new_thresh_mv = np.clip(new_thresh_mv,
                                    cfg.homeostasis_thresh_min_mv,
                                    cfg.homeostasis_thresh_max_mv)
            grp.v_thresh = new_thresh_mv * mV
        return new_counts

    # Training (unsupervised STDP + optional homeostasis)
    train_classes = list(train_dict.keys())
    prev_counts = [np.array(m.count).copy() for m in monitors_for_homeo]
    for trial in range(n_train_per_class):
        for class_label in train_classes:
            chunks = train_dict[class_label]
            if trial >= len(chunks):
                continue
            features = encode_sensor(chunks[trial], encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz
            net.run(chunk_dur)
            prev_counts = _apply_homeostasis(prev_counts)

    # Test: collect per-layer patterns per class
    test_classes = list(test_dict.keys())
    L4_p  = {c: [] for c in test_classes}
    L23_p = {c: [] for c in test_classes}
    L5_p  = {c: [] for c in test_classes}
    L6_p  = {c: [] for c in test_classes}
    for k in range(n_test_per_class):
        for class_label in test_classes:
            chunks = test_dict[class_label]
            if k >= len(chunks):
                continue
            features = encode_sensor(chunks[k], encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz
            c4_b  = np.array(mon_L4.count).copy()
            c23_b = np.array(mon_L23.count).copy()
            c5_b  = np.array(mon_L5.count).copy()
            c6_b  = np.array(mon_L6.count).copy()
            net.run(chunk_dur)
            L4_p[class_label].append(np.array(mon_L4.count) - c4_b)
            L23_p[class_label].append(np.array(mon_L23.count) - c23_b)
            L5_p[class_label].append(np.array(mon_L5.count) - c5_b)
            L6_p[class_label].append(np.array(mon_L6.count) - c6_b)

    return {
        "L4_patterns":  {c: np.array(L4_p[c])  for c in test_classes},
        "L23_patterns": {c: np.array(L23_p[c]) for c in test_classes},
        "L5_patterns":  {c: np.array(L5_p[c])  for c in test_classes},
        "L6_patterns":  {c: np.array(L6_p[c])  for c in test_classes},
        "n_synapses_total": sum(int(len(s)) for s in all_synapses),
        "n_synapses_input": int(len(syn_in_L4)),
        "n_synapses_ff": int(len(syn_L4_L23)) + int(len(syn_L23_L5)) + int(len(syn_L5_L6)),
        "n_synapses_fb": int(len(syn_L6_L4)),
        "n_synapses_rec_EE": (int(len(syn_L4_rec)) + int(len(syn_L23_rec))
                              + int(len(syn_L5_rec)) + int(len(syn_L6_rec))),
        "n_synapses_inhib": (int(len(syn_L4_EI)) + int(len(syn_L23_EI))
                             + int(len(syn_L5_EI)) + int(len(syn_L6_EI))
                             + int(len(syn_L4_IE)) + int(len(syn_L23_IE))
                             + int(len(syn_L5_IE)) + int(len(syn_L6_IE))),
        "total_L4_spikes":  int(len(mon_L4.i)),
        "total_L23_spikes": int(len(mon_L23.i)),
        "total_L5_spikes":  int(len(mon_L5.i)),
        "total_L6_spikes":  int(len(mon_L6.i)),
    }

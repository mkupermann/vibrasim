"""Brian2 closed-loop sensorimotor substrate — Stufe 6 of Phase A Proof.

Architecture extends the BET-068 hierarchical substrate with motor
neurons whose activity determines the NEXT input chunk. Closed loop:

  audio_t → L1 → L2 → motor[0..1] → choose audio_{t+1}

Active-inference minimum: substrate's spike-driven action shapes its
own future input. After training, substrate develops stable preference
for one class (or oscillates) — its "behavior" emerges from learned
weights, not from external supervision.

Brain inspiration:
  - Cortical sensorimotor loop (sensory → premotor → motor → action)
  - Active inference (Friston FEP) — substrate samples its environment
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Brian2ClosedLoopConfig:
    n_input: int = 10
    n_layer1: int = 100
    n_layer2: int = 50
    n_inh1: int = 25
    n_inh2: int = 12
    n_motor: int = 2
    input_rate_max_hz: float = 100.0
    chunk_duration_ms: float = 100.0
    rng_seed: int = 0


def train_and_run_closed_loop(train_chunks_by_class, test_chunks_by_class,
                              encoder_cfg, n_train_per_class, n_closed_loop_ticks,
                              cfg: Brian2ClosedLoopConfig):
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

    L1 = NeuronGroup(cfg.n_layer1, eqs_lif, threshold='v > v_thresh',
                     reset='v = v_reset', refractory=tau_ref, method='euler')
    L1.v = v_rest
    Inh1 = NeuronGroup(cfg.n_inh1, eqs_lif, threshold='v > v_thresh',
                       reset='v = v_reset', refractory=tau_ref, method='euler')
    Inh1.v = v_rest
    L2 = NeuronGroup(cfg.n_layer2, eqs_lif, threshold='v > v_thresh',
                     reset='v = v_reset', refractory=tau_ref, method='euler')
    L2.v = v_rest
    Inh2 = NeuronGroup(cfg.n_inh2, eqs_lif, threshold='v > v_thresh',
                       reset='v = v_reset', refractory=tau_ref, method='euler')
    Inh2.v = v_rest
    Motor = NeuronGroup(cfg.n_motor, eqs_lif, threshold='v > v_thresh',
                        reset='v = v_reset', refractory=tau_ref, method='euler')
    Motor.v = v_rest

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

    syn_in_L1 = Synapses(input_group, L1, model=stdp_eqs, on_pre=on_pre,
                          on_post=on_post, namespace=stdp_ns)
    syn_in_L1.connect(p=0.5)
    syn_in_L1.w = rng.uniform(0.5, 1.5, len(syn_in_L1))

    syn_L1_L2 = Synapses(L1, L2, model=stdp_eqs, on_pre=on_pre,
                          on_post=on_post, namespace=stdp_ns)
    syn_L1_L2.connect(p=0.3)
    syn_L1_L2.w = rng.uniform(0.3, 0.7, len(syn_L1_L2))

    # L2 → Motor: plastic STDP — substrate's "decision pathway"
    syn_L2_Motor = Synapses(L2, Motor, model=stdp_eqs, on_pre=on_pre,
                             on_post=on_post, namespace=stdp_ns)
    syn_L2_Motor.connect(True)  # all-to-all
    syn_L2_Motor.w = rng.uniform(0.2, 0.5, len(syn_L2_Motor))

    syn_L1_Inh1 = Synapses(L1, Inh1, 'w : 1', on_pre='ge_post += w')
    syn_L1_Inh1.connect(p=0.3)
    syn_L1_Inh1.w = 0.5
    syn_Inh1_L1 = Synapses(Inh1, L1, 'w : 1', on_pre='gi_post += w')
    syn_Inh1_L1.connect(p=0.4)
    syn_Inh1_L1.w = 1.0

    syn_L2_Inh2 = Synapses(L2, Inh2, 'w : 1', on_pre='ge_post += w')
    syn_L2_Inh2.connect(p=0.3)
    syn_L2_Inh2.w = 0.5
    syn_Inh2_L2 = Synapses(Inh2, L2, 'w : 1', on_pre='gi_post += w')
    syn_Inh2_L2.connect(p=0.4)
    syn_Inh2_L2.w = 1.0

    mon_L2 = SpikeMonitor(L2)
    mon_Motor = SpikeMonitor(Motor)
    net = Network(input_group, L1, Inh1, L2, Inh2, Motor,
                  syn_in_L1, syn_L1_L2, syn_L2_Motor,
                  syn_L1_Inh1, syn_Inh1_L1, syn_L2_Inh2, syn_Inh2_L2,
                  mon_L2, mon_Motor)

    chunk_dur = cfg.chunk_duration_ms * ms

    # PHASE 1: Training (open-loop, present classes alternately)
    train_classes = list(train_chunks_by_class.keys())
    for trial in range(n_train_per_class):
        for class_label in train_classes:
            chunks = train_chunks_by_class[class_label]
            if trial >= len(chunks):
                continue
            features = encode_sensor(chunks[trial], encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz
            net.run(chunk_dur)

    # PHASE 2: Closed loop — substrate's motor activity selects next class
    motor_choices = []
    class_history = []
    motor_by_class = {c: [] for c in train_classes}

    # Start with class 0
    current_class = train_classes[0]
    test_idx = {c: 0 for c in train_classes}

    for tick in range(n_closed_loop_ticks):
        chunks = test_chunks_by_class[current_class]
        idx = test_idx[current_class] % len(chunks)
        test_idx[current_class] += 1
        features = encode_sensor(chunks[idx], encoder_cfg)
        input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
        input_group.rates = input_rates_hz * Hz

        m_before = np.array(mon_Motor.count).copy()
        net.run(chunk_dur)
        m_after = np.array(mon_Motor.count)
        m_diff = m_after - m_before  # spikes per motor neuron this tick

        # Record motor firing for this class
        motor_by_class[current_class].append(m_diff.copy())
        class_history.append(current_class)

        # Substrate's "choice": motor neuron with highest firing rate determines next class
        winner_motor = int(np.argmax(m_diff))
        # Map motor → class: motor[i] → class index i mod n_classes
        next_class = train_classes[winner_motor % len(train_classes)]
        motor_choices.append(winner_motor)
        current_class = next_class

    # Analyze: motor preference for each class
    motor_by_class_arr = {c: np.array(motor_by_class[c]) for c in train_classes if motor_by_class[c]}

    # Selectivity: does motor[i] fire more for class i than for class !=i?
    motor_class_means = {}
    for c, m_array in motor_by_class_arr.items():
        motor_class_means[c] = m_array.mean(axis=0)  # mean spikes per motor neuron when class c present

    # Stability: count class transitions
    if len(class_history) > 1:
        transitions = sum(1 for i in range(1, len(class_history))
                          if class_history[i] != class_history[i-1])
        stability = 1.0 - (transitions / max(len(class_history) - 1, 1))
    else:
        stability = 0.0

    # Class dwell fractions
    dwell = {}
    for c in train_classes:
        dwell[c] = class_history.count(c) / max(len(class_history), 1)

    return {
        "motor_class_means": motor_class_means,
        "class_history": class_history,
        "motor_choices": motor_choices,
        "stability": stability,
        "dwell": dwell,
        "total_L2_spikes": int(len(mon_L2.i)),
        "total_motor_spikes": int(len(mon_Motor.i)),
        "final_W_L2_Motor_mean": float(np.mean(syn_L2_Motor.w)),
        "final_W_L2_Motor_std": float(np.std(syn_L2_Motor.w)),
    }

"""Brian2 critic-actor R-STDP — Frémaux & Gerstner 2016 architecture.

Fixes the credit-assignment problem from BET-067 (raw reward applied
uniformly) and BET-071 (motor neurons don't class-differentiate without
shaped plasticity).

Architecture:
  Input PoissonGroup (10) → Hidden LIF (100) [+Inh 25 lateral inhibition]
                            ↓
                            ↘ → Actor LIF (n_classes) — output neurons
                              → Critic LIF (10) — value estimation pop

After each trial:
  reward r = +1 if actor[true_class] fired strongest else 0
  V = critic population mean firing rate (proxy for value estimate)
  TD = r - V

  Δw_hidden_actor = η_actor · TD · eligibility   (per synapse)
  Δw_hidden_critic = η_critic · (r - V)            (drives critic toward r)

Eligibility per synapse decays with τ_elig, increments on pre·post
coincidence (STDP kernel). So only synapses with recent meaningful
pre→post correlation receive the TD-modulated update.

Reference: Frémaux & Gerstner 2016 Front. Neural Circuits, "Neuromodulated
spike-timing-dependent plasticity, and theory of three-factor learning rules"
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Brian2CriticActorConfig:
    n_input: int = 10
    n_hidden: int = 100
    n_inhibitory: int = 25
    n_actor: int = 2
    n_critic: int = 10
    input_rate_max_hz: float = 100.0
    chunk_duration_ms: float = 100.0
    eta_actor: float = 0.05
    eta_critic: float = 0.02
    rng_seed: int = 0


def train_and_test(train_dict, test_dict, encoder_cfg, n_train_per_class, n_test_per_class,
                   cfg: Brian2CriticActorConfig):
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
    hidden = NeuronGroup(cfg.n_hidden, eqs_lif, threshold='v > v_thresh',
                         reset='v = v_reset', refractory=tau_ref, method='euler')
    hidden.v = v_rest
    inh = NeuronGroup(cfg.n_inhibitory, eqs_lif, threshold='v > v_thresh',
                      reset='v = v_reset', refractory=tau_ref, method='euler')
    inh.v = v_rest
    actor = NeuronGroup(cfg.n_actor, eqs_lif, threshold='v > v_thresh',
                        reset='v = v_reset', refractory=tau_ref, method='euler')
    actor.v = v_rest
    critic = NeuronGroup(cfg.n_critic, eqs_lif, threshold='v > v_thresh',
                         reset='v = v_reset', refractory=tau_ref, method='euler')
    critic.v = v_rest

    stdp_eqs = '''
    w : 1
    dApre/dt = -Apre / taupre : 1 (event-driven)
    dApost/dt = -Apost / taupost : 1 (event-driven)
    '''
    on_pre_simple = '''
    ge += w
    Apre += dApre_val
    w = clip(w + Apost, 0, wmax)
    '''
    on_post_simple = '''
    Apost += dApost_val
    w = clip(w + Apre, 0, wmax)
    '''
    stdp_ns = {'taupre': 20 * ms, 'taupost': 20 * ms,
               'dApre_val': 0.01, 'dApost_val': -0.012, 'wmax': 2.0}

    rng = np.random.default_rng(cfg.rng_seed)

    # Input → Hidden: standard STDP (unsupervised feature learning)
    syn_in_hid = Synapses(input_group, hidden, model=stdp_eqs,
                          on_pre=on_pre_simple, on_post=on_post_simple,
                          namespace=stdp_ns)
    syn_in_hid.connect(p=0.5)
    syn_in_hid.w = rng.uniform(0.5, 1.5, len(syn_in_hid))

    # Hidden → Inh, Inh → Hidden: lateral inhibition for sparsity
    syn_hid_inh = Synapses(hidden, inh, 'w : 1', on_pre='ge_post += w')
    syn_hid_inh.connect(p=0.3)
    syn_hid_inh.w = 0.5
    syn_inh_hid = Synapses(inh, hidden, 'w : 1', on_pre='gi_post += w')
    syn_inh_hid.connect(p=0.4)
    syn_inh_hid.w = 1.0

    # Hidden → Actor: eligibility-trace plasticity, modulated externally by TD
    rstdp_eqs = '''
    w : 1
    dApre/dt = -Apre / taupre : 1 (event-driven)
    dApost/dt = -Apost / taupost : 1 (event-driven)
    delig/dt = -elig / tau_elig : 1 (clock-driven)
    '''
    on_pre_rstdp = '''
    ge_post += w
    Apre += dApre_val
    elig += Apost
    '''
    on_post_rstdp = '''
    Apost += dApost_val
    elig += Apre
    '''
    rstdp_ns = {'taupre': 20 * ms, 'taupost': 20 * ms,
                'dApre_val': 0.01, 'dApost_val': -0.005,
                'tau_elig': 500 * ms}

    syn_hid_actor = Synapses(hidden, actor, model=rstdp_eqs,
                             on_pre=on_pre_rstdp, on_post=on_post_rstdp,
                             namespace=rstdp_ns, method='euler')
    syn_hid_actor.connect(True)  # all-to-all (200 synapses)
    syn_hid_actor.w = rng.uniform(0.3, 0.7, len(syn_hid_actor))

    # Hidden → Critic: also eligibility-trace, but modulated by raw reward
    syn_hid_critic = Synapses(hidden, critic, model=rstdp_eqs,
                              on_pre=on_pre_rstdp, on_post=on_post_rstdp,
                              namespace=rstdp_ns, method='euler')
    syn_hid_critic.connect(p=0.5)
    syn_hid_critic.w = rng.uniform(0.3, 0.7, len(syn_hid_critic))

    # Actor lateral inhibition (winner-take-all between actor neurons)
    syn_actor_lat = Synapses(actor, actor, 'w : 1',
                             on_pre='gi_post += w * int(i != j)')
    syn_actor_lat.connect(condition='i != j')
    syn_actor_lat.w = 0.5

    mon_hidden = SpikeMonitor(hidden)
    mon_actor = SpikeMonitor(actor)
    mon_critic = SpikeMonitor(critic)
    net = Network(input_group, hidden, inh, actor, critic,
                  syn_in_hid, syn_hid_inh, syn_inh_hid,
                  syn_hid_actor, syn_hid_critic, syn_actor_lat,
                  mon_hidden, mon_actor, mon_critic)

    chunk_dur = cfg.chunk_duration_ms * ms

    # Training with TD-modulated plasticity
    train_classes = list(train_dict.keys())
    train_history = []
    critic_history = []
    td_history = []

    for trial in range(n_train_per_class):
        for true_class in train_classes:
            chunks = train_dict[true_class]
            if trial >= len(chunks):
                continue
            features = encode_sensor(chunks[trial], encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz

            a_before = np.array(mon_actor.count).copy()
            c_before = np.array(mon_critic.count).copy()
            net.run(chunk_dur)
            a_after = np.array(mon_actor.count)
            c_after = np.array(mon_critic.count)
            a_diff = a_after - a_before
            c_diff = c_after - c_before

            winner = int(np.argmax(a_diff))
            correct = (winner == true_class)
            train_history.append(correct)
            reward = 1.0 if correct else 0.0

            # Critic value estimate (normalize critic firing to [0, ~1])
            v_estimate = float(np.sum(c_diff)) / (cfg.n_critic * 5.0)  # rough scale
            v_estimate = min(max(v_estimate, 0.0), 1.0)
            critic_history.append(v_estimate)

            # TD error
            td = reward - v_estimate
            td_history.append(td)

            # Apply TD-modulated update to actor synapses
            actor_idx_post = np.array(syn_hid_actor.j)
            elig_actor = np.array(syn_hid_actor.elig)

            # Only synapses targeting the true_class actor neuron get full reward credit;
            # others get TD penalty for wrong-winner case.
            # But simpler: use TD * elig uniformly — the eligibility itself encodes pre·post,
            # which differs per neuron.
            dw_actor = cfg.eta_actor * td * elig_actor
            syn_hid_actor.w = np.clip(np.array(syn_hid_actor.w) + dw_actor, 0, 2.0)

            # Critic: drive toward observed reward
            elig_critic = np.array(syn_hid_critic.elig)
            dw_critic = cfg.eta_critic * (reward - v_estimate) * elig_critic
            syn_hid_critic.w = np.clip(np.array(syn_hid_critic.w) + dw_critic, 0, 2.0)

    # Test (no plasticity modulation)
    test_classes = list(test_dict.keys())
    accuracies = {}
    confusion = np.zeros((len(test_classes), len(test_classes)), dtype=int)
    for true_class in test_classes:
        correct = 0
        total = 0
        for chunk in test_dict[true_class][:n_test_per_class]:
            features = encode_sensor(chunk, encoder_cfg)
            input_rates_hz = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
            input_group.rates = input_rates_hz * Hz
            a_before = np.array(mon_actor.count).copy()
            net.run(chunk_dur)
            a_after = np.array(mon_actor.count)
            a_diff = a_after - a_before
            winner = int(np.argmax(a_diff))
            confusion[true_class, winner] += 1
            if winner == true_class:
                correct += 1
            total += 1
        accuracies[true_class] = correct / max(total, 1)

    train_late_acc = sum(train_history[-50:]) / 50 if len(train_history) >= 50 else 0.0
    early_acc = sum(train_history[:50]) / 50 if len(train_history) >= 50 else 0.0

    return {
        "accuracies": accuracies,
        "balanced_accuracy": float(np.mean(list(accuracies.values()))),
        "train_early_accuracy": early_acc,
        "train_late_accuracy": train_late_acc,
        "td_history_mean_first_50": float(np.mean(td_history[:50])) if len(td_history) >= 50 else 0.0,
        "td_history_mean_last_50": float(np.mean(td_history[-50:])) if len(td_history) >= 50 else 0.0,
        "critic_estimate_first_50": float(np.mean(critic_history[:50])) if len(critic_history) >= 50 else 0.0,
        "critic_estimate_last_50": float(np.mean(critic_history[-50:])) if len(critic_history) >= 50 else 0.0,
        "confusion_matrix": confusion.tolist(),
        "final_W_hidden_actor_mean": float(np.mean(syn_hid_actor.w)),
        "final_W_hidden_actor_std": float(np.std(syn_hid_actor.w)),
        "final_W_hidden_critic_mean": float(np.mean(syn_hid_critic.w)),
        "total_hidden_spikes": int(len(mon_hidden.i)),
        "total_actor_spikes": int(len(mon_actor.i)),
        "total_critic_spikes": int(len(mon_critic.i)),
    }

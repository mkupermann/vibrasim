"""Izhikevich neurons (2003) + R-STDP (Izhikevich 2007).

Brain-faithful primitives only:
  - Izhikevich quadratic integrate-and-fire model (matches diverse
    cortical firing patterns with 2 ODEs + 4 parameters)
  - Spike-Timing-Dependent Plasticity (Bi & Poo 1998)
  - Eligibility traces (Sutton 1988 / Izhikevich 2007 for STDP variant)
  - Dopamine-like reward signal modulates plasticity

Substrate primitives only. No statistical pattern matching, no
hand-designed algebra, no random fixed basis. Synapses develop
themselves via spike-timing and reward.

Izhikevich 2003 model:
  dv/dt = 0.04*v² + 5*v + 140 - u + I
  du/dt = a*(b*v - u)
  if v >= 30: spike → v = c, u = u + d

Cortical regular-spiking defaults (Izhikevich 2003 Fig 1):
  a=0.02, b=0.2, c=-65, d=8

R-STDP (Izhikevich 2007 Cerebral Cortex):
  - eligibility trace e[i,j](t) builds up via STDP
  - e decays with τ_e
  - ΔW[i,j] = α * R(t) * e[i,j](t)
  - reward globally broadcast, but only eligible synapses change

References:
  - Izhikevich EM, Simple Model of Spiking Neurons, IEEE TNN 2003
  - Izhikevich EM, Solving the distal reward problem through linkage
    of STDP and dopamine signaling, Cerebral Cortex 2007
  - Bi GQ & Poo MM, Synaptic modifications by spike timing, J Neurosci 1998
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class IzhikevichRSTDPConfig:
    n_input: int = 20
    n_hidden: int = 80
    n_output: int = 2          # for binary class task
    n_inhibitory: int = 20     # 10:1 E:I-ish; provides stabilizing inhibition
    # Izhikevich regular-spiking
    a_e: float = 0.02
    b_e: float = 0.2
    c_e: float = -65.0
    d_e: float = 8.0
    # Inhibitory (fast-spiking)
    a_i: float = 0.1
    b_i: float = 0.2
    c_i: float = -65.0
    d_i: float = 2.0
    # Synaptic weights
    w_init_exc: float = 5.0
    w_init_inh: float = -5.0
    w_max: float = 20.0
    w_min: float = -20.0
    # Connection densities
    p_input_to_hidden: float = 0.3
    p_hidden_to_hidden: float = 0.1
    p_hidden_to_output: float = 0.3
    p_inhibitory_to_hidden: float = 0.5
    # STDP
    stdp_A_plus: float = 0.05
    stdp_A_minus: float = 0.055
    stdp_tau: float = 20.0
    # Eligibility trace
    eligibility_tau: float = 1000.0  # ms — long enough for delayed reward
    # Input current scale
    input_drive: float = 20.0
    # Simulation
    dt_ms: float = 1.0
    rng_seed: int = 0


def initialise(cfg: IzhikevichRSTDPConfig) -> dict:
    rng = np.random.default_rng(cfg.rng_seed)
    n_in = cfg.n_input
    n_h = cfg.n_hidden
    n_o = cfg.n_output
    n_inh = cfg.n_inhibitory
    n_total = n_in + n_h + n_o + n_inh
    # Neuron parameters per neuron
    a = np.zeros(n_total, dtype=np.float64)
    b = np.zeros(n_total, dtype=np.float64)
    c = np.zeros(n_total, dtype=np.float64)
    d = np.zeros(n_total, dtype=np.float64)
    is_exc = np.ones(n_total, dtype=bool)
    # Excitatory neurons (input + hidden + output)
    a[:n_in + n_h + n_o] = cfg.a_e
    b[:n_in + n_h + n_o] = cfg.b_e
    c[:n_in + n_h + n_o] = cfg.c_e
    d[:n_in + n_h + n_o] = cfg.d_e
    # Inhibitory neurons (last n_inh)
    a[n_in + n_h + n_o:] = cfg.a_i
    b[n_in + n_h + n_o:] = cfg.b_i
    c[n_in + n_h + n_o:] = cfg.c_i
    d[n_in + n_h + n_o:] = cfg.d_i
    is_exc[n_in + n_h + n_o:] = False
    # Initial state
    v = np.full(n_total, cfg.c_e, dtype=np.float64)
    u = b * v
    # Connectivity + weights
    W = np.zeros((n_total, n_total), dtype=np.float64)
    # input → hidden (excitatory)
    in_idx = np.arange(n_in)
    h_idx = np.arange(n_in, n_in + n_h)
    o_idx = np.arange(n_in + n_h, n_in + n_h + n_o)
    inh_idx = np.arange(n_in + n_h + n_o, n_total)
    for i in in_idx:
        targets = rng.choice(h_idx, max(1, int(n_h * cfg.p_input_to_hidden)), replace=False)
        for j in targets:
            W[i, j] = cfg.w_init_exc * rng.uniform(0.5, 1.5)
    # hidden → hidden (sparse recurrent)
    for i in h_idx:
        targets = rng.choice(h_idx, max(1, int(n_h * cfg.p_hidden_to_hidden)), replace=False)
        for j in targets:
            if i != j:
                W[i, j] = cfg.w_init_exc * rng.uniform(0.5, 1.5)
    # hidden → output
    for i in h_idx:
        targets = rng.choice(o_idx, max(1, int(n_o * cfg.p_hidden_to_output)), replace=False)
        for j in targets:
            W[i, j] = cfg.w_init_exc * rng.uniform(0.5, 1.5)
    # inhibitory ← hidden (excitatory recurrent inhibition)
    for i in h_idx:
        targets = rng.choice(inh_idx, max(1, int(n_inh * 0.3)), replace=False)
        for j in targets:
            W[i, j] = cfg.w_init_exc * rng.uniform(0.5, 1.5)
    # inhibitory → hidden (inhibitory feedback)
    for i in inh_idx:
        targets = rng.choice(h_idx, max(1, int(n_h * cfg.p_inhibitory_to_hidden)), replace=False)
        for j in targets:
            W[i, j] = cfg.w_init_inh * rng.uniform(0.5, 1.5)
    return {
        "cfg": cfg,
        "n_in": n_in, "n_h": n_h, "n_o": n_o, "n_inh": n_inh, "n_total": n_total,
        "is_exc": is_exc, "a": a, "b": b, "c": c, "d": d,
        "v": v, "u": u, "W": W,
        "input_idx": in_idx, "hidden_idx": h_idx, "output_idx": o_idx, "inh_idx": inh_idx,
        "last_spike": np.full(n_total, -1e9, dtype=np.float64),
        "eligibility": np.zeros_like(W),
        "global_time_ms": 0.0,
        "spike_history": np.zeros(n_total, dtype=np.int64),
    }


def step(state: dict, input_current: np.ndarray, reward: float = 0.0) -> np.ndarray:
    """One simulation step. input_current: shape (n_input,) external drive.
    reward: dopamine-like signal at this step (typically 0, occasionally 1 or -1).
    Returns boolean array of which neurons spiked."""
    cfg = state["cfg"]
    n_total = state["n_total"]
    # Compose I per neuron: input neurons get external current, others get synaptic
    I_ext = np.zeros(n_total, dtype=np.float64)
    I_ext[state["input_idx"]] = input_current * cfg.input_drive
    # Synaptic current from previous spikes (delayed by 1 step for stability)
    # For simplicity: weight * spike_in_last_step
    # We compute spikes first, then use them for next-step synaptic
    # but here, use last-step's spikes effect on current step
    # Initialize from previous step's last_spikes
    spikes_prev = state.get("last_step_spikes", np.zeros(n_total, dtype=bool))
    I_syn = state["W"].T @ spikes_prev.astype(np.float64)
    I_total = I_ext + I_syn
    # Izhikevich dynamics (Euler with dt=cfg.dt_ms but typically half-step for stability)
    # Single-step approximation
    dv = 0.04 * state["v"]**2 + 5 * state["v"] + 140 - state["u"] + I_total
    state["v"] += dv * cfg.dt_ms
    du = state["a"] * (state["b"] * state["v"] - state["u"])
    state["u"] += du * cfg.dt_ms
    # Spikes
    spikes = state["v"] >= 30.0
    if spikes.any():
        spike_idx = np.where(spikes)[0]
        # Reset
        state["v"][spike_idx] = state["c"][spike_idx]
        state["u"][spike_idx] = state["u"][spike_idx] + state["d"][spike_idx]
        # STDP eligibility: pre→post LTP, post→pre LTD
        t = state["global_time_ms"]
        for post in spike_idx:
            # LTP: synapses where pre fired recently
            dt = t - state["last_spike"]  # shape (n_total,) per pre
            ltp = np.where((dt > 0) & (dt < 5 * cfg.stdp_tau),
                           cfg.stdp_A_plus * np.exp(-dt / cfg.stdp_tau), 0.0)
            state["eligibility"][:, post] += ltp
            # LTD: synapses where post is acting as pre that fires after others
            # (skip — handled symmetrically below)
        # LTD: for synapses where pre fires now, decrement based on previous post timing
        for pre in spike_idx:
            dt = t - state["last_spike"]  # how long since post fired
            ltd = np.where((dt > 0) & (dt < 5 * cfg.stdp_tau),
                           -cfg.stdp_A_minus * np.exp(-dt / cfg.stdp_tau), 0.0)
            state["eligibility"][pre, :] += ltd
        state["last_spike"][spike_idx] = t
        state["spike_history"] += spikes.astype(np.int64)
    # Eligibility decay
    state["eligibility"] *= np.exp(-cfg.dt_ms / cfg.eligibility_tau)
    # R-STDP: apply weight update gated by reward
    if reward != 0.0:
        state["W"] += reward * state["eligibility"]
        # Sign-preserving clip (excitatory stays >=0, inhibitory <=0)
        W_signs = np.sign(state["W"])  # nondeterministic for newly-changed sign synapses
        # Just clip absolute magnitude
        state["W"] = np.clip(state["W"], cfg.w_min, cfg.w_max)
    state["last_step_spikes"] = spikes
    state["global_time_ms"] += cfg.dt_ms
    return spikes

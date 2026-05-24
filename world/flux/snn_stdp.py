"""Spiking Neural Network with Spike-Timing-Dependent Plasticity.

Brain-faithful substrate. NOT statistical pattern matching. Information
encoded in spike timing. Learning via Hebbian STDP rule based on
relative pre/post-spike timing.

Genuinely different from LLM (transformer/attention) AND from prior
substrate (SOM/Replay/N-gram). Closer to biological neural computation
as understood pre-2020 neuroscience.

Architecture:
  Input layer: N_input Leaky Integrate-and-Fire (LIF) neurons.
              Each receives ONE feature dim of encoded audio as
              continuous current. Firing rate ∝ feature value.
  Hidden layer: N_hidden LIF neurons. Receive weighted spike inputs
              from input layer. Weights W[input,hidden] updated via STDP.

LIF neuron dynamics:
  τ_m * dV/dt = -(V - V_rest) + R * I_in(t)
  if V > V_thresh: emit spike, V → V_reset, refractory τ_ref

STDP rule (Bi & Poo 1998 form):
  if post-spike at time t_post, pre-spike at t_pre, Δt = t_post - t_pre:
    if Δt > 0: ΔW = +A_+ * exp(-Δt / τ_+)   (LTP, causal)
    if Δt < 0: ΔW = -A_- * exp(+Δt / τ_-)   (LTD, anti-causal)

References:
  - Bi GQ & Poo MM, Synaptic modifications in cultured hippocampal
    neurons: dependence on spike timing, synaptic strength, and
    postsynaptic cell type, J Neurosci 1998
  - Maass W, Networks of spiking neurons: the third generation of
    neural network models, Neural Networks 1997
  - Markram H et al, Regulation of synaptic efficacy by coincidence
    of postsynaptic APs and EPSPs, Science 1997 (original STDP)
  - Song S, Miller KD, Abbott LF, Competitive Hebbian learning through
    spike-timing-dependent synaptic plasticity, Nat Neurosci 2000
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from world.flux.cognitive_map import encode_sensor


@dataclass
class SNNConfig:
    """All parameters set to biologically-plausible defaults."""
    n_input: int = 10
    n_hidden: int = 50
    n_features: int = 10
    # LIF dynamics
    v_rest: float = -70.0      # mV
    v_thresh: float = -55.0    # mV (threshold)
    v_reset: float = -75.0     # mV (after spike)
    tau_m: float = 20.0        # membrane time constant (ms)
    tau_ref: int = 5           # refractory ticks
    r_membrane: float = 1.0    # input resistance scaling
    # Input encoding
    input_scale: float = 200.0  # converts feature value to LIF input current
    hidden_synapse_gain: float = 400.0  # synaptic current per unit weight per spike
    weight_normalization_sum: float = 2.0  # incoming weight sum per hidden neuron (homeostasis)
    # STDP
    stdp_A_plus: float = 0.005    # LTP magnitude
    stdp_A_minus: float = 0.0055  # LTD magnitude (slightly stronger for stability)
    stdp_tau_plus: float = 20.0    # LTP time window (ms)
    stdp_tau_minus: float = 20.0   # LTD time window (ms)
    w_init_scale: float = 0.5   # initial weight scale
    w_max: float = 1.0          # hard upper bound on weights
    w_min: float = 0.0          # hard lower bound (excitatory only)
    # Simulation
    dt_ms: float = 1.0         # 1ms simulation step
    chunk_duration_ms: int = 50  # process each audio chunk for 50ms
    sample_rate_hz: int = 16000
    samples_per_tick: int = 16
    fft_bands: int = 8
    rng_seed: int = 0


def initialise(cfg: SNNConfig) -> dict:
    rng = np.random.default_rng(cfg.rng_seed)
    return {
        "W": rng.uniform(0, cfg.w_init_scale, (cfg.n_input, cfg.n_hidden)).astype(np.float64),
        "V_input": np.full(cfg.n_input, cfg.v_rest, dtype=np.float64),
        "V_hidden": np.full(cfg.n_hidden, cfg.v_rest, dtype=np.float64),
        "refrac_input": np.zeros(cfg.n_input, dtype=np.int64),
        "refrac_hidden": np.zeros(cfg.n_hidden, dtype=np.int64),
        "last_spike_input": np.full(cfg.n_input, -1e9, dtype=np.float64),
        "last_spike_hidden": np.full(cfg.n_hidden, -1e9, dtype=np.float64),
        "global_time_ms": 0.0,
        "total_input_spikes": 0,
        "total_hidden_spikes": 0,
        "spike_rates_hidden": np.zeros(cfg.n_hidden, dtype=np.int64),
    }


def _lif_step(V, refrac, I_in, cfg):
    """One simulation step for a layer. Returns (V_new, refrac_new, spikes_bool)."""
    not_refractory = refrac == 0
    dV = (-(V - cfg.v_rest) + cfg.r_membrane * I_in) / cfg.tau_m * cfg.dt_ms
    V_new = np.where(not_refractory, V + dV, V)
    spikes = (V_new > cfg.v_thresh) & not_refractory
    V_new = np.where(spikes, cfg.v_reset, V_new)
    refrac_new = np.where(spikes, cfg.tau_ref, np.maximum(refrac - 1, 0))
    return V_new, refrac_new, spikes


def _stdp_update(W, pre_spikes, post_spikes, last_pre, last_post, t_ms, cfg):
    """Apply STDP rule to W based on current spikes + last-spike times."""
    # When post fires at t_ms, look at last_pre per input neuron
    # When pre fires at t_ms, look at last_post per hidden neuron
    if post_spikes.any():
        for j in np.where(post_spikes)[0]:
            dt = t_ms - last_pre  # shape (n_input,), positive if pre before post (LTP)
            ltp = np.where(dt > 0, cfg.stdp_A_plus * np.exp(-dt / cfg.stdp_tau_plus), 0.0)
            W[:, j] = np.clip(W[:, j] + ltp, cfg.w_min, cfg.w_max)
    if pre_spikes.any():
        for i in np.where(pre_spikes)[0]:
            dt = t_ms - last_post  # shape (n_hidden,), positive if post before pre (LTD)
            ltd = np.where(dt > 0, cfg.stdp_A_minus * np.exp(-dt / cfg.stdp_tau_minus), 0.0)
            W[i, :] = np.clip(W[i, :] - ltd, cfg.w_min, cfg.w_max)


def step(state: dict, audio_chunk: np.ndarray, cfg: SNNConfig) -> None:
    """Process one audio chunk for chunk_duration_ms simulation time."""
    if audio_chunk.size == 0:
        return
    features = encode_sensor(audio_chunk, cfg)
    # Map features to LIF input currents (rectified positive values)
    I_input_layer = np.maximum(features, 0.0) * cfg.input_scale

    n_steps = int(cfg.chunk_duration_ms / cfg.dt_ms)
    for _ in range(n_steps):
        # Input layer LIF
        state["V_input"], state["refrac_input"], spikes_in = _lif_step(
            state["V_input"], state["refrac_input"], I_input_layer, cfg
        )
        if spikes_in.any():
            state["total_input_spikes"] += int(spikes_in.sum())
            state["last_spike_input"][spikes_in] = state["global_time_ms"]
        # Hidden layer receives weighted input spikes as instantaneous current
        I_hidden = spikes_in.astype(np.float64) @ state["W"]
        state["V_hidden"], state["refrac_hidden"], spikes_h = _lif_step(
            state["V_hidden"], state["refrac_hidden"], I_hidden * cfg.hidden_synapse_gain, cfg
        )
        if spikes_h.any():
            state["total_hidden_spikes"] += int(spikes_h.sum())
            state["spike_rates_hidden"] += spikes_h.astype(np.int64)
            state["last_spike_hidden"][spikes_h] = state["global_time_ms"]
        # STDP update
        _stdp_update(state["W"], spikes_in, spikes_h,
                     state["last_spike_input"], state["last_spike_hidden"],
                     state["global_time_ms"], cfg)
        # Homeostasis: normalize incoming weights per hidden neuron after spike
        if spikes_h.any():
            for j in np.where(spikes_h)[0]:
                col_sum = state["W"][:, j].sum()
                if col_sum > 0:
                    state["W"][:, j] *= cfg.weight_normalization_sum / col_sum
        state["global_time_ms"] += cfg.dt_ms


def run(cfg: SNNConfig, n_ticks: int, audio_samples, state=None) -> dict:
    if state is None:
        state = initialise(cfg)
    if audio_samples is None:
        return state
    for tick in range(n_ticks):
        chunk = audio_samples[tick * cfg.samples_per_tick:(tick + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        step(state, chunk, cfg)
    return state


def measure_hidden_response(state, audio_chunks, cfg) -> np.ndarray:
    """For each chunk, measure per-neuron spike count during chunk processing.
    Returns array shape (n_chunks, n_hidden). RESETS spike counts after each chunk."""
    n = len(audio_chunks)
    responses = np.zeros((n, cfg.n_hidden), dtype=np.int64)
    for k, chunk in enumerate(audio_chunks):
        before = state["spike_rates_hidden"].copy()
        step(state, chunk, cfg)
        responses[k] = state["spike_rates_hidden"] - before
    return responses

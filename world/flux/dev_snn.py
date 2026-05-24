"""Developmental SNN — minimal scaffolding, raw audio input, observe emergence.

PARADIGM elimination: per operator instruction "Schritt für Schritt
eliminieren was nicht funktioniert". This substrate eliminates:
  - hand-designed encoder (no RMS, ZCR, FFT bands)
  - layered architecture (no input/hidden split)
  - feature engineering (raw audio amplitude directly)
  - bar-based classification (open-ended observation)

What remains as minimal scaffolding:
  - N LIF neurons placed at random 3D positions in [0,1]^3
  - Sparse random initial connectivity (density ~5%)
  - Connection delays proportional to spatial distance (biology)
  - Excitatory + inhibitory neurons (4:1 ratio, cortical norm)
  - Local STDP at each synapse (Bi & Poo 1998)
  - Homeostatic synaptic scaling (Turrigiano 2008)
  - Raw audio amplitude drives a designated "sensory" subset of neurons
    as direct current

Then: let it run. Observe what structure emerges.

No pre-specified "features". No pre-specified "categories". Substrate
develops whatever it develops.

References:
  - Bi GQ & Poo MM, Synaptic modifications dependent on spike timing,
    J Neurosci 1998
  - Turrigiano GG, The self-tuning neuron: synaptic scaling of
    excitatory synapses, Cell 2008
  - Buzsaki G, Rhythms of the Brain, OUP 2006
  - Markram H, Toledo-Rodriguez M, Wang Y, Gupta A, Silberberg G,
    Wu C, Interneurons of the neocortical inhibitory system,
    Nat Rev Neurosci 2004 (4:1 E:I ratio)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class DevSNNConfig:
    n_neurons: int = 200
    fraction_excitatory: float = 0.8  # Markram et al 4:1 E:I
    fraction_sensory: float = 0.1     # 10% receive direct audio input
    connection_density: float = 0.15  # 15% of possible synapses present
    distance_falloff: float = 1.0     # softer falloff (was 3.0)
    max_delay_steps: int = 20          # spatial-distance-proportional delays
    v_rest: float = -70.0
    v_thresh: float = -55.0
    v_reset: float = -75.0
    tau_m: float = 20.0  # ms
    tau_ref: int = 5
    # STDP
    stdp_A_plus: float = 0.005
    stdp_A_minus: float = 0.0055
    stdp_tau_plus: float = 20.0
    stdp_tau_minus: float = 20.0
    w_init: float = 2.0
    w_max: float = 5.0
    background_noise_current: float = 0.5  # small spontaneous activity
    # Homeostatic synaptic scaling (Turrigiano)
    target_firing_rate_hz: float = 5.0  # ~5 Hz typical cortical
    homeostasis_tau: float = 10_000.0   # slow timescale (ms)
    homeostasis_strength: float = 0.001
    # Input
    audio_to_current: float = 5000.0
    dt_ms: float = 1.0
    sample_rate_hz: int = 16000
    rng_seed: int = 0


def initialise(cfg: DevSNNConfig) -> dict:
    rng = np.random.default_rng(cfg.rng_seed)
    n = cfg.n_neurons
    # Random 3D positions
    pos = rng.uniform(0, 1, (n, 3))
    # Excitatory / inhibitory labels
    is_excitatory = rng.uniform(0, 1, n) < cfg.fraction_excitatory
    # Sparse random connectivity. Probability of connection scales with proximity.
    dist_matrix = np.sqrt(((pos[:, None, :] - pos[None, :, :]) ** 2).sum(axis=-1))
    # Connection probability falls with distance (biology-inspired)
    p_connect = cfg.connection_density * np.exp(-dist_matrix * cfg.distance_falloff)
    np.fill_diagonal(p_connect, 0)
    conn_mask = rng.uniform(0, 1, (n, n)) < p_connect
    # Weights: positive for E-presynaptic, negative for I-presynaptic
    W = np.zeros((n, n), dtype=np.float64)
    W[conn_mask] = cfg.w_init
    # Inhibitory rows are negative
    W[~is_excitatory, :] *= -1
    # Delays proportional to distance
    delays = np.clip((dist_matrix * cfg.max_delay_steps).astype(np.int64), 1, cfg.max_delay_steps)
    # Sensory subset
    n_sensory = max(1, int(n * cfg.fraction_sensory))
    sensory_neurons = rng.choice(n, n_sensory, replace=False)
    # State
    V = np.full(n, cfg.v_rest, dtype=np.float64)
    refrac = np.zeros(n, dtype=np.int64)
    # Spike delivery queue: list of (target, weight) to deliver at future time
    spike_queue = [[] for _ in range(cfg.max_delay_steps + 1)]
    # STDP traces
    last_spike = np.full(n, -1e9, dtype=np.float64)
    # Homeostasis: running firing rate per neuron
    running_rate = np.full(n, cfg.target_firing_rate_hz, dtype=np.float64)
    return {
        "cfg": cfg,
        "pos": pos, "is_excitatory": is_excitatory,
        "W": W, "conn_mask": conn_mask, "delays": delays,
        "sensory_neurons": sensory_neurons,
        "V": V, "refrac": refrac, "last_spike": last_spike,
        "spike_queue": spike_queue, "queue_ptr": 0,
        "running_rate": running_rate,
        "global_time_ms": 0.0,
        "total_spikes": 0,
        "spike_history": np.zeros(n, dtype=np.int64),  # cumulative spike count per neuron
    }


def step(state: dict, audio_sample: float) -> None:
    cfg = state["cfg"]
    n = cfg.n_neurons
    # Compute external input current
    rng = np.random.default_rng()
    I_ext = rng.standard_normal(n) * cfg.background_noise_current
    I_ext[state["sensory_neurons"]] += abs(audio_sample) * cfg.audio_to_current
    # Deliver scheduled spikes from queue
    delivered = state["spike_queue"][state["queue_ptr"]]
    I_syn = np.zeros(n, dtype=np.float64)
    for target, weight in delivered:
        I_syn[target] += weight
    state["spike_queue"][state["queue_ptr"]] = []
    state["queue_ptr"] = (state["queue_ptr"] + 1) % (cfg.max_delay_steps + 1)
    # LIF dynamics
    not_refractory = state["refrac"] == 0
    I_total = I_ext + I_syn
    dV = (-(state["V"] - cfg.v_rest) + I_total) / cfg.tau_m * cfg.dt_ms
    state["V"] = np.where(not_refractory, state["V"] + dV, state["V"])
    spikes = (state["V"] > cfg.v_thresh) & not_refractory
    state["V"] = np.where(spikes, cfg.v_reset, state["V"])
    state["refrac"] = np.where(spikes, cfg.tau_ref, np.maximum(state["refrac"] - 1, 0))
    if spikes.any():
        state["total_spikes"] += int(spikes.sum())
        state["spike_history"] += spikes.astype(np.int64)
        spike_idx = np.where(spikes)[0]
        # STDP update for each spiking neuron
        t_ms = state["global_time_ms"]
        for i in spike_idx:
            # LTP: for incoming connections where presynaptic fired before me
            pre_neurons = np.where(state["conn_mask"][:, i])[0]
            for j in pre_neurons:
                dt = t_ms - state["last_spike"][j]
                if 0 < dt < 100:  # within window
                    if state["is_excitatory"][j]:
                        state["W"][j, i] += cfg.stdp_A_plus * np.exp(-dt / cfg.stdp_tau_plus)
                        state["W"][j, i] = np.clip(state["W"][j, i], 0, cfg.w_max)
            # LTD: for outgoing connections where post fired before me (= I'm acting as pre that fires after post)
            post_neurons = np.where(state["conn_mask"][i, :])[0]
            for k in post_neurons:
                dt = t_ms - state["last_spike"][k]
                if 0 < dt < 100:
                    if state["is_excitatory"][i]:
                        state["W"][i, k] -= cfg.stdp_A_minus * np.exp(-dt / cfg.stdp_tau_minus)
                        state["W"][i, k] = np.clip(state["W"][i, k], 0, cfg.w_max)
        state["last_spike"][spike_idx] = t_ms
        # Schedule outgoing spikes with delays
        for i in spike_idx:
            for j in np.where(state["conn_mask"][i, :])[0]:
                delay = state["delays"][i, j]
                deliver_at = (state["queue_ptr"] + delay) % (cfg.max_delay_steps + 1)
                state["spike_queue"][deliver_at].append((j, state["W"][i, j]))
    # Homeostatic update — slow tracking of firing rate
    instant_rate = spikes.astype(np.float64) * (1000.0 / cfg.dt_ms)  # Hz this step
    state["running_rate"] = (1 - cfg.dt_ms / cfg.homeostasis_tau) * state["running_rate"] + \
                            (cfg.dt_ms / cfg.homeostasis_tau) * instant_rate
    # Scale incoming weights to push firing rate toward target
    rate_error = cfg.target_firing_rate_hz - state["running_rate"]
    scaling = 1 + cfg.homeostasis_strength * rate_error  # >1 if rate too low, <1 if too high
    # Apply to each post-neuron's incoming weights (column-wise)
    state["W"] *= scaling[None, :]
    state["W"] = np.clip(state["W"], -cfg.w_max, cfg.w_max)
    state["global_time_ms"] += cfg.dt_ms


def run_audio(state: dict, audio: np.ndarray) -> dict:
    """Step substrate through audio sample-by-sample.
    audio: 1D array of audio samples at sample_rate_hz.
    Each audio sample triggers one substrate step (1ms biological time)."""
    cfg = state["cfg"]
    # Decimate audio to dt_ms steps (audio is at 16kHz, dt=1ms means take every 16th sample)
    decimation = int(cfg.sample_rate_hz * cfg.dt_ms / 1000)
    for i in range(0, audio.size, decimation):
        sample = float(audio[i])
        step(state, sample)
    return state

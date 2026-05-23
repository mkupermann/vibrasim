"""BET-002 — Active Inference + Cognitive Map as learning substrate.

A 3D voxel grid where each cell holds a belief state (mean + diagonal
precision + visit count) over a hand-coded sensor vector. Audio is encoded
deterministically (RMS, zero-crossing-rate, FFT-band averages — no learned
embedding). Per tick: sample lands at a content-dependent position via
deterministic hash; prediction error drives a Bayesian update at that cell;
precision-weighted error propagates to 6 voxel neighbors (Friston's
prediction-error cascade).

The substrate has no backprop, no learning rate (the update strength is the
inverse of accumulated precision), no weights, no transformers, no
pretrained embeddings. It implements two known theories that have not been
realised as a live audio-learning substrate together:

  - Friston 2010+ — Free Energy Principle / Active Inference
  - Behrens et al 2018 — Cognitive Maps for Generalisation
  - O'Keefe & Nadel 1978 — Place Cells / Hippocampal map
  - Whittington et al 2020 — Tolman-Eichenbaum Machine

Per bet pre-registration LOGBOOK 2026-05-22, this is BET-002 in the bet
programme. The 5/5 test bar (T1-T5) is the WIN condition. T0 is a
diagnostic gate added after BET-001 exposed the trivial-mean-shift failure
mode (a uniform-plateau substrate would also pass T1+T2 on histogram-KL,
but T0 checks spatial structure exists, anti-trivial-plateau).

The hypothesis is pre-data: this substrate IF the bet's WIN bar is met
demonstrates content-coupled self-organising learning under the corrected
bet constraint (existing technologies verknüpft, no LLM/transformer/
embedding/BPE).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class MapConfig:
    """All parameters locked pre-data per BET-002."""
    grid_dims: tuple[int, int, int] = (30, 15, 8)
    n_features: int = 10           # sensor vector dimension
    alpha_precision_gain: float = 0.05  # how fast Λ accumulates
    beta_lateral: float = 0.1      # neighbour propagation strength
    sample_rate_hz: int = 16000
    samples_per_tick: int = 16
    fft_bands: int = 8             # bins for spectral feature
    initial_mu: float = 0.0
    initial_precision: float = 0.1
    position_hash_seed: int = 0


# ---------- Sensor encoding (deterministic, no learning) ----------
def encode_sensor(chunk: np.ndarray, cfg: MapConfig) -> np.ndarray:
    """Return a fixed-dimension feature vector for the audio chunk.

    Features: [RMS, zero-crossing-rate, FFT-band-energies (cfg.fft_bands)].
    Total = 2 + fft_bands = 10 dims under default config.
    """
    if chunk.size == 0:
        return np.zeros(cfg.n_features, dtype=np.float64)
    rms = float(np.sqrt(np.mean(chunk * chunk) + 1e-12))
    zcr = float(np.mean(np.abs(np.diff(np.sign(chunk)))) / 2.0)
    # Real FFT magnitudes, averaged into cfg.fft_bands log-spaced bands.
    if chunk.size >= 4:
        mag = np.abs(np.fft.rfft(chunk))
        if mag.size == 0:
            band = np.zeros(cfg.fft_bands)
        else:
            edges = np.linspace(0, mag.size, cfg.fft_bands + 1, dtype=int)
            band = np.array([
                mag[edges[i]:edges[i + 1] + 1].mean() if edges[i + 1] > edges[i] else 0.0
                for i in range(cfg.fft_bands)
            ], dtype=np.float64)
            # Normalise so feature scale is comparable to RMS/ZCR
            if band.sum() > 0:
                band = band / (band.sum() + 1e-12)
    else:
        band = np.zeros(cfg.fft_bands)
    feat = np.empty(cfg.n_features, dtype=np.float64)
    feat[0] = rms
    feat[1] = zcr
    feat[2:2 + cfg.fft_bands] = band
    return feat


# ---------- Position hash (content-dependent, deterministic) ----------
def position_hash(sample_index: int, sample_value: float, cfg: MapConfig) -> tuple[int, int, int]:
    """Deterministic mapping (sample_index, sample_value) → voxel (x, y, z).

    Both inputs contribute, so the same sample_index with different
    sample_values lands in different cells (verknüpfung G25's content-aware
    position channel — but used here for map indexing, not for substrate
    injection like G25 was).
    """
    Lx, Ly, Lz = cfg.grid_dims
    # 64-bit splitmix on bit-mixed combination
    sv_q = int(np.clip(np.round((sample_value + 1.0) * 65535.0 / 2.0), 0, 65535))
    seed = (sample_index * 2654435761) ^ (sv_q * 40503) ^ cfg.position_hash_seed
    seed &= 0xFFFFFFFF
    # splitmix64
    z = (seed + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    z = z ^ (z >> 31)
    x = int(z % Lx)
    y = int((z >> 16) % Ly)
    zc = int((z >> 32) % Lz)
    return x, y, zc


# ---------- Substrate state ----------
def initialise(cfg: MapConfig) -> dict:
    Lx, Ly, Lz = cfg.grid_dims
    mu = np.full((Lx, Ly, Lz, cfg.n_features), cfg.initial_mu, dtype=np.float64)
    Lambda = np.full((Lx, Ly, Lz, cfg.n_features), cfg.initial_precision, dtype=np.float64)
    N = np.zeros((Lx, Ly, Lz), dtype=np.int64)
    return {"mu": mu, "Lambda": Lambda, "N": N}


# ---------- Active-Inference update ----------
def _lateral_propagate(state: dict, x: int, y: int, z: int, e: np.ndarray, cfg: MapConfig) -> None:
    Lx, Ly, Lz = cfg.grid_dims
    mu = state["mu"]
    Lambda = state["Lambda"]
    for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        nx, ny, nz = x + dx, y + dy, z + dz
        if 0 <= nx < Lx and 0 <= ny < Ly and 0 <= nz < Lz:
            inv_lambda = 1.0 / (Lambda[nx, ny, nz] + 1e-9)
            mu[nx, ny, nz] += cfg.beta_lateral * inv_lambda * e


def step(state: dict, audio_chunk: np.ndarray, tick: int, cfg: MapConfig) -> None:
    """One Active-Inference tick.

    Samples in the chunk are processed one by one. For each: encode sensor
    on a 1-sample shifted window (or full chunk if too short to slide),
    project to a map cell via content-aware hash, Bayesian-update mu/Lambda/N,
    propagate precision-weighted error to 6 neighbours.
    """
    if audio_chunk.size == 0:
        return
    # Use the full chunk as the sensor window once per tick (simpler than
    # per-sample sliding). Position-hash uses the LAST sample of the chunk
    # to keep content dependence.
    sensor = encode_sensor(audio_chunk, cfg)
    sample_index = tick * cfg.samples_per_tick + (audio_chunk.size - 1)
    sample_value = float(audio_chunk[-1])
    x, y, z = position_hash(sample_index, sample_value, cfg)
    mu = state["mu"]
    Lambda = state["Lambda"]
    N = state["N"]
    e = sensor - mu[x, y, z]
    N[x, y, z] += 1
    mu[x, y, z] += e / float(N[x, y, z])
    Lambda[x, y, z] += cfg.alpha_precision_gain * (e * e)
    _lateral_propagate(state, x, y, z, e, cfg)


def run(
    cfg: MapConfig,
    n_ticks: int,
    audio_samples: np.ndarray | None,
    state: dict | None = None,
) -> dict:
    """Run the substrate for n_ticks. Returns the final state dict.

    If audio_samples is None, the substrate runs without input (negative
    control / rest-phase). If state is provided, continues from that state
    (used for T5 retention check: train then rest).
    """
    if state is None:
        state = initialise(cfg)
    if audio_samples is None:
        return state
    for tick in range(n_ticks):
        i0 = tick * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = audio_samples[i0:i1]
        if chunk.size == 0:
            continue
        step(state, chunk, tick, cfg)
    return state


# ---------- Held-out prediction (used by T4) ----------
def predict_at_position(state: dict, x: int, y: int, z: int) -> np.ndarray:
    return state["mu"][x, y, z].copy()


def evaluate_holdout(
    state: dict,
    holdout_samples: np.ndarray,
    cfg: MapConfig,
    tick_offset: int = 0,
) -> dict:
    """Per held-out chunk: encode sensor, compute prediction error against
    the cell the position-hash assigns, return cosine-similarity statistics.

    Returns dict with:
      - n: number of held-out chunks evaluated
      - mean_cosine: mean cosine similarity between sensor and predicted mu
      - precision: fraction with cosine > 0 (i.e. the cell's belief is on
        the same side of the origin as the test sensor)
    """
    cosines = []
    n_chunks = holdout_samples.size // cfg.samples_per_tick
    for k in range(n_chunks):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = holdout_samples[i0:i1]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        sample_index = (tick_offset + k) * cfg.samples_per_tick + (chunk.size - 1)
        sample_value = float(chunk[-1])
        x, y, z = position_hash(sample_index, sample_value, cfg)
        mu = predict_at_position(state, x, y, z)
        denom = np.linalg.norm(sensor) * np.linalg.norm(mu) + 1e-12
        if denom > 0:
            cos = float(np.dot(sensor, mu) / denom)
        else:
            cos = 0.0
        cosines.append(cos)
    if not cosines:
        return {"n": 0, "mean_cosine": 0.0, "precision": 0.0}
    cosines_np = np.array(cosines)
    return {
        "n": len(cosines),
        "mean_cosine": float(cosines_np.mean()),
        "precision": float((cosines_np > 0.0).mean()),
    }

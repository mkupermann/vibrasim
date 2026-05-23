"""BET-021 — cog_map β=0 + pseudo-rehearsal replay.

Cross-substrate-class robustness check: does the replay mechanism that
gave SOM (BET-012) its T8 PASS also work for cog_map β=0 (BET-006
baseline)? If yes → replay is universal. If no → replay is
SOM-specific.

Substrate:
  - cog_map β=0 baseline (BET-006 substrate, position-hash by
    sample_index+sample_value, Bayesian belief-update per cell,
    NO lateral propagation since β=0)
  - Adds FIFO buffer of (sensor, sample_index, sample_value) tuples,
    K=10000, replay_rate=1.0
  - Per wake-tick: encode, hash, update, push to buffer
  - Per replay-tick: sample buffer item, re-use stored (sample_index,
    sample_value) to recreate same position-hash, update that cell

Replay reactivates the SAME cell that was originally activated, so EN
inputs continue to reinforce EN-cells during WN training phase.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from world.flux.cognitive_map import encode_sensor, position_hash


@dataclass
class CogMapReplayConfig:
    """All parameters locked per BET-021."""
    grid_dims: tuple[int, int, int] = (30, 15, 8)
    n_features: int = 10
    alpha_precision_gain: float = 0.05
    beta_lateral: float = 0.0     # locked at 0 (BET-006 winning config)
    sample_rate_hz: int = 16000
    samples_per_tick: int = 16
    fft_bands: int = 8
    initial_mu: float = 0.0
    initial_precision: float = 0.1
    position_hash_seed: int = 0
    buffer_size: int = 10_000
    replay_rate: float = 1.0
    rng_seed: int = 0


def initialise(cfg: CogMapReplayConfig) -> dict:
    Lx, Ly, Lz = cfg.grid_dims
    mu = np.full((Lx, Ly, Lz, cfg.n_features), cfg.initial_mu, dtype=np.float64)
    Lambda = np.full((Lx, Ly, Lz, cfg.n_features), cfg.initial_precision, dtype=np.float64)
    N = np.zeros((Lx, Ly, Lz), dtype=np.int64)
    buffer = {
        "sensors": np.zeros((cfg.buffer_size, cfg.n_features), dtype=np.float64),
        "sample_indices": np.zeros(cfg.buffer_size, dtype=np.int64),
        "sample_values": np.zeros(cfg.buffer_size, dtype=np.float64),
        "head": 0, "fill": 0,
    }
    return {"mu": mu, "Lambda": Lambda, "N": N, "buffer": buffer, "global_tick": 0}


def _cog_map_update_at(state: dict, sensor: np.ndarray, sample_index: int,
                       sample_value: float, cfg: CogMapReplayConfig) -> None:
    """Bayesian belief update at the position determined by content-hash."""
    pos = position_hash(sample_index, sample_value, cfg)  # cfg is duck-typed; needs grid_dims + position_hash_seed
    x, y, z = pos
    mu = state["mu"]
    Lambda = state["Lambda"]
    N = state["N"]
    e = sensor - mu[x, y, z]
    N[x, y, z] += 1
    mu[x, y, z] += e / float(N[x, y, z])
    Lambda[x, y, z] += cfg.alpha_precision_gain * (e * e)


def step(state: dict, audio_chunk: np.ndarray, tick: int, cfg: CogMapReplayConfig) -> None:
    if audio_chunk.size == 0:
        return
    sensor = encode_sensor(audio_chunk, cfg)
    sample_index = tick * cfg.samples_per_tick + (audio_chunk.size - 1)
    sample_value = float(audio_chunk[-1])
    _cog_map_update_at(state, sensor, sample_index, sample_value, cfg)
    # Push to buffer
    buf = state["buffer"]
    buf["sensors"][buf["head"]] = sensor
    buf["sample_indices"][buf["head"]] = sample_index
    buf["sample_values"][buf["head"]] = sample_value
    buf["head"] = (buf["head"] + 1) % cfg.buffer_size
    buf["fill"] = min(buf["fill"] + 1, cfg.buffer_size)
    state["global_tick"] += 1

    # Replay
    rng = np.random.default_rng(state["global_tick"] * 1009 + cfg.rng_seed)
    n_replays = int(cfg.replay_rate)
    extra = cfg.replay_rate - n_replays
    if extra > 0 and rng.random() < extra:
        n_replays += 1
    if buf["fill"] > 0:
        for _ in range(n_replays):
            idx = int(rng.integers(0, buf["fill"]))
            _cog_map_update_at(
                state, buf["sensors"][idx],
                int(buf["sample_indices"][idx]),
                float(buf["sample_values"][idx]), cfg,
            )
            state["global_tick"] += 1


def run(
    cfg: CogMapReplayConfig,
    n_ticks: int,
    audio_samples: np.ndarray | None,
    state: dict | None = None,
) -> dict:
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


def evaluate_holdout(
    state: dict,
    holdout_samples: np.ndarray,
    cfg: CogMapReplayConfig,
    tick_offset: int = 0,
) -> dict:
    """T4-style: each chunk hashes to a position, cosine of (sensor, mu[pos])."""
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
        pos = position_hash(sample_index, sample_value, cfg)
        x, y, z = pos
        cell_mu = state["mu"][x, y, z]
        denom = np.linalg.norm(sensor) * np.linalg.norm(cell_mu) + 1e-12
        cos = float(np.dot(sensor, cell_mu) / denom) if denom > 0 else 0.0
        cosines.append(cos)
    if not cosines:
        return {"n": 0, "mean_cosine": 0.0, "precision": 0.0}
    arr = np.array(cosines)
    return {"n": len(cosines), "mean_cosine": float(arr.mean()),
            "precision": float((arr > 0).mean())}

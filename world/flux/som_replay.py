"""BET-012 — SOM with pseudo-rehearsal replay buffer.

Pre-LLM neurowissenschaftlich fundierte Lösung für catastrophic forgetting.
Robins 1995 introduced pseudo-rehearsal: store recent inputs in a buffer
and interleave their replay with new training. The substrate uses its own
past inputs to maintain learned content under new training pressure.

This is "internal" rehearsal — the substrate manages its own buffer and
chooses when to replay. No external supervisor, no class labels, no
explicit consolidation schedule. The replay rate and buffer size are
the substrate's pre-data parameters (locked).

Differences from BET-007 SOM:
  - Adds a FIFO buffer of size K=10_000 (= N_TICKS) storing past sensor
    feature vectors
  - Per wake-tick: encode input, push to buffer, do BMU update on input,
    then replay one random buffer item (extra BMU update). Replay rate
    is locked at 1.0 (one replay per wake-tick).

Catastrophic-forgetting resistance argument:
  Across 20k total updates (10k wake EN + 10k wake WN), the buffer
  preserves EN inputs through the entire WN phase (buffer size =
  N_TICKS), so replay continues to reinforce EN-trained cells even as
  WN-driven wake updates reshape other cells. Effective per-class
  exposure rebalances toward EN: 10k wake-EN + 5k replay-EN ≈ 15k
  EN-style updates vs 10k wake-WN + 5k replay-WN = 15k WN-style updates.
  S_AB should retain substantial EN-content.

References:
  - Robins, Catastrophic forgetting, rehearsal and pseudorehearsal,
    Connection Science 1995
  - Robins, McCallum, The consolidation of learning during sleep:
    comparing the pseudorehearsal and unlearning accounts, Neural
    Networks 1999
  - Atkinson, McCallum, Robins, Pseudorehearsal in feed-forward
    networks of size O(n²), 2018
  - Hennig, Self-supervised learning by reactivation in recurrent
    networks, Behavioural Brain Research 2021 (modern hippocampal
    replay account)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from world.flux.cognitive_map import encode_sensor


@dataclass
class SOMReplayConfig:
    """All parameters locked pre-data per BET-012."""
    grid_dims: tuple[int, int, int] = (30, 15, 8)
    n_features: int = 10
    eta_0: float = 0.5
    eta_decay_tau: float = 5000.0
    sigma_0: float = 5.0
    sigma_decay_tau: float = 3000.0
    sample_rate_hz: int = 16000
    samples_per_tick: int = 16
    fft_bands: int = 8
    initial_w_scale: float = 0.01
    rng_seed: int = 0
    # Replay-specific (locked pre-data)
    buffer_size: int = 10_000
    replay_rate: float = 1.0    # replays per wake-tick


def initialise(cfg: SOMReplayConfig) -> dict:
    Lx, Ly, Lz = cfg.grid_dims
    rng = np.random.default_rng(cfg.rng_seed)
    w = (rng.standard_normal((Lx, Ly, Lz, cfg.n_features)) * cfg.initial_w_scale).astype(np.float64)
    N = np.zeros((Lx, Ly, Lz), dtype=np.int64)
    ii, jj, kk = np.meshgrid(
        np.arange(Lx, dtype=np.float64),
        np.arange(Ly, dtype=np.float64),
        np.arange(Lz, dtype=np.float64),
        indexing="ij",
    )
    buffer = np.zeros((cfg.buffer_size, cfg.n_features), dtype=np.float64)
    return {
        "w": w, "N": N, "ii": ii, "jj": jj, "kk": kk,
        "buffer": buffer,
        "buffer_head": 0,
        "buffer_fill": 0,
        "global_tick": 0,
    }


def _find_bmu(state: dict, x: np.ndarray) -> tuple[int, int, int]:
    diff = state["w"] - x
    dist_sq = np.einsum("ijkl,ijkl->ijk", diff, diff)
    return np.unravel_index(int(np.argmin(dist_sq)), dist_sq.shape)


def _som_update(state: dict, sensor: np.ndarray, global_tick: int, cfg: SOMReplayConfig) -> None:
    bmu = _find_bmu(state, sensor)
    w = state["w"]
    diff = sensor - w
    eta_t = cfg.eta_0 * np.exp(-global_tick / cfg.eta_decay_tau)
    sigma_t = max(cfg.sigma_0 * np.exp(-global_tick / cfg.sigma_decay_tau), 0.5)
    grid_dist_sq = (
        (state["ii"] - bmu[0]) ** 2
        + (state["jj"] - bmu[1]) ** 2
        + (state["kk"] - bmu[2]) ** 2
    )
    h = np.exp(-grid_dist_sq / (2.0 * sigma_t * sigma_t))[..., None]
    w += eta_t * h * diff
    state["N"][bmu] += 1


def step(state: dict, audio_chunk: np.ndarray, tick: int, cfg: SOMReplayConfig) -> None:
    if audio_chunk.size == 0:
        return
    sensor = encode_sensor(audio_chunk, cfg)
    # Wake update + buffer push
    _som_update(state, sensor, state["global_tick"], cfg)
    state["buffer"][state["buffer_head"]] = sensor
    state["buffer_head"] = (state["buffer_head"] + 1) % cfg.buffer_size
    state["buffer_fill"] = min(state["buffer_fill"] + 1, cfg.buffer_size)
    state["global_tick"] += 1

    # Replay updates: sample buffer items and update SOM with them
    rng_replay = np.random.default_rng(state["global_tick"] * 1009 + cfg.rng_seed)
    n_replays = int(cfg.replay_rate)
    extra_fraction = cfg.replay_rate - n_replays
    if extra_fraction > 0 and rng_replay.random() < extra_fraction:
        n_replays += 1
    if state["buffer_fill"] > 0:
        for _ in range(n_replays):
            idx = int(rng_replay.integers(0, state["buffer_fill"]))
            replayed = state["buffer"][idx]
            _som_update(state, replayed, state["global_tick"], cfg)
            state["global_tick"] += 1


def run(
    cfg: SOMReplayConfig,
    n_ticks: int,
    audio_samples: np.ndarray | None,
    state: dict | None = None,
) -> dict:
    if state is None:
        state = initialise(cfg)
    if audio_samples is None:
        # Rest phase: do PURE replay (no new input). This is the "sleep" — the
        # substrate continues consolidating from its buffer.
        # For matching BET-007/009/011's "no-update during rest" semantic,
        # we still do nothing here. This is the locked-bar T5 protocol.
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
    cfg: SOMReplayConfig,
) -> dict:
    cosines = []
    n_chunks = holdout_samples.size // cfg.samples_per_tick
    for k in range(n_chunks):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = holdout_samples[i0:i1]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        diff = state["w"] - sensor
        dist_sq = np.einsum("ijkl,ijkl->ijk", diff, diff)
        bmu = np.unravel_index(int(np.argmin(dist_sq)), dist_sq.shape)
        w_bmu = state["w"][bmu]
        denom = np.linalg.norm(sensor) * np.linalg.norm(w_bmu) + 1e-12
        cos = float(np.dot(sensor, w_bmu) / denom) if denom > 0 else 0.0
        cosines.append(cos)
    if not cosines:
        return {"n": 0, "mean_cosine": 0.0, "precision": 0.0}
    cosines_np = np.array(cosines)
    return {
        "n": len(cosines),
        "mean_cosine": float(cosines_np.mean()),
        "precision": float((cosines_np > 0.0).mean()),
    }

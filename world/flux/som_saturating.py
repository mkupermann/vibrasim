"""BET-011 — Self-Organising Map with per-cell saturation.

Pre-LLM-era substrate combining Kohonen competitive learning with an
explicit per-cell capacity limit. Each cell has a saturation_threshold;
once a cell's visit count reaches that threshold it becomes
write-protected and no longer accepts BMU updates. New inputs whose
natural BMU is saturated are routed to the next-best UNSATURATED cell.

This is the substrate's own memory-consolidation rule: cells decide,
based on their visit history, when to STOP accepting new content. Early
inputs (EN class) fill the cells they competitively claim; once those
cells are saturated, later inputs (WN class) are forced to populate
DIFFERENT cells. The EN-content territory remains intact after WN
training.

The mechanism is local and non-supervised — no external class label,
no global "freeze" signal, no rehearsal. Self-determination over which
memories to preserve emerges from per-cell saturation.

References:
  - Kohonen, Self-Organized Formation of Topologically Correct Feature Maps,
    Biol Cybern 1982 (base SOM)
  - Kohonen, Self-Organizing Maps, Springer 2001 (textbook)
  - Marsland, Shapiro, Nehmzow, A self-organising network that grows when
    required, Neural Networks 2002 (Growing-When-Required net — related
    capacity-limited variant)
  - Bishop, Mixture Models and EM, Neural Computation for Pattern
    Recognition 2006 (per-component-capacity arguments in mixture models)

Pre-data prediction: per-cell saturation should specifically improve T8
(catastrophic-forgetting). T7 + T9 should be ≥ SOM baseline (BET-007).
T0-T5 should be ≥ SOM baseline.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from world.flux.cognitive_map import encode_sensor


@dataclass
class SOMSaturatingConfig:
    """All parameters locked pre-data per BET-011."""
    grid_dims: tuple[int, int, int] = (30, 15, 8)
    n_features: int = 10
    eta_0: float = 0.5
    eta_decay_tau: float = 5000.0
    sigma_0: float = 5.0
    sigma_decay_tau: float = 3000.0
    saturation_threshold: int = 30   # per-cell capacity (locked pre-data)
    sample_rate_hz: int = 16000
    samples_per_tick: int = 16
    fft_bands: int = 8
    initial_w_scale: float = 0.01
    rng_seed: int = 0


def initialise(cfg: SOMSaturatingConfig) -> dict:
    Lx, Ly, Lz = cfg.grid_dims
    rng = np.random.default_rng(cfg.rng_seed)
    w = (rng.standard_normal((Lx, Ly, Lz, cfg.n_features)) * cfg.initial_w_scale).astype(np.float64)
    N = np.zeros((Lx, Ly, Lz), dtype=np.int64)
    saturated = np.zeros((Lx, Ly, Lz), dtype=bool)
    ii, jj, kk = np.meshgrid(
        np.arange(Lx, dtype=np.float64),
        np.arange(Ly, dtype=np.float64),
        np.arange(Lz, dtype=np.float64),
        indexing="ij",
    )
    return {"w": w, "N": N, "saturated": saturated, "ii": ii, "jj": jj, "kk": kk}


def find_bmu_unsaturated(state: dict, x: np.ndarray) -> tuple[int, int, int] | None:
    """Return BMU coord among unsaturated cells, or None if all saturated."""
    diff = state["w"] - x
    dist_sq = np.einsum("ijkl,ijkl->ijk", diff, diff)
    # Mask saturated cells with +inf so they are not selected
    masked = np.where(state["saturated"], np.inf, dist_sq)
    if not np.isfinite(masked).any():
        return None
    flat = int(np.argmin(masked))
    return np.unravel_index(flat, masked.shape)


def step(state: dict, audio_chunk: np.ndarray, tick: int, cfg: SOMSaturatingConfig) -> None:
    if audio_chunk.size == 0:
        return
    sensor = encode_sensor(audio_chunk, cfg)
    bmu = find_bmu_unsaturated(state, sensor)
    if bmu is None:
        return  # all cells saturated — substrate has reached capacity
    w = state["w"]
    diff = sensor - w
    eta_t = cfg.eta_0 * np.exp(-tick / cfg.eta_decay_tau)
    sigma_t = max(cfg.sigma_0 * np.exp(-tick / cfg.sigma_decay_tau), 0.5)
    grid_dist_sq = (
        (state["ii"] - bmu[0]) ** 2
        + (state["jj"] - bmu[1]) ** 2
        + (state["kk"] - bmu[2]) ** 2
    )
    h = np.exp(-grid_dist_sq / (2.0 * sigma_t * sigma_t))[..., None]
    # Apply update only to UNSATURATED cells (saturated cells are write-protected)
    sat_mask = state["saturated"][..., None]
    w[:] = np.where(sat_mask, w, w + eta_t * h * diff)
    state["N"][bmu] += 1
    if state["N"][bmu] >= cfg.saturation_threshold:
        state["saturated"][bmu] = True


def run(
    cfg: SOMSaturatingConfig,
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
    cfg: SOMSaturatingConfig,
) -> dict:
    """Per held-out chunk: encode, find BMU (saturated OR not — for reading,
    use ALL cells; saturation only affects writing), return cosine(sensor, w[BMU])."""
    cosines = []
    n_chunks = holdout_samples.size // cfg.samples_per_tick
    for k in range(n_chunks):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = holdout_samples[i0:i1]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        # Reading: full-grid BMU (saturated cells participate in retrieval)
        diff = state["w"] - sensor
        dist_sq = np.einsum("ijkl,ijkl->ijk", diff, diff)
        flat = int(np.argmin(dist_sq))
        bmu = np.unravel_index(flat, dist_sq.shape)
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

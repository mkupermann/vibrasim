"""BET-007 — Self-Organising Map (Kohonen 1982) as learning substrate.

Alternative substrate class to BET-002's cognitive_map. Key inductive-bias
difference: BMU position is determined by COMPETITION (argmin ||w-x||) over
the whole grid, not by a content-aware hash. The map's topology preserves
similarity — similar inputs land at nearby cells — and that organisation
emerges from the competitive update rule rather than being engineered into
the position function.

Substrate:
  - 3D voxel grid, same shape as BET-002 for parity
  - Each cell holds a weight vector w in R^n_features
  - Same encoder as BET-002 (encode_sensor reused from cognitive_map module)
  - Per tick: encode → BMU search → update BMU + Gaussian neighbourhood
  - Learning rate eta(t) and neighbourhood radius sigma(t) both decay
    exponentially with tick index
  - No backprop, no learning rate gradient, no weights, no embedding,
    no transformer. Only the competitive-update rule.

References:
  - Kohonen, Self-Organized Formation of Topologically Correct Feature Maps,
    Biological Cybernetics 1982
  - Kohonen, The 'Neural' Phonetic Typewriter, IEEE Computer 1988 (SOMs
    on raw audio for phoneme maps)
  - Kohonen, Self-Organizing Maps, Springer 2001 (textbook)

The hypothesis for BET-007: if the BET-006 ablation NULLs (lateral propagation
in active-inference is not the only blocker), a fundamentally different
substrate class — competitive learning instead of Bayesian belief-update —
may clear the 5/5 bet bar. SOMs ARE topology-preserving by construction,
which is the property cognitive_map was meant to learn but apparently does
not under R-7-corpus audio.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from world.flux.cognitive_map import encode_sensor


@dataclass
class SOMConfig:
    """All parameters locked pre-data per BET-007."""
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


def initialise(cfg: SOMConfig) -> dict:
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
    return {"w": w, "N": N, "ii": ii, "jj": jj, "kk": kk}


def find_bmu(state: dict, x: np.ndarray) -> tuple[int, int, int]:
    """Argmin over all cells of squared L2 distance to x."""
    diff = state["w"] - x
    dist_sq = np.einsum("ijkl,ijkl->ijk", diff, diff)
    flat = int(np.argmin(dist_sq))
    return np.unravel_index(flat, dist_sq.shape)


def step(state: dict, audio_chunk: np.ndarray, tick: int, cfg: SOMConfig) -> None:
    if audio_chunk.size == 0:
        return
    # Convert chunk to encoder format. encode_sensor takes a MapConfig-like
    # object; SOMConfig has the n_features/fft_bands fields it needs.
    sensor = encode_sensor(audio_chunk, cfg)
    bmu = find_bmu(state, sensor)
    w = state["w"]
    diff = sensor - w  # (Lx,Ly,Lz,n_features)
    eta_t = cfg.eta_0 * np.exp(-tick / cfg.eta_decay_tau)
    sigma_t = max(cfg.sigma_0 * np.exp(-tick / cfg.sigma_decay_tau), 0.5)
    # Gaussian neighbourhood centred on BMU
    grid_dist_sq = (
        (state["ii"] - bmu[0]) ** 2
        + (state["jj"] - bmu[1]) ** 2
        + (state["kk"] - bmu[2]) ** 2
    )
    h = np.exp(-grid_dist_sq / (2.0 * sigma_t * sigma_t))[..., None]
    w += eta_t * h * diff
    state["N"][bmu] += 1


def run(
    cfg: SOMConfig,
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
    cfg: SOMConfig,
) -> dict:
    """Per held-out chunk: encode, find BMU, return cosine(sensor, w[BMU])."""
    cosines = []
    n_chunks = holdout_samples.size // cfg.samples_per_tick
    for k in range(n_chunks):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = holdout_samples[i0:i1]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        bmu = find_bmu(state, sensor)
        w_bmu = state["w"][bmu]
        denom = np.linalg.norm(sensor) * np.linalg.norm(w_bmu) + 1e-12
        if denom > 0:
            cos = float(np.dot(sensor, w_bmu) / denom)
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

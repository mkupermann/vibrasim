"""BET-010 — Sparse Distributed Memory (Kanerva 1988) with spatial topology.

Pre-LLM-era substrate class designed specifically for catastrophic-forgetting
resistance. Storage is DISTRIBUTED: each input activates many cells, and each
cell holds the SUM of contributions from many inputs. New inputs do not
overwrite old contributions — they add to them in additional dimensions of
the storage space. Recall via address-based activation extracts the
appropriate sum even after extensive intervening training.

Spatial topology is added by deriving each cell's binary address from
smoothed 3D random fields, so adjacent cells (in (x,y,z) grid) have
correlated (but not identical) binary addresses. This satisfies T9
(spatial autocorrelation) while preserving the SDM forgetting-resistance
property.

References:
  - Kanerva, Sparse Distributed Memory, MIT Press 1988
  - Kanerva, Sparse Distributed Memory and Related Models, in Associative
    Neural Memories (ed. Hassoun) 1993
  - Hely, Willshaw, Hayes, A new approach to Kanerva's sparse distributed
    memory, IEEE TNN 1997 (counter-array variant)

Substrate properties verknüpft with the bet's existing infrastructure:
  - Same encoder as cog_map / SOM (RMS + ZCR + 8 FFT bands → 10-D feature)
  - Same grid shape (30, 15, 8) for parity
  - Same audio (R-7 corpus)
  - Different update rule: SDM-distributed-storage instead of point-update
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import gaussian_filter

from world.flux.cognitive_map import encode_sensor


@dataclass
class SDMConfig:
    """All parameters locked pre-data per BET-010."""
    grid_dims: tuple[int, int, int] = (30, 15, 8)
    n_features: int = 10            # also the number of address bits
    address_smooth_sigma: float = 1.5  # spatial smoothing of address field
    hamming_radius: int = 3         # activation radius for write/read
    sample_rate_hz: int = 16000
    samples_per_tick: int = 16
    fft_bands: int = 8
    rng_seed: int = 0


def _make_smooth_binary_addresses(cfg: SDMConfig) -> np.ndarray:
    """Generate (Lx, Ly, Lz, n_bits) binary addresses with spatial smoothness.

    Each of the n_bits channels is an independent smoothed Gaussian random field
    on the 3D grid; the sign of the smoothed field gives the bit value at each
    cell. Adjacent cells thus have correlated (but not identical) addresses.
    """
    Lx, Ly, Lz = cfg.grid_dims
    rng = np.random.default_rng(cfg.rng_seed)
    raw = rng.standard_normal((Lx, Ly, Lz, cfg.n_features))
    smoothed = np.empty_like(raw)
    for b in range(cfg.n_features):
        smoothed[..., b] = gaussian_filter(raw[..., b], sigma=cfg.address_smooth_sigma, mode="wrap")
    return (smoothed > 0).astype(np.int8)


def initialise(cfg: SDMConfig) -> dict:
    Lx, Ly, Lz = cfg.grid_dims
    addresses = _make_smooth_binary_addresses(cfg)
    counters = np.zeros((Lx, Ly, Lz, cfg.n_features), dtype=np.float64)
    N = np.zeros((Lx, Ly, Lz), dtype=np.int64)
    return {"addresses": addresses, "counters": counters, "N": N}


def _activation_mask(state: dict, query_bits: np.ndarray, cfg: SDMConfig) -> np.ndarray:
    """Boolean mask (Lx,Ly,Lz) of cells whose address is within hamming_radius of query_bits."""
    hamming = np.sum(state["addresses"] != query_bits, axis=-1)
    return hamming <= cfg.hamming_radius


def _bits_of(x: np.ndarray) -> np.ndarray:
    return (x > 0).astype(np.int8)


def step(state: dict, audio_chunk: np.ndarray, tick: int, cfg: SDMConfig) -> None:
    if audio_chunk.size == 0:
        return
    sensor = encode_sensor(audio_chunk, cfg)
    query_bits = _bits_of(sensor - sensor.mean())  # zero-centred sign → binary address
    mask = _activation_mask(state, query_bits, cfg)
    if not mask.any():
        return
    # Distributed write: add sensor to counters of all activated cells.
    state["counters"][mask] += sensor
    state["N"][mask] += 1


def run(
    cfg: SDMConfig,
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


def predict_at(state: dict, sensor: np.ndarray, cfg: SDMConfig) -> np.ndarray:
    """Distributed read: mean of (counter/N) across all cells activated by sensor's bits."""
    query_bits = _bits_of(sensor - sensor.mean())
    mask = _activation_mask(state, query_bits, cfg)
    if not mask.any():
        return np.zeros(cfg.n_features, dtype=np.float64)
    counters = state["counters"][mask]    # (n_active, n_features)
    Ns = state["N"][mask].astype(np.float64).reshape(-1, 1)
    Ns_safe = np.where(Ns > 0, Ns, 1.0)
    per_cell_mean = counters / Ns_safe
    return per_cell_mean.mean(axis=0)


def evaluate_holdout(
    state: dict,
    holdout_samples: np.ndarray,
    cfg: SDMConfig,
) -> dict:
    """Per held-out chunk: encode, distributed read, cosine of (sensor, retrieved)."""
    cosines = []
    n_chunks = holdout_samples.size // cfg.samples_per_tick
    for k in range(n_chunks):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = holdout_samples[i0:i1]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        retrieved = predict_at(state, sensor, cfg)
        denom = np.linalg.norm(sensor) * np.linalg.norm(retrieved) + 1e-12
        if denom > 0:
            cos = float(np.dot(sensor, retrieved) / denom)
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

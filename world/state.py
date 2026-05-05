from __future__ import annotations
import numpy as np
from world.config import WorldConfig


class World:
    """Plain data container for the simulation. No physics methods — those live in `world.physics`."""

    def __init__(self, config: WorldConfig):
        self.config = config
        self.t: float = 0.0
        self.rng = np.random.default_rng(config.rng_seed)

        N = config.n_vibrations_max
        K = config.n_nodes_max

        # Vibration arrays
        self.s_pos = np.zeros((N, 2), dtype=np.float64)
        self.s_vel = np.zeros((N, 2), dtype=np.float64)
        self.s_freq = np.zeros(N, dtype=np.float64)
        self.s_pol = np.zeros(N, dtype=np.bool_)
        self.s_alive = np.zeros(N, dtype=np.bool_)
        self.s_locked_this_tick = np.zeros(N, dtype=np.bool_)
        self.n_alive: int = 0

        # Node arrays
        self.k_pos = np.zeros((K, 2), dtype=np.float64)
        self.k_freq = np.zeros(K, dtype=np.float64)
        self.k_pol = np.zeros(K, dtype=np.bool_)
        self.k_level = np.zeros(K, dtype=np.uint8)
        self.k_birth = np.zeros(K, dtype=np.float64)
        self.k_alive = np.zeros(K, dtype=np.bool_)
        self.k_locked_this_tick = np.zeros(K, dtype=np.bool_)

        # Composition (CSR-like)
        comp_caps = K * 4
        self.k_comp_offset = np.zeros(K + 1, dtype=np.int32)
        self.k_comp_indices = np.zeros(comp_caps, dtype=np.int32)
        self.k_comp_kind = np.zeros(K, dtype=np.uint8)
        self.k_comp_used: int = 0
        self.k_count: int = 0

        self._seed()

    # ------------------------------------------------------------------ seeding

    def _seed(self) -> None:
        cfg = self.config
        n = cfg.n_initial_vibrations
        if n == 0:
            return
        self.s_pos[:n, 0] = self.rng.uniform(0.0, cfg.box_size[0], size=n)
        self.s_pos[:n, 1] = self.rng.uniform(0.0, cfg.box_size[1], size=n)
        self.s_freq[:n] = self._sample_frequencies(n)
        self.s_pol[:n] = self.rng.random(n) < cfg.polarity_split
        self.s_vel[:n] = self._sample_velocities(n)
        self.s_alive[:n] = True
        self.n_alive = n

    def _sample_frequencies(self, n: int) -> np.ndarray:
        cfg = self.config
        if cfg.freq_distribution == "log":
            return np.exp(self.rng.uniform(np.log(cfg.freq_min), np.log(cfg.freq_max), size=n))
        elif cfg.freq_distribution == "uniform":
            return self.rng.uniform(cfg.freq_min, cfg.freq_max, size=n)
        else:
            raise ValueError(f"Unknown freq_distribution: {cfg.freq_distribution!r}")

    def _sample_velocities(self, n: int) -> np.ndarray:
        cfg = self.config
        speeds = self.rng.uniform(cfg.speed_min, cfg.speed_max, size=n)
        angles = self.rng.uniform(0.0, 2 * np.pi, size=n)
        v = np.empty((n, 2), dtype=np.float64)
        v[:, 0] = speeds * np.cos(angles)
        v[:, 1] = speeds * np.sin(angles)
        return v

    # --------------------------------------------------------------- allocation

    def allocate_node(
        self,
        pos: np.ndarray,
        freq: float,
        pol: bool,
        level: int,
        constituents: np.ndarray,
        comp_kind: int,
    ) -> int:
        """Append a new node. Returns its index."""
        i = self.k_count
        if i >= self.config.n_nodes_max:
            raise RuntimeError("Node capacity exhausted; increase n_nodes_max or run compaction")
        self.k_pos[i] = pos
        self.k_freq[i] = freq
        self.k_pol[i] = pol
        self.k_level[i] = level
        self.k_birth[i] = self.t
        self.k_alive[i] = True
        self.k_comp_kind[i] = comp_kind
        n_comp = len(constituents)
        start = self.k_comp_used
        end = start + n_comp
        if end > self.k_comp_indices.shape[0]:
            raise RuntimeError("Composition index capacity exhausted")
        self.k_comp_indices[start:end] = constituents
        self.k_comp_offset[i] = start
        self.k_comp_offset[i + 1] = end
        self.k_comp_used = end
        self.k_count += 1
        return i

    def reset_tick_locks(self) -> None:
        self.s_locked_this_tick[:] = False
        self.k_locked_this_tick[:] = False

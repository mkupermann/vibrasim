from __future__ import annotations
import numpy as np
from world.config import WorldConfig

LEVEL_TO_VIBRATIONS = {
    # Phase 1
    1: 2, 2: 4, 3: 6, 4: 8,
    # Phase 2: each atom contributes 8 vibrations; molecule = N atoms.
    5: 16, 6: 24, 7: 32, 8: 40, 9: 48, 10: 56, 11: 64,
}


class World:
    """3D physics state. SoA NumPy arrays, periodic boundaries on all three axes."""

    def __init__(self, config: WorldConfig):
        self.config = config
        self.t: float = 0.0
        self.rng = np.random.default_rng(config.rng_seed)

        N = config.n_vibrations_max
        K = config.n_nodes_max

        # Vibration arrays (3D)
        self.s_pos = np.zeros((N, 3), dtype=np.float64)
        self.s_vel = np.zeros((N, 3), dtype=np.float64)
        self.s_freq = np.zeros(N, dtype=np.float64)
        self.s_pol = np.zeros(N, dtype=np.bool_)
        self.s_alive = np.zeros(N, dtype=np.bool_)
        self.s_locked_this_tick = np.zeros(N, dtype=np.bool_)
        # Plan E — reward polarity tristate per vibration
        self.s_reward_polarity = np.zeros(N, dtype=np.int8)
        self.n_alive: int = 0

        # Node arrays (3D, with velocity for repulsion)
        self.k_pos = np.zeros((K, 3), dtype=np.float64)
        self.k_vel = np.zeros((K, 3), dtype=np.float64)
        self.k_freq = np.zeros(K, dtype=np.float64)
        self.k_pol = np.zeros(K, dtype=np.bool_)
        self.k_level = np.zeros(K, dtype=np.uint8)
        self.k_birth = np.zeros(K, dtype=np.float64)
        self.k_alive = np.zeros(K, dtype=np.bool_)
        self.k_locked_this_tick = np.zeros(K, dtype=np.bool_)
        # PHASE4-R1/R2/R3: per-node integrate-and-fire state.
        # Only level-4 atoms use these; other rows stay at zero.
        self.k_charge = np.zeros(K, dtype=np.float64)
        self.k_refractory_until = np.zeros(K, dtype=np.float64)
        # Plan A — per-node strength field (R2 strength-modulated decay).
        # Default 1.0 so newly-allocated nodes are not immediately decayed away.
        self.k_strength = np.ones(K, dtype=np.float64)
        # Plan B — per-molecule orientation vector for directional propagation.
        # Zero = no orientation inferred yet. Updated as a strength-weighted
        # running average when STDP detects a directional firing pair.
        self.k_orientation = np.zeros((K, 3), dtype=np.float64)
        # Plan E — reward polarity tristate (-1, 0, +1) per node
        # 0 = not from reward channel; +1 = fire_positive origin; -1 = fire_negative origin
        self.k_reward_polarity = np.zeros(K, dtype=np.int8)
        # Plan A.5 — slot recycling
        self.k_ref_count = np.zeros(K, dtype=np.int32)
        self._free_slots: list[int] = []
        self._free_slots_set: set[int] = set()
        # Firing log: (t, atom_index) tuples appended whenever an atom fires.
        # Keeps the substrate self-describing so measurements don't need
        # to re-derive firings from snapshot deltas.
        self.firing_events: list[tuple[float, int]] = []

        # CSR composition
        comp_caps = K * 16  # Plan A.5: larger to accommodate slot recycling appending
        self.k_comp_offset = np.zeros(K + 1, dtype=np.int32)
        # k_comp_end[i] stores the exclusive end of slot i's composition range.
        # Separate from k_comp_offset[i+1] so that recycling slot i does not
        # corrupt the start pointer of slot i+1 (which shares k_comp_offset[i+1]).
        self.k_comp_end = np.zeros(K, dtype=np.int32)
        self.k_comp_indices = np.zeros(comp_caps, dtype=np.int32)
        self.k_comp_kind = np.zeros(K, dtype=np.uint8)
        self.k_comp_used: int = 0
        self.k_count: int = 0

        self._seed()

    def _seed(self) -> None:
        cfg = self.config
        n = cfg.n_initial_vibrations
        if n == 0:
            return
        bx, by, bz = cfg.box_size
        self.s_pos[:n, 0] = self.rng.uniform(0.0, bx, size=n)
        self.s_pos[:n, 1] = self.rng.uniform(0.0, by, size=n)
        self.s_pos[:n, 2] = self.rng.uniform(0.0, bz, size=n)
        self.s_freq[:n] = self._sample_frequencies(n)
        self.s_pol[:n] = self.rng.random(n) < cfg.polarity_split
        self.s_vel[:n] = self._sample_velocities_3d(n)
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

    def _sample_velocities_3d(self, n: int) -> np.ndarray:
        """Isotropic 3D velocities with magnitudes uniformly distributed in [speed_min, speed_max]."""
        cfg = self.config
        speeds = self.rng.uniform(cfg.speed_min, cfg.speed_max, size=n)
        # Uniform points on the unit sphere (Marsaglia method)
        z = self.rng.uniform(-1.0, 1.0, size=n)
        phi = self.rng.uniform(0.0, 2 * np.pi, size=n)
        sqrt_omz2 = np.sqrt(1 - z * z)
        v = np.empty((n, 3), dtype=np.float64)
        v[:, 0] = speeds * sqrt_omz2 * np.cos(phi)
        v[:, 1] = speeds * sqrt_omz2 * np.sin(phi)
        v[:, 2] = speeds * z
        return v

    def allocate_node(
        self, pos: np.ndarray, freq: float, pol: bool, level: int,
        constituents: np.ndarray, comp_kind: int,
    ) -> int:
        # Try to recycle a dead, unreferenced slot first
        if self.config.slot_recycling_enabled and self._free_slots:
            i = self._free_slots.pop()
            self._free_slots_set.discard(i)
            # Reset all per-slot state (note: k_ref_count[i] is already 0 by
            # free-list invariant)
            self.k_pos[i] = 0
            self.k_vel[i] = 0
            self.k_freq[i] = 0
            self.k_pol[i] = False
            self.k_level[i] = 0
            self.k_birth[i] = 0
            self.k_alive[i] = False
            self.k_locked_this_tick[i] = False
            self.k_charge[i] = 0
            self.k_refractory_until[i] = 0
            self.k_strength[i] = 1.0
            self.k_orientation[i] = 0.0  # Plan B: clear stale direction inherited from dead predecessor
            self.k_reward_polarity[i] = 0  # Plan E: clear stale reward tag from dead predecessor
            # k_ref_count[i] is already 0 by free-list invariant
            # Ensure k_count covers this slot (it was previously allocated, so
            # k_count >= i+1 in normal operation; guard for test setups)
            if i >= self.k_count:
                self.k_count = i + 1
        else:
            i = self.k_count
            if i >= self.config.n_nodes_max:
                if getattr(self.config, "graceful_capacity", False):
                    return -1
                raise RuntimeError("Node capacity exhausted")
            self.k_count += 1

        # Populate the slot
        self.k_pos[i] = pos
        self.k_vel[i] = 0.0
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
        self.k_comp_end[i] = end
        self.k_comp_used = end

        # Increment ref counts of constituents (slot recycling bookkeeping).
        # Only applicable when constituents are node indices (comp_kind != 0);
        # comp_kind == 0 means constituents are vibration indices into s_* arrays.
        if self.config.slot_recycling_enabled and comp_kind != 0:
            for c in constituents:
                self.k_ref_count[int(c)] += 1

        return i

    def reset_tick_locks(self) -> None:
        if self.n_alive > 0:
            self.s_locked_this_tick[:self.n_alive] = False
        if self.k_count > 0:
            self.k_locked_this_tick[:self.k_count] = False

    def total_vibrations(self) -> int:
        """Count of vibrations free + bound (for ambient-stability bookkeeping)."""
        free = int(self.s_alive.sum())
        bound = 0
        for level, vib_count in LEVEL_TO_VIBRATIONS.items():
            n_level = int(((self.k_level == level) & self.k_alive).sum())
            bound += n_level * vib_count
        return free + bound

    def ambient_density(self) -> float:
        """Free vibrations per unit volume."""
        bx, by, bz = self.config.box_size
        return float(self.s_alive.sum()) / (bx * by * bz)

    def compact(self) -> None:
        """Pack alive vibrations into the front of the array.

        Refuses to compact when any nodes exist (`k_count > 0`) — vibration
        compaction renames vibration indices, but `k_comp_indices` for level-1
        nodes (electrons) holds the old indices and would be silently corrupted.
        """
        if self.k_count > 0:
            raise RuntimeError(
                "compact() refused: vibration compaction would corrupt "
                f"k_comp_indices for the {self.k_count} existing nodes. "
                "Compaction must be performed before any electrons form, or "
                "extended to remap composition indices (deferred)."
            )
        alive_idx = np.where(self.s_alive)[0]
        n = len(alive_idx)
        if n == 0:
            self.s_pos[:] = 0
            self.s_vel[:] = 0
            self.s_freq[:] = 0
            self.s_pol[:] = False
            self.s_alive[:] = False
            self.n_alive = 0
            return
        self.s_pos[:n] = self.s_pos[alive_idx]
        self.s_vel[:n] = self.s_vel[alive_idx]
        self.s_freq[:n] = self.s_freq[alive_idx]
        self.s_pol[:n] = self.s_pol[alive_idx]
        self.s_alive[:n] = True
        self.s_alive[n:] = False
        self.n_alive = n

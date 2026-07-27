"""Bridges  SoA container for node-to-node directed weighted edges.

A bridge connects a source node to a destination node and carries a
scalar weight that grows with through-flux and decays without it
(spec 5.5). Bridges are directed: bridge(ab) is distinct from
bridge(ba). Nodes survive while they have at least one alive bridge;
when their last bridge breaks they dissociate (handled in plasticity).

This module now supports multiple topologies:
- "homogeneous": Default, all-to-all within binding radius (F1a-F1b).
- "barabasi_albert": Scale-free network topology (biologically inspired).
- "small_world": Small-world network topology (high clustering, short paths).
"""
from __future__ import annotations
import numpy as np
from typing import Literal


class Bridges:
    """Pre-allocated SoA container for bridges between nodes.

    Slot reuse identical to `Quanta` / `Nodes`: lowest-index free slot
    wins on `add`; `_next_search` cursor advances past the just-filled
    slot.

    Each bridge carries (src_slot, dst_slot, weight, last_flux_tick).
    `last_flux_tick` is the most recent tick at which flux through the
    bridge was nonzero  used by the F1b plasticity rule.
    """

    def __init__(self, max_bridges: int):
        self.max_bridges = int(max_bridges)
        N = self.max_bridges
        self.src = np.zeros(N, dtype=np.int64)
        self.dst = np.zeros(N, dtype=np.int64)
        self.weight = np.zeros(N, dtype=np.float64)
        self.last_flux_tick = np.zeros(N, dtype=np.int64)
        self.alive = np.zeros(N, dtype=np.bool_)
        self._next_search = 0

    def n_alive(self) -> int:
        return int(self.alive.sum())

    def add(self, src: int, dst: int, weight: float,
            born_tick: int) -> int:
        N = self.max_bridges
        for i in range(N):
            j = (self._next_search + i) % N
            if not self.alive[j]:
                self.src[j] = int(src)
                self.dst[j] = int(dst)
                self.weight[j] = float(weight)
                self.last_flux_tick[j] = int(born_tick)
                self.alive[j] = True
                self._next_search = (j + 1) % N
                return j
        return -1

    def remove(self, slot: int) -> None:
        if not self.alive[slot]:
            return
        self.alive[slot] = False
        self.weight[slot] = 0.0
        self._next_search = min(self._next_search, slot)

    def find(self, src: int, dst: int) -> int:
        """Return the alive bridge slot with (src, dst) or -1.

        Directed: bridge(ab) and bridge(ba) are distinct.
        """
        mask = self.alive & (self.src == src) & (self.dst == dst)
        idx = np.where(mask)[0]
        if idx.size == 0:
            return -1
        return int(idx[0])

    def clear(self) -> None:
        """Remove all bridges."""
        self.alive[:] = False
        self.weight[:] = 0.0
        self._next_search = 0


class BiologicalBridges(Bridges):
    """Bridges with biological network topology support.
    
    Supports:
    - "barabasi_albert": Scale-free network (preferential attachment).
    - "small_world": Watts-Strogatz small-world network.
    - "er": Erdős-Rényi random graph.
    
    Usage:
        bridges = BiologicalBridges(max_bridges=10000, topology="barabasi_albert")
        bridges.initialize_for_nodes(n_nodes=100, m=3)  # For Barabási-Albert
    """
    
    TopologyType = Literal["homogeneous", "barabasi_albert", "small_world", "er"]
    
    def __init__(
        self,
        max_bridges: int,
        topology: TopologyType = "homogeneous",
        **topology_kwargs
    ):
        super().__init__(max_bridges)
        self.topology = topology
        self.topology_kwargs = topology_kwargs
        self._node_degrees: np.ndarray | None = None  # For Barabási-Albert
    
    def initialize_for_nodes(self, n_nodes: int, rng: np.random.Generator | None = None) -> None:
        """Initialize bridges with the specified topology for n_nodes.
        
        Args:
            n_nodes: Number of nodes to connect.
            rng: Random number generator (optional).
        """
        if rng is None:
            rng = np.random.default_rng()
        
        self.clear()
        
        if self.topology == "barabasi_albert":
            self._initialize_barabasi_albert(n_nodes, rng)
        elif self.topology == "small_world":
            self._initialize_small_world(n_nodes, rng)
        elif self.topology == "er":
            self._initialize_er(n_nodes, rng)
        # "homogeneous" does nothing (bridges added on-demand)
    
    def _initialize_barabasi_albert(
        self,
        n_nodes: int,
        rng: np.random.Generator,
        m: int = 3,
        w0: float = 1.0
    ) -> None:
        """Barabási-Albert scale-free network initialization.
        
        Starts with m fully connected nodes, then adds nodes one by one,
        each connecting to m existing nodes with probability proportional
        to their degree (preferential attachment).
        
        Args:
            n_nodes: Total number of nodes.
            rng: Random number generator.
            m: Number of edges per new node (m <= existing nodes).
            w0: Initial bridge weight.
        """
        if n_nodes <= m:
            # Fully connect all nodes
            for i in range(n_nodes):
                for j in range(i + 1, n_nodes):
                    self.add(i, j, w0, born_tick=0)
                    self.add(j, i, w0, born_tick=0)  # Directed both ways
            return
        
        # Start with m fully connected nodes
        for i in range(m):
            for j in range(i + 1, m):
                self.add(i, j, w0, born_tick=0)
                self.add(j, i, w0, born_tick=0)
        
        # Track degrees for preferential attachment
        degrees = np.array([m - 1] * m, dtype=np.float64)  # Each of first m nodes has m-1 edges
        
        # Add remaining nodes
        for new_node in range(m, n_nodes):
            # Select m existing nodes with probability proportional to degree
            total_degree = degrees.sum()
            if total_degree <= 0:
                # Fallback: connect to random nodes
                targets = rng.choice(new_node, size=m, replace=False)
            else:
                probs = degrees / total_degree
                targets = rng.choice(new_node, size=m, replace=False, p=probs)
            
            # Add bridges (directed both ways)
            for target in targets:
                self.add(new_node, target, w0, born_tick=0)
                self.add(target, new_node, w0, born_tick=0)
                degrees[target] += 1
            
            degrees = np.append(degrees, m)  # New node has m edges
    
    def _initialize_small_world(
        self,
        n_nodes: int,
        rng: np.random.Generator,
        k: int = 4,
        p: float = 0.1,
        w0: float = 1.0
    ) -> None:
        """Watts-Strogatz small-world network initialization.
        
        Creates a ring lattice where each node is connected to its k
        nearest neighbors, then rewires each edge with probability p.
        
        Args:
            n_nodes: Number of nodes.
            rng: Random number generator.
            k: Number of nearest neighbors (must be even).
            p: Rewiring probability.
            w0: Initial bridge weight.
        """
        if k >= n_nodes or k % 2 != 0:
            k = min(4, n_nodes - 1)  # Fallback
        
        # Create ring lattice
        for i in range(n_nodes):
            for j in range(1, k // 2 + 1):
                target = (i + j) % n_nodes
                self.add(i, target, w0, born_tick=0)
                self.add(target, i, w0, born_tick=0)
        
        # Rewire with probability p
        alive_bridges = np.where(self.alive)[0]
        for bridge_idx in alive_bridges:
            if rng.random() < p:
                src = int(self.src[bridge_idx])
                # Find all possible targets (excluding self and existing connections)
                existing_targets = set()
                for b in range(self.max_bridges):
                    if self.alive[b] and self.src[b] == src:
                        existing_targets.add(int(self.dst[b]))
                
                possible_targets = [t for t in range(n_nodes) 
                                   if t != src and t not in existing_targets]
                if possible_targets:
                    new_target = rng.choice(possible_targets)
                    self.dst[bridge_idx] = new_target
    
    def _initialize_er(
        self,
        n_nodes: int,
        rng: np.random.Generator,
        p: float = 0.1,
        w0: float = 1.0
    ) -> None:
        """Erdős-Rényi random graph initialization.
        
        Each edge is included with probability p.
        
        Args:
            n_nodes: Number of nodes.
            rng: Random number generator.
            p: Edge probability.
            w0: Initial bridge weight.
        """
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if rng.random() < p:
                    self.add(i, j, w0, born_tick=0)
                    self.add(j, i, w0, born_tick=0)


def create_bridges(
    max_bridges: int = 10000,
    topology: str = "homogeneous",
    **kwargs
) -> Bridges:
    """Factory function to create Bridges with the specified topology.
    
    Args:
        max_bridges: Maximum number of bridges.
        topology: One of "homogeneous", "barabasi_albert", "small_world", "er".
        **kwargs: Topology-specific arguments.
    
    Returns:
        Bridges or BiologicalBridges instance.
    """
    if topology == "homogeneous":
        return Bridges(max_bridges)
    else:
        return BiologicalBridges(max_bridges, topology=topology, **kwargs)

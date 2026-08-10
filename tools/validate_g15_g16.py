"""G15/G16 Validation: Test dreaming and self-awareness in Flux vs. Legacy.

This script tests:
1. G15 (Dreaming): Offline replay + concept blending.
2. G16 (Self-Awareness): Self-model + prediction error + workspace winner.

Usage:
    python tools/validate_g15_g16.py --duration 30.0 --seed 42
"""
from __future__ import annotations
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import time
import numpy as np
from dataclasses import dataclass


@dataclass
class G15G16Config:
    """Configuration for G15/G16 validation."""
    duration: float = 30.0
    seed: int = 42
    
    # Legacy parameters
    n_initial_vibrations: int = 1000
    box_size: tuple[float, float, float] = (60.0, 60.0, 60.0)
    
    # Flux parameters
    flux_cube_dims: tuple[int, int, int] = (60, 60, 60)
    flux_n_quanta: int = 1000


def test_legacy_g15_g16(cfg: G15G16Config) -> dict:
    """Test G15/G16 in Legacy substrate."""
    from world.config import WorldConfig
    from world.state import World
    from world.physics import tick as legacy_tick
    from world.dream import apply_dream
    from world.self_aware import apply_self_aware
    
    # Create config with G15/G16 enabled
    legacy_cfg = WorldConfig(
        rng_seed=cfg.seed,
        box_size=cfg.box_size,
        n_initial_vibrations=cfg.n_initial_vibrations,
        n_vibrations_max=2048,
        n_nodes_max=8192,  # Increased to match Flux
        # Enable dreaming and self-awareness
        dream_mode_enabled=True,
        dream_replay_seeds_per_tick=5,
        dream_replay_seed_charge=10.0,
        self_aware_enabled=True,
        self_model_window=10.0,
    )
    
    world = World(legacy_cfg)
    
    # Run simulation with G15/G16
    n_ticks = int(cfg.duration / legacy_cfg.dt)
    results = {
        "times": [],
        "atoms": [],
        "dream_events": [],
        "self_aware_events": [],
    }
    
    for tick_index in range(n_ticks):
        # Apply dreaming (G15)
        if legacy_cfg.dream_mode_enabled:
            dream_result = apply_dream(world, legacy_cfg.dt)
            results["dream_events"].append(dream_result)
        
        # Apply self-awareness (G16)
        if legacy_cfg.self_aware_enabled:
            self_aware_result = apply_self_aware(world, legacy_cfg.dt)
            results["self_aware_events"].append(self_aware_result)
        
        # Run physics tick
        legacy_tick(world, legacy_cfg.dt)
        
        # Record stats every 60 ticks (~1s)
        if tick_index % 60 == 0:
            results["times"].append(world.t)
            results["atoms"].append(int(((world.k_level == 4) & world.k_alive).sum()))
    
    return results


def test_flux_g15_g16(cfg: G15G16Config) -> dict:
    """Test G15/G16 in Flux substrate."""
    from world.flux.grid import Grid
    from world.flux.quantum import Quanta
    from world.flux.dynamics import tick
    from world.flux.boundary import inject_hot_floor
    from world.flux.binding import BindingConfig
    from world.flux.bridges import Bridges
    from world.flux.structures import Nodes
    from world.flux.dream import DreamConfig, apply_dream
    from world.flux.self_aware import SelfAwareConfig, SelfAwareState, apply_self_aware
    
    # Initialize Flux world
    grid = Grid(cfg.flux_cube_dims, 1.0)
    quanta = Quanta(cfg.flux_n_quanta)
    nodes = Nodes(1024)
    bridges = Bridges(1024 * 10)
    
    # Initialize quanta
    rng = np.random.default_rng(cfg.seed)
    grid_size = np.array(cfg.flux_cube_dims) * grid.voxel_size
    quanta.pos = rng.uniform(0, grid_size, size=(cfg.flux_n_quanta, 3)).astype(np.float64)
    quanta.vel = rng.uniform(-5, 5, size=(cfg.flux_n_quanta, 3)).astype(np.float64)
    quanta.freq = rng.uniform(100, 10000, size=cfg.flux_n_quanta).astype(np.float64)
    quanta.polarity = rng.choice([-1, 1], size=cfg.flux_n_quanta)
    quanta.alive[:cfg.flux_n_quanta // 2] = True
    
    # Configs
    binding_cfg = BindingConfig()
    
    # G15/G16 configs
    dream_cfg = DreamConfig(
        dream_mode_enabled=True,
        dream_replay_seeds_per_tick=5,
        dream_replay_seed_energy=10.0,
    )
    
    self_aware_cfg = SelfAwareConfig(
        self_aware_enabled=True,
        binding_cfg=binding_cfg,
    )
    self_aware_state = SelfAwareState()
    
    # Injector
    def injector(quanta, grid):
        return inject_hot_floor(quanta, grid, n=5, energy_per=10.0, freq_mean=1000.0)
    
    # Run simulation
    dt = 1.0 / 60.0
    n_ticks = int(cfg.duration / dt)
    results = {
        "times": [],
        "nodes": [],
        "dream_events": [],
        "self_aware_events": [],
    }
    
    for tick_index in range(n_ticks):
        # Apply dreaming (G15) - called BEFORE tick
        if dream_cfg.dream_mode_enabled:
            dream_result = apply_dream(
                quanta, nodes, grid, dt,
                cfg=dream_cfg,
                tick_index=tick_index,
                rng=np.random.default_rng(cfg.seed + tick_index),
            )
            results["dream_events"].append(dream_result)
        
        # Run physics tick. dream/self_aware are applied manually above/below
        # for their diagnostics dicts — do NOT also pass their cfgs into tick(),
        # or both get applied twice per tick (bug found 2026-08-10).
        tick(
            quanta, grid, dt,
            injector=injector,
            nodes=nodes,
            binding_cfg=binding_cfg,
            bridges=bridges,
            rng=np.random.default_rng(cfg.seed + tick_index),
            tick_index=tick_index,
        )
        
        # Apply self-awareness (G16) - called AFTER tick
        if self_aware_cfg.self_aware_enabled:
            self_aware_result = apply_self_aware(
                quanta, nodes, grid, dt,
                cfg=self_aware_cfg,
                state=self_aware_state,
                tick_index=tick_index,
            )
            results["self_aware_events"].append(self_aware_result)
        
        # Record stats every 60 ticks (~1s)
        if tick_index % 60 == 0:
            results["times"].append(tick_index * dt)
            results["nodes"].append(nodes.n_alive())
    
    return results


def compare_g15_g16(legacy_results: dict, flux_results: dict) -> dict:
    """Compare G15/G16 results."""
    comparison = {
        "legacy_dream_events": sum(1 for e in legacy_results["dream_events"] if e.get("replay_seeds_fired", 0) > 0),
        "flux_dream_events": sum(1 for e in flux_results["dream_events"] if e.get("replay_seeds_fired", 0) > 0),
        "legacy_self_aware_events": sum(1 for e in legacy_results["self_aware_events"] if e.get("active_patterns", 0) > 0),
        "flux_self_aware_events": sum(1 for e in flux_results["self_aware_events"] if e.get("active_patterns", 0) > 0),
        "legacy_max_atoms": max(legacy_results["atoms"]) if legacy_results["atoms"] else 0,
        "flux_max_nodes": max(flux_results["nodes"]) if flux_results["nodes"] else 0,
    }
    
    return comparison


def print_g15_g16_comparison(comparison: dict) -> None:
    """Print G15/G16 comparison results."""
    print("\n" + "=" * 60)
    print("G15/G16 VALIDATION RESULTS")
    print("=" * 60)
    
    print(f"\nDreaming (G15):")
    print(f"  Legacy: {comparison['legacy_dream_events']} dream events")
    print(f"  Flux:   {comparison['flux_dream_events']} dream events")
    
    print(f"\nSelf-Awareness (G16):")
    print(f"  Legacy: {comparison['legacy_self_aware_events']} self-aware events")
    print(f"  Flux:   {comparison['flux_self_aware_events']} self-aware events")
    
    print(f"\nStructure Formation:")
    print(f"  Legacy: {comparison['legacy_max_atoms']} max atoms")
    print(f"  Flux:   {comparison['flux_max_nodes']} max nodes")
    
    print("\n" + "=" * 60)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate G15/G16 in Flux vs. Legacy"
    )
    parser.add_argument("--duration", type=float, default=30.0,
                        help="Simulation duration in seconds (default: 30.0)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    
    args = parser.parse_args(argv)
    
    cfg = G15G16Config(
        duration=args.duration,
        seed=args.seed,
    )
    
    print(f"Running G15/G16 validation with seed={cfg.seed}, duration={cfg.duration}s...")
    
    print("\n1. Testing Legacy G15/G16...")
    start = time.time()
    try:
        legacy_results = test_legacy_g15_g16(cfg)
        legacy_time = time.time() - start
        print(f"   Legacy G15/G16 completed in {legacy_time:.2f}s")
    except Exception as e:
        print(f"   Legacy G15/G16 FAILED: {e}")
        legacy_results = {"times": [], "atoms": [], "dream_events": [], "self_aware_events": []}
    
    print("\n2. Testing Flux G15/G16...")
    start = time.time()
    try:
        flux_results = test_flux_g15_g16(cfg)
        flux_time = time.time() - start
        print(f"   Flux G15/G16 completed in {flux_time:.2f}s")
    except Exception as e:
        print(f"   Flux G15/G16 FAILED: {e}")
        flux_results = {"times": [], "nodes": [], "dream_events": [], "self_aware_events": []}
    
    print("\n3. Comparing G15/G16 results...")
    comparison = compare_g15_g16(legacy_results, flux_results)
    print_g15_g16_comparison(comparison)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

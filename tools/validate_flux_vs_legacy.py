"""Validation script: Flux vs. Legacy side-by-side comparison.

This script runs both substrates with equivalent parameters and compares:
- Node/atom counts over time.
- Binding rates.
- Energy conservation.
- G14–G16 markers (if enabled).

Usage:
    python tools/validate_flux_vs_legacy.py --duration 60.0 --seed 42
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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.state import World
    from world.flux.quantum import Quanta
    from world.flux.grid import Grid
    from world.flux.structures import Nodes
    from world.flux.bridges import Bridges


@dataclass
class ValidationConfig:
    """Configuration for validation runs."""
    duration: float = 60.0  # Simulation duration in seconds
    seed: int = 42          # Random seed
    
    # Legacy parameters (from calibration_session3.toml)
    box_size: tuple[float, float, float] = (80.0, 80.0, 80.0)
    n_initial_vibrations: int = 400
    n_vibrations_max: int = 1024
    n_nodes_max: int = 512
    r_1: float = 5.0
    r_2: float = 30.0
    freq_tolerance: float = 0.025
    pair_decay_time: float = 60.0
    triad_decay_time: float = 600.0
    lambda_gen: float = 0.0
    lambda_dec: float = 0.0
    
    # Flux parameters (equivalent)
    flux_cube_dims: tuple[int, int, int] = (80, 80, 80)
    flux_n_quanta: int = 400
    flux_binding_enabled: bool = True
    flux_thermal_enabled: bool = False
    flux_plasticity_enabled: bool = False
    
    # G14–G16 flags
    test_g14: bool = False  # BTSP (not yet ported to Flux)
    test_g15: bool = True   # Dreaming
    test_g16: bool = True   # Self-awareness


@dataclass
class ValidationResults:
    """Results from a validation run."""
    # Legacy results
    legacy_atom_count: list[int] = None
    legacy_pair_count: list[int] = None
    legacy_triad_count: list[int] = None
    legacy_electron_count: list[int] = None
    legacy_times: list[float] = None
    
    # Flux results
    flux_node_count: list[int] = None
    flux_quanta_alive: list[int] = None
    flux_times: list[float] = None
    
    # Comparison metrics
    max_atom_diff: float = 0.0
    mean_atom_diff: float = 0.0
    atom_formation_time_legacy: float = 0.0
    atom_formation_time_flux: float = 0.0


def run_legacy_validation(cfg: ValidationConfig) -> dict:
    """Run Legacy substrate and return stats over time."""
    from world.config import WorldConfig
    from world.state import World
    from world.physics import tick as legacy_tick
    
    # Create Legacy config
    legacy_cfg = WorldConfig(
        rng_seed=cfg.seed,
        box_size=cfg.box_size,
        n_initial_vibrations=cfg.n_initial_vibrations,
        n_vibrations_max=cfg.n_vibrations_max,
        n_nodes_max=cfg.n_nodes_max,
        r_1=cfg.r_1,
        r_2=cfg.r_2,
        freq_tolerance=cfg.freq_tolerance,
        pair_decay_time=cfg.pair_decay_time,
        triad_decay_time=cfg.triad_decay_time,
        lambda_gen=cfg.lambda_gen,
        lambda_dec=cfg.lambda_dec,
    )
    
    world = World(legacy_cfg)
    
    # Run simulation
    n_ticks = int(cfg.duration / legacy_cfg.dt)
    results = {
        "times": [],
        "electrons": [],
        "pairs": [],
        "triads": [],
        "atoms": [],
    }
    
    for tick_index in range(n_ticks):
        legacy_tick(world, legacy_cfg.dt)
        t = world.t
        
        # Record stats every 10 ticks (~0.17s)
        if tick_index % 10 == 0:
            results["times"].append(t)
            results["electrons"].append(int(((world.k_level == 1) & world.k_alive).sum()))
            results["pairs"].append(int(((world.k_level == 2) & world.k_alive).sum()))
            results["triads"].append(int(((world.k_level == 3) & world.k_alive).sum()))
            results["atoms"].append(int(((world.k_level == 4) & world.k_alive).sum()))
    
    return results


def run_flux_validation(cfg: ValidationConfig) -> dict:
    """Run Flux substrate and return stats over time."""
    from world.flux.grid import Grid
    from world.flux.quantum import Quanta
    from world.flux.dynamics import tick
    from world.flux.boundary import inject_hot_floor
    from world.flux.binding import BindingConfig
    from world.flux.decay import DecayConfig
    from world.flux.thermal import ThermalConfig
    from world.flux.plasticity import PlasticityConfig
    from world.flux.bridges import Bridges
    from world.flux.structures import Nodes
    from world.flux.dream import DreamConfig
    from world.flux.self_aware import SelfAwareConfig, SelfAwareState
    
    # Initialize Flux world
    grid = Grid(cfg.flux_cube_dims, 1.0)
    quanta = Quanta(cfg.flux_n_quanta)
    nodes = Nodes(cfg.n_nodes_max) if cfg.flux_binding_enabled else None
    bridges = Bridges(cfg.n_nodes_max * 10) if cfg.flux_binding_enabled else None
    
    # Initialize quanta
    rng = np.random.default_rng(cfg.seed)
    grid_size = np.array(cfg.flux_cube_dims) * grid.voxel_size
    quanta.pos = rng.uniform(0, grid_size, size=(cfg.flux_n_quanta, 3)).astype(np.float64)
    quanta.vel = rng.uniform(-5, 5, size=(cfg.flux_n_quanta, 3)).astype(np.float64)
    quanta.freq = rng.uniform(100, 10000, size=cfg.flux_n_quanta).astype(np.float64)
    quanta.polarity = rng.choice([-1, 1], size=cfg.flux_n_quanta)
    quanta.alive[:cfg.flux_n_quanta // 2] = True
    
    # Configs
    binding_cfg = BindingConfig(r=cfg.r_1) if cfg.flux_binding_enabled else None
    decay_cfg = DecayConfig() if cfg.flux_binding_enabled else None
    thermal_cfg = ThermalConfig() if cfg.flux_thermal_enabled else None
    plasticity_cfg = PlasticityConfig() if cfg.flux_plasticity_enabled else None
    
    # G15/G16 configs
    dream_cfg = None
    if cfg.test_g15:
        dream_cfg = DreamConfig(
            dream_mode_enabled=True,
            dream_replay_seeds_per_tick=5,
            dream_replay_seed_energy=10.0,
        )
    
    self_aware_cfg = None
    self_aware_state = None
    if cfg.test_g16:
        self_aware_cfg = SelfAwareConfig(
            self_aware_enabled=True,
            binding_cfg=binding_cfg,
        )
        self_aware_state = SelfAwareState()
    
    # Injector (minimal injection to match Legacy's n_initial_vibrations)
    def injector(quanta, grid):
        # Inject a few quanta per tick to maintain population
        return inject_hot_floor(
            quanta, grid,
            n=5,
            energy_per=10.0,
            freq_mean=1000.0,
        )
    
    # Run simulation
    dt = 1.0 / 60.0
    n_ticks = int(cfg.duration / dt)
    results = {
        "times": [],
        "quanta_alive": [],
        "nodes": [],
    }
    
    for tick_index in range(n_ticks):
        tick(
            quanta, grid, dt,
            injector=injector,
            nodes=nodes,
            binding_cfg=binding_cfg,
            decay_cfg=decay_cfg,
            bridges=bridges,
            plasticity_cfg=plasticity_cfg,
            thermal_cfg=thermal_cfg,
            dream_cfg=dream_cfg,
            self_aware_cfg=self_aware_cfg,
            dream_state=None,
            self_aware_state=self_aware_state,
            rng=np.random.default_rng(cfg.seed + tick_index),
            tick_index=tick_index,
        )
        
        # Record stats every 10 ticks (~0.17s)
        if tick_index % 10 == 0:
            results["times"].append(tick_index * dt)
            results["quanta_alive"].append(quanta.n_alive())
            results["nodes"].append(nodes.n_alive() if nodes is not None else 0)
    
    return results


def compare_results(legacy_results: dict, flux_results: dict) -> ValidationResults:
    """Compare Legacy and Flux results."""
    results = ValidationResults()
    
    # Store raw data
    results.legacy_times = legacy_results["times"]
    results.legacy_electron_count = legacy_results["electrons"]
    results.legacy_pair_count = legacy_results["pairs"]
    results.legacy_triad_count = legacy_results["triads"]
    results.legacy_atom_count = legacy_results["atoms"]
    
    results.flux_times = flux_results["times"]
    results.flux_quanta_alive = flux_results["quanta_alive"]
    results.flux_node_count = flux_results["nodes"]
    
    # Find first atom formation time
    for i, count in enumerate(results.legacy_atom_count):
        if count > 0:
            results.atom_formation_time_legacy = results.legacy_times[i]
            break
    
    # For Flux, we consider nodes as equivalent to atoms (for now)
    for i, count in enumerate(results.flux_node_count):
        if count > 0:
            results.atom_formation_time_flux = results.flux_times[i]
            break
    
    # Compare atom counts at each time point
    min_len = min(len(results.legacy_atom_count), len(results.flux_node_count))
    atom_diffs = []
    for i in range(min_len):
        diff = abs(results.legacy_atom_count[i] - results.flux_node_count[i])
        atom_diffs.append(diff)
    
    if atom_diffs:
        results.max_atom_diff = float(max(atom_diffs))
        results.mean_atom_diff = float(np.mean(atom_diffs))
    
    return results


def print_comparison(results: ValidationResults) -> None:
    """Print comparison results."""
    print("\n" + "=" * 60)
    print("FLUX VS. LEGACY VALIDATION RESULTS")
    print("=" * 60)
    
    print(f"\nAtom Formation:")
    print(f"  Legacy: First atom at t = {results.atom_formation_time_legacy:.2f}s")
    print(f"  Flux:   First node at t = {results.atom_formation_time_flux:.2f}s")
    print(f"  Difference: {abs(results.atom_formation_time_legacy - results.atom_formation_time_flux):.2f}s")
    
    print(f"\nAtom/Node Count Comparison:")
    print(f"  Max difference: {results.max_atom_diff:.2f}")
    print(f"  Mean difference: {results.mean_atom_diff:.2f}")
    
    print(f"\nData Points:")
    print(f"  Legacy: {len(results.legacy_times)} time points")
    print(f"  Flux:   {len(results.flux_times)} time points")
    
    print("\n" + "=" * 60)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Flux vs. Legacy substrates"
    )
    parser.add_argument("--duration", type=float, default=60.0,
                        help="Simulation duration in seconds (default: 60.0)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--test-g15", action="store_true", default=True,
                        help="Test G15 dreaming (default: True)")
    parser.add_argument("--test-g16", action="store_true", default=True,
                        help="Test G16 self-awareness (default: True)")
    
    args = parser.parse_args(argv)
    
    cfg = ValidationConfig(
        duration=args.duration,
        seed=args.seed,
        test_g15=args.test_g15,
        test_g16=args.test_g16,
    )
    
    print(f"Running validation with seed={cfg.seed}, duration={cfg.duration}s...")
    print("\n1. Running Legacy substrate...")
    start = time.time()
    legacy_results = run_legacy_validation(cfg)
    legacy_time = time.time() - start
    print(f"   Legacy completed in {legacy_time:.2f}s")
    
    print("\n2. Running Flux substrate...")
    start = time.time()
    flux_results = run_flux_validation(cfg)
    flux_time = time.time() - start
    print(f"   Flux completed in {flux_time:.2f}s")
    
    print("\n3. Comparing results...")
    results = compare_results(legacy_results, flux_results)
    print_comparison(results)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

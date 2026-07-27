"""CLI entry point for the Flux Substrate simulation.

This is the primary way to run the Flux-based substrate (F0-F1c).
Usage:
    python -m world run-flux --duration 60.0 --snapshot-every 5.0
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path
import numpy as np

from world.flux.grid import Grid
from world.flux.quantum import Quanta
from world.flux.dynamics import tick, Injector
from world.flux.boundary import inject_hot_floor, absorb_cold_faces
from world.flux.binding import BindingConfig
from world.flux.decay import DecayConfig
from world.flux.thermal import ThermalConfig
from world.flux.plasticity import PlasticityConfig
from world.flux.bridges import Bridges
from world.flux.structures import Nodes
from world.flux.audit import EnergyAuditor


def create_flux_world(
    cube_dims: tuple[int, int, int] = (80, 40, 10),
    voxel_size: float = 1.0,
    n_quanta: int = 10000,
    rng_seed: int | None = 42,
    thermal_enabled: bool = True,
    binding_enabled: bool = True,
    plasticity_enabled: bool = True,
) -> tuple[Quanta, Grid, Nodes | None, Bridges | None]:
    """Initialize a Flux substrate world with sensible defaults (F1c-compatible)."""
    rng = np.random.default_rng(rng_seed)
    
    # Grid
    grid = Grid(cube_dims, voxel_size)
    
    # Quanta (free vibrations)
    quanta = Quanta(n_quanta, rng=rng)
    
    # Initialize positions and velocities
    quanta.pos = rng.uniform(0, grid.size, size=(n_quanta, 3)).astype(np.float64)
    quanta.vel = rng.uniform(-5, 5, size=(n_quanta, 3)).astype(np.float64)
    quanta.freq = rng.uniform(100, 10000, size=n_quanta).astype(np.float64)
    quanta.polarity = rng.choice([-1, 1], size=n_quanta)
    quanta.alive[:n_quanta // 2] = True  # Start with 50% alive
    
    # Nodes and Bridges (for F1b+)
    nodes = Nodes() if binding_enabled else None
    bridges = Bridges() if binding_enabled else None
    
    return quanta, grid, nodes, bridges


def create_injector(grid: Grid, energy_per_tick: float = 100.0) -> Injector:
    """Create a hot-floor injector for the Flux substrate."""
    def injector(quanta: Quanta, grid: Grid) -> float:
        return inject_hot_floor(quanta, grid, energy_per_tick)
    return injector


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="world run-flux",
        description="Flux Substrate Simulation (F0-F1c)"
    )
    parser.add_argument("--duration", type=float, default=60.0,
                        help="Simulation duration in seconds (default: 60.0)")
    parser.add_argument("--snapshot-every", type=float, default=None,
                        help="Save snapshot every N seconds")
    parser.add_argument("--snapshot-dir", type=Path, default=None,
                        help="Directory to save snapshots")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--cube", type=int, nargs=3, default=[80, 40, 10],
                        help="Grid dimensions as Lx Ly Lz (default: 80 40 10)")
    parser.add_argument("--n-quanta", type=int, default=10000,
                        help="Number of quanta (default: 10000)")
    parser.add_argument("--thermal", action="store_true", default=True,
                        help="Enable thermal dynamics (F1c)")
    parser.add_argument("--binding", action="store_true", default=True,
                        help="Enable binding (F1a)")
    parser.add_argument("--plasticity", action="store_true", default=True,
                        help="Enable plasticity (F1b)")
    parser.add_argument("--energy-audit", action="store_true", default=False,
                        help="Enable energy conservation audit")
    
    args = parser.parse_args(argv)
    
    # Initialize world
    cube_dims = tuple(args.cube)
    quanta, grid, nodes, bridges = create_flux_world(
        cube_dims=cube_dims,
        n_quanta=args.n_quanta,
        rng_seed=args.seed,
        thermal_enabled=args.thermal,
        binding_enabled=args.binding,
        plasticity_enabled=args.plasticity,
    )
    
    # Configs
    binding_cfg = BindingConfig() if args.binding else None
    decay_cfg = DecayConfig() if args.binding else None
    thermal_cfg = ThermalConfig() if args.thermal else None
    plasticity_cfg = PlasticityConfig() if args.plasticity else None
    
    # Injector
    injector = create_injector(grid, energy_per_tick=100.0)
    
    # Energy auditor
    auditor = EnergyAuditor() if args.energy_audit else None
    
    # Snapshot setup
    if args.snapshot_dir:
        args.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Simulation loop
    dt = 1.0 / 60.0  # Fixed timestep
    n_ticks = int(args.duration / dt)
    snap_step = int(args.snapshot_every / dt) if args.snapshot_every else None
    
    start = time.time()
    total_energy_exported = 0.0
    total_binding_heat = 0.0
    total_decay_heat = 0.0
    
    try:
        for tick_index in range(n_ticks):
            t = tick_index * dt
            
            result = tick(
                quanta, grid, dt,
                injector=injector,
                nodes=nodes,
                binding_cfg=binding_cfg,
                decay_cfg=decay_cfg,
                bridges=bridges,
                plasticity_cfg=plasticity_cfg,
                thermal_cfg=thermal_cfg,
                rng=np.random.default_rng(args.seed + tick_index) if args.seed else None,
                tick_index=tick_index,
            )
            
            if nodes is not None:
                E_exported, binding_heat, decay_heat = result
                total_energy_exported += E_exported
                total_binding_heat += binding_heat
                total_decay_heat += decay_heat
            else:
                E_exported = result
                total_energy_exported += E_exported
            
            # Print stats every 10 ticks (for progress feedback)
            if (tick_index + 1) % 60 == 0:
                _print_stats(quanta, nodes, t, total_energy_exported)
            
            # Save snapshot
            if snap_step and (tick_index + 1) % snap_step == 0 and args.snapshot_dir:
                _save_snapshot(quanta, nodes, bridges, grid, args.snapshot_dir, t)
                _print_stats(quanta, nodes, t, total_energy_exported)
        
    except KeyboardInterrupt:
        print("\n# Interrupted by user")
    
    wall = time.time() - start
    print(f"# done  {args.duration:.1f} simulated s in {wall:.1f} wall s "
          f"({args.duration / wall:.1f}x real-time)")
    _print_stats(quanta, nodes, args.duration, total_energy_exported)
    
    if args.energy_audit and auditor:
        print(f"# Energy audit: exported={total_energy_exported:.2f}, "
              f"binding_heat={total_binding_heat:.2f}, decay_heat={total_decay_heat:.2f}")
    
    return 0


def _print_stats(quanta: Quanta, nodes: Nodes | None, t: float, energy_exported: float) -> None:
    n_alive = quanta.n_alive()
    n_nodes = nodes.n_alive() if nodes is not None else 0
    n_bridges = nodes.n_bridges() if nodes is not None else 0
    
    print(f"t = {t:7.2f} | quanta_alive {n_alive:6d} | nodes {n_nodes:4d} | "
          f"bridges {n_bridges:4d} | E_exported {energy_exported:.2f}")


def _save_snapshot(
    quanta: Quanta,
    nodes: Nodes | None,
    bridges: Bridges | None,
    grid: Grid,
    snapshot_dir: Path,
    t: float,
) -> None:
    """Save a snapshot of the Flux world state."""
    import numpy as np
    snapshot_path = snapshot_dir / f"flux_t_{t:.2f}.npz"
    
    data = {
        "quanta_pos": quanta.pos,
        "quanta_vel": quanta.vel,
        "quanta_freq": quanta.freq,
        "quanta_polarity": quanta.polarity,
        "quanta_alive": quanta.alive,
        "t": t,
    }
    
    if nodes is not None:
        data["nodes_pos"] = nodes.pos
        data["nodes_alive"] = nodes.alive
        data["nodes_level"] = nodes.level
    
    if bridges is not None:
        data["bridges_src"] = bridges.src
        data["bridges_dst"] = bridges.dst
        data["bridges_strength"] = bridges.strength
    
    np.savez(snapshot_path, **data)


if __name__ == "__main__":
    sys.exit(main())

"""CLI entry point for the World of Vibrations simulation.

Default substrate: Flux (F0-F1c, recommended).
Use `--substrate legacy` for the original (deprecated).

Usage:
    python -m world run --substrate flux --duration 60.0  # Flux (default)
    python -m world run --substrate legacy --duration 60.0  # Legacy (deprecated)
"""
from __future__ import annotations
import argparse
import sys
import time
from dataclasses import replace
from pathlib import Path

from world.config import WorldConfig, load_config
from world.state import World
from world.physics import tick as legacy_tick
from world.snapshot import save_snapshot, snapshot_filename


def run_legacy(args: argparse.Namespace, cfg: WorldConfig) -> int:
    """Run the legacy substrate simulation (DEPRECATED).
    
    WARNING: Legacy substrate is deprecated as of 2026-08-10.
    Use --substrate flux instead. Legacy will be removed in a future release.
    No new features will be added to Legacy; only critical bug fixes.
    """
    import warnings
    # Force deprecation warnings to be displayed
    warnings.filterwarnings("always", category=DeprecationWarning)
    warnings.warn(
        "LEGACY SUBSTRATE IS DEPRECATED as of 2026-08-10. "
        "Use --substrate flux instead. "
        "Legacy will be removed in a future release. "
        "No new features will be added; only critical bug fixes.",
        DeprecationWarning,
        stacklevel=2
    )
    if args.seed is not None:
        cfg = replace(cfg, rng_seed=args.seed)
    world = World(cfg)

    if args.snapshot_dir:
        args.snapshot_dir.mkdir(parents=True, exist_ok=True)

    preview = None
    if args.preview:
        from world.preview import LivePreview
        preview = LivePreview(world)
        preview.start()

    n_ticks = int(args.duration / cfg.dt)
    snap_step = int(args.snapshot_every / cfg.dt) if args.snapshot_every else None
    start = time.time()
    try:
        for k in range(n_ticks):
            legacy_tick(world, cfg.dt)
            if snap_step and (k + 1) % snap_step == 0 and args.snapshot_dir:
                path = args.snapshot_dir / snapshot_filename(world.t)
                save_snapshot(world, path)
                _print_legacy_stats(world)
    finally:
        if preview:
            preview.stop()

    wall = time.time() - start
    print(f"# done  {args.duration:.1f} simulated s in {wall:.1f} wall s "
          f"({args.duration / wall:.1f} real-time)")
    _print_legacy_stats(world)
    if args.save:
        save_snapshot(world, args.save)
    return 0


def run_flux(args: argparse.Namespace) -> int:
    """Run the Flux substrate simulation by delegating to world.run_flux.

    Single source of truth for the flux loop is world/run_flux.py::main —
    this wrapper only translates the `world run` argparse namespace into
    run_flux argv (review 2026-08-10: the previous inline copy of the loop
    had already drifted from run_flux.py).
    """
    from world.run_flux import main as flux_main

    flux_argv = [f"--duration={args.duration}"]
    if args.snapshot_every is not None:
        flux_argv.append(f"--snapshot-every={args.snapshot_every}")
    if args.snapshot_dir is not None:
        flux_argv.append(f"--snapshot-dir={args.snapshot_dir}")
    if args.seed is not None:
        flux_argv.append(f"--seed={args.seed}")
    if args.cube:
        flux_argv.append("--cube")
        flux_argv.extend(str(c) for c in args.cube)
    if args.n_quanta is not None:
        flux_argv.append(f"--n-quanta={args.n_quanta}")
    flux_argv.append("--thermal" if args.thermal else "--no-thermal")
    flux_argv.append("--binding" if args.binding else "--no-binding")
    flux_argv.append("--plasticity" if args.plasticity else "--no-plasticity")
    if args.energy_audit:
        flux_argv.append("--energy-audit")
    if args.dream:
        flux_argv.append("--dream")
        flux_argv.append(f"--dream-seeds={args.dream_seeds}")
        flux_argv.append(f"--dream-energy={args.dream_energy}")
    if args.self_aware:
        flux_argv.append("--self-aware")
    if args.visualize:
        flux_argv.append("--visualize")
        flux_argv.append(f"--viz-interval={args.viz_interval}")
        flux_argv.append(f"--viz-dir={args.viz_dir}")

    return flux_main(flux_argv)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="world", description="World of Vibrations")
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    # Main run command
    run = sub.add_parser("run", help="Run simulation (Flux by default)")
    run.add_argument("--substrate", type=str, default="flux",
                     choices=["flux", "legacy"],
                     help="Substrate to use: 'flux' (default, F0-F1c, recommended) or 'legacy' (deprecated)")
    run.add_argument("--config", type=Path, default=None,
                     help="Config file (legacy only)")
    run.add_argument("--duration", type=float, default=60.0)
    run.add_argument("--snapshot-every", type=float, default=None)
    run.add_argument("--snapshot-dir", type=Path, default=None)
    run.add_argument("--save", type=Path, default=None)
    run.add_argument("--seed", type=int, default=None)
    run.add_argument("--preview", action="store_true",
                     help="Open PyVista live preview (legacy only)")
    
    # Flux-specific arguments (only used when substrate=flux)
    run.add_argument("--cube", type=int, nargs=3, default=None,
                     help="Grid dimensions Lx Ly Lz (flux only, default: 80 40 10)")
    run.add_argument("--n-quanta", type=int, default=None,
                     help="Number of quanta (flux only, default: 10000)")
    run.add_argument("--thermal", action=argparse.BooleanOptionalAction, default=True,
                     help="Enable thermal dynamics (flux only, F1c)")
    run.add_argument("--binding", action=argparse.BooleanOptionalAction, default=True,
                     help="Enable binding (flux only, F1a)")
    run.add_argument("--plasticity", action=argparse.BooleanOptionalAction, default=True,
                     help="Enable plasticity (flux only, F1b)")
    run.add_argument("--energy-audit", action="store_true", default=False,
                     help="Enable energy conservation audit (flux only)")
    run.add_argument("--dream", action="store_true", default=False,
                     help="Enable G15 dreaming (flux only)")
    run.add_argument("--self-aware", action="store_true", default=False,
                     help="Enable G16 self-awareness (flux only)")
    run.add_argument("--dream-seeds", type=int, default=5,
                     help="Number of dream replay seeds per tick (flux only, default: 5)")
    run.add_argument("--dream-energy", type=float, default=10.0,
                     help="Energy to inject per dream seed (flux only, default: 10.0)")
    run.add_argument("--visualize", action="store_true", default=False,
                     help="Enable 3D visualization (saves frames to --viz-dir)")
    run.add_argument("--viz-interval", type=float, default=2.0,
                     help="Visualization update interval in seconds (default: 2.0)")
    run.add_argument("--viz-dir", type=str, default="/tmp/flux_viz",
                     help="Directory to save visualization frames (default: /tmp/flux_viz)")
    gui = sub.add_parser("gui", help="Open the interactive PyVista viewer (legacy only)")
    gui.add_argument("--config", type=Path, default=None)
    gui.add_argument("--seed", type=int, default=None)
    gui.add_argument("--snapshot-dir", type=Path, default=None)

    args = parser.parse_args(argv)

    if args.cmd == "gui":
        from world.interactive import run_interactive
        return run_interactive(
            config_path=args.config,
            seed=args.seed,
            snapshot_dir=args.snapshot_dir,
        )

    if args.cmd == "run":
        if args.substrate == "flux":
            return run_flux(args)
        else:  # legacy
            cfg = load_config(args.config)
            return run_legacy(args, cfg)

    return 0


def _print_legacy_stats(world):
    n_v = int(world.s_alive.sum())
    n_e = int(((world.k_level == 1) & world.k_alive).sum())
    n_p = int(((world.k_level == 2) & world.k_alive).sum())
    n_t = int(((world.k_level == 3) & world.k_alive).sum())
    n_a = int(((world.k_level == 4) & world.k_alive).sum())
    print(f"t = {world.t:7.2f} | total_v {world.total_vibrations():6d} "
          f"| ambient {world.ambient_density():.4e} "
          f"| vibr {n_v:5d} | e- {n_e:4d} | pair {n_p:3d} | "
          f"triad {n_t:3d} | atom {n_a:3d}")


if __name__ == "__main__":
    sys.exit(main())

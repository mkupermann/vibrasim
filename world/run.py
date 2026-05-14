"""CLI entry point for the World of Vibrations simulation."""
from __future__ import annotations
import argparse
import sys
import time
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig, load_config
from world.state import World
from world.physics import tick
from world.snapshot import save_snapshot, snapshot_filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="world", description="World of Vibrations")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    run.add_argument("--config", type=Path, default=None)
    run.add_argument("--duration", type=float, default=60.0)
    run.add_argument("--snapshot-every", type=float, default=None)
    run.add_argument("--snapshot-dir", type=Path, default=None)
    run.add_argument("--save", type=Path, default=None)
    run.add_argument("--seed", type=int, default=None)
    run.add_argument("--preview", action="store_true",
                     help="open PyVista live preview alongside the simulation")

    gui = sub.add_parser("gui", help="open the interactive PyVista viewer (play/pause, sliders, picker)")
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

    cfg = load_config(args.config)
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
            tick(world, cfg.dt)
            if snap_step and (k + 1) % snap_step == 0 and args.snapshot_dir:
                path = args.snapshot_dir / snapshot_filename(world.t)
                save_snapshot(world, path)
                _print_stats(world)
    finally:
        if preview:
            preview.stop()

    wall = time.time() - start
    print(f"# done — {args.duration:.1f} simulated s in {wall:.1f} wall s "
          f"({args.duration / wall:.1f}× real-time)")
    _print_stats(world)
    if args.save:
        save_snapshot(world, args.save)
    return 0


def _print_stats(world):
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

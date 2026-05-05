"""CLI entry point for the World of Vibrations simulation."""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path
import numpy as np

from world.config import WorldConfig, load_config
from world.state import World
from world.physics import tick


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="world", description="World of Vibrations")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="run the simulation")
    run.add_argument("--config", type=Path, default=None,
                     help="TOML override file for WorldConfig")
    run.add_argument("--headless", action="store_true",
                     help="run without opening a Pygame window")
    run.add_argument("--duration", type=float, default=None,
                     help="seconds of simulated time (headless only)")
    run.add_argument("--snapshot-every", type=float, default=None,
                     help="print stats line every N simulated seconds (headless)")
    run.add_argument("--save", type=Path, default=None,
                     help="write final state to NPZ on exit")
    run.add_argument("--seed", type=int, default=None, help="override rng_seed")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    if args.seed is not None:
        from dataclasses import replace
        cfg = replace(cfg, rng_seed=args.seed)
    world = World(cfg)

    if args.headless:
        return _run_headless(world, cfg, args)
    return _run_window(world, cfg)


def _run_headless(world: World, cfg: WorldConfig, args) -> int:
    duration = args.duration if args.duration is not None else 60.0
    n_ticks = int(duration / cfg.dt)
    snap_step = int(args.snapshot_every / cfg.dt) if args.snapshot_every else None
    start = time.time()
    for k in range(n_ticks):
        tick(world, cfg.dt)
        if snap_step and (k + 1) % snap_step == 0:
            _print_stats(world)
    wall = time.time() - start
    print(f"# done — {duration:.1f} simulated s in {wall:.1f} wall s "
          f"({duration / wall:.1f}× real-time)")
    _print_stats(world)
    if args.save:
        _save_state(world, args.save)
    return 0


def _run_window(world: World, cfg: WorldConfig) -> int:
    import pygame
    from world.render import Renderer
    renderer = Renderer(world)
    paused = False
    try:
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return 0
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        return 0
                    if ev.key == pygame.K_SPACE:
                        paused = not paused
                    if ev.key == pygame.K_r:
                        world = World(cfg)
                        renderer.world = world
                        paused = False
            if not paused:
                tick(world, cfg.dt)
            renderer.draw()
    finally:
        renderer.close()


def _print_stats(world: World) -> None:
    n_v = int(world.n_alive)
    n_e = int(np.sum((world.k_level[:world.k_count] == 1) & world.k_alive[:world.k_count]))
    n_p = int(np.sum((world.k_level[:world.k_count] == 2) & world.k_alive[:world.k_count]))
    n_t = int(np.sum((world.k_level[:world.k_count] == 3) & world.k_alive[:world.k_count]))
    n_a = int(np.sum((world.k_level[:world.k_count] == 4) & world.k_alive[:world.k_count]))
    print(f"t = {world.t:7.2f} | vibr {n_v:5d} | e- {n_e:4d} | "
          f"pair {n_p:4d} | triad {n_t:4d} | atom {n_a:4d}")


def _save_state(world: World, path: Path) -> None:
    np.savez(path,
             s_pos=world.s_pos, s_vel=world.s_vel, s_freq=world.s_freq,
             s_pol=world.s_pol, s_alive=world.s_alive,
             k_pos=world.k_pos, k_freq=world.k_freq, k_pol=world.k_pol,
             k_level=world.k_level, k_birth=world.k_birth, k_alive=world.k_alive,
             k_comp_offset=world.k_comp_offset, k_comp_indices=world.k_comp_indices,
             k_comp_kind=world.k_comp_kind, t=world.t)


if __name__ == "__main__":
    sys.exit(main())

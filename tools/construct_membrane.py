"""Hand-construct a synthetic shell of molecules for stability testing.

Places `n_molecules` molecules at evenly-spaced points on a sphere using the
Fibonacci lattice. Each molecule is a synthetic level-5 (di-atomic) node with
no actual atom constituents — adequate for testing whether the placement holds
together under repulsion and ambient regeneration.

Usage:
    python tools/construct_membrane.py --output shell.npz \
        [--centre 50,50,50] [--radius 30] [--n-molecules 30]
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot


def fibonacci_sphere(n: int, radius: float, centre: np.ndarray) -> np.ndarray:
    """Return n points evenly distributed on the surface of a sphere.

    Uses the Fibonacci spiral / golden-angle method for low-discrepancy coverage.
    """
    points = np.zeros((n, 3), dtype=np.float64)
    golden = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        y = 1.0 - 2.0 * i / max(n - 1, 1)
        r_xy = math.sqrt(max(1.0 - y * y, 0.0))
        theta = i * golden
        x = math.cos(theta) * r_xy
        z = math.sin(theta) * r_xy
        points[i] = centre + radius * np.array([x, y, z])
    return points


def construct_shell(world: World, centre: np.ndarray, radius: float,
                    n_molecules: int, level: int = 5,
                    base_freq: float = 30000.0) -> list[int]:
    """Place n_molecules molecules on a Fibonacci sphere. Returns slot indices."""
    points = fibonacci_sphere(n_molecules, radius, centre)
    indices: list[int] = []
    for i, p in enumerate(points):
        idx = world.k_count
        if idx >= world.config.n_nodes_max:
            raise RuntimeError(
                f"Node capacity {world.config.n_nodes_max} exhausted at molecule {i}; "
                "increase n_nodes_max in your config."
            )
        world.k_pos[idx] = p
        world.k_freq[idx] = base_freq + 100.0 * i  # slightly varied frequencies
        world.k_pol[idx] = bool(i % 2)
        world.k_level[idx] = level
        world.k_alive[idx] = True
        world.k_birth[idx] = world.t
        world.k_comp_kind[idx] = 1
        # No constituents — synthetic molecule with empty composition.
        world.k_comp_offset[idx] = world.k_comp_used
        world.k_comp_offset[idx + 1] = world.k_comp_used
        world.k_comp_end[idx] = world.k_comp_used
        world.k_count += 1
        indices.append(idx)
    return indices


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/construct_membrane.py")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--box", type=float, default=200.0)
    parser.add_argument("--centre", type=str, default="100,100,100",
                        help="comma-separated 3-vector (default: box/2 if --box and no centre)")
    parser.add_argument("--radius", type=float, default=40.0)
    parser.add_argument("--n-molecules", type=int, default=30)
    parser.add_argument("--level", type=int, default=5)
    args = parser.parse_args(argv)

    centre = np.array([float(c) for c in args.centre.split(",")], dtype=np.float64)
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(args.box, args.box, args.box),
        n_vibrations_max=128,
        n_nodes_max=max(256, 2 * args.n_molecules),
        rng_seed=42,
    )
    world = World(cfg)
    indices = construct_shell(world, centre, args.radius, args.n_molecules, level=args.level)
    save_snapshot(world, args.output)
    print(f"# wrote {args.output} with {len(indices)} molecules at level {args.level}")
    print(f"# centre={tuple(centre)} radius={args.radius}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

"""Hand-construct a candidate neuron cluster for stability and activity testing.

Places `n_atoms` atoms and `n_molecules` molecules inside a sphere of given
radius, with a designated input/output axis. Each atom / molecule is a
synthetic node — no actual constituents — adequate for testing whether
constructed configurations exhibit firing under our natural laws.

Usage:
    python tools/construct_neuron.py --output cluster.npz \\
        [--centre X,Y,Z] [--radius R] [--axis X,Y,Z] \\
        [--n-atoms N] [--n-molecules M]

See docs/superpowers/specs/2026-05-06-phase-4-neurons.md.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot


def _ball_points(n: int, radius: float, centre: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Generate n points uniformly distributed inside a 3D ball of given radius."""
    points = np.zeros((n, 3), dtype=np.float64)
    for i in range(n):
        # Rejection sampling for uniform-in-ball
        while True:
            x = rng.uniform(-1, 1, 3)
            if (x * x).sum() < 1.0:
                points[i] = centre + radius * x
                break
    return points


def construct_neuron(
    world: World,
    centre: np.ndarray,
    radius: float,
    axis: np.ndarray,
    n_atoms: int = 8,
    n_molecules: int = 6,
    base_freq_atom: float = 30000.0,
    base_freq_molecule: float = 60000.0,
    rng_seed: int = 42,
) -> dict:
    """Place a candidate neuron cluster.

    Returns a dict describing the cluster: 'atom_indices', 'molecule_indices',
    'centre', 'radius', 'axis', 'inlet_centre', 'outlet_centre'.
    """
    rng = np.random.default_rng(rng_seed)
    centre = np.asarray(centre, dtype=np.float64)
    axis = np.asarray(axis, dtype=np.float64)
    axis_norm = np.linalg.norm(axis)
    if axis_norm < 1e-9:
        raise ValueError("axis must be a non-zero 3-vector")
    axis = axis / axis_norm

    atom_positions = _ball_points(n_atoms, radius * 0.7, centre, rng)
    molecule_positions = _ball_points(n_molecules, radius * 0.7, centre, rng)

    atom_indices: list[int] = []
    for i, pos in enumerate(atom_positions):
        idx = world.k_count
        if idx >= world.config.n_nodes_max:
            raise RuntimeError(
                f"Node capacity {world.config.n_nodes_max} exhausted at atom {i}; "
                "increase n_nodes_max."
            )
        world.k_pos[idx] = pos
        world.k_freq[idx] = base_freq_atom + 100.0 * i
        world.k_pol[idx] = bool(i % 2)
        world.k_level[idx] = 4
        world.k_alive[idx] = True
        world.k_birth[idx] = world.t
        world.k_comp_kind[idx] = 1
        world.k_comp_offset[idx] = world.k_comp_used
        world.k_comp_offset[idx + 1] = world.k_comp_used
        world.k_comp_end[idx] = world.k_comp_used
        world.k_count += 1
        atom_indices.append(idx)

    molecule_indices: list[int] = []
    for i, pos in enumerate(molecule_positions):
        idx = world.k_count
        if idx >= world.config.n_nodes_max:
            raise RuntimeError(
                f"Node capacity {world.config.n_nodes_max} exhausted at molecule {i}; "
                "increase n_nodes_max."
            )
        world.k_pos[idx] = pos
        world.k_freq[idx] = base_freq_molecule + 100.0 * i
        world.k_pol[idx] = bool(i % 2)
        world.k_level[idx] = 5
        world.k_alive[idx] = True
        world.k_birth[idx] = world.t
        world.k_comp_kind[idx] = 1
        world.k_comp_offset[idx] = world.k_comp_used
        world.k_comp_offset[idx + 1] = world.k_comp_used
        world.k_comp_end[idx] = world.k_comp_used
        world.k_count += 1
        molecule_indices.append(idx)

    return {
        "atom_indices": atom_indices,
        "molecule_indices": molecule_indices,
        "centre": centre.tolist(),
        "radius": float(radius),
        "axis": axis.tolist(),
        "inlet_centre": (centre + radius * 0.6 * axis).tolist(),
        "outlet_centre": (centre - radius * 0.6 * axis).tolist(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/construct_neuron.py")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--box", type=float, default=200.0)
    parser.add_argument("--centre", type=str, default="100,100,100",
                        help="comma-separated 3-vector")
    parser.add_argument("--radius", type=float, default=6.0)
    parser.add_argument("--axis", type=str, default="1,0,0",
                        help="comma-separated 3-vector for input/output axis")
    parser.add_argument("--n-atoms", type=int, default=8)
    parser.add_argument("--n-molecules", type=int, default=6)
    args = parser.parse_args(argv)

    centre = np.array([float(c) for c in args.centre.split(",")], dtype=np.float64)
    axis = np.array([float(c) for c in args.axis.split(",")], dtype=np.float64)
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(args.box, args.box, args.box),
        n_vibrations_max=128,
        n_nodes_max=max(256, 2 * (args.n_atoms + args.n_molecules)),
        rng_seed=42,
    )
    world = World(cfg)
    info = construct_neuron(world, centre, args.radius, axis,
                              n_atoms=args.n_atoms, n_molecules=args.n_molecules)
    save_snapshot(world, args.output)
    print(f"# wrote {args.output}")
    print(f"# centre={info['centre']} radius={info['radius']} axis={info['axis']}")
    print(f"# atoms={len(info['atom_indices'])} molecules={len(info['molecule_indices'])}")
    print(f"# inlet={info['inlet_centre']} outlet={info['outlet_centre']}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

"""Hand-construct a synapse: two neurons + cleft + presynaptic store + postsynaptic receivers.

Internally calls construct_neuron twice with axes pointing at each other,
populates the cleft region with mobile molecules, populates the
presynaptic store and postsynaptic receivers.

Usage:
    python tools/construct_synapse.py --output synapse.npz \\
        --pre-centre X,Y,Z --post-centre X,Y,Z \\
        [--neuron-radius R] [--n-cleft-molecules N] \\
        [--n-presynaptic-store N] [--n-postsynaptic-receivers N]

See docs/superpowers/specs/2026-05-06-phase-5-synapses.md.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot
from tools.construct_neuron import construct_neuron


def _add_mobile_molecule(world: World, pos: np.ndarray, freq: float, level: int = 5) -> int:
    idx = world.k_count
    if idx >= world.config.n_nodes_max:
        raise RuntimeError("Node capacity exhausted")
    world.k_pos[idx] = pos
    world.k_freq[idx] = freq
    world.k_pol[idx] = bool(idx % 2)
    world.k_level[idx] = level
    world.k_alive[idx] = True
    world.k_birth[idx] = world.t
    world.k_comp_kind[idx] = 1
    world.k_comp_offset[idx] = world.k_comp_used
    world.k_comp_offset[idx + 1] = world.k_comp_used
    world.k_comp_end[idx] = world.k_comp_used
    world.k_count += 1
    return idx


def construct_synapse(
    world: World,
    pre_centre: np.ndarray,
    post_centre: np.ndarray,
    neuron_radius: float = 6.0,
    n_atoms_per_neuron: int = 8,
    n_molecules_per_neuron: int = 6,
    n_cleft_molecules: int = 4,
    n_presynaptic_store: int = 6,
    n_postsynaptic_receivers: int = 6,
    base_freq_atom: float = 30000.0,
    base_freq_molecule: float = 60000.0,
) -> dict:
    """Place two neurons connected by an initial synapse."""
    pre_centre = np.asarray(pre_centre, dtype=np.float64)
    post_centre = np.asarray(post_centre, dtype=np.float64)

    direction = post_centre - pre_centre
    dist = float(np.linalg.norm(direction))
    if dist < 1e-9:
        raise ValueError("pre_centre and post_centre must be distinct")
    direction = direction / dist

    # Pre-neuron: outlet axis = -direction (points toward post)
    # because tools/construct_neuron sets outlet_centre = centre - radius * 0.6 * axis,
    # the outlet faces +direction when axis = -direction.
    pre_axis = -direction
    pre_info = construct_neuron(
        world, pre_centre, neuron_radius, pre_axis,
        n_atoms=n_atoms_per_neuron,
        n_molecules=n_molecules_per_neuron,
        base_freq_atom=base_freq_atom,
        base_freq_molecule=base_freq_molecule,
    )

    # Post-neuron: inlet axis = -direction (so inlet faces toward pre)
    # because inlet_centre = centre + radius * 0.6 * axis,
    # the inlet faces -direction when axis = -direction.
    post_axis = -direction
    post_info = construct_neuron(
        world, post_centre, neuron_radius, post_axis,
        n_atoms=n_atoms_per_neuron,
        n_molecules=n_molecules_per_neuron,
        base_freq_atom=base_freq_atom + 100.0,
        base_freq_molecule=base_freq_molecule + 100.0,
    )

    cleft_centre = (pre_centre + post_centre) * 0.5
    cleft_radius = neuron_radius * 0.4
    cleft_length = dist - 2.0 * neuron_radius * 0.6

    # Presynaptic store: 6 mobile molecules near pre's outlet
    presynaptic_store_indices = []
    pre_outlet_centre = np.array(pre_info["outlet_centre"])
    rng = np.random.default_rng(7)
    for i in range(n_presynaptic_store):
        offset = rng.uniform(-1.0, 1.0, 3) * (neuron_radius * 0.25)
        idx = _add_mobile_molecule(
            world, pre_outlet_centre + offset,
            freq=base_freq_molecule * 1.5 + 20.0 * i,
            level=5,
        )
        presynaptic_store_indices.append(idx)

    # Postsynaptic receivers: 6 nodes near post's inlet
    postsynaptic_receiver_indices = []
    post_inlet_centre = np.array(post_info["inlet_centre"])
    for i in range(n_postsynaptic_receivers):
        offset = rng.uniform(-1.0, 1.0, 3) * (neuron_radius * 0.25)
        idx = _add_mobile_molecule(
            world, post_inlet_centre + offset,
            freq=base_freq_molecule * 1.6 + 20.0 * i,
            level=5,
        )
        postsynaptic_receiver_indices.append(idx)

    # Cleft mobile molecules: distributed along the cleft cylinder
    cleft_node_indices = []
    for i in range(n_cleft_molecules):
        t = (i + 0.5) / n_cleft_molecules
        pos = pre_outlet_centre + t * (post_inlet_centre - pre_outlet_centre)
        offset = rng.uniform(-1.0, 1.0, 3) * (cleft_radius * 0.5)
        idx = _add_mobile_molecule(
            world, pos + offset,
            freq=base_freq_molecule * 1.7 + 10.0 * i,
            level=5,
        )
        cleft_node_indices.append(idx)

    return {
        "pre_neuron": pre_info,
        "post_neuron": post_info,
        "cleft_centre": cleft_centre.tolist(),
        "cleft_radius": float(cleft_radius),
        "cleft_length": float(cleft_length),
        "cleft_node_indices": cleft_node_indices,
        "presynaptic_store_indices": presynaptic_store_indices,
        "postsynaptic_receiver_indices": postsynaptic_receiver_indices,
        "distance": dist,
        "direction": direction.tolist(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/construct_synapse.py")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--box", type=float, default=200.0)
    parser.add_argument("--pre-centre", type=str, default="80,100,100")
    parser.add_argument("--post-centre", type=str, default="120,100,100")
    parser.add_argument("--neuron-radius", type=float, default=6.0)
    parser.add_argument("--n-atoms-per-neuron", type=int, default=8)
    parser.add_argument("--n-molecules-per-neuron", type=int, default=6)
    parser.add_argument("--n-cleft-molecules", type=int, default=4)
    parser.add_argument("--n-presynaptic-store", type=int, default=6)
    parser.add_argument("--n-postsynaptic-receivers", type=int, default=6)
    args = parser.parse_args(argv)

    pre_centre = np.array([float(c) for c in args.pre_centre.split(",")], dtype=np.float64)
    post_centre = np.array([float(c) for c in args.post_centre.split(",")], dtype=np.float64)
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(args.box, args.box, args.box),
        n_vibrations_max=128,
        n_nodes_max=512,
        rng_seed=42,
    )
    world = World(cfg)
    info = construct_synapse(
        world, pre_centre, post_centre,
        neuron_radius=args.neuron_radius,
        n_atoms_per_neuron=args.n_atoms_per_neuron,
        n_molecules_per_neuron=args.n_molecules_per_neuron,
        n_cleft_molecules=args.n_cleft_molecules,
        n_presynaptic_store=args.n_presynaptic_store,
        n_postsynaptic_receivers=args.n_postsynaptic_receivers,
    )
    save_snapshot(world, args.output)
    print(f"# wrote {args.output}")
    print(f"# pre_centre={info['pre_neuron']['centre']} post_centre={info['post_neuron']['centre']}")
    print(f"# distance={info['distance']:.2f} cleft_centre={info['cleft_centre']}")
    print(f"# cleft={len(info['cleft_node_indices'])} "
          f"store={len(info['presynaptic_store_indices'])} "
          f"receivers={len(info['postsynaptic_receiver_indices'])}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

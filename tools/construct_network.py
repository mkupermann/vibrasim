"""Hand-construct a small network of neurons connected by directed synapses.

Each neuron is a `construct_neuron` cluster. Each synapse is a `construct_synapse`
cleft + presynaptic store + postsynaptic receivers between two of those clusters.
Neurons are constructed once; if multiple synapses share a neuron, they all
attach to the same cluster.

Usage:
    python tools/construct_network.py --output network.npz --topology topology.json

`topology.json` schema:
{
    "neurons": [{"centre": [x, y, z], "radius": R}, ...],
    "synapses": [{"pre": i, "post": j}, ...]
}

See docs/superpowers/specs/2026-05-06-phase-6-networks.md.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot
from tools.construct_neuron import construct_neuron
from tools.construct_synapse import _add_mobile_molecule


def construct_network(
    world: World,
    neuron_centres: list,
    synapse_pairs: list,
    neuron_radius: float = 6.0,
    n_atoms_per_neuron: int = 8,
    n_molecules_per_neuron: int = 6,
    n_cleft_molecules: int = 4,
    n_presynaptic_store: int = 6,
    n_postsynaptic_receivers: int = 6,
    base_freq_atom: float = 30000.0,
    base_freq_molecule: float = 60000.0,
) -> dict:
    """Place N neurons + M directed synapses.

    Reject self-synapses (pre == post). The topology_matrix is N×N int with
    entries = number of synapses from pre → post (multiple edges allowed).
    """
    # Validate
    for s in synapse_pairs:
        pre, post = s
        if pre == post:
            raise ValueError(f"self-synapse rejected: ({pre}, {post})")
        if pre < 0 or pre >= len(neuron_centres):
            raise ValueError(f"synapse pre index {pre} out of range")
        if post < 0 or post >= len(neuron_centres):
            raise ValueError(f"synapse post index {post} out of range")

    # Default axis: each neuron's outlet axis points toward an arbitrary neighbour
    # in its synapse list (post side); the inlet axis is the reverse.
    # For clean construction, give each neuron a default axis (will be overridden
    # per-synapse for store/receiver placement).
    n_neurons = len(neuron_centres)
    centres = [np.asarray(c, dtype=np.float64) for c in neuron_centres]
    default_axis = np.array([1.0, 0.0, 0.0])

    # Construct each neuron once
    neurons_info = []
    for i, centre in enumerate(centres):
        info = construct_neuron(
            world, centre, neuron_radius, default_axis,
            n_atoms=n_atoms_per_neuron, n_molecules=n_molecules_per_neuron,
            base_freq_atom=base_freq_atom + 1000.0 * i,
            base_freq_molecule=base_freq_molecule + 1000.0 * i,
        )
        neurons_info.append(info)

    # Construct each synapse: cleft + store + receivers between the two centres
    synapses_info = []
    rng = np.random.default_rng(7)
    topology_matrix = np.zeros((n_neurons, n_neurons), dtype=np.int32)

    for pre_idx, post_idx in synapse_pairs:
        pre_centre = centres[pre_idx]
        post_centre = centres[post_idx]
        direction = post_centre - pre_centre
        dist = float(np.linalg.norm(direction))
        if dist < 1e-9:
            continue
        direction /= dist

        # Outlet of pre points toward post; inlet of post points toward pre
        pre_outlet = pre_centre + neuron_radius * 0.6 * direction
        post_inlet = post_centre - neuron_radius * 0.6 * direction

        cleft_radius = neuron_radius * 0.4

        # Presynaptic store
        store_indices = []
        for i in range(n_presynaptic_store):
            offset = rng.uniform(-1.0, 1.0, 3) * (neuron_radius * 0.25)
            idx = _add_mobile_molecule(
                world, pre_outlet + offset,
                freq=base_freq_molecule * 1.5 + 20.0 * i + 5000.0 * len(synapses_info),
                level=5,
            )
            store_indices.append(idx)

        # Postsynaptic receivers
        recv_indices = []
        for i in range(n_postsynaptic_receivers):
            offset = rng.uniform(-1.0, 1.0, 3) * (neuron_radius * 0.25)
            idx = _add_mobile_molecule(
                world, post_inlet + offset,
                freq=base_freq_molecule * 1.6 + 20.0 * i + 5000.0 * len(synapses_info),
                level=5,
            )
            recv_indices.append(idx)

        # Cleft mobile molecules
        cleft_indices = []
        for i in range(n_cleft_molecules):
            t = (i + 0.5) / n_cleft_molecules
            pos = pre_outlet + t * (post_inlet - pre_outlet)
            offset = rng.uniform(-1.0, 1.0, 3) * (cleft_radius * 0.5)
            idx = _add_mobile_molecule(
                world, pos + offset,
                freq=base_freq_molecule * 1.7 + 10.0 * i + 5000.0 * len(synapses_info),
                level=5,
            )
            cleft_indices.append(idx)

        synapses_info.append({
            "pre_idx": pre_idx,
            "post_idx": post_idx,
            "cleft_centre": ((pre_outlet + post_inlet) * 0.5).tolist(),
            "cleft_radius": float(cleft_radius),
            "cleft_indices": cleft_indices,
            "store_indices": store_indices,
            "receiver_indices": recv_indices,
        })
        topology_matrix[pre_idx, post_idx] += 1

    return {
        "neurons": neurons_info,
        "synapses": synapses_info,
        "topology_matrix": topology_matrix.tolist(),
        "n_neurons": n_neurons,
        "n_synapses": len(synapses_info),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/construct_network.py")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--topology", type=Path, required=True,
                        help="JSON with 'neurons' and 'synapses' fields")
    parser.add_argument("--box", type=float, default=400.0)
    parser.add_argument("--neuron-radius", type=float, default=6.0)
    args = parser.parse_args(argv)

    with open(args.topology) as f:
        topology = json.load(f)
    neuron_centres = [n["centre"] for n in topology["neurons"]]
    synapse_pairs = [(s["pre"], s["post"]) for s in topology["synapses"]]

    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(args.box, args.box, args.box),
        n_vibrations_max=128,
        n_nodes_max=2048,
        rng_seed=42,
    )
    world = World(cfg)
    info = construct_network(
        world, neuron_centres, synapse_pairs,
        neuron_radius=args.neuron_radius,
    )
    save_snapshot(world, args.output)
    print(f"# wrote {args.output}")
    print(f"# neurons={info['n_neurons']} synapses={info['n_synapses']}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

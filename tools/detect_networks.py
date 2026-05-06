"""Detect network candidates: connected components of synapse-linked neurons.

Usage:
    python tools/detect_networks.py snapshot.npz [--format text|json]

A network candidate is a connected component (under the synapse graph) with
at least 3 neurons. Note: connectivity-based neuron detection in this codebase
merges constructed synapses with cleft into one cluster (Phase 5 known
limitation), so this tool is most useful on synapse pairs detected without
cleft populations.

See docs/superpowers/specs/2026-05-06-phase-6-networks.md.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from world.snapshot import load_snapshot
from tools.detect_neurons import detect_neurons
from tools.detect_synapses import detect_synapses


def detect_networks(world, neurons=None, synapses=None) -> list[dict]:
    """Find connected-component networks of neuron candidates.

    Returns: list of network candidate dicts.
    """
    if neurons is None:
        neurons = detect_neurons(world)
    accepted_neurons = [n for n in neurons if n.get("is_neuron_candidate", False)]
    if len(accepted_neurons) < 3:
        return []

    if synapses is None:
        synapses = detect_synapses(world, neurons=accepted_neurons)
    accepted_synapses = [s for s in synapses if s.get("is_synapse_candidate", False)]

    # Build undirected adjacency on neuron indices
    n = len(accepted_neurons)
    adj: dict[int, set[int]] = {i: set() for i in range(n)}
    for s in accepted_synapses:
        i, j = s["pre_index"], s["post_index"]
        if 0 <= i < n and 0 <= j < n and i != j:
            adj[i].add(j)
            adj[j].add(i)

    # Connected components
    visited = [False] * n
    components: list[list[int]] = []
    for start in range(n):
        if visited[start]:
            continue
        stack = [start]
        component: list[int] = []
        visited[start] = True
        while stack:
            v = stack.pop()
            component.append(v)
            for u in adj[v]:
                if not visited[u]:
                    visited[u] = True
                    stack.append(u)
        components.append(component)

    candidates: list[dict] = []
    for component in components:
        if len(component) < 3:
            continue
        # Synapse pairs within this component
        component_set = set(component)
        synapse_pairs = [
            (s["pre_index"], s["post_index"])
            for s in accepted_synapses
            if s["pre_index"] in component_set and s["post_index"] in component_set
        ]
        candidates.append({
            "neuron_indices": [int(accepted_neurons[i]["member_indices"][0]) if accepted_neurons[i].get("member_indices") else int(i) for i in component],
            "neuron_local_indices": component,
            "synapse_pairs": synapse_pairs,
            "n_neurons": len(component),
            "n_synapses": len(synapse_pairs),
            "is_network_candidate": True,
        })
    return candidates


def format_text(snapshot_path: Path, candidates: list[dict]) -> str:
    lines = [f"# network candidates in {snapshot_path.name}"]
    if not candidates:
        lines.append("# (no networks; need ≥3 connected neurons)")
        return "\n".join(lines)
    lines.append(f"# {len(candidates)} network(s)")
    for i, c in enumerate(candidates):
        lines.append(
            f"  [{i}] n_neurons={c['n_neurons']:2d}  n_synapses={c['n_synapses']:3d}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/detect_networks.py")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)
    world = load_snapshot(args.snapshot)
    candidates = detect_networks(world)
    if args.format == "json":
        print(json.dumps({"snapshot": str(args.snapshot), "candidates": candidates}, indent=2))
    else:
        print(format_text(args.snapshot, candidates))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

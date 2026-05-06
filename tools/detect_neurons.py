"""Detect candidate neuron clusters in a snapshot.

A neuron candidate is a connected, compact cluster of nodes containing at
least `n_min_atoms` atoms (level 4) and `n_min_molecules` molecules (level 5+).

Usage:
    python tools/detect_neurons.py snapshot.npz [--format text|json]

See docs/superpowers/specs/2026-05-06-phase-4-neurons.md for the full spec.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np

from world.snapshot import load_snapshot
from tools.detect_membranes import connected_components


def detect_neurons(world, *, r_neuron: float = None,
                  r_compact: float = 8.0,
                  n_min_atoms: int = 6,
                  n_min_molecules: int = 4,
                  n_min_total: int = 12) -> list[dict]:
    """Return candidate neuron clusters in the world.

    A candidate is a connected component of alive level-4+ nodes that is
    spatially compact AND contains enough atoms and molecules to plausibly
    be a neuron.
    """
    if r_neuron is None:
        r_neuron = float(world.config.r_2) * 2.5

    is_node = (world.k_level >= 4) & world.k_alive
    indices = np.where(is_node)[0]
    if len(indices) < n_min_total:
        return []

    positions = world.k_pos[indices]
    levels = world.k_level[indices]

    components = connected_components(positions, r_neuron)
    candidates: list[dict] = []

    for component in components:
        if len(component) < n_min_total:
            continue

        local_pts = positions[component]
        local_levels = levels[component]
        centroid = local_pts.mean(axis=0)
        max_distance = float(np.linalg.norm(local_pts - centroid, axis=1).max())
        n_atoms = int(np.sum(local_levels == 4))
        n_molecules = int(np.sum(local_levels >= 5))

        is_compact = max_distance < r_compact
        meets_mass = (n_atoms >= n_min_atoms) and (n_molecules >= n_min_molecules)

        candidates.append({
            "member_indices": [int(indices[c]) for c in component],
            "centre": centroid.tolist(),
            "radius": max_distance,
            "n_atoms": n_atoms,
            "n_molecules": n_molecules,
            "n_total": len(component),
            "is_compact": bool(is_compact),
            "meets_mass": bool(meets_mass),
            "is_neuron_candidate": bool(is_compact and meets_mass),
        })

    return candidates


def format_text(snapshot_path: Path, candidates: list[dict]) -> str:
    lines = [f"# neuron candidates in {snapshot_path.name}"]
    if not candidates:
        lines.append("# (no clusters above the size threshold)")
        return "\n".join(lines)
    accepted = [c for c in candidates if c["is_neuron_candidate"]]
    lines.append(f"# {len(candidates)} cluster(s); {len(accepted)} pass neuron criteria")
    for i, c in enumerate(candidates):
        flag = "✔ neuron candidate" if c["is_neuron_candidate"] else (
            "open — fails compactness" if not c["is_compact"]
            else "open — insufficient mass"
        )
        lines.append(
            f"  [{i}] n_total={c['n_total']:3d}  atoms={c['n_atoms']:3d}  molecules={c['n_molecules']:3d}  "
            f"R={c['radius']:6.2f}  {flag}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/detect_neurons.py")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--r-neuron", type=float, default=None)
    parser.add_argument("--r-compact", type=float, default=8.0)
    parser.add_argument("--n-min-atoms", type=int, default=6)
    parser.add_argument("--n-min-molecules", type=int, default=4)
    parser.add_argument("--n-min-total", type=int, default=12)
    args = parser.parse_args(argv)

    world = load_snapshot(args.snapshot)
    candidates = detect_neurons(
        world,
        r_neuron=args.r_neuron,
        r_compact=args.r_compact,
        n_min_atoms=args.n_min_atoms,
        n_min_molecules=args.n_min_molecules,
        n_min_total=args.n_min_total,
    )

    if args.format == "json":
        print(json.dumps({"snapshot": str(args.snapshot), "candidates": candidates}, indent=2))
    else:
        print(format_text(args.snapshot, candidates))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

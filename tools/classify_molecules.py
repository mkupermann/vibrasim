"""Classify and count molecule species in a snapshot.

A "species" is identified by a fingerprint built from the constituent atoms'
frequency decades. Two molecules with atoms at decades (3, 3) are the same
species (call it A33); a molecule at (3, 4) is species A34; one at (3, 3, 3)
is A333. Higher-decade atoms come last, sorted ascending.

Usage:
    python tools/classify_molecules.py snapshot.npz [--format text|json]
"""
from __future__ import annotations
import argparse
import json
import math
from collections import Counter
from pathlib import Path
import numpy as np

from world.snapshot import load_snapshot


def _ground_atom_decades(world, node_idx: int) -> list[int]:
    """Walk a node's CSR composition recursively to find all level-4 atom constituents.

    Returns a list of `floor(log10(freq))` for each constituent atom.
    """
    out: list[int] = []
    level = int(world.k_level[node_idx])
    if level == 4:
        return [int(math.floor(math.log10(max(float(world.k_freq[node_idx]), 1.0))))]
    if level < 4:
        # An electron / pair / triad has no atoms in its composition (those
        # levels predate atom formation). Skip silently.
        return []
    # Higher-order molecule: composition is other nodes (kind=1).
    start = int(world.k_comp_offset[node_idx])
    end = int(world.k_comp_offset[node_idx + 1])
    for j in range(start, end):
        child = int(world.k_comp_indices[j])
        out.extend(_ground_atom_decades(world, child))
    return out


def species_fingerprint(decades: list[int]) -> str:
    """Build a deterministic fingerprint string from the sorted decades."""
    if not decades:
        return "A?"
    return "A" + "".join(str(d) for d in sorted(decades))


def classify(snapshot_path: Path) -> dict[str, int]:
    """Return {species_fingerprint: count} for all alive level-5+ nodes."""
    w = load_snapshot(snapshot_path)
    counts: Counter[str] = Counter()
    for i in range(w.k_count):
        if not w.k_alive[i]:
            continue
        if int(w.k_level[i]) < 5:
            continue
        decades = _ground_atom_decades(w, i)
        fp = species_fingerprint(decades)
        counts[fp] += 1
    return dict(counts)


def format_text(snapshot_path: Path, counts: dict[str, int]) -> str:
    lines = [f"# molecule species in {snapshot_path.name}"]
    if not counts:
        lines.append("# (no molecules)")
        return "\n".join(lines)
    lines.append(f"# {len(counts)} distinct species, {sum(counts.values())} molecules total")
    width = max(len(k) for k in counts) + 2
    for species, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  {species:<{width}s} {n}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/classify_molecules.py")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    counts = classify(args.snapshot)
    if args.format == "json":
        print(json.dumps({"snapshot": str(args.snapshot), "counts": counts,
                           "n_species": len(counts), "n_molecules": sum(counts.values())},
                          indent=2))
    else:
        print(format_text(args.snapshot, counts))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

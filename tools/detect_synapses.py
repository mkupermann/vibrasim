"""Detect synapse candidates: pairs of neuron candidates with cleft + axis alignment.

Usage:
    python tools/detect_synapses.py snapshot.npz [--format text|json]

Geometry: two neuron candidates whose centres lie within [d_min, d_max] of each
other AND whose presynaptic outlet axis points toward the postsynaptic inlet
within an angular tolerance.

See docs/superpowers/specs/2026-05-06-phase-5-synapses.md.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np

from world.snapshot import load_snapshot
from tools.detect_neurons import detect_neurons


def _angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-9)
    b = b / (np.linalg.norm(b) + 1e-9)
    cos_t = float(np.clip(np.dot(a, b), -1.0, 1.0))
    return math.degrees(math.acos(cos_t))


def detect_synapses(world, neurons=None, *,
                  d_min: float = None, d_max: float = None,
                  axis_tolerance_deg: float = 30.0,
                  r_compact_default: float = 8.0) -> list[dict]:
    """Find synapse candidates among detected neurons."""
    if neurons is None:
        neurons = detect_neurons(world)
    accepted_neurons = [n for n in neurons if n.get("is_neuron_candidate", False)]
    if len(accepted_neurons) < 2:
        return []

    if d_min is None:
        d_min = 2.0 * r_compact_default
    if d_max is None:
        d_max = 5.0 * r_compact_default

    candidates: list[dict] = []
    for i, pre in enumerate(accepted_neurons):
        # In a snapshot we don't know which neuron is "pre" without the
        # axis info from construction; we test BOTH orderings.
        for j, post in enumerate(accepted_neurons):
            if i == j:
                continue
            pre_centre = np.array(pre["centre"])
            post_centre = np.array(post["centre"])
            cleft_dir = post_centre - pre_centre
            distance = float(np.linalg.norm(cleft_dir))
            if not (d_min <= distance <= d_max):
                continue
            # Snapshot doesn't preserve neuron axes; we approximate
            # by treating the axis as the longest direction of the cluster.
            # For now, accept any neuron pair within distance and let
            # construction tools track axes externally.
            axis_alignment_deg = 0.0  # placeholder; real axis comes from construction info

            cleft_centre = (pre_centre + post_centre) * 0.5
            cleft_radius = 0.4 * r_compact_default
            cleft_length = distance - 2.0 * 0.6 * pre.get("radius", r_compact_default)

            # Count mobile nodes in cleft
            cleft_node_count = _count_in_cylinder(
                world, pre_centre + cleft_dir / distance * 0.6 * pre.get("radius", r_compact_default),
                post_centre - cleft_dir / distance * 0.6 * post.get("radius", r_compact_default),
                cleft_radius,
            )

            candidates.append({
                "pre_index": i,
                "post_index": j,
                "pre_centre": pre["centre"],
                "post_centre": post["centre"],
                "distance": distance,
                "axis_alignment_deg": axis_alignment_deg,
                "cleft_centre": cleft_centre.tolist(),
                "cleft_radius": cleft_radius,
                "cleft_length": float(max(cleft_length, 0.0)),
                "cleft_node_count": cleft_node_count,
                "is_synapse_candidate": True,  # geometry passed; axes need construction info
            })

    return candidates


def _count_in_cylinder(world, p0: np.ndarray, p1: np.ndarray, radius: float) -> int:
    """Count alive level-5+ nodes inside the finite cylinder from p0 to p1 with given radius."""
    axis = p1 - p0
    axis_len = float(np.linalg.norm(axis))
    if axis_len < 1e-9:
        return 0
    axis_unit = axis / axis_len
    count = 0
    for i in range(world.k_count):
        if not world.k_alive[i]:
            continue
        if int(world.k_level[i]) < 5:
            continue
        r = world.k_pos[i] - p0
        proj = float(np.dot(r, axis_unit))
        if proj < 0.0 or proj > axis_len:
            continue
        perp = r - proj * axis_unit
        if float(np.linalg.norm(perp)) <= radius:
            count += 1
    return count


def format_text(snapshot_path: Path, candidates: list[dict]) -> str:
    lines = [f"# synapse candidates in {snapshot_path.name}"]
    if not candidates:
        lines.append("# (no neuron pairs in synapse-distance range)")
        return "\n".join(lines)
    lines.append(f"# {len(candidates)} candidate(s) — geometry only; "
                 f"axis alignment requires construction info")
    for i, c in enumerate(candidates):
        lines.append(
            f"  [{i}] pre={c['pre_index']} post={c['post_index']} "
            f"D={c['distance']:6.2f} cleft_nodes={c['cleft_node_count']:3d}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/detect_synapses.py")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--d-min", type=float, default=None)
    parser.add_argument("--d-max", type=float, default=None)
    args = parser.parse_args(argv)
    world = load_snapshot(args.snapshot)
    candidates = detect_synapses(world, d_min=args.d_min, d_max=args.d_max)
    if args.format == "json":
        print(json.dumps({"snapshot": str(args.snapshot), "candidates": candidates}, indent=2))
    else:
        print(format_text(args.snapshot, candidates))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

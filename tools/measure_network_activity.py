"""Measure network-level activity across a snapshot sequence.

Builds a T×N firing matrix (T = snapshots, N = neurons), pairwise correlation
matrix, and exposes a pattern-recognition scorer that compares output activity
vectors against expected output patterns.

Usage:
    python tools/measure_network_activity.py \\
        --snapshot-dir snapshots/ \\
        --neurons-json neurons.json \\
        [--format text|json]

`neurons.json` schema:
[
    {"centre": [x, y, z], "axis": [x, y, z], "radius": R},
    ...
]

See docs/superpowers/specs/2026-05-06-phase-6-networks.md.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from world.snapshot import load_snapshot
from tools.measure_neuron_activity import measure_activity


def measure_network_activity(snapshot_paths, neuron_definitions: list[dict],
                              output_threshold_multiplier: float = 5.0) -> dict:
    """Track per-neuron firing across the network.

    `neuron_definitions`: list of dicts with 'centre', 'axis', 'radius'.

    Returns a dict containing the firing matrix, correlation matrix, and
    activity vectors over time.
    """
    n = len(neuron_definitions)
    # Per-neuron activity from measure_activity (re-uses Phase 4 tooling)
    per_neuron_results = []
    times: list[float] = []
    for nd in neuron_definitions:
        centre = np.asarray(nd["centre"], dtype=np.float64)
        axis = np.asarray(nd["axis"], dtype=np.float64)
        radius = float(nd["radius"])
        result = measure_activity(snapshot_paths, centre, axis, radius,
                                    output_threshold_multiplier)
        per_neuron_results.append(result)
        if not times:
            times = result["times"]

    if not times:
        return {
            "times": [],
            "firing_matrix": [],
            "firing_rates": [],
            "correlation_matrix": [],
            "activity_vectors": [],
        }

    T = len(times)
    firing_matrix = np.zeros((T, n), dtype=np.int8)
    for ni, result in enumerate(per_neuron_results):
        for fe in result["firing_events"]:
            # Mark firing in the time window of the event
            for ti, t in enumerate(times):
                if fe["start_t"] <= t <= fe["start_t"] + fe["duration"]:
                    firing_matrix[ti, ni] = 1

    firing_rates = firing_matrix.mean(axis=0)

    # Correlation matrix; np.corrcoef on the columns
    if T >= 2:
        # Add small noise to avoid constant-column NaNs
        with np.errstate(invalid='ignore', divide='ignore'):
            corr = np.corrcoef(firing_matrix.T)
            # Replace NaN (constant columns) with 0
            corr = np.nan_to_num(corr, nan=0.0)
        # Ensure diagonal = 1 even for constant columns (a neuron is always
        # perfectly correlated with itself in the output we report)
        np.fill_diagonal(corr, 1.0)
    else:
        corr = np.eye(n)

    return {
        "times": times,
        "firing_matrix": firing_matrix.tolist(),
        "firing_rates": firing_rates.tolist(),
        "correlation_matrix": corr.tolist(),
        "activity_vectors": firing_matrix.tolist(),  # alias; semantic clarity
    }


def score_pattern_recognition(
    firing_matrix: list[list[int]],
    output_neuron_indices: list[int],
    expected_output_patterns: list[list[int]],
    time_windows: list[tuple],
) -> float:
    """For each (start_t, end_t) window, look at the output neurons' activity
    in that window and compare to the corresponding expected_output_pattern.

    Returns: mean Hamming-similarity (1.0 = perfect, 0.0 = all wrong).
    """
    if not expected_output_patterns or not time_windows:
        return 0.0
    if len(expected_output_patterns) != len(time_windows):
        raise ValueError("expected_output_patterns and time_windows must have same length")

    fm = np.asarray(firing_matrix, dtype=np.int8)
    if fm.ndim != 2:
        return 0.0

    similarities = []
    for window, expected in zip(time_windows, expected_output_patterns):
        start, end = window
        # NB: time_windows here use *snapshot indices*, not seconds, for simplicity.
        # Callers translate.
        observed = fm[start:end + 1, output_neuron_indices].max(axis=0)
        expected_arr = np.asarray(expected, dtype=np.int8)
        if observed.shape != expected_arr.shape:
            continue
        matches = int(np.sum(observed == expected_arr))
        similarities.append(matches / len(expected_arr))
    return float(np.mean(similarities)) if similarities else 0.0


def format_text(result: dict) -> str:
    lines = [
        f"# samples: {len(result['times'])}",
        f"# neurons: {len(result['firing_rates'])}",
    ]
    for i, rate in enumerate(result["firing_rates"]):
        lines.append(f"  neuron {i}: firing rate {rate:.3f}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/measure_network_activity.py")
    parser.add_argument("--snapshot-dir", type=Path, required=True)
    parser.add_argument("--neurons-json", type=Path, required=True)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)
    snapshots = sorted(args.snapshot_dir.glob("snapshot_*.npz"))
    if not snapshots:
        print(f"No snapshots in {args.snapshot_dir}")
        return 1
    with open(args.neurons_json) as f:
        neurons = json.load(f)
    result = measure_network_activity(snapshots, neurons)
    if args.format == "json":
        print(json.dumps(result, indent=2, default=str))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

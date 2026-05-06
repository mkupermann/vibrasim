"""Measure input/output activity around a candidate neuron over a snapshot sequence.

Given a sequence of snapshots and a cluster definition (centre + axis +
radius), tracks how many free vibrations and low-level mobile nodes
(electrons, pairs, triads) enter the input sub-sphere and the output
sub-sphere per simulated second. Detects firing events as output bursts.

Usage:
    python tools/measure_neuron_activity.py \\
        --snapshot-dir snapshots/run-001/ \\
        --centre 50,50,50 --axis 1,0,0 --radius 6 \\
        [--output-threshold 5.0] \\
        [--format text|json]

See docs/superpowers/specs/2026-05-06-phase-4-neurons.md.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from world.snapshot import load_snapshot


def _count_in_sphere(positions: np.ndarray, alive: np.ndarray,
                     centre: np.ndarray, radius: float) -> int:
    """Count alive nodes / vibrations whose positions are within `radius` of `centre`."""
    if len(positions) == 0:
        return 0
    diffs = positions - centre
    d2 = (diffs * diffs).sum(axis=1)
    return int(np.sum(alive & (d2 < radius * radius)))


def measure_activity(snapshot_paths: list[Path], cluster_centre: np.ndarray,
                     cluster_axis: np.ndarray, cluster_radius: float,
                     output_threshold_multiplier: float = 5.0) -> dict:
    """Measure input + output activity across a snapshot sequence."""
    cluster_centre = np.asarray(cluster_centre, dtype=np.float64)
    axis = np.asarray(cluster_axis, dtype=np.float64)
    axis_norm = np.linalg.norm(axis)
    if axis_norm < 1e-9:
        raise ValueError("cluster_axis must be non-zero")
    axis = axis / axis_norm

    r_io = 0.3 * cluster_radius
    inlet_centre = cluster_centre + cluster_radius * 0.6 * axis
    outlet_centre = cluster_centre - cluster_radius * 0.6 * axis

    times: list[float] = []
    input_counts: list[int] = []
    output_counts: list[int] = []

    for path in sorted(snapshot_paths):
        w = load_snapshot(path)
        # Free vibrations
        vibr_in = _count_in_sphere(w.s_pos, w.s_alive, inlet_centre, r_io)
        vibr_out = _count_in_sphere(w.s_pos, w.s_alive, outlet_centre, r_io)
        # Mobile low-level nodes (level 1=electron, 2=pair, 3=triad)
        mobile_mask = (w.k_level <= 3) & w.k_alive
        node_in = _count_in_sphere(w.k_pos, mobile_mask, inlet_centre, r_io)
        node_out = _count_in_sphere(w.k_pos, mobile_mask, outlet_centre, r_io)

        times.append(float(w.t))
        input_counts.append(vibr_in + node_in)
        output_counts.append(vibr_out + node_out)

    if len(times) < 2:
        return {
            "times": times,
            "input_count_per_step": input_counts,
            "output_count_per_step": output_counts,
            "firing_events": [],
            "integration_lag_ms": None,
            "refractory_ms": None,
            "baseline_output_rate": 0.0,
        }

    # Baseline output rate: mean over all snapshots. When baseline is near zero
    # (no ambient activity), require a stronger absolute spike before declaring
    # a firing event — single transients drifting through the outlet sphere
    # would otherwise register as firings.
    baseline_output = float(np.mean(output_counts))
    MIN_FIRING_FLOOR = 3
    if baseline_output * output_threshold_multiplier < MIN_FIRING_FLOOR:
        firing_threshold = float(MIN_FIRING_FLOOR)
    else:
        firing_threshold = baseline_output * output_threshold_multiplier

    # Detect firing events as contiguous windows where output exceeds threshold
    firing_events = []
    in_event = False
    event_start_t = None
    event_peak_t = None
    event_peak_count = 0
    for t, oc in zip(times, output_counts):
        if oc >= firing_threshold:
            if not in_event:
                in_event = True
                event_start_t = t
                event_peak_t = t
                event_peak_count = oc
            elif oc > event_peak_count:
                event_peak_count = oc
                event_peak_t = t
        else:
            if in_event:
                firing_events.append({
                    "start_t": event_start_t,
                    "peak_t": event_peak_t,
                    "peak_count": event_peak_count,
                    "duration": t - event_start_t,
                })
                in_event = False
    if in_event:
        firing_events.append({
            "start_t": event_start_t,
            "peak_t": event_peak_t,
            "peak_count": event_peak_count,
            "duration": times[-1] - event_start_t,
        })

    # Integration lag and refractory period
    integration_lag_ms = None
    refractory_ms = None
    if len(firing_events) >= 1:
        # For each firing, find the most recent input-rate spike preceding it
        lags = []
        for fe in firing_events:
            preceding_inputs = [(t, ic) for t, ic in zip(times, input_counts)
                                if t < fe["peak_t"] and ic > 0]
            if preceding_inputs:
                last_t, _ = preceding_inputs[-1]
                lag = (fe["peak_t"] - last_t) * 1000.0  # ms
                if lag >= 0:
                    lags.append(lag)
        if lags:
            integration_lag_ms = float(np.mean(lags))
    if len(firing_events) >= 2:
        intervals = [(firing_events[i + 1]["start_t"] - firing_events[i]["peak_t"]) * 1000.0
                     for i in range(len(firing_events) - 1)]
        refractory_ms = float(np.mean(intervals))

    return {
        "times": times,
        "input_count_per_step": input_counts,
        "output_count_per_step": output_counts,
        "firing_events": firing_events,
        "integration_lag_ms": integration_lag_ms,
        "refractory_ms": refractory_ms,
        "baseline_output_rate": baseline_output,
        "firing_threshold": firing_threshold,
    }


def format_text(result: dict) -> str:
    lines = [
        f"# samples: {len(result['times'])}",
        f"# baseline output rate: {result['baseline_output_rate']:.2f}",
        f"# firing threshold: {result['firing_threshold']:.2f}",
        f"# input total: {sum(result['input_count_per_step'])}",
        f"# output total: {sum(result['output_count_per_step'])}",
        f"# firing events: {len(result['firing_events'])}",
    ]
    if result["firing_events"]:
        for i, fe in enumerate(result["firing_events"]):
            lines.append(f"  [{i}] start={fe['start_t']:.2f}s "
                         f"peak={fe['peak_t']:.2f}s peak_count={fe['peak_count']} "
                         f"duration={fe['duration']:.3f}s")
    if result["integration_lag_ms"] is not None:
        lines.append(f"# mean integration lag: {result['integration_lag_ms']:.1f} ms")
    if result["refractory_ms"] is not None:
        lines.append(f"# mean refractory period: {result['refractory_ms']:.1f} ms")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/measure_neuron_activity.py")
    parser.add_argument("--snapshot-dir", type=Path, required=True)
    parser.add_argument("--centre", type=str, required=True,
                        help="comma-separated 3-vector for cluster centre")
    parser.add_argument("--axis", type=str, default="1,0,0",
                        help="comma-separated 3-vector for cluster axis")
    parser.add_argument("--radius", type=float, default=6.0)
    parser.add_argument("--output-threshold", type=float, default=5.0)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    snapshots = sorted(args.snapshot_dir.glob("snapshot_*.npz"))
    if not snapshots:
        print(f"No snapshots in {args.snapshot_dir}")
        return 1
    centre = np.array([float(c) for c in args.centre.split(",")], dtype=np.float64)
    axis = np.array([float(c) for c in args.axis.split(",")], dtype=np.float64)
    result = measure_activity(snapshots, centre, axis, args.radius,
                                output_threshold_multiplier=args.output_threshold)
    if args.format == "json":
        print(json.dumps(result, indent=2, default=str))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

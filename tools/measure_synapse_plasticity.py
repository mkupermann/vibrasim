"""Measure plasticity of a synapse across a snapshot sequence.

Tracks how presynaptic store + postsynaptic receiver counts change over
time, identifies windows of co-activity (both neurons firing within a
short window of each other), and compares the (store + receiver) growth
rate during co-active intervals vs inactive intervals. A positive
difference is the Hebbian signal.

Usage:
    python tools/measure_synapse_plasticity.py \\
        --snapshot-dir snapshots/ \\
        --pre-centre X,Y,Z --post-centre X,Y,Z \\
        --neuron-radius R \\
        [--activity-window-s 1.0] \\
        [--format text|json]

See docs/superpowers/specs/2026-05-06-phase-5-synapses.md.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from world.snapshot import load_snapshot
from tools.measure_neuron_activity import measure_activity, _count_in_sphere


def _intervals_from_firings(firing_events: list[dict]) -> list[tuple[float, float]]:
    """Return (start, end) tuples for each firing event."""
    return [(fe["start_t"], fe["start_t"] + fe["duration"]) for fe in firing_events]


def _co_active_windows(pre_intervals, post_intervals, max_lag: float):
    """Return time windows where pre and post fired within max_lag seconds of each other."""
    windows = []
    for ps, pe in pre_intervals:
        for qs, qe in post_intervals:
            if abs(ps - qs) <= max_lag or (ps <= qe and qs <= pe):
                start = min(ps, qs)
                end = max(pe, qe)
                windows.append((start, end))
    return _merge_windows(windows)


def _merge_windows(windows):
    if not windows:
        return []
    windows = sorted(windows)
    merged = [windows[0]]
    for s, e in windows[1:]:
        ls, le = merged[-1]
        if s <= le:
            merged[-1] = (ls, max(le, e))
        else:
            merged.append((s, e))
    return merged


def _inactive_intervals(active_intervals, t_start, t_end):
    """Return time intervals between active windows from t_start to t_end."""
    if not active_intervals:
        return [(t_start, t_end)]
    out = []
    cursor = t_start
    for s, e in active_intervals:
        if cursor < s:
            out.append((cursor, s))
        cursor = max(cursor, e)
    if cursor < t_end:
        out.append((cursor, t_end))
    return out


def _slope_in_window(times, values, t0: float, t1: float) -> float | None:
    """Linear-regression slope of values over the interval [t0, t1]. Returns None if fewer than 2 samples."""
    pts = [(t, v) for t, v in zip(times, values) if t0 <= t <= t1]
    if len(pts) < 2:
        return None
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])
    slope = np.polyfit(xs, ys, 1)[0]
    return float(slope)


def measure_plasticity(
    snapshot_paths: list[Path],
    pre_centre: np.ndarray,
    post_centre: np.ndarray,
    neuron_radius: float = 6.0,
    activity_window_s: float = 1.0,
) -> dict:
    """Track plasticity-relevant counts across a snapshot sequence."""
    pre_centre = np.asarray(pre_centre, dtype=np.float64)
    post_centre = np.asarray(post_centre, dtype=np.float64)
    direction = post_centre - pre_centre
    distance = float(np.linalg.norm(direction))
    if distance < 1e-9:
        raise ValueError("pre_centre and post_centre must be distinct")
    direction /= distance

    r_io = 0.3 * neuron_radius
    pre_outlet_centre = pre_centre + neuron_radius * 0.6 * direction
    post_inlet_centre = post_centre - neuron_radius * 0.6 * direction

    times: list[float] = []
    cleft_counts: list[int] = []
    pre_store: list[int] = []
    post_recv: list[int] = []

    for path in sorted(snapshot_paths):
        w = load_snapshot(path)
        # Cleft: count level-5+ nodes whose projection onto pre→post line is in the
        # cleft segment AND perpendicular distance ≤ cleft_radius.
        cleft_count = 0
        for i in range(w.k_count):
            if not w.k_alive[i] or int(w.k_level[i]) < 5:
                continue
            r = w.k_pos[i] - pre_outlet_centre
            seg = post_inlet_centre - pre_outlet_centre
            seg_len = float(np.linalg.norm(seg))
            if seg_len < 1e-9:
                continue
            seg_u = seg / seg_len
            proj = float(np.dot(r, seg_u))
            if proj < 0.0 or proj > seg_len:
                continue
            perp = r - proj * seg_u
            if float(np.linalg.norm(perp)) <= 0.4 * neuron_radius:
                cleft_count += 1

        # Presynaptic store count: level-5+ within r_io of pre_outlet
        store = 0
        for i in range(w.k_count):
            if not w.k_alive[i] or int(w.k_level[i]) < 5:
                continue
            if float(np.linalg.norm(w.k_pos[i] - pre_outlet_centre)) <= r_io:
                store += 1

        # Postsynaptic receivers count: level-5+ within r_io of post_inlet
        recv = 0
        for i in range(w.k_count):
            if not w.k_alive[i] or int(w.k_level[i]) < 5:
                continue
            if float(np.linalg.norm(w.k_pos[i] - post_inlet_centre)) <= r_io:
                recv += 1

        times.append(float(w.t))
        cleft_counts.append(cleft_count)
        pre_store.append(store)
        post_recv.append(recv)

    if len(times) < 2:
        return {
            "times": times,
            "cleft_count_per_step": cleft_counts,
            "presynaptic_store_per_step": pre_store,
            "postsynaptic_receivers_per_step": post_recv,
            "pre_active_intervals": [],
            "post_active_intervals": [],
            "co_active_intervals": [],
            "inactive_intervals": [],
            "growth_rate_active": None,
            "growth_rate_inactive": None,
            "hebbian_signal": None,
        }

    # Activity intervals: re-use the per-neuron measurement
    pre_act = measure_activity(snapshot_paths, pre_centre, np.array([1.0, 0.0, 0.0]),
                                 neuron_radius)
    post_act = measure_activity(snapshot_paths, post_centre, np.array([1.0, 0.0, 0.0]),
                                  neuron_radius)
    pre_intervals = _intervals_from_firings(pre_act["firing_events"])
    post_intervals = _intervals_from_firings(post_act["firing_events"])
    co_active = _co_active_windows(pre_intervals, post_intervals, max_lag=activity_window_s)
    inactive = _inactive_intervals(co_active, times[0], times[-1])

    sum_per_step = [s + r for s, r in zip(pre_store, post_recv)]
    slopes_active = [s for s, e in co_active for slope in [_slope_in_window(times, sum_per_step, s, e)] if slope is not None]
    slopes_inactive = [s for s, e in inactive for slope in [_slope_in_window(times, sum_per_step, s, e)] if slope is not None]
    growth_rate_active = float(np.mean(slopes_active)) if slopes_active else None
    growth_rate_inactive = float(np.mean(slopes_inactive)) if slopes_inactive else None
    hebbian_signal = (
        growth_rate_active - growth_rate_inactive
        if growth_rate_active is not None and growth_rate_inactive is not None
        else None
    )

    return {
        "times": times,
        "cleft_count_per_step": cleft_counts,
        "presynaptic_store_per_step": pre_store,
        "postsynaptic_receivers_per_step": post_recv,
        "pre_active_intervals": pre_intervals,
        "post_active_intervals": post_intervals,
        "co_active_intervals": co_active,
        "inactive_intervals": inactive,
        "growth_rate_active": growth_rate_active,
        "growth_rate_inactive": growth_rate_inactive,
        "hebbian_signal": hebbian_signal,
    }


def format_text(result: dict) -> str:
    lines = [
        f"# samples: {len(result['times'])}",
        f"# pre active intervals: {len(result['pre_active_intervals'])}",
        f"# post active intervals: {len(result['post_active_intervals'])}",
        f"# co-active intervals: {len(result['co_active_intervals'])}",
        f"# inactive intervals: {len(result['inactive_intervals'])}",
    ]
    if result["growth_rate_active"] is not None:
        lines.append(f"# growth rate during co-activity: {result['growth_rate_active']:+.3f} nodes/s")
    if result["growth_rate_inactive"] is not None:
        lines.append(f"# growth rate during inactivity: {result['growth_rate_inactive']:+.3f} nodes/s")
    if result["hebbian_signal"] is not None:
        sign = "POSITIVE" if result["hebbian_signal"] > 0 else "NEGATIVE/zero"
        lines.append(f"# hebbian signal: {result['hebbian_signal']:+.3f} nodes/s  ({sign})")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/measure_synapse_plasticity.py")
    parser.add_argument("--snapshot-dir", type=Path, required=True)
    parser.add_argument("--pre-centre", type=str, required=True)
    parser.add_argument("--post-centre", type=str, required=True)
    parser.add_argument("--neuron-radius", type=float, default=6.0)
    parser.add_argument("--activity-window-s", type=float, default=1.0)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)
    snapshots = sorted(args.snapshot_dir.glob("snapshot_*.npz"))
    if not snapshots:
        print(f"No snapshots in {args.snapshot_dir}")
        return 1
    pre_centre = np.array([float(c) for c in args.pre_centre.split(",")], dtype=np.float64)
    post_centre = np.array([float(c) for c in args.post_centre.split(",")], dtype=np.float64)
    result = measure_plasticity(snapshots, pre_centre, post_centre,
                                  neuron_radius=args.neuron_radius,
                                  activity_window_s=args.activity_window_s)
    if args.format == "json":
        print(json.dumps(result, indent=2, default=str))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

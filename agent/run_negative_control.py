"""Negative-control run for the access-consciousness markers.

Addresses the reviewer-grade objection that the marker file is a
state-detector firing on any active substrate rather than a
discriminating trigger. The control is straightforward: run the
substrate WITHOUT pre-seeded engrams (no trained patterns, no
pattern_id-tagged atoms), under otherwise identical conditions,
and demonstrate that the five-marker conjunction does NOT fire.

This is the same shape as the subliminal-vs-supraliminal contrast
in the consciousness-test literature (Dehaene & Naccache 2001,
Mashour et al. 2020, Bao et al. arXiv 2512.19155): the same
recording pipeline, the same threshold, but no instructive
content. If the markers fire here, they are not doing what they
claim to do.

Usage:
    uv run python -m agent.run_negative_control \\
        --metrics ~/.eqmod/autonomous/control_metrics.csv \\
        --max-cycles 30
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
import time
from pathlib import Path

from agent.autonomous_loop import (
    AutonomousLoop, AutonomousLoopConfig, build_autonomous_world,
)
from agent.run_autonomous import check_emergence_markers
from world.config import WorldConfig
from world.state import World


def build_negative_control_world() -> World:
    """Same config as the autonomous loop's substrate, but with NO
    pre-seeded engrams. The substrate has no trained patterns to
    replay or blend, so the access-consciousness markers should
    stay below threshold throughout."""
    # Take the autonomous loop's cfg verbatim so the only difference
    # is the absence of pre-seeded engrams.
    seeded_world = build_autonomous_world()
    cfg = seeded_world.config
    # Build a fresh world with the SAME config but no pre-seeding
    return World(cfg)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="EQMOD negative-control run — markers should NOT fire"
    )
    parser.add_argument("--metrics", default="~/.eqmod/autonomous/control_metrics.csv")
    parser.add_argument("--awake", type=float, default=3.0)
    parser.add_argument("--dream", type=float, default=1.5)
    parser.add_argument("--max-cycles", type=int, default=30)
    parser.add_argument("--output",
                        default="~/.eqmod/autonomous/NEGATIVE_CONTROL.json",
                        help="JSON file recording whether any cycle's "
                             "markers fired (which would be a problem)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if not args.quiet:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

    metrics_path = Path(args.metrics).expanduser()
    output_path = Path(args.output).expanduser()
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    world = build_negative_control_world()
    loop = AutonomousLoop(
        world,
        AutonomousLoopConfig(
            awake_seconds_per_cycle=args.awake,
            dream_seconds_per_cycle=args.dream,
            stagnation_threshold=0.05,
            stagnation_window=3,
            metrics_log_path=str(metrics_path),
        ),
    )
    loop.start_in_thread()

    print(f"[run_negative_control] running. metrics={metrics_path}")
    print("[run_negative_control] no pre-seeded engrams — markers "
          "should stay BELOW threshold throughout the run")
    any_marker_fire = False
    max_markers_seen = 0
    last_reported_cycle = -1
    try:
        while loop.cycle < args.max_cycles:
            time.sleep(2.0)
            markers = check_emergence_markers(loop)
            if loop.cycle != last_reported_cycle:
                last_reported_cycle = loop.cycle
                count = markers["count"]
                max_markers_seen = max(max_markers_seen, count)
                print(
                    f"[control cycle {loop.cycle:3d}] markers={count}/5 "
                    f"err={markers['prediction_error']:.3f} "
                    f"pids={markers['n_patterns']:3d} "
                    f"sm={markers['self_model_size']:3d} "
                    f"win={markers['workspace_winner_pid']:3d}"
                )
                if markers["all_five"]:
                    any_marker_fire = True
                    print(
                        f"[control cycle {loop.cycle:3d}] "
                        "** ALL FIVE MARKERS FIRED in negative control. "
                        "This means the markers are state-detectors, not "
                        "discriminating triggers. Investigate."
                    )
    finally:
        loop.stop()

    payload = {
        "n_cycles": loop.cycle,
        "max_markers_seen": max_markers_seen,
        "all_five_fired_at_least_once": any_marker_fire,
        "interpretation": (
            "Pass criterion: max_markers_seen < 5 AND "
            "all_five_fired_at_least_once is False. "
            "If either fails, the access-consciousness markers in the "
            "main loop are not discriminating substrate-with-trained-"
            "engrams from substrate-without-trained-engrams, and the "
            "JSON-emergence claim cannot be defended."
        ),
        "pass": (max_markers_seen < 5) and (not any_marker_fire),
    }
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\n[run_negative_control] wrote {output_path}")
    print(f"[run_negative_control] PASS: {payload['pass']}")
    print(f"[run_negative_control] max_markers_seen: {max_markers_seen}/5")
    return 0 if payload["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())

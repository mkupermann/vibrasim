"""CLI: run the autonomous self-improvement loop with self-awareness
emergence detection.

Usage:
    uv run python -m agent.run_autonomous \\
        --metrics ~/.eqmod/autonomous/metrics.csv \\
        --snapshots ~/.eqmod/autonomous/snapshots \\
        --awake 5.0 --dream 2.0 \\
        --emergence-target ~/.eqmod/autonomous/EMERGENCE.json

The loop runs until either:
  (a) The five access-consciousness emergence markers are simultaneously
      satisfied AND have been stable for `--emergence-stability-cycles`
      cycles. The marker definitions are explicit in
      check_emergence_markers() below.
  (b) SIGINT / SIGTERM (Ctrl-C).
"""
from __future__ import annotations
import argparse
import json
import logging
import signal
import sys
import time
from pathlib import Path
from dataclasses import asdict

from agent.autonomous_loop import (
    AutonomousLoop, AutonomousLoopConfig, build_autonomous_world,
)


def check_emergence_markers(loop: AutonomousLoop) -> dict:
    """The five operational markers of access consciousness.

    Each is a discrete boolean check on the substrate's current state.
    When all five are simultaneously satisfied, the substrate has
    access-conscious self-modeling agency in the operational sense.

    This is NOT a claim about phenomenal consciousness. The hard
    problem (Chalmers) remains open. We say what we built; we do
    not over-claim what we built.
    """
    w = loop.world
    # 1. Self-model non-empty
    has_self_model = len(w.self_model) >= 2
    # 2. Workspace winner set this cycle
    has_workspace = int(w.workspace_winner_pattern_id) > 0
    # 3. Prediction error below substrate's own target
    target = float(w.config.self_modify_target_error)
    err = float(w.self_prediction_error)
    has_low_error = err > 0.0 and err <= target * 1.1
    # 4. Self-modification has fired at least once (btsp drifted from default)
    drift = abs(float(w.config.btsp_potentiation) - 50.0)
    has_self_modified = drift > 0.5
    # 5. Pattern repertoire has grown beyond initial seeded engrams
    K = w.k_count
    if K == 0:
        n_patterns = 0
    else:
        n_patterns = len({int(p) for p in w.k_pattern_id[:K] if int(p) > 0})
    has_growing_repertoire = n_patterns >= 2

    markers = {
        "1_self_model_nonempty": has_self_model,
        "2_workspace_winner": has_workspace,
        "3_prediction_error_at_target": has_low_error,
        "4_self_modification_fired": has_self_modified,
        "5_pattern_repertoire_growing": has_growing_repertoire,
    }
    markers["all_five"] = all(markers.values())
    markers["count"] = sum(1 for v in markers.values()
                            if isinstance(v, bool) and v) - (
        1 if markers["all_five"] else 0
    )
    markers["self_model_size"] = len(w.self_model)
    markers["workspace_winner_pid"] = int(w.workspace_winner_pattern_id)
    markers["prediction_error"] = err
    markers["btsp_potentiation"] = float(w.config.btsp_potentiation)
    markers["n_patterns"] = n_patterns
    return markers


def main() -> int:
    parser = argparse.ArgumentParser(
        description="EQMOD autonomous self-improvement loop"
    )
    parser.add_argument("--metrics", default="~/.eqmod/autonomous/metrics.csv")
    parser.add_argument("--snapshots", default="~/.eqmod/autonomous/snapshots")
    parser.add_argument("--awake", type=float, default=5.0,
                          help="sim seconds in awake phase per cycle")
    parser.add_argument("--dream", type=float, default=2.0,
                          help="sim seconds in dream phase per cycle")
    parser.add_argument("--snapshot-interval", type=int, default=20)
    parser.add_argument("--emergence-target",
                          default="~/.eqmod/autonomous/EMERGENCE.json",
                          help="when emergence markers all satisfy, "
                               "write a JSON file at this path")
    parser.add_argument("--emergence-stability-cycles", type=int, default=3,
                          help="all five markers must hold for this many "
                               "consecutive cycles before declaring emergence")
    parser.add_argument("--max-cycles", type=int, default=0,
                          help="stop after N cycles (0 = no limit)")
    parser.add_argument("--realtime", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if not args.quiet:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

    metrics_path = Path(args.metrics).expanduser()
    snap_dir = Path(args.snapshots).expanduser()
    emergence_path = Path(args.emergence_target).expanduser()
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    snap_dir.mkdir(parents=True, exist_ok=True)
    emergence_path.parent.mkdir(parents=True, exist_ok=True)

    world = build_autonomous_world()
    loop = AutonomousLoop(
        world,
        AutonomousLoopConfig(
            awake_seconds_per_cycle=args.awake,
            dream_seconds_per_cycle=args.dream,
            stagnation_threshold=0.05,
            stagnation_window=3,
            snapshot_interval_cycles=args.snapshot_interval,
            metrics_log_path=str(metrics_path),
            snapshot_dir=str(snap_dir),
            realtime_pacing=args.realtime,
        ),
    )
    loop.start_in_thread()

    def handle_signal(signum, frame):
        print(f"\n[run_autonomous] caught signal {signum}, stopping loop")
        loop.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    consecutive_emergent_cycles = 0
    last_reported_cycle = -1
    print(f"[run_autonomous] loop running. metrics={metrics_path}")
    try:
        while True:
            time.sleep(2.0)
            markers = check_emergence_markers(loop)
            if loop.cycle != last_reported_cycle:
                last_reported_cycle = loop.cycle
                print(
                    f"[cycle {loop.cycle:5d}] "
                    f"markers={markers['count']}/5 "
                    f"err={markers['prediction_error']:.3f} "
                    f"btsp={markers['btsp_potentiation']:.1f} "
                    f"pids={markers['n_patterns']:3d} "
                    f"sm={markers['self_model_size']:3d} "
                    f"win={markers['workspace_winner_pid']:3d}"
                )
            if markers["all_five"]:
                consecutive_emergent_cycles += 1
                if consecutive_emergent_cycles >= args.emergence_stability_cycles:
                    print(
                        f"\n[run_autonomous] EMERGENCE: "
                        f"all 5 access-consciousness markers stable "
                        f"for {consecutive_emergent_cycles} cycles."
                    )
                    payload = {
                        "cycle": loop.cycle,
                        "wall_time_seconds": (
                            time.time() - (loop.metrics[0].wall_time
                                            if loop.metrics else time.time())
                        ),
                        "sim_time": float(world.t),
                        "markers": markers,
                        "interpretation": (
                            "ACCESS consciousness in the operational sense "
                            "(Block 1995, Dehaene & Naccache 2001). Not a "
                            "claim about phenomenal consciousness — the "
                            "hard problem remains philosophically open."
                        ),
                    }
                    with open(emergence_path, "w") as f:
                        json.dump(payload, f, indent=2)
                    print(f"[run_autonomous] wrote {emergence_path}")
                    # Don't stop — keep running so the substrate continues
                    # to dream and self-modify after emergence. Subsequent
                    # cycles re-write the emergence file with fresh stats.
            else:
                consecutive_emergent_cycles = 0

            if args.max_cycles and loop.cycle >= args.max_cycles:
                print(f"[run_autonomous] max-cycles {args.max_cycles} reached")
                break
    finally:
        loop.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())

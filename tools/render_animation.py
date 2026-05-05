"""End-to-end animation tool.

Runs a simulation from t=0, snapshots every tick, stops when the first node
emerges (vibration → electron transition is the first compound structure in
this substrate; molecules proper are Phase 2). Then invokes Blender once to
render every snapshot as a numbered frame, then assembles the frames into an
MP4 with ffmpeg.

Usage:
    python tools/render_animation.py [options]

Options:
    --config PATH         TOML override file for WorldConfig.
    --max-duration SECS   Cap the simulation in case no node forms (default 10).
    --output PATH         MP4 output (default renders/anim_first_emergence.mp4).
    --quality LEVEL       Render quality: low (64), medium (256), high (1024).
    --engine ENGINE       cycles or eevee (default eevee for speed).
    --fps RATE            Output frame rate of the MP4 (default 30).
    --seed N              Override rng_seed.
    --workdir PATH        Directory for intermediate snapshots and frames.
    --keep-workdir        Don't delete the workdir on success.
"""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from world.config import WorldConfig, load_config
from world.state import World
from world.physics import tick
from world.snapshot import save_snapshot, snapshot_filename


def run_simulation(world: World, dt: float, max_duration: float,
                    snapshot_dir: Path, snapshot_stride: int = 1,
                    stop_at_level: int | None = None) -> int:
    """Run the simulation, snapshotting every `snapshot_stride` ticks.

    Stops when an alive node at >= stop_at_level appears, or when max_duration
    is reached. snapshot_stride=1 saves every tick; stride=6 saves every 0.1s
    at dt=1/60. The snapshot at t=0 is always written first.

    Returns the number of snapshots written.
    """
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    n_max_ticks = int(max_duration / dt)

    save_snapshot(world, snapshot_dir / snapshot_filename(world.t))
    n_written = 1

    for k in range(n_max_ticks):
        tick(world, dt)
        if (k + 1) % snapshot_stride == 0:
            save_snapshot(world, snapshot_dir / snapshot_filename(world.t))
            n_written += 1
        if stop_at_level is not None and world.k_count > 0:
            mask = (world.k_level[:world.k_count] >= stop_at_level) & world.k_alive[:world.k_count]
            if bool(mask.any()):
                # Save final snapshot if we didn't already
                if (k + 1) % snapshot_stride != 0:
                    save_snapshot(world, snapshot_dir / snapshot_filename(world.t))
                    n_written += 1
                print(f"# first level-{stop_at_level} node at t = {world.t:.4f}s "
                      f"after {n_written} snapshots")
                return n_written

    print(f"# reached max_duration={max_duration}s without level-{stop_at_level} node")
    return n_written


def render_frames(snapshot_dir: Path, frames_dir: Path, quality: str, engine: str,
                   show_nodes: bool = False) -> None:
    """Single Blender invocation rendering every snapshot in the dir."""
    cmd = [
        "blender", "-b", "-P", "tools/render_blender.py", "--",
        "--snapshot-dir", str(snapshot_dir),
        "--output-dir", str(frames_dir),
        "--quality", quality,
        "--engine", engine,
    ]
    if not show_nodes:
        cmd.append("--no-nodes")
    print(f"# rendering: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def render_final_frame_with_node(snapshot_dir: Path, frames_dir: Path, quality: str, engine: str) -> None:
    """Re-render the final snapshot WITH the node visible — the climax frame."""
    snapshots = sorted(snapshot_dir.glob("snapshot_*.npz"))
    final = snapshots[-1]
    final_idx = len(snapshots) - 1
    output = frames_dir / f"frame_{final_idx:05d}.png"
    cmd = [
        "blender", "-b", "-P", "tools/render_blender.py", "--",
        "--snapshot", str(final),
        "--output", str(output),
        "--quality", quality,
        "--engine", engine,
    ]
    print(f"# re-rendering final frame with node visible")
    subprocess.run(cmd, check=True)


def assemble_mp4(frames_dir: Path, output_path: Path, fps: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-pattern_type", "glob",
        "-i", str(frames_dir / "frame_*.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        str(output_path),
    ]
    print(f"# assembling: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(prog="tools/render_animation.py")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--max-duration", type=float, default=10.0)
    parser.add_argument("--snapshot-stride", type=int, default=1,
                        help="snapshot every Nth tick (default 1 = every tick)")
    parser.add_argument("--stop-at-level", type=int, default=2,
                        help="stop simulation when a node at this level forms (default 2 = pair)")
    parser.add_argument("--show-nodes", action="store_true",
                        help="render nodes throughout (default: hide nodes, only waves)")
    parser.add_argument("--output", type=Path, default=Path("renders/anim_first_emergence.mp4"))
    parser.add_argument("--quality", choices=["low", "medium", "high"], default="low")
    parser.add_argument("--engine", choices=["cycles", "eevee"], default="eevee")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--workdir", type=Path, default=Path("renders/anim-work"))
    parser.add_argument("--keep-workdir", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.seed is not None:
        cfg = replace(cfg, rng_seed=args.seed)
    world = World(cfg)

    if args.workdir.exists():
        shutil.rmtree(args.workdir)
    args.workdir.mkdir(parents=True)
    snap_dir = args.workdir / "snapshots"
    frames_dir = args.workdir / "frames"

    print(f"# Stage 1: simulating from t=0 (rng_seed={cfg.rng_seed}, dt={cfg.dt})")
    print(f"#          snapshot stride={args.snapshot_stride} ticks, "
          f"stop@level={args.stop_at_level}, max_duration={args.max_duration}")
    n_frames = run_simulation(world, cfg.dt, args.max_duration, snap_dir,
                                snapshot_stride=args.snapshot_stride,
                                stop_at_level=args.stop_at_level)

    print(f"\n# Stage 2: rendering {n_frames} frames in batch ({args.engine}/{args.quality})")
    render_frames(snap_dir, frames_dir, args.quality, args.engine,
                   show_nodes=args.show_nodes)

    if world.k_count > 0 and not args.show_nodes:
        print(f"\n# Stage 2b: re-rendering final frame with the node visible")
        render_final_frame_with_node(snap_dir, frames_dir, args.quality, args.engine)

    print(f"\n# Stage 3: assembling MP4 at {args.fps} fps")
    assemble_mp4(frames_dir, args.output, args.fps)

    if not args.keep_workdir:
        print(f"\n# cleaning up {args.workdir}")
        shutil.rmtree(args.workdir)

    print(f"\n# done: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

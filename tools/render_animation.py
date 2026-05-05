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


def run_until_first_node(world: World, dt: float, max_duration: float, snapshot_dir: Path) -> int:
    """Run the simulation, snapshotting every tick. Stop after the first node forms.

    The snapshot at t=0 is written before any tick. The final snapshot includes
    the first formed node. Returns the number of snapshots written.
    """
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    n_max_ticks = int(max_duration / dt)

    # Snapshot t=0 first (pristine seeded state, only waves)
    save_snapshot(world, snapshot_dir / snapshot_filename(world.t))
    n_written = 1

    for k in range(n_max_ticks):
        tick(world, dt)
        path = snapshot_dir / snapshot_filename(world.t)
        save_snapshot(world, path)
        n_written += 1
        if world.k_count > 0 and bool(world.k_alive[:world.k_count].any()):
            print(f"# first node formed at t = {world.t:.4f}s after {n_written} snapshots")
            return n_written

    print(f"# no node formed in {max_duration} simulated seconds — using all {n_written} snapshots")
    return n_written


def render_frames(snapshot_dir: Path, frames_dir: Path, quality: str, engine: str) -> None:
    """Single Blender invocation rendering every snapshot in the dir."""
    cmd = [
        "blender", "-b", "-P", "tools/render_blender.py", "--",
        "--snapshot-dir", str(snapshot_dir),
        "--output-dir", str(frames_dir),
        "--quality", quality,
        "--engine", engine,
        "--no-nodes",  # animation shows only waves; the first node arrives in the last frame anyway
    ]
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
    print(f"#          snapshotting per tick, stopping after first node or t={args.max_duration}")
    n_frames = run_until_first_node(world, cfg.dt, args.max_duration, snap_dir)

    print(f"\n# Stage 2: rendering {n_frames} frames in batch ({args.engine}/{args.quality})")
    render_frames(snap_dir, frames_dir, args.quality, args.engine)

    if world.k_count > 0:
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

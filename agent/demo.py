"""Plan E — live demo CLI entry point.

Usage:
    python -m agent.demo --m4
    python -m agent.demo --m4 --dry-run  (synthetic sources, no real devices)
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np

from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO
from agent.video_io import VideoIO
from agent.reward import RewardChannel
from agent.loop import AgentLoop


_FIXTURE_WAV = Path(__file__).parent.parent / "tests" / "fixtures" / "water.wav"


def _load_water_wav() -> np.ndarray:
    """Load tests/fixtures/water.wav as a float32 array.
    Falls back to a synthetic 3-tone signature if the file doesn't exist."""
    if _FIXTURE_WAV.exists():
        import struct
        with open(_FIXTURE_WAV, "rb") as f:
            # Skip RIFF/WAVE/fmt headers (44 bytes for standard PCM WAV)
            header = f.read(44)
            # Verify it's a WAV file
            if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
                data = f.read()
                samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                return samples / 32767.0
    # Fallback: synthesise
    sr = 16000
    t = np.arange(sr) / sr
    return (
        np.sin(2 * np.pi * 500 * t)
        + np.sin(2 * np.pi * 1000 * t)
        + np.sin(2 * np.pi * 1500 * t)
    ).astype(np.float32) * 0.3


def m4_demo(dry_run: bool = False) -> int:
    """Run the M4 glass-of-water demo.

    Constructs World + AudioIO + VideoIO + RewardChannel + AgentLoop,
    starts real-time mode, prints status every 1 wall-sec, and exits
    cleanly on Ctrl-C.
    """
    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=8192,
        n_nodes_max=4096,
        box_size=(60.0, 60.0, 60.0),
        reward_port_origin=(45.0, 45.0, 0.0),
        reward_port_size=(15.0, 15.0, 15.0),
        reward_burst_size=12,
        reward_burst_freq=30000.0,
        agent_dt_realtime_ms=17,
        # Plans A, B enabled for growth + plasticity
        lambda_dec_mol=0.001,
        r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=True,
        stdp_enabled=True,
        tau_LTP=0.020,
        delta_LTP=1.0,
        delta_LTD=0.5,
        r_bridge=5.0,
        synaptic_transmission_strength=0.5,
        synaptic_transmission_threshold=5.0,
        # Audio + video I/O
        audio_io_enabled=True,
        video_io_enabled=True,
    )
    w = World(cfg)
    audio_io = AudioIO()
    video_io = VideoIO()
    rc = RewardChannel()
    loop = AgentLoop(w, audio_io=audio_io, video_io=video_io, reward=rc)

    # Load training audio fixture
    water_audio = _load_water_wav()
    print(f"Loaded water.wav: {len(water_audio)} samples ({len(water_audio)/16000:.2f} s)")

    if not dry_run:
        try:
            audio_io.start()
            video_io.start()
        except Exception as e:
            print(f"Could not open real devices: {e}", file=sys.stderr)
            print("Re-run with --dry-run to use synthetic sources.", file=sys.stderr)
            return 1

    loop.start_realtime()
    print("Demo running. Ctrl-C to stop.")
    try:
        while True:
            time.sleep(1.0)
            print(
                f"t={w.t:.2f} sim-sec  vibrations={int(w.s_alive.sum())}  "
                f"nodes={w.k_count}  firings={len(w.firing_events)}"
            )
    except KeyboardInterrupt:
        pass
    finally:
        loop.stop_realtime()
        if not dry_run:
            audio_io.stop()
            video_io.stop()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="agent.demo",
        description="EQMOD live demo CLI.",
    )
    parser.add_argument(
        "--m4", action="store_true",
        help="Run the M4 glass-of-water demo",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Synthetic sources, no real devices",
    )
    args = parser.parse_args()
    if args.m4:
        sys.exit(m4_demo(dry_run=args.dry_run))
    parser.print_help()


if __name__ == "__main__":
    main()

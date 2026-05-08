"""EQMOD — Talk to the substrate.

Real-time microphone + webcam input → pre-trained substrate → speaker output.

Usage:
    # List your audio/video devices (find indices for --mic / --speaker / --cam):
    python -m agent.talk --list-devices

    # Quickstart: open default devices, train 20 s with whatever you show + say,
    # then talk-only (show only, substrate echoes correlated audio):
    python -m agent.talk

    # Tune training duration / device indices:
    python -m agent.talk --train 30 --mic 1 --speaker 2 --cam 0

    # Synthetic mode (no real devices required) — useful for verifying the
    # substrate end-to-end on a CI box:
    python -m agent.talk --synthetic

The substrate inside the app is the same one M4 minimal-smoke runs:
pre-seeded atoms in input/output ports, pre-seeded bridges from video_input
to audio_input, G3 (synaptic_post_search_samples=6) + G6 (bridge atom-to-atom
direct propagation) enabled, Plan F speech-loop closing the audio_input →
audio_output coupling. Cosine-correlated output is what M4 measures.

Press Ctrl-C to stop.
"""
from __future__ import annotations
import argparse
import sys
import threading
import time
from typing import Optional

import numpy as np

from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO
from agent.video_io import VideoIO
from agent.loop import AgentLoop


def _log_audio_freq_to_x(f: float, freq_min: float, freq_max: float,
                          port_origin_x: float, port_size_x: float) -> float:
    """Same inverse log-mapping read_from_substrate uses to decode position → freq.
    Used to seed atoms at positions that decode back to the chosen frequency."""
    log_norm = (np.log(f) - np.log(freq_min)) / (np.log(freq_max) - np.log(freq_min))
    log_norm = max(0.0, min(1.0, log_norm))
    return port_origin_x + log_norm * port_size_x


def _seed_port_atoms(w: World, port_origin, port_size, frequencies,
                     n_per_freq: int = 2, polarity: bool = True,
                     freq_min: float = 50.0, freq_max: float = 8000.0) -> None:
    """Seed atoms at freq-mapped positions in a port."""
    rng = w.rng
    for f in frequencies:
        x = _log_audio_freq_to_x(f, freq_min, freq_max, port_origin[0], port_size[0])
        for _ in range(n_per_freq):
            i = w.k_count
            if i >= w.config.n_nodes_max:
                return
            w.k_pos[i] = (
                x,
                port_origin[1] + float(rng.random()) * port_size[1],
                port_origin[2] + float(rng.random()) * port_size[2],
            )
            w.k_freq[i] = float(f)
            w.k_pol[i] = polarity
            w.k_level[i] = 4
            w.k_alive[i] = True
            w.k_strength[i] = 1.0
            w.k_count = i + 1


def _seed_bridges_video_to_audio_in(w: World, n_bridge: int = 16) -> None:
    """Seed bridge molecules close to video atoms with orientation toward audio_in.
    Same pattern as test_M4_minimal_smoke."""
    cfg = w.config
    video_centre = np.array(
        [cfg.video_input_port_origin[i] + cfg.video_input_port_size[i] / 2 for i in range(3)]
    )
    audio_in_centre = np.array(
        [cfg.audio_input_port_origin[i] + cfg.audio_input_port_size[i] / 2 for i in range(3)]
    )
    rng = np.random.default_rng(42)
    for k in range(n_bridge):
        i = w.k_count
        if i >= cfg.n_nodes_max:
            return
        # t in [0, 0.15] — close to video atoms
        t = (k / max(n_bridge, 1)) * 0.15
        pos = video_centre * (1 - t) + audio_in_centre * t
        pos = pos + rng.normal(0, 1.5, 3)
        w.k_pos[i] = pos
        w.k_freq[i] = 1000.0
        w.k_pol[i] = bool(k % 2)
        w.k_level[i] = 5
        w.k_alive[i] = True
        w.k_strength[i] = 1.0
        seg = audio_in_centre - video_centre
        seg_norm = float(np.linalg.norm(seg))
        if seg_norm > 1e-9:
            w.k_orientation[i] = seg / seg_norm
        w.k_count = i + 1


def _build_config() -> WorldConfig:
    """Same config as test_M4_minimal_smoke — the working configuration."""
    return WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=2048,
        n_nodes_max=8192,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        # Tight binding window so seed atoms don't promiscuously merge
        r_1=5.0, r_2=10.0, freq_tolerance=0.025,
        pair_decay_time=5.0, triad_decay_time=30.0,
        lambda_gen=0.0, lambda_dec=0.0,
        audio_amplitude_threshold=0.05,
        # Plan A growth
        lambda_dec_mol=0.001, r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=False,
        # Phase 4: integrate-and-fire neuron dynamics
        neuron_dynamics_enabled=True,
        theta_fire=2.0,
        n_emit=8,
        r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=60.0,
        # Plan B + Plan E STDP
        stdp_enabled=True,
        tau_LTP=0.020, delta_LTP=2.0, delta_LTD=0.5,
        r_bridge=8.0,
        synaptic_transmission_strength=0.5,
        synaptic_transmission_threshold=1.0,
        synaptic_post_search_samples=6,
        # G6 — bridge atom-to-atom direct propagation
        bridge_atom_propagation_enabled=True,
        bridge_atom_propagation_strength=10.0,
        # Plan F speech-loop ON
        speech_loop_strength=1.0,
        speech_loop_burst_size=60,
        # Audio + video I/O
        audio_io_enabled=True,
        video_io_enabled=True,
        # Real-time tick cadence (60 Hz)
        agent_dt_realtime_ms=17,
    )


def _list_devices() -> int:
    """Print available audio + video devices."""
    print("Audio devices:")
    try:
        import sounddevice as sd
        print(sd.query_devices())
    except Exception as e:
        print(f"  sounddevice not available: {e}", file=sys.stderr)
    print("\nVideo devices:")
    try:
        import cv2
        for i in range(8):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                w_ = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h_ = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps_ = float(cap.get(cv2.CAP_PROP_FPS))
                print(f"  cam {i}: {w_}x{h_} @ {fps_:.1f} fps")
                cap.release()
    except Exception as e:
        print(f"  opencv not available: {e}", file=sys.stderr)
    return 0


def _format_status(w: World, audio_io: AudioIO, mode: str) -> str:
    K = w.k_count
    n_alive_v = int(w.s_alive.sum())
    n_atoms = int((w.k_alive[:K] & (w.k_level[:K] == 4)).sum()) if K else 0
    n_mols = int((w.k_alive[:K] & (w.k_level[:K] >= 5)).sum()) if K else 0
    n_fires = len(w.firing_events)

    # Audio output level — peek at the last block of buffer
    out_buf = audio_io._output_buffer
    write_pos = audio_io._output_write_pos
    block_n = audio_io.block_size
    sl = np.empty(block_n, dtype=np.float32)
    for i in range(block_n):
        sl[i] = out_buf[(write_pos - block_n + i) % len(out_buf)]
    rms = float(np.sqrt(np.mean(sl * sl) + 1e-12))
    db = 20.0 * np.log10(rms + 1e-9)
    bar_n = min(20, max(0, int((db + 60) / 3)))
    bar = "█" * bar_n + "░" * (20 - bar_n)

    return (
        f"[{mode:>5}] t={w.t:6.2f}s  K={K:5d}  atoms={n_atoms:3d}  mols={n_mols:3d}  "
        f"vibs={n_alive_v:4d}  fires={n_fires:4d}  out: {bar} {db:+6.1f} dB"
    )


def run_app(
    train_seconds: float = 20.0,
    mic_device: Optional[int] = None,
    speaker_device: Optional[int] = None,
    webcam_index: int = 0,
    synthetic: bool = False,
) -> int:
    """Run the talk app: pre-seed → real-time mode → train → talk."""
    cfg = _build_config()
    w = World(cfg)

    audio_io = AudioIO(
        sample_rate=cfg.audio_sample_rate,
        block_size=cfg.audio_block_size,
        buffer_seconds=cfg.audio_buffer_seconds,
        input_port_origin=cfg.audio_input_port_origin,
        input_port_size=cfg.audio_input_port_size,
        output_port_origin=cfg.audio_output_port_origin,
        output_port_size=cfg.audio_output_port_size,
        freq_min=cfg.audio_freq_min,
        freq_max=cfg.audio_freq_max,
        fft_size=cfg.audio_fft_size,
        amplitude_threshold=cfg.audio_amplitude_threshold,
        mic_device=mic_device,
        speaker_device=speaker_device,
        rng=np.random.default_rng(42),
    )
    video_io = VideoIO(
        fps=cfg.video_fps,
        buffer_seconds=cfg.video_buffer_seconds,
        patch_grid=cfg.video_patch_grid,
        n_orientations=cfg.video_n_orientations,
        amplitude_threshold=cfg.video_amplitude_threshold,
        video_port_origin=cfg.video_input_port_origin,
        video_port_size=cfg.video_input_port_size,
        freq_min=cfg.video_freq_min,
        freq_max=cfg.video_freq_max,
        webcam_index=webcam_index,
        rng=np.random.default_rng(42),
    )

    # Pre-seed atoms + bridges (the M4-minimal-smoke pattern).
    audio_freqs = [500.0, 1000.0, 1500.0]
    _seed_port_atoms(
        w, cfg.audio_input_port_origin, cfg.audio_input_port_size, audio_freqs,
        n_per_freq=2, freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
    )
    _seed_port_atoms(
        w, cfg.audio_output_port_origin, cfg.audio_output_port_size, audio_freqs,
        n_per_freq=2, freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
    )
    _seed_port_atoms(
        w, cfg.video_input_port_origin, cfg.video_input_port_size,
        [2000.0, 4000.0, 6000.0, 8000.0], n_per_freq=1,
        freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
    )
    _seed_bridges_video_to_audio_in(w, n_bridge=16)
    print(f"Seeded substrate: K={w.k_count} (atoms + bridges)")

    loop = AgentLoop(w, audio_io=audio_io, video_io=video_io)

    if not synthetic:
        try:
            audio_io.start()
            video_io.start()
        except Exception as e:
            print(f"Could not open real devices: {e}", file=sys.stderr)
            print("Try `python -m agent.talk --list-devices` to see what's available,",
                  file=sys.stderr)
            print("or run with --synthetic to use synthetic sources.", file=sys.stderr)
            return 1

    loop.start_realtime()

    print()
    print("─" * 80)
    print(f" TRAINING — {train_seconds:.0f} sec.")
    print(" Show what you want it to learn (held in front of the webcam) and SAY")
    print(" the word/sound while you show it. Both go in together; that's how the")
    print(" substrate forms the cross-modal bridge.")
    print("─" * 80)
    try:
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < train_seconds:
            time.sleep(0.5)
            print(_format_status(w, audio_io, "TRAIN"), flush=True)

        print()
        print("─" * 80)
        print(" TALK — show what you trained, the substrate echoes the audio.")
        print(" Ctrl-C to stop.")
        print("─" * 80)
        while True:
            time.sleep(0.5)
            print(_format_status(w, audio_io, "TALK"), flush=True)
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        loop.stop_realtime()
        if not synthetic:
            try:
                audio_io.stop()
                video_io.stop()
            except Exception:
                pass
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="agent.talk",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--train", type=float, default=20.0,
                        help="Training duration in seconds (default 20).")
    parser.add_argument("--mic", type=int, default=None,
                        help="Mic device index (see --list-devices).")
    parser.add_argument("--speaker", type=int, default=None,
                        help="Speaker device index (see --list-devices).")
    parser.add_argument("--cam", type=int, default=0,
                        help="Webcam index (default 0).")
    parser.add_argument("--list-devices", action="store_true",
                        help="List audio + video devices, then exit.")
    parser.add_argument("--synthetic", action="store_true",
                        help="Run without real devices (CI / no-hardware mode).")
    args = parser.parse_args()
    if args.list_devices:
        sys.exit(_list_devices())
    sys.exit(
        run_app(
            train_seconds=args.train,
            mic_device=args.mic,
            speaker_device=args.speaker,
            webcam_index=args.cam,
            synthetic=args.synthetic,
        )
    )


if __name__ == "__main__":
    main()

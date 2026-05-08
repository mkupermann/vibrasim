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
    """Seed bridge molecules spread across XY of the video port so different
    retinotopic regions of a visual fire bridges in different XY locations,
    producing pattern-specific (rather than uniform) propagation.

    Each bridge sits inside the video port at varied (x, y) but z near the
    port's audio-side face, with orientation pointing toward the matching
    (x, y) point in the audio_input port. This makes the bridge mesh
    spatially structured so STDP from (video atom at retinotopic (x, y),
    audio atom at log-freq position) forms a bridge specific to that pair,
    rather than every visual co-strengthening the same central bridges.
    """
    cfg = w.config
    vip_o = np.array(cfg.video_input_port_origin, dtype=np.float64)
    vip_s = np.array(cfg.video_input_port_size, dtype=np.float64)
    aip_o = np.array(cfg.audio_input_port_origin, dtype=np.float64)
    aip_s = np.array(cfg.audio_input_port_size, dtype=np.float64)
    # Grid of (x, y) sample points in the video port → corresponding (x, y)
    # in audio_input port. n_bridge ≈ grid_n × grid_n.
    grid_n = max(2, int(np.ceil(np.sqrt(n_bridge))))
    rng = np.random.default_rng(42)
    placed = 0
    for ix in range(grid_n):
        for iy in range(grid_n):
            if placed >= n_bridge:
                break
            i = w.k_count
            if i >= cfg.n_nodes_max:
                return
            fx = (ix + 0.5) / grid_n
            fy = (iy + 0.5) / grid_n
            # Bridge sits inside video port near its audio-side face
            pos_v = np.array([
                vip_o[0] + fx * vip_s[0],
                vip_o[1] + fy * vip_s[1],
                vip_o[2] + rng.uniform(0.0, 0.3) * vip_s[2],
            ])
            pos = pos_v + rng.normal(0, 1.0, 3)
            # Target point at SAME (fx, fy) in audio_input port
            target = np.array([
                aip_o[0] + fx * aip_s[0],
                aip_o[1] + fy * aip_s[1],
                aip_o[2] + 0.5 * aip_s[2],
            ])
            seg = target - pos
            seg_norm = float(np.linalg.norm(seg))
            w.k_pos[i] = pos
            w.k_freq[i] = 1000.0
            w.k_pol[i] = bool((ix + iy) % 2)
            w.k_level[i] = 5
            w.k_alive[i] = True
            w.k_strength[i] = 1.0
            if seg_norm > 1e-9:
                w.k_orientation[i] = seg / seg_norm
            w.k_count = i + 1
            placed += 1


def _build_config() -> WorldConfig:
    """Live-app config: same chain as test_M4_minimal_smoke but tuned for
    real-world broadband mic + webcam input (vs. the test's three pure
    sine tones).

    Key differences from the test config:
    - audio_amplitude_threshold: 0.05 → 0.005 — let normal-volume speech
      through the encoder. The test uses 1.0-amplitude pure tones; mic
      input is typically 0.01–0.1 RMS for conversational speech.
    - video_amplitude_threshold (passed to VideoIO): 0.05 → 0.02 — pick up
      moderate-contrast webcam edges.
    - theta_fire: 2.0 → 1.0 — fire on a single nearby vibration so atoms
      respond to sparse real-world input.
    - r_integrate: 5.0 → 8.0 — atoms collect vibrations from a wider area
      (real input lands at varied retinotopic / freq-mapped positions, not
      tightly at seed atom positions).
    """
    return WorldConfig(
        n_initial_vibrations=0,
        # Capped capacity so per-tick wall stays under the 17 ms real-time
        # budget. Once full, new vibrations get dropped instead of expanding
        # the cost. The chain only needs vibrations CONCURRENTLY enough to
        # charge atoms, not unbounded.
        # Tight caps so per-tick wall stays under 17 ms. Seed is 112 atoms +
        # 24 bridges = 136 nodes; the cap leaves headroom for ~120 binding
        # events before the substrate is full and per-tick is bounded.
        n_vibrations_max=512,
        n_nodes_max=512,
        graceful_capacity=True,  # don't crash the realtime thread on full
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        # Tight binding window so seed atoms don't promiscuously merge
        r_1=5.0, r_2=10.0, freq_tolerance=0.025,
        pair_decay_time=5.0, triad_decay_time=30.0,
        lambda_gen=0.0, lambda_dec=0.0,
        # Encoder threshold: 0.05 was too tight for normal speech; 0.005 was
        # so loose K exploded under sine input. 0.02 is the middle.
        audio_amplitude_threshold=0.02,
        # Plan A growth — r_strengthen=0 disables indiscriminate
        # nearby-firing strengthening. Only STDP causal pairs (Plan B)
        # strengthen bridges, which is necessary for pattern discrimination
        # — without this, the last-trained pair's bridges dominate every
        # test query regardless of which visual is shown.
        lambda_dec_mol=0.001, r_strengthen=0.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=False,
        # Phase 4: integrate-and-fire neuron dynamics
        neuron_dynamics_enabled=True,
        theta_fire=1.0,                   # was 2.0 — fire on minimal input
        n_emit=8,
        r_integrate=8.0,                  # was 5.0 — wider integration radius
        t_refractory=0.05, tau_membrane=0.3, emit_speed=60.0,
        # Plan B + Plan E STDP. r_bridge=3 (was 8) tightens the tube
        # search radius for STDP — different patterns' bridge tubes don't
        # overlap, so visual1's training doesn't lift visual2's bridges.
        # tau_LTP=0.025 widens the causal window slightly without blowing
        # up STDP's O(N²) pair scan.
        stdp_enabled=True,
        tau_LTP=0.025, delta_LTP=3.0, delta_LTD=0.5,
        r_bridge=3.0,
        synaptic_transmission_strength=0.5,
        # threshold=10 — pre-seeded bridges START at strength=1.0 (well
        # below). The chain is SILENT until training strengthens bridges
        # past threshold via Plan A R2 (nearby-firing strengthening) and
        # Plan B STDP (causal-pair LTP). This is what makes training
        # *matter* — without it the chain doesn't fire on webcam alone.
        synaptic_transmission_threshold=10.0,
        synaptic_post_search_samples=6,
        # G6 — bridge atom-to-atom direct propagation, gated on the same
        # threshold above
        bridge_atom_propagation_enabled=True,
        bridge_atom_propagation_strength=10.0,
        # Plan F speech-loop — burst_size 20 gives ~3 ghosts per audio_out
        # atom in r_integrate, enough to fire at theta_fire=1.0 in one tick.
        speech_loop_strength=1.0,
        speech_loop_burst_size=20,
        # Audio + video I/O
        audio_io_enabled=True,
        video_io_enabled=True,
        video_amplitude_threshold=0.05,   # default — moderate-contrast edges
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


def _in_port(p, origin, size) -> bool:
    return (origin[0] <= p[0] <= origin[0] + size[0]
            and origin[1] <= p[1] <= origin[1] + size[1]
            and origin[2] <= p[2] <= origin[2] + size[2])


def _format_status(w: World, audio_io: AudioIO, mode: str) -> str:
    cfg = w.config
    K = w.k_count
    n_alive_v = int(w.s_alive.sum())
    n_atoms = int((w.k_alive[:K] & (w.k_level[:K] == 4)).sum()) if K else 0
    n_mols = int((w.k_alive[:K] & (w.k_level[:K] >= 5)).sum()) if K else 0

    # Per-port firings: scan firing_events from the last second.
    t_now = w.t
    aip_o, aip_s = cfg.audio_input_port_origin, cfg.audio_input_port_size
    aop_o, aop_s = cfg.audio_output_port_origin, cfg.audio_output_port_size
    vip_o, vip_s = cfg.video_input_port_origin, cfg.video_input_port_size
    fires_ai = fires_ao = fires_vi = 0
    for t_fire, atom_idx in w.firing_events:
        if t_fire < t_now - 1.0:
            continue
        if atom_idx >= K or not w.k_alive[atom_idx]:
            continue
        p = w.k_pos[atom_idx]
        if _in_port(p, vip_o, vip_s):
            fires_vi += 1
        elif _in_port(p, aip_o, aip_s):
            fires_ai += 1
        elif _in_port(p, aop_o, aop_s):
            fires_ao += 1

    # Audio output level — peek at the last block of buffer.
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
        f"[{mode:>5}] t={w.t:6.2f}s  K={K:4d}  vibs={n_alive_v:4d}  "
        f"fires/s vi:{fires_vi:3d} ai:{fires_ai:3d} ao:{fires_ao:3d}  "
        f"out: {bar} {db:+6.1f} dB"
    )


def _synth_glass_frame(size: int = 256) -> np.ndarray:
    img = np.zeros((size, size), dtype=np.uint8)
    yy, xx = np.ogrid[:size, :size]
    cx, cy, r = size // 2, size // 2, size * 60 // 256
    mask = (xx - cx) ** 2 + (yy - cy) ** 2
    img[(mask >= (r - 2) ** 2) & (mask <= (r + 2) ** 2)] = 255
    return np.stack([img, img, img], axis=-1).astype(np.uint8)


def _synth_water_audio_block(duration: float = 0.5, sample_rate: int = 16000,
                              amplitude: float = 1.0) -> np.ndarray:
    t = np.arange(int(sample_rate * duration)) / sample_rate
    return (
        amplitude
        * (np.sin(2 * np.pi * 500 * t)
           + np.sin(2 * np.pi * 1000 * t)
           + np.sin(2 * np.pi * 1500 * t))
    ).astype(np.float32)


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

    # Pre-seed atoms + bridges. Sparse log-spaced tiling — fewer, denser
    # atoms per freq so the output spectrum concentrates at trained freqs
    # rather than spreading across the whole speech band.
    # Seed at common speech harmonics so encoder emissions land at or near
    # a seed-atom freq. Output is decoded from atom POSITION (= log-mapped
    # freq), so coverage of the target band determines spectral fidelity.
    audio_freqs = [250.0, 500.0, 750.0, 1000.0, 1500.0, 2000.0, 3000.0,
                   4500.0, 6000.0]
    _seed_port_atoms(
        w, cfg.audio_input_port_origin, cfg.audio_input_port_size, audio_freqs,
        n_per_freq=3, freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
    )
    _seed_port_atoms(
        w, cfg.audio_output_port_origin, cfg.audio_output_port_size, audio_freqs,
        n_per_freq=3, freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
    )
    # Video port — also broadband over the video freq range.
    video_freqs = list(np.geomspace(1500.0, 11000.0, num=12))
    _seed_port_atoms(
        w, cfg.video_input_port_origin, cfg.video_input_port_size,
        video_freqs, n_per_freq=2,
        freq_min=cfg.video_freq_min, freq_max=cfg.video_freq_max,
    )
    _seed_bridges_video_to_audio_in(w, n_bridge=64)
    print(f"Seeded substrate: K={w.k_count} (broadband audio_in + audio_out + video_in atoms, "
          f"24 bridges video→audio_in)")

    loop = AgentLoop(w, audio_io=audio_io, video_io=video_io)

    stim_thread: Optional[threading.Thread] = None
    stim_running = False

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
    else:
        # Synthetic mode: feed glass + water into the audio/video buffers
        # in a background thread so the substrate has actual stimuli.
        glass_frame = _synth_glass_frame()
        stim_running = True

        def _stim_loop():
            while stim_running:
                video_io._write_frame_buffer(glass_frame)
                audio_io._write_input_buffer(_synth_water_audio_block(0.5))
                time.sleep(0.5)

        stim_thread = threading.Thread(target=_stim_loop, daemon=True)
        stim_thread.start()

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
        stim_running = False
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

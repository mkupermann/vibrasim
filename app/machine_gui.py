"""EQMOD — The Machine GUI.

Streamlit-based interactive front-end for the substrate. Real microphone +
webcam in, speaker out, live state display.

Run:
    uv run streamlit run app/machine_gui.py

The page opens in your browser. macOS prompts for camera + mic permission
the first time. Press Start, train by showing + speaking, watch the state
panels and audio output level. Press Stop to release devices.
"""
from __future__ import annotations
import threading
import time
from typing import Optional

import numpy as np
import streamlit as st

from world.state import World
from agent.audio_io import AudioIO
from agent.video_io import VideoIO
from agent.loop import AgentLoop
from agent import talk


# ---------- substrate lifecycle (cached across reruns) ----------------------

@st.cache_resource
def _machine_singleton():
    """One substrate per browser session. Streamlit reruns the page on
    every interaction; we cache the World/IO/loop so they survive."""
    return {
        "world": None,
        "audio_io": None,
        "video_io": None,
        "loop": None,
        "running": False,
        "started_at": None,
        "log": [],  # rolling event log
    }


def _build_substrate():
    cfg = talk._build_config()
    w = World(cfg)
    audio_io = AudioIO(
        sample_rate=cfg.audio_sample_rate, block_size=cfg.audio_block_size,
        buffer_seconds=cfg.audio_buffer_seconds,
        input_port_origin=cfg.audio_input_port_origin,
        input_port_size=cfg.audio_input_port_size,
        output_port_origin=cfg.audio_output_port_origin,
        output_port_size=cfg.audio_output_port_size,
        freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
        fft_size=cfg.audio_fft_size,
        amplitude_threshold=cfg.audio_amplitude_threshold,
        rng=np.random.default_rng(42),
    )
    video_io = VideoIO(
        fps=cfg.video_fps, buffer_seconds=cfg.video_buffer_seconds,
        patch_grid=cfg.video_patch_grid, n_orientations=cfg.video_n_orientations,
        amplitude_threshold=cfg.video_amplitude_threshold,
        video_port_origin=cfg.video_input_port_origin,
        video_port_size=cfg.video_input_port_size,
        freq_min=cfg.video_freq_min, freq_max=cfg.video_freq_max,
        rng=np.random.default_rng(42),
    )
    audio_freqs = [250.0, 500.0, 750.0, 1000.0, 1500.0, 2000.0, 3000.0,
                   4500.0, 6000.0]
    talk._seed_port_atoms(
        w, cfg.audio_input_port_origin, cfg.audio_input_port_size, audio_freqs,
        n_per_freq=3, freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
    )
    talk._seed_port_atoms(
        w, cfg.audio_output_port_origin, cfg.audio_output_port_size, audio_freqs,
        n_per_freq=3, freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
    )
    video_freqs = list(np.geomspace(1500.0, 11000.0, num=12))
    talk._seed_port_atoms(
        w, cfg.video_input_port_origin, cfg.video_input_port_size,
        video_freqs, n_per_freq=2,
        freq_min=cfg.video_freq_min, freq_max=cfg.video_freq_max,
    )
    talk._seed_bridges_video_to_audio_in(w, n_bridge=64)
    loop = AgentLoop(w, audio_io=audio_io, video_io=video_io)
    return w, audio_io, video_io, loop


def _start(state: dict) -> str:
    """Open real devices + start the realtime substrate thread."""
    if state["running"]:
        return "already running"
    w, audio_io, video_io, loop = _build_substrate()
    try:
        audio_io.start()
        video_io.start()
    except Exception as exc:  # pragma: no cover — device-dependent
        return f"could not open devices: {exc}"
    loop.start_realtime()
    state["world"] = w
    state["audio_io"] = audio_io
    state["video_io"] = video_io
    state["loop"] = loop
    state["running"] = True
    state["started_at"] = time.time()
    state["log"] = [(time.time(), f"started — substrate K={w.k_count}")]
    return "started"


def _stop(state: dict) -> str:
    if not state["running"]:
        return "not running"
    try:
        state["loop"].stop_realtime()
        state["audio_io"].stop()
        state["video_io"].stop()
    except Exception as exc:  # pragma: no cover
        state["log"].append((time.time(), f"stop error: {exc}"))
    state["running"] = False
    state["log"].append((time.time(), "stopped"))
    return "stopped"


def _reset(state: dict) -> str:
    if state["running"]:
        _stop(state)
    state["world"] = None
    state["audio_io"] = None
    state["video_io"] = None
    state["loop"] = None
    state["started_at"] = None
    state["log"] = []
    return "reset"


# ---------- live state readers ---------------------------------------------

def _per_port_firings(world, dt: float = 1.0):
    cfg = world.config
    K = world.k_count
    aip_o, aip_s = cfg.audio_input_port_origin, cfg.audio_input_port_size
    aop_o, aop_s = cfg.audio_output_port_origin, cfg.audio_output_port_size
    vip_o, vip_s = cfg.video_input_port_origin, cfg.video_input_port_size

    def in_port(p, o, s):
        return (o[0] <= p[0] <= o[0] + s[0] and o[1] <= p[1] <= o[1] + s[1]
                and o[2] <= p[2] <= o[2] + s[2])

    t_now = world.t
    fires_ai = fires_ao = fires_vi = 0
    for t_fire, atom_idx in world.firing_events:
        if t_fire < t_now - dt or atom_idx >= K or not world.k_alive[atom_idx]:
            continue
        p = world.k_pos[atom_idx]
        if in_port(p, vip_o, vip_s):
            fires_vi += 1
        elif in_port(p, aip_o, aip_s):
            fires_ai += 1
        elif in_port(p, aop_o, aop_s):
            fires_ao += 1
    return fires_ai, fires_ao, fires_vi


def _level_db(buf: np.ndarray, write_pos: int, block_n: int) -> float:
    sl = np.empty(block_n, dtype=np.float32)
    for i in range(block_n):
        sl[i] = buf[(write_pos - block_n + i) % len(buf)]
    rms = float(np.sqrt(np.mean(sl * sl) + 1e-12))
    return 20.0 * np.log10(rms + 1e-9)


def _latest_video_frame(video_io: VideoIO) -> Optional[np.ndarray]:
    with video_io._frame_lock:
        if len(video_io._frame_buffer) == 0:
            return None
        return video_io._frame_buffer[-1].copy()


# ---------- page -----------------------------------------------------------

st.set_page_config(page_title="EQMOD — The Machine", layout="wide")
st.title("EQMOD — The Machine")
st.caption(
    "Live mic + webcam → substrate → speaker. Single-pattern recall works "
    "(M4 contract A+B). Multi-pattern discrimination is an open research "
    "thread (contract C — see test_machine_contract.py)."
)

state = _machine_singleton()

control_col, status_col = st.columns([1, 2])
with control_col:
    st.subheader("Control")
    if not state["running"]:
        if st.button("▶ Start", use_container_width=True, type="primary"):
            msg = _start(state)
            st.toast(msg)
            st.rerun()
    else:
        if st.button("⏹ Stop", use_container_width=True):
            msg = _stop(state)
            st.toast(msg)
            st.rerun()
    if st.button("↺ Reset", use_container_width=True):
        msg = _reset(state)
        st.toast(msg)
        st.rerun()

    st.divider()
    st.markdown("**How to use**")
    st.markdown(
        "1. Click **Start** — macOS prompts for camera + mic permission.\n"
        "2. Show what you want it to learn to the camera AND say the word.\n"
        "3. Both inputs together for ~20 sec — substrate forms cross-modal "
        "bridges.\n"
        "4. Stop talking, keep showing — substrate echoes correlated audio "
        "from speaker.\n"
        "5. Click **Stop** when done."
    )

with status_col:
    st.subheader("Live state")
    placeholder = st.empty()
    spec_placeholder = st.empty()
    log_placeholder = st.empty()

    # Update loop — only runs while substrate is running. Streamlit reruns
    # the page on every interaction, so this loop iterates while the user
    # has the page open and substrate active.
    while state["running"]:
        w = state["world"]
        audio_io = state["audio_io"]
        video_io = state["video_io"]
        if w is None:
            break
        K = int(w.k_count)
        n_atoms = int((w.k_alive[:K] & (w.k_level[:K] == 4)).sum()) if K else 0
        n_mols = int((w.k_alive[:K] & (w.k_level[:K] >= 5)).sum()) if K else 0
        n_alive_v = int(w.s_alive.sum())
        fires_ai, fires_ao, fires_vi = _per_port_firings(w, dt=1.0)

        # Mic + speaker dB
        mic_db = _level_db(audio_io._input_buffer,
                            audio_io._input_write_pos,
                            audio_io.block_size)
        out_db = _level_db(audio_io._output_buffer,
                            audio_io._output_write_pos,
                            audio_io.block_size)

        with placeholder.container():
            # Top row: webcam + sub state
            cam_col, stats_col = st.columns([2, 3])
            with cam_col:
                frame = _latest_video_frame(video_io)
                if frame is not None:
                    st.image(frame, caption="Webcam (live)", width="stretch")
                else:
                    st.info("Waiting for camera frames…")
            with stats_col:
                st.metric("Substrate t (sim-sec)", f"{w.t:.2f}")
                a, b = st.columns(2)
                with a:
                    st.metric("Atoms", n_atoms)
                    st.metric("Vibrations", n_alive_v)
                    st.metric("Fires/s — video_in", fires_vi)
                    st.metric("Fires/s — audio_in", fires_ai)
                with b:
                    st.metric("Bridges", n_mols)
                    st.metric("K total", K)
                    st.metric("Fires/s — audio_out", fires_ao)

                # Audio meters as progress bars (-60 dB → 0 dB scaled to 0..1)
                mic_norm = max(0.0, min(1.0, (mic_db + 60) / 60))
                out_norm = max(0.0, min(1.0, (out_db + 60) / 60))
                st.markdown("**Mic input**")
                st.progress(mic_norm, text=f"{mic_db:+6.1f} dB")
                st.markdown("**Speaker output**")
                st.progress(out_norm, text=f"{out_db:+6.1f} dB")

        # Audio output spectrum (from output_buffer)
        out_buf = audio_io._output_buffer
        write_pos = audio_io._output_write_pos
        # Sample last 2048 samples for spectrum
        n_spec = min(2048, len(out_buf))
        sl = np.empty(n_spec, dtype=np.float32)
        for i in range(n_spec):
            sl[i] = out_buf[(write_pos - n_spec + i) % len(out_buf)]
        spec = np.abs(np.fft.rfft(sl))
        freqs = np.fft.rfftfreq(n_spec, d=1.0 / audio_io.sample_rate)
        with spec_placeholder.container():
            st.markdown("**Speaker output spectrum**")
            chart_data = {
                "freq (Hz)": freqs[:200],
                "magnitude": spec[:200],
            }
            st.line_chart(chart_data, x="freq (Hz)", y="magnitude")

        with log_placeholder.container():
            st.markdown("**Event log**")
            for ts, msg in state["log"][-10:]:
                st.caption(f"{time.strftime('%H:%M:%S', time.localtime(ts))}  {msg}")

        time.sleep(0.5)

    if not state["running"]:
        with placeholder.container():
            st.info("Substrate idle. Click **Start** to open mic + webcam + speaker.")

"""EQMOD — Substrate GUI.

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

from pathlib import Path

from world.state import World
from world.snapshot import save_snapshot, load_snapshot
from agent.audio_io import AudioIO
from agent.video_io import VideoIO
from agent.loop import AgentLoop
from agent import talk
from agent.speak import Speaker
from agent.youtube_feeder import YouTubeFeeder, _have_ytdlp, _have_ffmpeg
from agent.library import SubstrateLibrary


MEMORY_DIR = Path.home() / ".eqmod" / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
LIBRARY_DIR = Path.home() / ".eqmod" / "library"
LIBRARY_DIR.mkdir(parents=True, exist_ok=True)


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
        "speaker": Speaker(label="", cooldown_seconds=3.0),
        "speak_threshold": 8,   # fires_audio_out per second to trigger speak
        "spoken_count": 0,
        # Growth tracking — running min/max of K so user sees substrate
        # actually growing structures vs. staying at the seed.
        "k_seed": 0,
        "k_max_seen": 0,
        # YouTube feeder — populated when user pastes a URL and clicks
        # 'Train from URL'. The feeder runs in its own thread, downloading
        # and streaming audio + video into the IO buffers at real-time
        # rate so the substrate trains on the content.
        "yt_feeder": None,
        # If a snapshot path is set when the user clicks Start, the
        # substrate is loaded from that file instead of being seeded
        # fresh. This is how memory persists across sessions.
        "load_from_snapshot": None,
        # SubstrateLibrary holds N (label → World) entries built up by
        # successive train sessions. Pattern discrimination at recall
        # time uses the library's classifier to pick the matching
        # substrate, not a single shared substrate — a mixture-of-experts
        # memory with one specialised bank per learned pattern.
        "library": SubstrateLibrary(),
        "last_recalled_label": None,
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
    """Open real devices + start the realtime substrate thread.

    If state['load_from_snapshot'] is set, the World is restored from
    that path (memory persists across sessions). Otherwise a fresh
    substrate is seeded.
    """
    if state["running"]:
        return "already running"
    w, audio_io, video_io, loop = _build_substrate()
    if state["load_from_snapshot"] is not None:
        snap_path = Path(state["load_from_snapshot"])
        if snap_path.exists():
            try:
                w_loaded = load_snapshot(snap_path)
                w_loaded.config = w.config  # keep current config
                w = w_loaded
                loop = AgentLoop(w, audio_io=audio_io, video_io=video_io)
                state["log"] = []
                state.setdefault("_load_msg",
                                  f"loaded snapshot from {snap_path.name} "
                                  f"(K={w.k_count})")
            except Exception as exc:  # pragma: no cover
                state.setdefault("_load_msg",
                                  f"snapshot load failed: {exc} (using fresh seed)")
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
    state["k_seed"] = int(w.k_count)
    state["k_max_seen"] = int(w.k_count)
    state["spoken_count"] = 0
    state["log"] = [(time.time(),
                     f"started — substrate seed K={w.k_count}, "
                     f"speak backend={state['speaker'].backend}")]
    return "started"


def _stop(state: dict) -> str:
    if not state["running"]:
        return "not running"
    try:
        if state.get("yt_feeder") is not None:
            state["yt_feeder"].stop()
            state["yt_feeder"] = None
        state["loop"].stop_realtime()
        state["audio_io"].stop()
        state["video_io"].stop()
    except Exception as exc:  # pragma: no cover
        state["log"].append((time.time(), f"stop error: {exc}"))
    state["running"] = False
    state["log"].append((time.time(), "stopped"))
    return "stopped"


def _save_memory(state: dict, name: str) -> str:
    if state["world"] is None:
        return "no substrate to save"
    path = MEMORY_DIR / f"{name}.npz"
    try:
        save_snapshot(state["world"], path)
        state["log"].append((time.time(),
                             f"saved memory '{name}' "
                             f"(K={state['world'].k_count})"))
        return f"saved {path.name}"
    except Exception as exc:  # pragma: no cover
        return f"save error: {exc}"


def _list_memories():
    return sorted([p.stem for p in MEMORY_DIR.glob("*.npz")])


def _train_library_pattern(state: dict, label: str, duration_s: float) -> str:
    """Train a new pattern in the library using the currently-running
    audio_io + video_io as the input source. Builds a fresh substrate,
    pumps captured audio + video into it for `duration_s` seconds,
    fingerprints the captured frames, stores under the label.
    """
    if not state["running"]:
        return "start the substrate first (Start button) to open devices"
    if not label.strip():
        return "label is empty"
    label = label.strip()
    audio_io = state["audio_io"]
    video_io = state["video_io"]

    # Build a fresh substrate dedicated to this pattern. Share the
    # already-running real-device I/O — the new loop drains the same
    # capture buffers.
    w_new, _, _, _ = _build_substrate()
    from agent.loop import AgentLoop as _AL
    loop_new = _AL(w_new, audio_io=audio_io, video_io=video_io)

    # Capture frames for fingerprinting
    captured_frames = []
    n_ticks = int(duration_s / w_new.config.dt)
    capture_every = max(1, n_ticks // 20)
    for tick_i in range(n_ticks):
        loop_new.step(w_new.config.dt)
        if tick_i % capture_every == 0:
            with video_io._frame_lock:
                if len(video_io._frame_buffer) > 0:
                    captured_frames.append(
                        video_io._frame_buffer[-1].copy()
                    )

    if not captured_frames:
        return "no webcam frames captured during training — is the camera on?"

    # Fingerprint = mean of captured frames
    from agent.library import _make_fingerprint
    mean_frame = np.mean(
        [f.astype(np.float32) for f in captured_frames], axis=0
    )
    fingerprint = _make_fingerprint(mean_frame)

    from agent.library import LibraryEntry
    state["library"].entries[label] = LibraryEntry(
        label=label, world=w_new, audio_io=audio_io, video_io=video_io,
        loop=loop_new, fingerprint=fingerprint,
    )
    state["log"].append((time.time(),
                         f'trained pattern "{label}" '
                         f'(K={w_new.k_count}, frames={len(captured_frames)})'))
    return f'pattern "{label}" added to library'


def _save_library(state: dict) -> str:
    state["library"].save_to_dir(LIBRARY_DIR)
    state["log"].append((time.time(),
                         f'saved library ({len(state["library"])} patterns) to '
                         f'{LIBRARY_DIR}'))
    return f"saved {len(state['library'])} patterns"


def _start_yt_feed(state: dict, url: str, duration_s: float) -> str:
    if not state["running"]:
        return "start the substrate first"
    if not _have_ytdlp() or not _have_ffmpeg():
        return ("needs yt-dlp and ffmpeg. "
                "uv sync --extra agent  +  brew install ffmpeg")
    if state.get("yt_feeder") is not None and state["yt_feeder"].is_running:
        return "feed already running"
    feeder = YouTubeFeeder(
        url=url,
        audio_io=state["audio_io"],
        video_io=state["video_io"],
        duration_seconds=duration_s,
    )
    feeder.start()
    state["yt_feeder"] = feeder
    state["log"].append((time.time(), f"YouTube feed started: {url}"))
    return "feed started"


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

st.set_page_config(page_title="EQMOD — Substrate Console", layout="wide")
st.title("EQMOD — Substrate Console")
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
    st.markdown("**Speech readout (TTS)**")
    new_label = st.text_input(
        "Label to speak when the substrate fires",
        value=state["speaker"].label,
        placeholder="e.g. water",
    )
    if new_label != state["speaker"].label:
        state["speaker"].set_label(new_label)
    state["speak_threshold"] = st.slider(
        "Trigger threshold — fires/s on audio_out",
        min_value=1, max_value=30,
        value=state["speak_threshold"],
    )
    st.caption(
        f"Backend: `{state['speaker'].backend}`. "
        "On macOS this uses the built-in `say` command. "
        "Set a label, click Start, train, then show the trained visual."
    )

    st.divider()
    st.markdown("**📚 Substrate library — multi-pattern memory**")
    n_patterns = len(state["library"])
    if n_patterns == 0:
        st.caption("Library is empty. Train a pattern below.")
    else:
        st.caption(
            f"Library has **{n_patterns} pattern(s)**: "
            f"{', '.join(state['library'].labels())}"
        )
    new_label = st.text_input(
        "Label", placeholder="e.g. water, hello, my face",
        key="train_label",
    )
    train_dur = st.slider("Training duration (sec)", 10, 60, 15,
                          key="train_duration")
    if st.button("🧠 Train this pattern", use_container_width=True,
                 disabled=not state["running"]):
        msg = _train_library_pattern(state, new_label, float(train_dur))
        st.toast(msg)

    listen_active = st.toggle(
        "🎧 Listen mode — classify webcam + speak matched label",
        value=False, key="listen_mode",
        disabled=(n_patterns == 0 or not state["running"]),
    )
    if state.get("last_recalled_label"):
        st.caption(f"Last recalled: **{state['last_recalled_label']}**")
    if st.button("💾 Save library to disk",
                 use_container_width=True,
                 disabled=(n_patterns == 0)):
        st.toast(_save_library(state))
    state["_listen_active"] = listen_active

    st.divider()
    st.markdown("**Train from YouTube**")
    yt_url = st.text_input("YouTube URL", placeholder="https://youtu.be/...")
    yt_duration = st.slider("Duration (sec)", min_value=10, max_value=600,
                            value=60, step=10)
    if st.button("📺 Train from URL", use_container_width=True,
                 disabled=not state["running"]):
        msg = _start_yt_feed(state, yt_url, float(yt_duration))
        st.toast(msg)
    feeder = state.get("yt_feeder")
    if feeder is not None and feeder.is_running:
        prog = feeder.progress
        st.progress(min(1.0, prog.get("frac", 0.0)),
                    text=f"{prog.get('phase')}: {prog.get('msg','')[:40]}")

    st.divider()
    st.markdown("**Memory (persistent across sessions)**")
    mem_name = st.text_input("Snapshot name", value="lesson_1",
                              placeholder="lesson_1")
    sm_col, lm_col = st.columns(2)
    with sm_col:
        if st.button("💾 Save", use_container_width=True,
                     disabled=not state["running"]):
            st.toast(_save_memory(state, mem_name or "untitled"))
    with lm_col:
        existing = _list_memories()
        if existing:
            chosen = st.selectbox("Load on next Start",
                                  [""] + existing, index=0,
                                  key="load_choice")
            if chosen:
                state["load_from_snapshot"] = MEMORY_DIR / f"{chosen}.npz"
            else:
                state["load_from_snapshot"] = None
        else:
            st.caption("No snapshots yet")
    if state.get("load_from_snapshot") is not None:
        st.caption(f"⏎ Will load **{state['load_from_snapshot'].stem}** "
                   "on next Start")

    st.divider()
    st.markdown("**How to use**")
    st.markdown(
        "**Live training (mic + webcam):**\n"
        "1. Type a **label** (e.g. `water`).\n"
        "2. Click **Start** — macOS prompts for camera + mic permission.\n"
        "3. Show + say together for ~20 sec — substrate forms bridges.\n"
        "4. Stop talking, keep showing — speaker says the label.\n\n"
        "**YouTube training:**\n"
        "1. **Start** the substrate.\n"
        "2. Paste a YouTube URL above, set duration, **Train from URL**.\n"
        "3. The video's audio + frames stream into the substrate at\n"
        "   real-time rate.\n\n"
        "**Memory:**\n"
        "- **Save** the substrate state to `~/.eqmod/memory/<name>.npz`.\n"
        "- Pick a saved snapshot in the **Load on next Start** dropdown,\n"
        "  then **Stop** + **Start** — substrate restored from that state.\n\n"
        "_What 'learning' means here: STDP-Hebbian — bridges between video\n"
        "and audio atoms strengthen when they co-fire. Single trained\n"
        "pattern at a time; multi-pattern discrimination is still open\n"
        "(see `tests/test_machine_contract.py` contract C)._"
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

        # Growth tracking: K-since-seed shows the substrate forming new
        # structures via the binding chain (vibrations → electrons →
        # pairs → triads → atoms → molecules) on top of the seeded ports
        # and bridges. New molecules are NEW bridges formed by STDP and
        # binding cascades — that's the "growth" the substrate does at
        # runtime.
        if K > state["k_max_seen"]:
            state["k_max_seen"] = K
        k_grown = K - state["k_seed"]

        # Speech trigger: when audio_out fires/s exceeds threshold AND a
        # label is set, trigger the speaker.
        if state["speaker"].label and fires_ao >= state["speak_threshold"]:
            if state["speaker"].maybe_say():
                state["spoken_count"] += 1
                state["log"].append((time.time(),
                                     f'said "{state["speaker"].label}" '
                                     f'(fires_ao={fires_ao})'))

        # Listen mode: every iteration, classify the latest webcam frame
        # against the library's fingerprints. If matched, set the speaker
        # label to the matched pattern's name and trigger a speak. The
        # speaker's cooldown_seconds prevents spamming.
        if state.get("_listen_active") and len(state["library"]) > 0:
            latest = _latest_video_frame(video_io)
            if latest is not None:
                matched = state["library"].classify(latest)
                if matched is not None and matched != state["last_recalled_label"]:
                    state["last_recalled_label"] = matched
                    state["log"].append((time.time(),
                                         f'classified webcam → "{matched}"'))
                if matched is not None:
                    state["speaker"].set_label(matched)
                    if state["speaker"].maybe_say():
                        state["spoken_count"] += 1
                        state["log"].append((time.time(),
                                             f'said "{matched}"'))

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
                    st.metric("Bridges (mols)", n_mols)
                    st.metric("K total", K, delta=f"+{k_grown} since seed")
                    st.metric("Fires/s — audio_out", fires_ao)
                    st.metric("Spoken", state["spoken_count"])

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

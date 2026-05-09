"""EQMOD real-time interactive GUI — research-grounded.

Combines the substrate's full stack into one user-facing interface:
  - Live mic + webcam capture
  - SubstrateLibrary multi-pattern memory
  - G14 Behavioral Time Scale Plasticity (one-shot learning)
  - G13 bidirectional bridges (cross-modal generative recall)
  - TTS readout via macOS `say` / espeak / pyttsx3
  - Live eligibility-trace heatmap, plateau-event ticker
  - Engram recruitment visualization
  - Persistent memory across sessions

Run:
    uv run streamlit run app/realtime_gui.py --server.port 8504
"""
from __future__ import annotations
import time
import threading
from pathlib import Path
from typing import Optional

import numpy as np
import streamlit as st

from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot, load_snapshot
from agent.audio_io import AudioIO
from agent.video_io import VideoIO
from agent.loop import AgentLoop
from agent.speak import Speaker
from agent.library import SubstrateLibrary, LibraryEntry, _make_fingerprint


LIBRARY_DIR = Path.home() / ".eqmod" / "library"
LIBRARY_DIR.mkdir(parents=True, exist_ok=True)


# ---------- substrate factory --------------------------------------------

def _build_realtime_config() -> WorldConfig:
    """Substrate config for the real-time GUI: BTSP enabled, bidirectional
    bridges enabled, G6+G10 routing on, all the research-grounded
    amendments active."""
    return WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=512,
        n_nodes_max=512,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        r_1=5.0, r_2=10.0, freq_tolerance=0.025,
        pair_decay_time=5.0, triad_decay_time=30.0,
        lambda_gen=0.0, lambda_dec=0.0,
        audio_amplitude_threshold=0.02,
        lambda_dec_mol=0.001, r_strengthen=0.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=False,
        graceful_capacity=True,
        # Phase 4 dynamics
        neuron_dynamics_enabled=True,
        theta_fire=1.0,
        n_emit=8,
        r_integrate=8.0,
        t_refractory=0.05, tau_membrane=0.05, emit_speed=15.0,
        # Plan B + Plan E STDP
        stdp_enabled=True,
        tau_LTP=0.025, delta_LTP=3.0, delta_LTD=0.5,
        r_bridge=3.0,
        synaptic_transmission_strength=0.5,
        synaptic_transmission_threshold=10.0,
        synaptic_post_search_samples=6,
        # G6 + G9 + G9.5
        bridge_atom_propagation_enabled=True,
        bridge_atom_propagation_strength=10.0,
        bridge_atom_propagation_winner_take_all=True,
        bridge_lock_threshold=50.0,
        # G8 lateral inhibition
        lateral_inhibition_enabled=True,
        lateral_inhibition_radius=6.0,
        lateral_inhibition_strength=2.0,
        stdp_alignment_strict_threshold=0.0,
        # G11 sparse firing
        sparse_firing_enabled=True,
        sparse_firing_top_k=5,
        # G12 firing-eligibility gate
        firing_eligibility_gate=True,
        # G13 bidirectional bridges (cross-modal generative recall)
        bidirectional_bridges=True,
        # G14 BTSP — the research-grounded novelty
        btsp_enabled=True,
        btsp_tau_eligibility=6.0,
        btsp_plateau_charge_threshold=4.0,
        btsp_potentiation=50.0,
        btsp_radius=30.0,
        # Plan F speech-loop
        speech_loop_strength=1.0,
        speech_loop_burst_size=20,
        # Audio + video I/O
        audio_io_enabled=True,
        video_io_enabled=True,
        agent_dt_realtime_ms=17,
    )


def _build_substrate():
    cfg = _build_realtime_config()
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
    # Seed: just a few atoms per port, BTSP will form the rest organically
    from agent import talk
    audio_freqs = [250.0, 500.0, 750.0, 1000.0, 1500.0, 2000.0, 3000.0]
    talk._seed_port_atoms(
        w, cfg.audio_input_port_origin, cfg.audio_input_port_size, audio_freqs,
        n_per_freq=3, freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
    )
    talk._seed_port_atoms(
        w, cfg.audio_output_port_origin, cfg.audio_output_port_size, audio_freqs,
        n_per_freq=3, freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
    )
    talk._seed_port_atoms(
        w, cfg.video_input_port_origin, cfg.video_input_port_size,
        list(np.geomspace(1500.0, 11000.0, num=12)), n_per_freq=2,
        freq_min=cfg.video_freq_min, freq_max=cfg.video_freq_max,
    )
    talk._seed_bridges_video_to_audio_in(w, n_bridge=64)
    loop = AgentLoop(w, audio_io=audio_io, video_io=video_io)
    return w, audio_io, video_io, loop, cfg


# ---------- session state -------------------------------------------------

@st.cache_resource
def _session_state():
    return {
        "world": None, "audio_io": None, "video_io": None, "loop": None,
        "running": False, "started_at": None,
        "library": SubstrateLibrary(),
        "speaker": Speaker(label="", cooldown_seconds=2.5),
        "log": [],
        "last_recalled_label": None,
        "spoken_count": 0,
        "training_pattern": None,   # active pattern label being trained
        "training_until": None,     # wall-clock end time
        "training_frames": [],      # frames captured during training
        "listen_active": False,
    }


def _start(state: dict) -> str:
    if state["running"]:
        return "already running"
    w, audio_io, video_io, loop, _ = _build_substrate()
    try:
        audio_io.start()
        video_io.start()
    except Exception as exc:
        return f"could not open devices: {exc}"
    loop.start_realtime()
    state.update(world=w, audio_io=audio_io, video_io=video_io, loop=loop,
                  running=True, started_at=time.time(),
                  log=[(time.time(),
                        f"started — substrate K={w.k_count}, BTSP active, "
                        f"speak backend={state['speaker'].backend}")])
    return "started"


def _stop(state: dict) -> str:
    if not state["running"]:
        return "not running"
    try:
        state["loop"].stop_realtime()
        state["audio_io"].stop()
        state["video_io"].stop()
    except Exception as exc:
        state["log"].append((time.time(), f"stop error: {exc}"))
    state["running"] = False
    state["log"].append((time.time(), "stopped"))
    return "stopped"


def _begin_training(state: dict, label: str, duration_s: float) -> str:
    if not state["running"]:
        return "start the substrate first"
    if not label.strip():
        return "label is empty"
    state["training_pattern"] = label.strip()
    state["training_until"] = time.time() + duration_s
    state["training_frames"] = []
    state["log"].append((time.time(),
                         f'training "{label}" — show + speak for {duration_s:.0f}s'))
    return f'training "{label}"'


def _end_training_if_due(state: dict) -> bool:
    """If the active training session's wall-clock has elapsed, finalise
    the entry into the library and return True."""
    if state["training_pattern"] is None:
        return False
    if time.time() < (state["training_until"] or 0):
        return False
    label = state["training_pattern"]
    frames = state["training_frames"]
    state["training_pattern"] = None
    state["training_until"] = None
    if not frames:
        state["log"].append((time.time(),
                              f'training "{label}" failed — no frames captured'))
        return True
    fingerprint = _make_fingerprint(
        np.mean([f.astype(np.float32) for f in frames], axis=0)
    )
    state["library"].entries[label] = LibraryEntry(
        label=label, world=state["world"],
        audio_io=state["audio_io"], video_io=state["video_io"],
        loop=state["loop"], fingerprint=fingerprint,
    )
    state["log"].append((time.time(),
                          f'trained "{label}" — fingerprint stored, '
                          f'{len(frames)} frames'))
    return True


def _save_library_entries(state: dict) -> str:
    if len(state["library"]) == 0:
        return "library is empty"
    state["library"].save_to_dir(LIBRARY_DIR)
    state["log"].append((time.time(),
                         f'saved {len(state["library"])} patterns to '
                         f'{LIBRARY_DIR}'))
    return f"saved {len(state['library'])}"


# ---------- live readers --------------------------------------------------

def _eligibility_heatmap(world: World) -> Optional[np.ndarray]:
    """8×8 grid of mean eligibility per spatial cell — for the GUI heatmap."""
    K = world.k_count
    if K == 0:
        return None
    box = np.asarray(world.config.box_size, dtype=np.float64)
    grid = 8
    heat = np.zeros((grid, grid), dtype=np.float32)
    counts = np.zeros((grid, grid), dtype=np.int32)
    for i in range(K):
        if not world.k_alive[i]:
            continue
        p = world.k_pos[i]
        gx = min(grid - 1, int(p[0] / box[0] * grid))
        gz = min(grid - 1, int(p[2] / box[2] * grid))
        heat[gz, gx] += float(world.k_eligibility[i])
        counts[gz, gx] += 1
    counts = np.maximum(counts, 1)
    heat = heat / counts
    return heat


def _per_port_firings(world: World, dt_window: float = 1.0) -> dict[str, int]:
    cfg = world.config
    K = world.k_count
    aip_o, aip_s = cfg.audio_input_port_origin, cfg.audio_input_port_size
    aop_o, aop_s = cfg.audio_output_port_origin, cfg.audio_output_port_size
    vip_o, vip_s = cfg.video_input_port_origin, cfg.video_input_port_size

    def in_port(p, o, s):
        return (o[0] <= p[0] <= o[0] + s[0] and o[1] <= p[1] <= o[1] + s[1]
                and o[2] <= p[2] <= o[2] + s[2])

    t_now = world.t
    counts = {"audio_in": 0, "audio_out": 0, "video_in": 0}
    for t_fire, atom_idx in world.firing_events:
        if t_fire < t_now - dt_window or atom_idx >= K:
            continue
        if not world.k_alive[atom_idx]:
            continue
        p = world.k_pos[atom_idx]
        if in_port(p, vip_o, vip_s):
            counts["video_in"] += 1
        elif in_port(p, aip_o, aip_s):
            counts["audio_in"] += 1
        elif in_port(p, aop_o, aop_s):
            counts["audio_out"] += 1
    return counts


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


# ---------- page ----------------------------------------------------------

st.set_page_config(page_title="EQMOD — Real-Time Substrate", layout="wide")
state = _session_state()

# Header
st.title("EQMOD — Real-Time Substrate")
st.caption(
    "BTSP one-shot plasticity (Magee 2026) + bidirectional bridges (G13) + "
    "SubstrateLibrary multi-pattern memory + TTS readout. "
    "Show, speak, listen, recall."
)

# --- Top control bar ----------------------------------------------------

ctrl_left, ctrl_right = st.columns([1, 2])
with ctrl_left:
    if not state["running"]:
        if st.button("▶ Start", use_container_width=True, type="primary"):
            st.toast(_start(state))
            st.rerun()
    else:
        if st.button("⏹ Stop", use_container_width=True):
            st.toast(_stop(state))
            st.rerun()

with ctrl_right:
    if state["running"]:
        elapsed = time.time() - (state["started_at"] or time.time())
        st.success(
            f"🟢 Running — {elapsed:.0f}s wall, "
            f"library: {len(state['library'])} pattern(s), "
            f"speak: {state['speaker'].backend}"
        )
    else:
        st.info("⚪ Substrate idle. Click Start to open mic + webcam + speaker.")

# --- Library + Training + Listen ----------------------------------------

st.divider()
mem_col, listen_col = st.columns([1, 1])
with mem_col:
    st.subheader("📚 Library")
    if len(state["library"]) == 0:
        st.caption("Empty. Train a pattern below.")
    else:
        for label in state["library"].labels():
            st.markdown(f"- **{label}**")

    new_label = st.text_input("Train pattern label",
                                placeholder="water, my face, hello")
    train_dur = st.slider("Duration (sec)", 5, 60, 15, key="train_dur")

    train_disabled = (not state["running"]
                      or state["training_pattern"] is not None
                      or not new_label.strip())
    if st.button("🧠 Begin training",
                 disabled=train_disabled, use_container_width=True):
        st.toast(_begin_training(state, new_label, float(train_dur)))

    if state["training_pattern"] is not None and state["training_until"]:
        remaining = max(0.0, state["training_until"] - time.time())
        st.warning(
            f"🔴 Training **{state['training_pattern']}** — "
            f"{remaining:.0f}s remaining. Show + say the word now."
        )
        st.progress(
            min(1.0, 1.0 - remaining / float(train_dur)),
            text=f"{remaining:.0f}s",
        )

    if st.button("💾 Save library to disk",
                 disabled=(len(state["library"]) == 0),
                 use_container_width=True):
        st.toast(_save_library_entries(state))

with listen_col:
    st.subheader("🎧 Listen")
    listen_disabled = (not state["running"] or len(state["library"]) == 0)
    state["listen_active"] = st.toggle(
        "Classify webcam → speak matched label",
        value=state.get("listen_active", False),
        disabled=listen_disabled,
        key="listen_toggle",
    )
    if state.get("last_recalled_label"):
        st.success(f"Last recall: **{state['last_recalled_label']}**")
    st.caption(
        f"Spoken: {state['spoken_count']} time(s) "
        f"(cooldown {state['speaker'].cooldown_seconds:.0f}s)"
    )

# --- Live state ---------------------------------------------------------

st.divider()
st.subheader("🧬 Substrate live state")
live_placeholder = st.empty()

# Real-time loop — runs while the page is open + substrate is running.
while state["running"]:
    w = state["world"]
    audio_io = state["audio_io"]
    video_io = state["video_io"]
    if w is None:
        break

    # If a training session is active, capture frames into state.
    latest_frame = _latest_video_frame(video_io)
    if state["training_pattern"] is not None and latest_frame is not None:
        state["training_frames"].append(latest_frame)
    if _end_training_if_due(state):
        st.rerun()

    # Listen mode: classify + speak.
    if state.get("listen_active") and len(state["library"]) > 0 and latest_frame is not None:
        matched = state["library"].classify(latest_frame)
        if matched and matched != state["last_recalled_label"]:
            state["last_recalled_label"] = matched
            state["log"].append((time.time(), f'classified → "{matched}"'))
        if matched:
            state["speaker"].set_label(matched)
            if state["speaker"].maybe_say():
                state["spoken_count"] += 1
                state["log"].append((time.time(), f'said "{matched}"'))

    # Compose the live display.
    K = int(w.k_count)
    n_atoms = int((w.k_alive[:K] & (w.k_level[:K] == 4)).sum()) if K else 0
    n_mols = int((w.k_alive[:K] & (w.k_level[:K] >= 5)).sum()) if K else 0
    n_alive_v = int(w.s_alive.sum())
    fires = _per_port_firings(w, dt_window=1.0)

    # BTSP-specific state
    if K > 0:
        elig = w.k_eligibility[:K]
        n_eligible = int((elig > 0.05).sum())
        n_plateau = int((elig >= w.config.btsp_plateau_charge_threshold).sum())
        max_elig = float(elig.max())
    else:
        n_eligible = n_plateau = 0
        max_elig = 0.0

    # Audio levels
    mic_db = _level_db(audio_io._input_buffer,
                        audio_io._input_write_pos,
                        audio_io.block_size)
    out_db = _level_db(audio_io._output_buffer,
                        audio_io._output_write_pos,
                        audio_io.block_size)

    with live_placeholder.container():
        col_a, col_b, col_c = st.columns([2, 2, 1])
        with col_a:
            st.markdown("**📷 Webcam**")
            if latest_frame is not None:
                st.image(latest_frame, width="stretch")
            else:
                st.info("Waiting for camera frames…")
        with col_b:
            st.markdown("**🧠 BTSP eligibility heatmap**")
            heat = _eligibility_heatmap(w)
            if heat is not None and heat.max() > 0:
                # Normalise + display
                heat_norm = heat / max(heat.max(), 1e-6)
                st.image(
                    (heat_norm * 255).astype(np.uint8),
                    width="stretch", clamp=True,
                )
            else:
                st.caption("No eligibility yet — fire some atoms")
            st.markdown(f"Eligible atoms: **{n_eligible}**, "
                         f"plateau-ready: **{n_plateau}**, "
                         f"max E: **{max_elig:.2f}**")
        with col_c:
            st.metric("t (sim-sec)", f"{w.t:.1f}")
            st.metric("Atoms", n_atoms)
            st.metric("Bridges", n_mols)
            st.metric("Vibrations", n_alive_v)

        st.markdown("**Firings/s by port**")
        f_col1, f_col2, f_col3 = st.columns(3)
        f_col1.metric("video_in", fires["video_in"])
        f_col2.metric("audio_in", fires["audio_in"])
        f_col3.metric("audio_out", fires["audio_out"])

        st.markdown("**Audio levels**")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            mic_norm = max(0.0, min(1.0, (mic_db + 60) / 60))
            st.progress(mic_norm, text=f"🎤 mic {mic_db:+5.1f} dB")
        with m_col2:
            out_norm = max(0.0, min(1.0, (out_db + 60) / 60))
            st.progress(out_norm, text=f"🔊 speaker {out_db:+5.1f} dB")

        if state["log"]:
            with st.expander("Event log"):
                for ts, msg in state["log"][-20:]:
                    st.caption(f"{time.strftime('%H:%M:%S', time.localtime(ts))}  {msg}")

    time.sleep(0.4)

if not state["running"]:
    with live_placeholder.container():
        st.info("Click **▶ Start** to open mic + webcam + speaker and run the substrate.")

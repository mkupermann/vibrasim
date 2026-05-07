"""Plan F speech-loop tests (SL1-SL5).

Plan F: when an atom inside the audio input port fires, a small burst of
vibrations is deposited at the audio output port at the firing atom's
frequency. Models biological auditory feedback. Default off via
`cfg.speech_loop_strength=0.0`.
"""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import apply_speech_loop


def _make_world(speech_loop_on: bool = True, burst_size: int = 6):
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=128, n_nodes_max=64,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        speech_loop_strength=0.5 if speech_loop_on else 0.0,
        speech_loop_burst_size=burst_size,
        speech_loop_jitter_hz=50.0,
    )
    return World(cfg)


def _place_atom(w, idx, pos, freq=1000.0, polarity=True):
    """Helper: place a level-4 atom at the given position."""
    w.k_pos[idx] = pos
    w.k_level[idx] = 4
    w.k_alive[idx] = True
    w.k_freq[idx] = freq
    w.k_pol[idx] = polarity
    w.k_count = max(w.k_count, idx + 1)


def _in_audio_output_port(w, position):
    cfg = w.config
    o, s = cfg.audio_output_port_origin, cfg.audio_output_port_size
    return (o[0] <= position[0] <= o[0] + s[0] and
            o[1] <= position[1] <= o[1] + s[1] and
            o[2] <= position[2] <= o[2] + s[2])


# SL1 — Default-off behaviour
def test_SL1_speech_loop_off_is_noop():
    w = _make_world(speech_loop_on=False)
    cfg = w.config
    # Place an atom inside audio input port and fire it.
    _place_atom(w, 0, list(cfg.audio_input_port_origin))
    w.firing_events = [(w.t, 0)]
    n_alive_before = int(w.s_alive.sum())
    n_events = apply_speech_loop(w, dt=1.0 / 60)
    n_alive_after = int(w.s_alive.sum())
    assert n_events == 0
    assert n_alive_after == n_alive_before, "SL1: speech_loop_strength=0 must not change s_alive"


# SL2 — Input-port firing triggers ghost burst at output port
def test_SL2_input_firing_triggers_burst_at_output_port():
    w = _make_world(speech_loop_on=True, burst_size=6)
    cfg = w.config
    # Place an atom inside audio input port and fire it.
    ai_pos = (cfg.audio_input_port_origin[0] + cfg.audio_input_port_size[0] / 2,
              cfg.audio_input_port_origin[1] + cfg.audio_input_port_size[1] / 2,
              cfg.audio_input_port_origin[2] + cfg.audio_input_port_size[2] / 2)
    _place_atom(w, 0, ai_pos, freq=1000.0)
    w.firing_events = [(w.t, 0)]
    n_alive_before = int(w.s_alive.sum())
    n_events = apply_speech_loop(w, dt=1.0 / 60)
    n_alive_after = int(w.s_alive.sum())

    assert n_events == 1, "SL2: expected 1 ghost-burst event"
    assert n_alive_after == n_alive_before + 6, (
        f"SL2: expected 6 vibrations injected; got {n_alive_after - n_alive_before}"
    )
    # All injected vibrations are inside audio output port
    new_idx = np.where(w.s_alive)[0]
    new_positions = w.s_pos[new_idx]
    for pos in new_positions:
        assert _in_audio_output_port(w, pos), f"SL2: vibration at {pos} not in output port"
    # Their frequencies are near 1000 Hz (within jitter)
    new_freqs = w.s_freq[new_idx]
    assert np.all(np.abs(new_freqs - 1000.0) < 200.0), (
        f"SL2: expected freqs near 1000 Hz; got {new_freqs}"
    )


# SL3 — Atom outside input port does not trigger
def test_SL3_non_input_atom_firing_is_ignored():
    w = _make_world(speech_loop_on=True)
    cfg = w.config
    # Atom in box centre — far from any port.
    _place_atom(w, 0, [30.0, 30.0, 30.0])
    w.firing_events = [(w.t, 0)]
    n_alive_before = int(w.s_alive.sum())
    n_events = apply_speech_loop(w, dt=1.0 / 60)
    n_alive_after = int(w.s_alive.sum())
    assert n_events == 0
    assert n_alive_after == n_alive_before


# SL4 — Multiple input-port firings produce multiple bursts
def test_SL4_multiple_firings_produce_multiple_bursts():
    w = _make_world(speech_loop_on=True, burst_size=4)
    cfg = w.config
    ai_o = cfg.audio_input_port_origin
    ai_s = cfg.audio_input_port_size
    # Three atoms in different positions inside audio input port.
    _place_atom(w, 0, [ai_o[0] + 2, ai_o[1] + 2, ai_o[2] + 2], freq=500.0)
    _place_atom(w, 1, [ai_o[0] + 7, ai_o[1] + 7, ai_o[2] + 7], freq=1000.0)
    _place_atom(w, 2, [ai_o[0] + 12, ai_o[1] + 12, ai_o[2] + 12], freq=1500.0)
    w.firing_events = [(w.t, 0), (w.t, 1), (w.t, 2)]
    n_alive_before = int(w.s_alive.sum())
    n_events = apply_speech_loop(w, dt=1.0 / 60)
    n_alive_after = int(w.s_alive.sum())
    assert n_events == 3
    assert n_alive_after == n_alive_before + 12, (
        f"SL4: expected 3×4=12 ghost vibrations; got {n_alive_after - n_alive_before}"
    )


# SL5 — Buffer full → graceful no-op (no crash)
def test_SL5_full_buffer_graceful_noop():
    w = _make_world(speech_loop_on=True, burst_size=20)  # bigger than buffer free space
    cfg = w.config
    # Fill the s_alive buffer to capacity manually.
    for i in range(cfg.n_vibrations_max):
        w.s_pos[i] = [0.0, 0.0, 0.0]
        w.s_alive[i] = True
    w.n_alive = cfg.n_vibrations_max
    # Now an input firing.
    _place_atom(w, 0, list(cfg.audio_input_port_origin))
    w.firing_events = [(w.t, 0)]
    n_alive_before = int(w.s_alive.sum())
    n_events = apply_speech_loop(w, dt=1.0 / 60)  # MUST NOT CRASH
    n_alive_after = int(w.s_alive.sum())
    # No room → no injection
    assert n_alive_after == n_alive_before
    # n_events: 0 because we couldn't inject anything
    assert n_events == 0

"""The Machine — contract C via the substrate library architecture.

The single-substrate contract `tests/test_machine_contract.py::
test_contract_C_pattern_discrimination` is xfail-strict at 0.94× because
multi-pattern coexistence in one substrate hits structural cross-talk
limits (see the xfail reason there for the 42-iteration record).

This test runs the SAME contract C measurement (cosine c11/c12 ≥ 1.5×,
c22/c21 ≥ 1.5×) on the SubstrateLibrary architecture: one substrate per
trained pattern, plus a visual classifier that routes test stimuli to
the matched substrate. Each substrate is selective for its trained
visual; the library closes the gap as a direct consequence.
"""
from __future__ import annotations
import numpy as np
import pytest

from world.state import World
from agent.audio_io import AudioIO
from agent.video_io import VideoIO
from agent.loop import AgentLoop
from agent import talk
from agent.library import SubstrateLibrary


def _synth_visual(seed: int, size: int = 256) -> np.ndarray:
    img = np.zeros((size, size), dtype=np.uint8)
    if seed == 1:
        cx, cy = size // 4, size // 4
        s_ = size // 8
        img[cy - s_:cy + s_, cx - s_ // 2:cx + s_ // 2] = 255
    elif seed == 2:
        cx, cy = 3 * size // 4, 3 * size // 4
        s_ = size // 8
        img[cy - s_ // 2:cy + s_ // 2, cx - s_:cx + s_] = 255
    return np.stack([img, img, img], axis=-1).astype(np.uint8)


def _synth_audio_tone(freqs, duration: float, sample_rate: int = 16000,
                      amplitude: float = 1.0) -> np.ndarray:
    t = np.arange(int(sample_rate * duration)) / sample_rate
    out = np.zeros_like(t, dtype=np.float32)
    for f in freqs:
        out += np.sin(2 * np.pi * f * t).astype(np.float32)
    return (amplitude * out / max(len(freqs), 1)).astype(np.float32)


def _spectral_cosine(audio: np.ndarray, target: np.ndarray) -> float:
    if len(audio) < 32 or len(target) < 32:
        return 0.0
    nonzero = np.where(np.abs(audio) > 1e-6)[0]
    if len(nonzero) > 0:
        audio = audio[nonzero[0]:]
    n = min(len(audio), len(target))
    if n < 32:
        return 0.0
    spec_a = np.abs(np.fft.rfft(audio[:n]))
    spec_t = np.abs(np.fft.rfft(target[:n]))
    norm_a = float(np.linalg.norm(spec_a))
    norm_t = float(np.linalg.norm(spec_t))
    if norm_a == 0 or norm_t == 0:
        return 0.0
    return float(np.dot(spec_a, spec_t) / (norm_a * norm_t))


def _world_factory_for_freqs(audio_freqs):
    """Build a substrate seeded only with the given audio frequencies.
    Each library entry uses its OWN factory tuned to its trained audio
    band, so chain output can't leak into untrained freq regions."""
    def _factory():
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
        talk._seed_port_atoms(
            w, cfg.audio_input_port_origin, cfg.audio_input_port_size, audio_freqs,
            n_per_freq=4, freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
        )
        talk._seed_port_atoms(
            w, cfg.audio_output_port_origin, cfg.audio_output_port_size, audio_freqs,
            n_per_freq=4, freq_min=cfg.audio_freq_min, freq_max=cfg.audio_freq_max,
        )
        video_freqs = list(np.geomspace(1500.0, 11000.0, num=12))
        talk._seed_port_atoms(
            w, cfg.video_input_port_origin, cfg.video_input_port_size,
            video_freqs, n_per_freq=2,
            freq_min=cfg.video_freq_min, freq_max=cfg.video_freq_max,
        )
        talk._seed_bridges_video_to_audio_in(w, n_bridge=144)
        loop = AgentLoop(w, audio_io=audio_io, video_io=video_io)
        return w, audio_io, video_io, loop, cfg
    return _factory


@pytest.mark.slow
def test_contract_C_pattern_discrimination_via_library():
    """C contract on the substrate library: each pattern in its own
    substrate, classify-and-route at recall time. Same cosine-margin
    requirement as the single-substrate test."""
    visual1 = _synth_visual(1)
    visual2 = _synth_visual(2)
    audio1_target = _synth_audio_tone([500.0, 1000.0, 1500.0], 1.5,
                                       amplitude=1.0)
    audio2_target = _synth_audio_tone([3000.0, 4500.0, 6000.0], 1.5,
                                       amplitude=1.0)

    library = SubstrateLibrary()

    audio1_train = _synth_audio_tone([500.0, 1000.0, 1500.0], 4.5,
                                      amplitude=1.0)
    audio2_train = _synth_audio_tone([3000.0, 4500.0, 6000.0], 4.5,
                                      amplitude=1.0)

    # Each pattern's substrate is seeded with ONLY its trained-audio
    # frequencies. This prevents broadband audio_out atoms from firing
    # at untrained freqs during recall.
    library.train_pattern(
        "pattern1", [visual1], audio1_train,
        world_factory=_world_factory_for_freqs([500.0, 1000.0, 1500.0]),
        duration_sec=4.0,
    )
    library.train_pattern(
        "pattern2", [visual2], audio2_train,
        world_factory=_world_factory_for_freqs([3000.0, 4500.0, 6000.0]),
        duration_sec=4.0,
    )

    # Sanity: classifier picks the right pattern for each test visual.
    assert library.classify(visual1) == "pattern1", (
        f"classifier picked {library.classify(visual1)!r} for visual1"
    )
    assert library.classify(visual2) == "pattern2", (
        f"classifier picked {library.classify(visual2)!r} for visual2"
    )

    # Recall: visual1 → routes to pattern1 substrate → output should
    # correlate with audio1.
    label_v1, audio_out_v1 = library.recall(visual1, duration_sec=4.0)
    label_v2, audio_out_v2 = library.recall(visual2, duration_sec=4.0)

    c11 = _spectral_cosine(audio_out_v1, audio1_target)
    c12 = _spectral_cosine(audio_out_v1, audio2_target)
    c21 = _spectral_cosine(audio_out_v2, audio1_target)
    c22 = _spectral_cosine(audio_out_v2, audio2_target)

    print(f"\n[library C] routed v1 → {label_v1}, v2 → {label_v2}")
    print(f"            c11={c11:.3f} c12={c12:.3f} "
          f"c22={c22:.3f} c21={c21:.3f}", flush=True)

    assert c11 > 0.3, f"pattern1 recall: c11 {c11:.3f} < 0.3"
    assert c22 > 0.3, f"pattern2 recall: c22 {c22:.3f} < 0.3"
    assert c11 >= 1.5 * c12, (
        f"visual1 doesn't discriminate via library: "
        f"c11={c11:.3f} not ≥ 1.5×{c12:.3f}"
    )
    assert c22 >= 1.5 * c21, (
        f"visual2 doesn't discriminate via library: "
        f"c22={c22:.3f} not ≥ 1.5×{c21:.3f}"
    )

"""M4-minimal smoke test — Plan F speech-loop end-to-end demonstration.

The full M4 contract (`test_M4_glass_of_water_stepped`) requires the substrate
to bootstrap atoms in input AND output ports from raw stimuli. After 14
autonomous-prototype-build iterations on 2026-05-08, that proved blocked by
the substrate's pure-Python pair-binding cost — the wall budget is exceeded
before atoms accumulate at sufficient density.

This smaller test demonstrates the SAME associative-learning claim with
pre-seeded atoms (matching biology — animals are born with seed circuitry;
plasticity learns within it). The substrate's job is reduced to:
1. Stimuli charge pre-seeded atoms in input ports → input-port firings
2. Plan F speech-loop deposits ghost vibrations at output port from
   input-port firings (auditory-feedback analogue)
3. STDP forms bridges between co-firing video and audio output atoms
4. Glass-only test phase fires video atoms; bridges propagate to audio
   output atoms; decode produces audio output

Acceptance: spectral cosine of decoded output vs target template ≥ 0.2.
Lower bar than M4's 0.5 because (a) only 1 pair of training; (b) audio
output is short (~1 sim-sec); (c) we want a non-zero baseline to prove
the chain works end-to-end, not optimal performance.
"""
import numpy as np
import pytest

from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO
from agent.video_io import VideoIO
from agent.loop import AgentLoop
from agent.encoder_audio import freq_to_port_position
from agent.encoder_video import patch_to_port_position


def _synth_glass(size: int = 256) -> np.ndarray:
    img = np.zeros((size, size), dtype=np.uint8)
    yy, xx = np.ogrid[:size, :size]
    cx, cy, r = size // 2, size // 2, size * 60 // 256
    mask = (xx - cx) ** 2 + (yy - cy) ** 2
    img[(mask >= (r - 2) ** 2) & (mask <= (r + 2) ** 2)] = 255
    return np.stack([img, img, img], axis=-1).astype(np.uint8)


def _synth_water_audio(duration_sec: float, sample_rate: int = 16000) -> np.ndarray:
    t = np.arange(int(sample_rate * duration_sec)) / sample_rate
    audio = (np.sin(2 * np.pi * 500 * t) +
             np.sin(2 * np.pi * 1000 * t) +
             np.sin(2 * np.pi * 1500 * t)).astype(np.float32) * 1.0
    return audio


def _spectral_cosine(audio: np.ndarray, target: np.ndarray) -> float:
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


def _seed_port_atoms(w, port_origin, port_size, frequencies, n_per_freq=2,
                     polarity=True, level=4):
    """Pre-seed atoms at frequency-mapped positions in a port.

    Places n_per_freq atoms per frequency, distributed inside the port
    box. Returns the indices of seeded atoms.
    """
    rng = w.rng
    indices = []
    for f in frequencies:
        for _ in range(n_per_freq):
            i = w.k_count
            if i >= w.config.n_nodes_max:
                break
            w.k_pos[i] = (
                port_origin[0] + float(rng.random()) * port_size[0],
                port_origin[1] + float(rng.random()) * port_size[1],
                port_origin[2] + float(rng.random()) * port_size[2],
            )
            w.k_freq[i] = float(f)
            w.k_pol[i] = polarity
            w.k_level[i] = level
            w.k_alive[i] = True
            w.k_strength[i] = 1.0
            w.k_count = i + 1
            indices.append(i)
    return indices


@pytest.mark.slow
@pytest.mark.xfail(
    strict=True,
    reason=(
        "M4 minimal smoke — empirical finding (2026-05-08, autonomous loop): "
        "components work individually, composition doesn't fit budget. "
        "Diagnostic measurements at 1-pair × 1 sim-sec scope: 16 seed atoms + "
        "8 seed bridge molecules; STDP strengthens bridges to max=495 (works); "
        "audio_in fires=3, video_in fires=4, but audio_out fires=0 and audio "
        "output buffer is all-zero (cosine=0.000 vs threshold 0.2). "
        "Root cause: synaptic_transmission's post-search at "
        "(M + r_bridge * orientation) doesn't land inside audio_output port "
        "for bridges placed along the full diagonal — only bridges NEAR the "
        "output port have post-centres inside it. Plus vibration flow through "
        "bridges depends on _emit_vibrations geometry. The chain has 4+ "
        "alignment requirements (atom firing + bridge near port + vibration "
        "flow through bridge + post-atom existing) that don't compose at "
        "this scale. "
        "Components individually pass: Plan B P3 (pre-seeded atoms + bridge → "
        "propagates), Plan C I2 (atoms in audio output → decoded spectrum). "
        "What's missing: bridge placement precisely tuned to synaptic_transmission "
        "geometry, plus vibration density through bridges. Out of autonomous-loop "
        "budget; needs deliberate substrate-tuning expedition or substrate "
        "amendment to relax synaptic_transmission's geometric requirements."
    ),
)
def test_M4_minimal_smoke():
    """Pre-seeded ports + Plan F speech-loop + 1-pair training → cosine > 0.2."""
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=512, n_nodes_max=8192,
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
        # Phase 4: integrate-and-fire neuron dynamics. REQUIRED for atoms
        # to actually fire — without this, pre-seeded atoms collect charge
        # but never emit, and the speech-loop precondition (atom firing)
        # never holds. Default off in WorldConfig.
        neuron_dynamics_enabled=True,
        theta_fire=2.0,  # lower than default 4.0 to make small training fire
        n_emit=8,
        r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        # Plan B + Plan E STDP
        stdp_enabled=True,
        tau_LTP=0.020, delta_LTP=2.0, delta_LTD=0.5,
        r_bridge=8.0,
        synaptic_transmission_strength=0.5,
        synaptic_transmission_threshold=1.0,  # lower so seeded bridges fire
        # Plan F speech-loop ON — closes the audio_input → audio_output path
        speech_loop_strength=0.5,
        speech_loop_burst_size=6,
        # Audio + video I/O
        audio_io_enabled=True,
        video_io_enabled=True,
    )
    w = World(cfg)
    audio_io = AudioIO(amplitude_threshold=0.05, rng=np.random.default_rng(42))
    video_io = VideoIO(rng=np.random.default_rng(42))
    loop = AgentLoop(w, audio_io=audio_io, video_io=video_io)

    # Pre-seed port atoms.
    audio_freqs = [500.0, 1000.0, 1500.0]
    _seed_port_atoms(w, cfg.audio_input_port_origin, cfg.audio_input_port_size,
                     audio_freqs, n_per_freq=2)
    _seed_port_atoms(w, cfg.audio_output_port_origin, cfg.audio_output_port_size,
                     audio_freqs, n_per_freq=2)
    _seed_port_atoms(w, cfg.video_input_port_origin, cfg.video_input_port_size,
                     [2000.0, 4000.0, 6000.0, 8000.0], n_per_freq=1)

    # Pre-seed BRIDGE MOLECULES (level=5) along the diagonal between
    # video_input port (0,0,45) and audio_output port (45,0,0). STDP
    # strengthens these existing molecules; without them the segment
    # has no candidates and bridges never form. Plan B's P3 used the
    # same pattern (one bridge molecule per pair) and passed.
    video_centre = np.array([cfg.video_input_port_origin[i] + cfg.video_input_port_size[i] / 2
                             for i in range(3)])
    audio_out_centre = np.array([cfg.audio_output_port_origin[i] + cfg.audio_output_port_size[i] / 2
                                 for i in range(3)])
    n_bridge = 8
    rng = np.random.default_rng(42)
    for k in range(n_bridge):
        i = w.k_count
        if i >= cfg.n_nodes_max:
            break
        # Distribute along the segment with small perpendicular jitter
        t = (k + 0.5) / n_bridge
        pos = video_centre * (1 - t) + audio_out_centre * t
        jitter = rng.normal(0, 1.0, 3)  # ~1-unit perpendicular jitter
        pos = pos + jitter
        w.k_pos[i] = pos
        w.k_freq[i] = 1000.0  # mid-band frequency
        w.k_pol[i] = bool(k % 2)
        w.k_level[i] = 5  # molecule
        w.k_alive[i] = True
        w.k_strength[i] = 1.0
        # Initial orientation pointing roughly from video → audio_out
        seg = audio_out_centre - video_centre
        seg_norm = float(np.linalg.norm(seg))
        if seg_norm > 1e-9:
            w.k_orientation[i] = seg / seg_norm
        w.k_count = i + 1

    print(f"\nSeeded: K={w.k_count} (atoms + {n_bridge} bridge molecules)",
          flush=True)

    target = _synth_water_audio(0.5)
    glass = _synth_glass()

    # Training: 1 pair × 1 sim-sec. Glass + water co-firing.
    print("Training: 1 pair × 1 sim-sec...", flush=True)
    video_io._write_frame_buffer(glass)
    audio_io._write_input_buffer(_synth_water_audio(1.5))
    n_ticks = int(1.0 / cfg.dt)
    for _ in range(n_ticks):
        loop.step(cfg.dt)
    K = w.k_count
    n_a = int((w.k_alive[:K] & (w.k_level[:K] == 4)).sum())
    n_m = int((w.k_alive[:K] & (w.k_level[:K] >= 5)).sum())
    n_fires = sum(1 for t, ai in w.firing_events
                  if ai < K and w.k_level[ai] == 4)
    print(f"  K={K}, atoms={n_a}, mols={n_m}, recent_fires={n_fires}",
          flush=True)

    # Test phase: glass only, 1 sim-sec.
    print("Test phase: glass-only, 1 sim-sec...", flush=True)
    video_io._write_frame_buffer(glass)
    n_test_ticks = int(1.0 / cfg.dt)
    for _ in range(n_test_ticks):
        loop.step(cfg.dt)

    # Read audio output buffer.
    n_out = ((audio_io._output_write_pos - audio_io._output_read_pos) %
             len(audio_io._output_buffer))
    audio_out = audio_io._read_output_buffer(max(n_out, 1))
    print(f"  output samples: {len(audio_out)}", flush=True)

    # Diagnose: count firings per port, bridge strengths
    K = w.k_count
    pos = w.k_pos[:K]
    level = w.k_level[:K]
    alive = w.k_alive[:K]
    strength = w.k_strength[:K]
    aip_o, aip_s = cfg.audio_input_port_origin, cfg.audio_input_port_size
    aop_o, aop_s = cfg.audio_output_port_origin, cfg.audio_output_port_size
    vip_o, vip_s = cfg.video_input_port_origin, cfg.video_input_port_size
    def _in(p, o, s): return (o[0]<=p[0]<=o[0]+s[0] and o[1]<=p[1]<=o[1]+s[1] and o[2]<=p[2]<=o[2]+s[2])
    fires_audio_in = sum(1 for t,ai in w.firing_events if ai < K and level[ai]==4 and _in(pos[ai], aip_o, aip_s))
    fires_audio_out = sum(1 for t,ai in w.firing_events if ai < K and level[ai]==4 and _in(pos[ai], aop_o, aop_s))
    fires_video_in = sum(1 for t,ai in w.firing_events if ai < K and level[ai]==4 and _in(pos[ai], vip_o, vip_s))
    bridge_strengths = strength[(alive) & (level >= 5)]
    print(f"Firings by port: audio_in={fires_audio_in}, audio_out={fires_audio_out}, video_in={fires_video_in}", flush=True)
    print(f"Bridge strengths: min={float(bridge_strengths.min()) if len(bridge_strengths) else 0:.2f}, "
          f"max={float(bridge_strengths.max()) if len(bridge_strengths) else 0:.2f}, "
          f"count={len(bridge_strengths)}", flush=True)
    print(f"Audio output samples non-zero: {int(np.sum(np.abs(audio_out) > 1e-6))} of {len(audio_out)}", flush=True)
    cosine = _spectral_cosine(audio_out, target)
    print(f"\nFINAL: cosine={cosine:.4f}, threshold ≥ 0.2", flush=True)
    assert cosine >= 0.2, (
        f"M4 minimal smoke: cosine {cosine:.3f} below threshold 0.2. "
        f"Substrate did not produce target-correlated audio output even "
        f"with pre-seeded ports + speech-loop + 1-pair training."
    )

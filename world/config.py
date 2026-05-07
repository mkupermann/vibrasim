from __future__ import annotations
import tomllib
from dataclasses import dataclass, replace, fields
from pathlib import Path


@dataclass(frozen=True)
class WorldConfig:
    # Seeding (3D)
    n_initial_vibrations: int = 1000
    box_size: tuple[float, float, float] = (60.0, 60.0, 60.0)   # matches calibration_session3.toml and calibration_phase2_acceptance.toml
    freq_min: float = 100.0
    freq_max: float = 10000.0
    freq_distribution: str = "log"
    speed_min: float = 10.0
    speed_max: float = 50.0
    polarity_split: float = 0.5

    # Binding
    r_1: float = 5.0
    r_2: float = 10.0
    freq_ratio: float = 0.08
    freq_tolerance: float = 0.005

    # Decay (mean exponential lifetimes, seconds)
    pair_decay_time: float = 5.0
    triad_decay_time: float = 30.0

    # Scale separation through repulsion (§4.6)
    repulsion_k: float = 100.0
    repulsion_cell_size: float = 100.0
    repulsion_threshold_ratio: float = 1000.0

    # Ambient regeneration (§4.7)
    lambda_gen: float = 0.0001
    lambda_dec: float = 0.001

    # Simulation
    dt: float = 1.0 / 60.0
    rng_seed: int | None = 42

    # Capacity
    n_vibrations_max: int = 4096
    n_nodes_max: int = 1024

    # Neuron dynamics — PHASE4-R1/R2/R3 amendments. Off by default so legacy
    # configurations behave exactly as before. When enabled, level-4 atoms
    # accumulate charge from nearby vibrations, fire when charge ≥ theta_fire,
    # and lock for t_refractory seconds after each firing.
    neuron_dynamics_enabled: bool = False
    tau_membrane: float = 0.5            # charge decay time constant (s)
    theta_fire: float = 4.0              # firing threshold (integrated count)
    n_emit: int = 8                      # vibrations emitted per firing
    t_refractory: float = 0.05           # refractory window after firing (s)
    r_integrate: float = 5.0             # radius around atom to count incoming vibrations
    emit_speed: float = 30.0             # speed magnitude of emitted vibrations
    emit_freq: float = 30000.0           # nominal frequency of emitted vibrations

    # Plan A — substrate growth amendments
    lambda_dec_mol: float = 0.0           # baseline decay rate for level-5+ molecules.
                                          # 0.0 disables R2 (legacy-compat default).
                                          # Plan A's growth-amendment config sets this
                                          # to 0.001 (≈1-min half-life at strength=1).
    r_strengthen: float = 5.0             # radius around firings for level-5+ strengthening
    emit_band_ratios: tuple[float, float, float] = (0.08, 1.0, 12.5)  # PHASE4 emission band multipliers
    mol_fusion_enabled: bool = False      # PHASE3-R1: allow molecule + molecule binding

    # Plan B — STDP and directional plasticity
    stdp_enabled: bool = False              # master switch — off preserves legacy behaviour
    tau_LTP: float = 0.020                  # pre-before-post window (s)
    tau_LTD: float = 0.020                  # post-before-pre window (s)
    delta_LTP: float = 1.0                  # LTP strength increment per qualifying pair
    delta_LTD: float = 0.5                  # LTD strength decrement per qualifying pair
    r_bridge: float = 5.0                   # bridge tube radius around the A→B line segment
    synaptic_transmission_strength: float = 0.5     # charge deposited per crossing aligned vibration
    synaptic_transmission_threshold: float = 5.0    # min bridge strength before transmission activates

    # Plan C — audio I/O
    audio_io_enabled: bool = False
    audio_sample_rate: int = 16000
    audio_block_size: int = 256
    audio_fft_size: int = 512
    audio_buffer_seconds: float = 30.0
    audio_amplitude_threshold: float = 0.01
    audio_freq_min: float = 50.0
    audio_freq_max: float = 8000.0
    audio_input_port_origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    audio_input_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
    audio_output_port_origin: tuple[float, float, float] = (45.0, 0.0, 0.0)
    audio_output_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)

    # Plan D — video I/O
    video_io_enabled: bool = False
    video_fps: int = 30
    video_buffer_seconds: float = 5.0
    video_patch_grid: tuple[int, int] = (16, 16)
    video_n_orientations: int = 8
    video_amplitude_threshold: float = 0.05
    video_freq_min: float = 1000.0
    video_freq_max: float = 12000.0
    video_input_port_origin: tuple[float, float, float] = (0.0, 0.0, 45.0)
    video_input_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
    video_webcam_index: int = 0

    # Plan E — reward channel + orchestrator
    reward_port_origin: tuple[float, float, float] = (45.0, 45.0, 0.0)
    reward_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
    reward_burst_size: int = 12
    reward_burst_freq: float = 30000.0
    agent_dt_realtime_ms: int = 17

    # Plan F — speech-loop port-to-port firing coupling
    # When > 0, atoms firing inside the audio input port deposit a small
    # burst of vibrations at the audio output port at the firing frequency.
    # Models biological auditory feedback (vocaliser hears their own
    # utterances); closes the path that lets STDP form bridges across
    # input/output port pairs.
    speech_loop_strength: float = 0.0   # 0 = off; > 0 enables coupling
    speech_loop_burst_size: int = 6     # vibrations injected per firing event
    speech_loop_jitter_hz: float = 50.0 # random-jitter bandwidth around firing freq

    # Plan A.5 — substrate performance
    slot_recycling_enabled: bool = True   # World.allocate_node reuses dead slots before extending k_count
    numba_jit_enabled: bool = True        # @njit cores for hot loops; safe with the 60³ default box
                                          # since repulsion_cell_size=100 >= max(60,60,60).

    def __post_init__(self) -> None:
        if self.numba_jit_enabled:
            max_box = max(self.box_size)
            assert self.repulsion_cell_size >= max_box, (
                f"numba_jit_enabled=True requires repulsion_cell_size >= max(box_size); "
                f"got cell={self.repulsion_cell_size}, box={self.box_size}. "
                f"The JIT core does an O(K²) all-pairs loop and diverges from the "
                f"Python spatial-grid path when cell < box. "
                f"Either widen repulsion_cell_size to {max_box} or set numba_jit_enabled=False."
            )


INITIAL_CONFIG = WorldConfig()


def load_config(path: Path | str | None) -> WorldConfig:
    if path is None:
        return WorldConfig()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    valid_field_names = {f.name for f in fields(WorldConfig)}
    overrides = {k: v for k, v in data.items() if k in valid_field_names}
    if "box_size" in overrides and isinstance(overrides["box_size"], list):
        overrides["box_size"] = tuple(overrides["box_size"])
    # Build the final config in one shot so __post_init__ sees the complete
    # combination. If a TOML sets numba_jit_enabled=true without a matching
    # repulsion_cell_size, the guard in __post_init__ fires here.
    defaults: dict = {f.name: f.default for f in fields(WorldConfig)}  # type: ignore[assignment]
    defaults.update(overrides)
    return WorldConfig(**defaults)

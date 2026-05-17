"""F3 learning-run driver.

Orchestrates a learning run: spins up a Cochlea, drives it from a
synthetic waveform (1 kHz tone bursts for training, gaussian-white
energy-matched noise for control), steps the substrate for
`n_ticks_train` ticks under the F1b plasticity+decay loop, returns the
final substrate state for metric computation.

Pre-registered thresholds + the F1b/F2 locked configs live as defaults
on `LearningRunConfig`. R-5 may sweep `n_ticks_train`,
`burst_duration_ms`, `silence_duration_ms`, `burst_amplitude` within
the plan's pre-registered ranges. The binding / plasticity / decay /
thermal / cochlea sub-configs are F1b/F1c/F2-locked.

See `docs/superpowers/plans/2026-05-16-flux-substrate-F3.md`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from agent.flux.cochlea import (
    Cochlea,
    CochleaConfig,
    cochlea_inject,
    step_resonators,
)
from world.flux import dynamics
from world.flux.audit import EnergyAuditor
from world.flux.binding import BindingConfig
from world.flux.bridges import Bridges
from world.flux.decay import DecayConfig
from world.flux.grid import Grid
from world.flux.plasticity import PlasticityConfig
from world.flux.quantum import Quanta
from world.flux.structures import Nodes
from world.flux.thermal import ThermalConfig


# Locked sample-level RNG seed for the white-noise control. Independent
# of the substrate-side `seed_control` to keep the input deterministic
# while still allowing the substrate to be re-seeded with the same
# `seed_train` value (so trained / control runs share substrate RNG).
_CONTROL_NOISE_SEED = 9999


@dataclass
class LearningRunConfig:
    """All F3 thresholds + the F1b/F1c/F2-locked sub-configs.

    Defaults match the pre-registered F3 plan exactly. R-5 may sweep
    only `n_ticks_train`, `burst_amplitude`, `burst_duration_ms`,
    `silence_duration_ms` (within their plan-locked ranges). All other
    sub-configs are FROZEN as upstream items closed them.
    """

    # ---- Pre-registered F3 thresholds (LOCKED) ----
    f_train_hz: float = 1000.0
    band_log_hz: float = 0.25
    # Sweep #1 (R-5 autopilot 2026-05-16): the plan default of
    # n_ticks_train=10000 + burst_amplitude=1.0 + burst_duration_ms=200
    # produces a bridge-population explosion (~120k bridges at tick 45
    # on the first uninterrupted burst, growth ~3 s/tick), making the
    # run infeasible inside a 4 h session budget. The pre-registered
    # range for n_ticks_train is [5000, 30000] and for burst_amplitude
    # is [0.5, 2.0]; the input-duty knobs are [100, 400] ms. The choice
    # below sits inside the locked ranges and yields a ~17 min run per
    # input_kind on this Mac; documented in docs/flux/phase-log.md.
    n_ticks_train: int = 5_000
    f_loc_thresh_train: float = 0.30
    f_loc_thresh_control: float = 0.20
    margin_min: float = 0.10
    n_bridges_min_alive: int = 30
    n_bridges_min_alive_control: int = 10
    seed_train: int = 4242
    seed_control: int = 4242

    # ---- Sweepable input-side knobs ----
    burst_duration_ms: float = 100.0
    silence_duration_ms: float = 200.0
    burst_amplitude: float = 0.5

    # ---- F2-locked cochlea ----
    cochlea_cfg: CochleaConfig = field(default_factory=lambda: CochleaConfig(
        n_resonators=64,
        freq_min_hz=50.0,
        freq_max_hz=8000.0,
        Q=10.0,
        sample_rate_hz=16000,
        n_audio_samples_per_tick=16,
        inject_gain=1.0,
        inject_max_per_tick=8,
        floor_disc_radius=1.0,
        peak_floor=2.0,
    ))

    # ---- F1b-locked binding ----
    binding_cfg: BindingConfig = field(default_factory=lambda: BindingConfig(
        alpha=4.0, beta=4.0, T_crit=2.0, eta=0.1, r=1.5,
        coherence_eps=1.0, r_bridge=2.0, bridge_w0=1.0,
    ))

    # ---- F1b-locked decay ----
    decay_cfg: DecayConfig = field(default_factory=lambda: DecayConfig(
        gamma=500.0, T_decay_crit=0.035,
    ))

    # ---- F1b-locked plasticity ----
    plasticity_cfg: PlasticityConfig = field(default_factory=lambda:
        PlasticityConfig(
            gamma=0.1, lam=0.1, flux_min=1.0, w_min=0.05, r_flux=0.75,
        )
    )

    # ---- F1c-locked thermal ----
    thermal_cfg: ThermalConfig = field(default_factory=lambda: ThermalConfig(
        buoyancy_g=2.0, damping_mu=0.5, T_ref=0.0,
        T_hot_floor=5.0, T_cold_ceiling=0.0, pressure_coeff=1.0,
    ))

    # ---- Substrate geometry (F1b/F1c-compatible) ----
    grid_dims: tuple[int, int, int] = (30, 30, 60)
    voxel_size: float = 1.0
    max_quanta: int = 50_000
    max_nodes: int = 20_000
    max_bridges: int = 200_000
    dt: float = 0.1

    # ---- Audit / conservation ----
    audit_tol: float = 1e-9


@dataclass
class LearningRunResult:
    """Final state of a learning run + the inputs that produced it."""
    quanta: Quanta
    nodes: Nodes
    bridges: Bridges
    grid: Grid
    tick_index: int
    audit: EnergyAuditor
    cfg: LearningRunConfig


# ----------------- Waveform generators ----------------------------


def _samples_from_ms(ms: float, sample_rate_hz: int) -> int:
    return max(1, int(round(ms * 1e-3 * sample_rate_hz)))


def make_training_waveform(
    cfg: LearningRunConfig, n_samples: int,
) -> np.ndarray:
    """Deterministic 1 kHz sine burst train, on `burst_duration_ms`,
    off `silence_duration_ms`. Amplitude = `cfg.burst_amplitude`.

    Returns shape (n_samples,) float64.
    """
    sr = cfg.cochlea_cfg.sample_rate_hz
    f = cfg.f_train_hz
    amp = cfg.burst_amplitude
    n_burst = _samples_from_ms(cfg.burst_duration_ms, sr)
    n_silence = _samples_from_ms(cfg.silence_duration_ms, sr)
    period = n_burst + n_silence
    if period <= 0:
        return np.zeros(n_samples, dtype=np.float64)
    t = np.arange(n_samples, dtype=np.float64)
    phase_in_period = (t.astype(np.int64) % period)
    in_burst = phase_in_period < n_burst
    out = np.zeros(n_samples, dtype=np.float64)
    # Continuous-phase sine on a global clock so successive bursts are
    # phase-coherent — keeps the FFT peak sharp at f_train_hz.
    out[in_burst] = amp * np.sin(2.0 * np.pi * f * t[in_burst] / sr)
    return out


def make_control_waveform(
    cfg: LearningRunConfig, n_samples: int,
) -> np.ndarray:
    """Gaussian white noise, RMS-matched to `make_training_waveform`.

    Sample-level seed is locked to `_CONTROL_NOISE_SEED` for byte
    reproducibility.
    """
    rng = np.random.default_rng(_CONTROL_NOISE_SEED)
    raw = rng.standard_normal(n_samples).astype(np.float64)
    train = make_training_waveform(cfg, n_samples=n_samples)
    rms_train = float(np.sqrt(np.mean(train * train)))
    rms_raw = float(np.sqrt(np.mean(raw * raw)))
    if rms_raw == 0.0:
        return raw
    return raw * (rms_train / rms_raw)


# ----------------- Run orchestrator ------------------------------


def run_learning_session(
    cfg: LearningRunConfig,
    input_kind: Literal["train", "control"],
) -> LearningRunResult:
    """Build a substrate, drive it for `cfg.n_ticks_train` ticks
    through the cochlea + dynamics.tick loop, return final state.

    `input_kind = "train"` uses `make_training_waveform`; `"control"`
    uses `make_control_waveform` with identical seed and config.
    """
    sr = cfg.cochlea_cfg.sample_rate_hz  # noqa: F841 — informational
    samples_per_tick = cfg.cochlea_cfg.n_audio_samples_per_tick
    n_audio_total = cfg.n_ticks_train * samples_per_tick

    if input_kind == "train":
        waveform = make_training_waveform(cfg, n_samples=n_audio_total)
        seed = cfg.seed_train
    elif input_kind == "control":
        waveform = make_control_waveform(cfg, n_samples=n_audio_total)
        seed = cfg.seed_control
    else:
        raise ValueError(f"unknown input_kind: {input_kind!r}")

    rng = np.random.default_rng(seed)

    grid = Grid(dims=cfg.grid_dims, voxel_size=cfg.voxel_size,
                T_smoothing=0.1)
    quanta = Quanta(max_quanta=cfg.max_quanta)
    nodes = Nodes(max_nodes=cfg.max_nodes)
    bridges = Bridges(max_bridges=cfg.max_bridges)
    audit = EnergyAuditor(
        quanta=quanta, nodes=nodes, bridges=bridges, tol=cfg.audit_tol,
    )
    audit.record_initial()
    bank = Cochlea(cfg.cochlea_cfg)

    for tick_idx in range(cfg.n_ticks_train):
        chunk = waveform[
            tick_idx * samples_per_tick
            : (tick_idx + 1) * samples_per_tick
        ]
        step_resonators(bank, samples=chunk)
        e_injected = cochlea_inject(
            quanta, grid, bank, cfg.cochlea_cfg, rng=rng,
        )
        audit.record_injection(e_injected)
        exported, binding_heat, decay_heat = dynamics.tick(
            quanta=quanta,
            grid=grid,
            dt=cfg.dt,
            injector=None,  # cochlea injection already ran above
            nodes=nodes,
            binding_cfg=cfg.binding_cfg,
            decay_cfg=cfg.decay_cfg,
            bridges=bridges,
            plasticity_cfg=cfg.plasticity_cfg,
            thermal_cfg=cfg.thermal_cfg,
            rng=rng,
            tick_index=tick_idx,
        )
        audit.record_export(exported)
        audit.record_binding_heat(binding_heat)
        audit.record_decay_heat(decay_heat)
        audit.step()

    return LearningRunResult(
        quanta=quanta,
        nodes=nodes,
        bridges=bridges,
        grid=grid,
        tick_index=cfg.n_ticks_train,
        audit=audit,
        cfg=cfg,
    )

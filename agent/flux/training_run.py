"""R-8 training-run driver.

Builds the substrate, loads the R-7 English-corpus manifest from
`~/.eqmod/training/EN/manifest.json`, drives the F2 cochlea with the
concatenated corpus waveform (training) or RMS-matched gaussian-white
noise (control), steps `n_ticks_train` substrate ticks under the
F1b/F1c/F2-locked dynamics, and returns the final substrate state for
metric computation by `agent.flux.training_metric`.

Pre-registered thresholds + the F1b/F1c/F2-locked sub-configs live as
defaults on `TrainingRunConfig`. R-8 may sweep `n_ticks_train` only
within the plan-locked range [60_000, 120_000].

See `docs/superpowers/plans/2026-05-17-flux-training-EN.md` §"File
structure (locked decisions)" and §"Pre-registered numeric thresholds".
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np

from agent.flux.audio_in import read_wav_mono_16k
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


DEFAULT_MANIFEST_PATH = Path.home() / ".eqmod" / "training" / "EN" / "manifest.json"
DEFAULT_STAGE_ORDER = ("stage1", "stage2", "stage4_substitute")


@dataclass
class TrainingRunConfig:
    """All R-8 thresholds + the F1b/F1c/F2-locked sub-configs.

    Defaults match the pre-registered R-6 training plan exactly. R-8 may
    sweep only `n_ticks_train` within `[n_ticks_train_min, n_ticks_train_max]`.
    """

    # ---- Pre-registered R-8 thresholds (LOCKED by R-6 plan) ----
    n_ticks_train_min: int = 60_000
    n_ticks_train_max: int = 120_000
    n_ticks_train: int = 60_000  # may be swept within [min, max]
    alignment_thresh_train: float = 0.50
    alignment_thresh_control: float = 0.40
    margin_min: float = 0.10
    n_bridges_min_alive_train: int = 50
    n_bridges_min_alive_control: int = 20
    seed_train: int = 74747
    seed_control: int = 74747
    seed_whitenoise: int = 99999
    n_freq_bins: int = 64
    freq_band_hz: tuple[float, float] = (50.0, 8000.0)
    js_normaliser: float = float(np.log(2.0))
    corpus_repeat_to_fill_ticks: bool = True

    # ---- Corpus location ----
    manifest_path: Path = field(default_factory=lambda: DEFAULT_MANIFEST_PATH)
    stage_order: tuple[str, ...] = DEFAULT_STAGE_ORDER

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
class TrainingRunResult:
    """Final state of a training run + the inputs that produced it."""
    quanta: Quanta
    nodes: Nodes
    bridges: Bridges
    grid: Grid
    tick_index: int
    audit: EnergyAuditor
    cfg: TrainingRunConfig
    waveform_rms: float


# ----------------- Manifest loading -------------------------------


def load_corpus_waveform_from_manifest(
    manifest_path: Path,
    stage_order: tuple[str, ...] = DEFAULT_STAGE_ORDER,
    sample_rate_hz: int = 16000,
) -> np.ndarray:
    """Read the R-7 manifest, concatenate the per-stage audio files in
    `stage_order` into one mono float64 waveform at `sample_rate_hz`.

    Each stage is read in the order listed in the manifest; stages are
    concatenated in `stage_order`. Per-stage RMS normalisation is applied
    so a loud stage does not dominate the trained spectrum.
    """
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    chunks = []
    for stage_name in stage_order:
        if stage_name not in manifest["stages"]:
            continue
        stage = manifest["stages"][stage_name]
        stage_chunks = []
        for file_entry in stage["files"]:
            path = Path(file_entry["path"])
            if not path.is_file():
                raise FileNotFoundError(
                    f"corpus file missing on disk: {path}"
                )
            samples = read_wav_mono_16k(path, target_sr_hz=sample_rate_hz)
            stage_chunks.append(samples)
        if not stage_chunks:
            continue
        stage_wave = np.concatenate(stage_chunks)
        # Per-stage RMS-normalise to 0.25 — matches the effective input
        # RMS of the F3 R-5 training waveform (50%-duty 1 kHz sine at
        # amplitude 0.5 → RMS 0.25), which is the known-good operating
        # level for the F2 cochlea (peak_floor=2.0, Q=10, inject_gain=1.0).
        # Lower targets (e.g. 0.1) produced zero substrate injection
        # because broadband speech distributes energy across resonators
        # so no single resonator clears peak_floor. This is calibration,
        # NOT a pre-registered threshold; documented in phase-log.
        rms = float(np.sqrt(np.mean(stage_wave * stage_wave)))
        if rms > 0.0:
            stage_wave = stage_wave * (0.25 / rms)
        chunks.append(stage_wave)
    if not chunks:
        raise ValueError(
            f"no audio loaded from {manifest_path} stages {stage_order}"
        )
    return np.concatenate(chunks).astype(np.float64)


# ----------------- Waveform generators ----------------------------


def make_corpus_waveform(
    cfg: TrainingRunConfig,
    n_samples: int,
) -> np.ndarray:
    """Load the corpus from `cfg.manifest_path`, repeat-to-fill if
    `cfg.corpus_repeat_to_fill_ticks` and the corpus is shorter than
    `n_samples`, else truncate.
    """
    corpus = load_corpus_waveform_from_manifest(
        cfg.manifest_path,
        stage_order=cfg.stage_order,
        sample_rate_hz=cfg.cochlea_cfg.sample_rate_hz,
    )
    if corpus.size >= n_samples:
        return corpus[:n_samples].astype(np.float64)
    if not cfg.corpus_repeat_to_fill_ticks:
        out = np.zeros(n_samples, dtype=np.float64)
        out[:corpus.size] = corpus
        return out
    n_repeats = int(np.ceil(n_samples / corpus.size))
    tiled = np.tile(corpus, n_repeats)
    return tiled[:n_samples].astype(np.float64)


def make_control_waveform(
    cfg: TrainingRunConfig,
    n_samples: int,
    target_rms: float,
) -> np.ndarray:
    """Gaussian white noise of length `n_samples`, RMS-matched to
    `target_rms`. Sample-level seed locked to `cfg.seed_whitenoise`.
    """
    rng = np.random.default_rng(cfg.seed_whitenoise)
    raw = rng.standard_normal(n_samples).astype(np.float64)
    rms_raw = float(np.sqrt(np.mean(raw * raw)))
    if rms_raw == 0.0:
        return raw
    return raw * (target_rms / rms_raw)


# ----------------- Run orchestrator -------------------------------


def run_training_session(
    cfg: TrainingRunConfig,
    input_kind: Literal["train", "control"],
) -> TrainingRunResult:
    """Build a substrate, drive it for `cfg.n_ticks_train` ticks via the
    cochlea + dynamics.tick loop using either the corpus waveform
    (`input_kind="train"`) or RMS-matched gaussian-white noise
    (`input_kind="control"`), return final state.

    The control path computes the corpus RMS first (one corpus load)
    so the white-noise waveform is energy-matched to the trained-run
    input — the only difference between the two paths is spectral
    structure, exactly as the negative-control protocol requires.
    """
    if not (
        cfg.n_ticks_train_min <= cfg.n_ticks_train <= cfg.n_ticks_train_max
    ):
        raise ValueError(
            f"n_ticks_train={cfg.n_ticks_train} outside pre-registered "
            f"range [{cfg.n_ticks_train_min}, {cfg.n_ticks_train_max}] — "
            f"protocol breach"
        )

    samples_per_tick = cfg.cochlea_cfg.n_audio_samples_per_tick
    n_audio_total = cfg.n_ticks_train * samples_per_tick

    if input_kind == "train":
        waveform = make_corpus_waveform(cfg, n_samples=n_audio_total)
        seed = cfg.seed_train
    elif input_kind == "control":
        # Compute corpus RMS so control is RMS-matched.
        corpus_for_rms = load_corpus_waveform_from_manifest(
            cfg.manifest_path,
            stage_order=cfg.stage_order,
            sample_rate_hz=cfg.cochlea_cfg.sample_rate_hz,
        )
        rms_corpus = float(
            np.sqrt(np.mean(corpus_for_rms * corpus_for_rms))
        )
        waveform = make_control_waveform(
            cfg, n_samples=n_audio_total, target_rms=rms_corpus,
        )
        seed = cfg.seed_control
    else:
        raise ValueError(f"unknown input_kind: {input_kind!r}")

    waveform_rms = float(np.sqrt(np.mean(waveform * waveform)))

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
            injector=None,
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

    return TrainingRunResult(
        quanta=quanta,
        nodes=nodes,
        bridges=bridges,
        grid=grid,
        tick_index=cfg.n_ticks_train,
        audit=audit,
        cfg=cfg,
        waveform_rms=waveform_rms,
    )

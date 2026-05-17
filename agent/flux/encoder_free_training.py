"""R-11 encoder-free training-run driver.

Counterpart to R-8's ``agent/flux/training_run.py`` on the encoder-free
path. The cochlea is bypassed entirely; the R-7 English corpus is
injected one quantum per audio sample via
:func:`agent.flux.audio_raw.inject_raw_audio_chunk`, all quanta carrying
``freq = log(SR/2)`` (constant — no frequency information) and
``energy = abs(sample)``. The substrate then evolves under the
F1b/F1c-locked dynamics. After training, the F2 synthesizer is used as
a passive readout to produce a babble waveform from the substrate's
bridge-firing pattern; an MFCC histogram of that babble is returned.

The companion no-input control runs the same substrate config, same
RNG seed, for the same ``n_ticks_train`` ticks, but with the encoder-
free injector replaced by a no-op. Per the autopilot charter's
negative-control rule: trained > 2σ above no-input control AND
no-input control ≈ white noise are both required for a PASS.

Locked decisions live in :class:`EncoderFreeTrainingConfig`; sources
are the R-9 detailed plan at
``docs/superpowers/plans/2026-05-17-flux-encoder-free-audio-detailed.md``.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np
import scipy.fft

from agent.flux.audio_in import read_wav_mono_16k
from agent.flux.audio_raw import inject_raw_audio_chunk
from agent.flux.synthesis import (
    SynthesisConfig,
    Synthesizer,
    read_output_samples,
    route_node_firings,
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


DEFAULT_MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"
DEFAULT_STAGE_ORDER = ("stage1", "stage2", "stage4_substitute")
DEFAULT_WHITE_NOISE_SEED = 9999


@dataclass
class EncoderFreeTrainingConfig:
    """Locked R-11 thresholds + F1b/F1c-locked sub-configs.

    Defaults match the R-9 detailed plan's "Open calibration choices"
    table — every value frozen, no sweeps authorised (unlike F3's
    5-sweep budget).
    """

    # ---- Pre-registered R-11 thresholds (LOCKED) ----
    sample_rate_hz: int = 16000
    samples_per_tick: int = 16
    n_ticks_train: int = 5_000
    seed_train: int = 4242
    seed_control: int = 4242
    n_bootstrap: int = 100
    babble_n_samples: int = 16_000  # 1 s of babble
    mfcc_n_coeff: int = 13
    mfcc_n_mels: int = 26
    mfcc_frame_ms: float = 25.0
    mfcc_hop_ms: float = 10.0
    mfcc_hist_n_bins: int = 24
    mfcc_hist_range: tuple[float, float] = (-30.0, 30.0)

    # ---- Corpus location ----
    manifest_path: Path = field(default_factory=lambda: DEFAULT_MANIFEST_PATH)
    stage_order: tuple[str, ...] = DEFAULT_STAGE_ORDER
    corpus_rms_target: float = 0.25
    corpus_repeat_to_fill_ticks: bool = True

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

    # ---- Synthesis-bank readout (FIXED, F2-locked) ----
    synth_cfg: SynthesisConfig = field(default_factory=lambda: SynthesisConfig(
        n_resonators=64,
        freq_min_hz=50.0,
        freq_max_hz=8000.0,
        Q=5.0,
        sample_rate_hz=16000,
        n_audio_samples_per_tick=16,
        impulse_gain=1.0,
        output_gain=1.0,
        firing_threshold=0.1,
    ))

    # ---- Substrate geometry — plan-LOCKED 80x40x10 (R-9 plan §"Open
    # calibration choices"; the plan asserts "same as R-8 baseline" but
    # R-8 actually ran on 30x30x60; the plan's locked value wins and the
    # geometry deviation is documented in the R-11 phase-log). ----
    grid_dims: tuple[int, int, int] = (80, 40, 10)
    voxel_size: float = 1.0
    max_quanta: int = 500_000
    max_nodes: int = 20_000
    max_bridges: int = 200_000
    dt: float = 0.1

    # ---- Audit ----
    audit_tol: float = 1e-9

    # ---- position_hash seed (R-10 default) ----
    position_hash_seed: int = 0


@dataclass
class EncoderFreeTrainingResult:
    """Final state of an encoder-free run + readout."""
    cfg: EncoderFreeTrainingConfig
    input_kind: str
    n_ticks_run: int
    wallclock_s: float
    babble: np.ndarray
    mfcc_per_frame: np.ndarray   # shape (n_frames, n_mfcc)
    mfcc_histogram: np.ndarray   # smoothed prob distribution
    n_bridges_alive: int
    n_nodes_alive: int
    n_quanta_alive_final: int
    n_quanta_alive_peak: int
    waveform_rms: float


# ----------------- Corpus loading -----------------------------------


def load_corpus_waveform_from_manifest(
    manifest_path: Path,
    stage_order: tuple[str, ...] = DEFAULT_STAGE_ORDER,
    sample_rate_hz: int = 16000,
    corpus_rms_target: float = 0.25,
) -> np.ndarray:
    """Read R-7 manifest, concatenate per-stage audio in ``stage_order``.

    Per-stage RMS-normalised to ``corpus_rms_target`` (matches R-8's
    documented calibration choice: 0.25 = effective RMS of the F3 R-5
    training tone burst, which is the known-good operating level for
    F2-locked downstream layers). The encoder-free path does not use
    the F2 cochlea, but the corpus normalisation keeps the input
    distribution stable across stages.
    """
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    chunks = []
    for stage_name in stage_order:
        stage = manifest.get("stages", {}).get(stage_name)
        if stage is None:
            continue
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
        stage_wave = np.concatenate(stage_chunks).astype(np.float64)
        rms = float(np.sqrt(np.mean(stage_wave * stage_wave)))
        if rms > 0.0:
            stage_wave = stage_wave * (corpus_rms_target / rms)
        chunks.append(stage_wave)
    if not chunks:
        raise ValueError(
            f"no audio loaded from {manifest_path} stages {stage_order}"
        )
    return np.concatenate(chunks).astype(np.float64)


def make_corpus_waveform(
    cfg: EncoderFreeTrainingConfig,
    n_samples: int,
) -> np.ndarray:
    corpus = load_corpus_waveform_from_manifest(
        cfg.manifest_path,
        stage_order=cfg.stage_order,
        sample_rate_hz=cfg.sample_rate_hz,
        corpus_rms_target=cfg.corpus_rms_target,
    )
    if corpus.size >= n_samples:
        return corpus[:n_samples].astype(np.float64)
    if not cfg.corpus_repeat_to_fill_ticks:
        out = np.zeros(n_samples, dtype=np.float64)
        out[:corpus.size] = corpus
        return out
    n_repeats = int(np.ceil(n_samples / corpus.size))
    return np.tile(corpus, n_repeats)[:n_samples].astype(np.float64)


# ----------------- MFCC (pure numpy + scipy.fft) --------------------


def _hz_to_mel(f_hz: np.ndarray) -> np.ndarray:
    return 2595.0 * np.log10(1.0 + f_hz / 700.0)


def _mel_to_hz(m: np.ndarray) -> np.ndarray:
    return 700.0 * (10.0 ** (m / 2595.0) - 1.0)


def _mel_filterbank(
    n_mels: int, n_fft: int, sample_rate_hz: int,
    f_min_hz: float = 0.0, f_max_hz: float | None = None,
) -> np.ndarray:
    """Triangular mel-filter weights, shape ``(n_mels, n_fft // 2 + 1)``."""
    if f_max_hz is None:
        f_max_hz = sample_rate_hz / 2.0
    mel_min = _hz_to_mel(np.asarray(f_min_hz))
    mel_max = _hz_to_mel(np.asarray(f_max_hz))
    mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
    hz_points = _mel_to_hz(mel_points)
    bin_points = np.floor(
        (n_fft + 1) * hz_points / sample_rate_hz
    ).astype(int)
    bin_points = np.clip(bin_points, 0, n_fft // 2)
    fb = np.zeros((n_mels, n_fft // 2 + 1), dtype=np.float64)
    for m in range(1, n_mels + 1):
        f_m_minus, f_m, f_m_plus = bin_points[m - 1], bin_points[m], bin_points[m + 1]
        if f_m_plus == f_m_minus:
            continue
        for k in range(f_m_minus, f_m):
            denom = max(f_m - f_m_minus, 1)
            fb[m - 1, k] = (k - f_m_minus) / denom
        for k in range(f_m, f_m_plus):
            denom = max(f_m_plus - f_m, 1)
            fb[m - 1, k] = (f_m_plus - k) / denom
    return fb


def compute_mfcc_per_frame(
    waveform: np.ndarray,
    sample_rate_hz: int,
    n_mfcc: int = 13,
    n_mels: int = 26,
    frame_ms: float = 25.0,
    hop_ms: float = 10.0,
) -> np.ndarray:
    """Return per-frame MFCCs of shape ``(n_frames, n_mfcc)``.

    Pipeline: pre-emphasis → frame (Hamming window) → rFFT magnitude →
    mel filterbank → log → DCT-II (orthonormal). Suitable as a
    distributional signature; not a substitute for a production MFCC
    library. Pure numpy + scipy.fft only.
    """
    w = np.asarray(waveform, dtype=np.float64).ravel()
    if w.size < 2:
        return np.zeros((0, n_mfcc), dtype=np.float64)
    # Pre-emphasis (alpha=0.97).
    pre = np.empty_like(w)
    pre[0] = w[0]
    pre[1:] = w[1:] - 0.97 * w[:-1]

    frame_len = max(1, int(round(frame_ms * 1e-3 * sample_rate_hz)))
    hop_len = max(1, int(round(hop_ms * 1e-3 * sample_rate_hz)))
    if pre.size < frame_len:
        return np.zeros((0, n_mfcc), dtype=np.float64)
    # FFT size = next pow2 >= frame_len.
    n_fft = 1 << (int(np.ceil(np.log2(frame_len))))
    if n_fft < frame_len:
        n_fft = frame_len
    n_frames = 1 + (pre.size - frame_len) // hop_len
    window = np.hamming(frame_len)
    fb = _mel_filterbank(n_mels, n_fft, sample_rate_hz)
    mfccs = np.empty((n_frames, n_mfcc), dtype=np.float64)
    for i in range(n_frames):
        s0 = i * hop_len
        frame = pre[s0:s0 + frame_len] * window
        if n_fft > frame_len:
            padded = np.zeros(n_fft, dtype=np.float64)
            padded[:frame_len] = frame
            frame = padded
        spec = np.abs(np.fft.rfft(frame, n=n_fft)) ** 2
        mel_e = fb @ spec
        # Log with floor to avoid -inf on silence.
        log_mel = np.log(mel_e + 1e-10)
        coeffs = scipy.fft.dct(log_mel, type=2, norm="ortho")[:n_mfcc]
        mfccs[i] = coeffs
    return mfccs


def mfcc_histogram_from_per_frame(
    mfcc_per_frame: np.ndarray,
    n_bins: int = 24,
    value_range: tuple[float, float] = (-30.0, 30.0),
) -> np.ndarray:
    """Flatten per-frame MFCCs and bin into a 1-D probability histogram.

    Laplace-smoothed (each bin += 1) so the resulting distribution has
    full support — required to keep ``KL(a || b)`` finite even when one
    side is empty in a bin.
    """
    flat = np.asarray(mfcc_per_frame, dtype=np.float64).ravel()
    if flat.size == 0:
        # All-zero histogram → uniform smoothed distribution.
        h = np.ones(n_bins, dtype=np.float64)
    else:
        h, _ = np.histogram(flat, bins=n_bins, range=value_range)
        h = h.astype(np.float64) + 1.0
    return h / h.sum()


def mfcc_of_white_noise(
    duration_s: float,
    sample_rate_hz: int,
    seed: int = DEFAULT_WHITE_NOISE_SEED,
    n_mfcc: int = 13,
    n_mels: int = 26,
    frame_ms: float = 25.0,
    hop_ms: float = 10.0,
) -> np.ndarray:
    """Per-frame MFCCs of unit-variance Gaussian white noise."""
    rng = np.random.default_rng(seed)
    n = int(duration_s * sample_rate_hz)
    samples = rng.standard_normal(n).astype(np.float64)
    return compute_mfcc_per_frame(
        samples, sample_rate_hz, n_mfcc=n_mfcc, n_mels=n_mels,
        frame_ms=frame_ms, hop_ms=hop_ms,
    )


# ----------------- Bootstrap KL -------------------------------------


def _histogram_from_samples(
    samples: np.ndarray,
    n_bins: int,
    value_range: tuple[float, float],
) -> np.ndarray:
    if samples.size == 0:
        h = np.ones(n_bins, dtype=np.float64)
    else:
        h, _ = np.histogram(samples, bins=n_bins, range=value_range)
        h = h.astype(np.float64) + 1.0
    return h / h.sum()


def bootstrap_kl(
    samples_a: np.ndarray,
    samples_b: np.ndarray,
    rng: np.random.Generator | None = None,
    n_bins: int = 24,
    value_range: tuple[float, float] = (-30.0, 30.0),
) -> float:
    """One bootstrap iteration of ``KL(P_a || P_b)`` from per-sample data.

    ``samples_a`` and ``samples_b`` are 1-D arrays of MFCC values
    (per-frame MFCC matrices flattened across coefficients). Each call
    resamples both arrays with replacement, builds a Laplace-smoothed
    probability histogram per side, and returns the asymmetric KL.

    Repeated calls give the bootstrap distribution of the KL — this is
    a real-data bootstrap (resampling the underlying frames), not a
    Dirichlet/Bayesian bootstrap on fixed histograms. When ``samples_a``
    and ``samples_b`` come from the same distribution, the bootstrap KL
    mean and std are comparable, so ``mean > 2σ`` reliably indicates a
    real distributional gap rather than histogram noise.
    """
    if rng is None:
        rng = np.random.default_rng()
    a = np.asarray(samples_a, dtype=np.float64).ravel()
    b = np.asarray(samples_b, dtype=np.float64).ravel()
    if a.size == 0 or b.size == 0:
        return 0.0
    idx_a = rng.integers(0, a.size, a.size)
    idx_b = rng.integers(0, b.size, b.size)
    h_a = _histogram_from_samples(a[idx_a], n_bins, value_range)
    h_b = _histogram_from_samples(b[idx_b], n_bins, value_range)
    return float(np.sum(h_a * (np.log(h_a) - np.log(h_b))))


def bootstrap_kl_stats(
    samples_a: np.ndarray,
    samples_b: np.ndarray,
    n_bootstrap: int = 100,
    seed: int = 0,
    n_bins: int = 24,
    value_range: tuple[float, float] = (-30.0, 30.0),
) -> tuple[float, float, np.ndarray]:
    """Run ``n_bootstrap`` :func:`bootstrap_kl` calls; return (mean, std, samples)."""
    rng = np.random.default_rng(seed)
    samples = np.fromiter(
        (
            bootstrap_kl(
                samples_a, samples_b, rng=rng,
                n_bins=n_bins, value_range=value_range,
            )
            for _ in range(n_bootstrap)
        ),
        dtype=np.float64, count=n_bootstrap,
    )
    return float(samples.mean()), float(samples.std(ddof=1)), samples


# ----------------- Run orchestrator ---------------------------------


def run_encoder_free_training(
    cfg: EncoderFreeTrainingConfig,
    input_kind: Literal["audio", "no_input"],
) -> EncoderFreeTrainingResult:
    """Drive the substrate for ``cfg.n_ticks_train`` ticks.

    ``input_kind="audio"`` injects the R-7 corpus one quantum per
    sample via the encoder-free path. ``input_kind="no_input"`` skips
    the injector entirely (matched-wallclock no-input control). Other
    state — grid, RNG seed, sub-configs, ticks-per-run — is identical
    across the two paths.

    Babble is then generated by stepping the substrate ``babble_n_samples
    // samples_per_tick`` additional ticks with no audio input, routing
    bridge-flux deltas through the F2 synthesis bank, and reading
    impulse-driven output samples each tick. MFCC per-frame is computed
    over the resulting babble waveform.
    """
    if input_kind not in ("audio", "no_input"):
        raise ValueError(f"unknown input_kind: {input_kind!r}")

    sr = cfg.sample_rate_hz
    spt = cfg.samples_per_tick
    n_audio_total = cfg.n_ticks_train * spt

    if input_kind == "audio":
        waveform = make_corpus_waveform(cfg, n_samples=n_audio_total)
    else:
        # Matched-wallclock no-input control: zero waveform; injector
        # consumes the same code path (same per-sample loop) so per-tick
        # cost is comparable. The encoder-free injector still does NOT
        # run for no_input — see the tick loop below.
        waveform = np.zeros(n_audio_total, dtype=np.float64)
    waveform_rms = float(np.sqrt(np.mean(waveform * waveform)))

    # Substrate-side RNG: same seed for both input kinds (matched control).
    seed = cfg.seed_train if input_kind == "audio" else cfg.seed_control
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

    n_quanta_alive_peak = 0
    t0 = time.perf_counter()
    for tick_idx in range(cfg.n_ticks_train):
        if input_kind == "audio":
            chunk = waveform[tick_idx * spt:(tick_idx + 1) * spt]
            inject_raw_audio_chunk(
                quanta, grid, chunk,
                base_sample_index=tick_idx * spt,
                sample_rate_hz=sr, rng=rng,
                position_hash_seed=cfg.position_hash_seed,
            )
        exported, _binding_heat, _decay_heat = dynamics.tick(
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
        n_alive = int(quanta.alive.sum())
        if n_alive > n_quanta_alive_peak:
            n_quanta_alive_peak = n_alive
    wallclock_train_s = time.perf_counter() - t0

    # ---- Babble generation (synthesis as passive probe) ----
    bank = Synthesizer(cfg.synth_cfg)
    n_babble_ticks = max(1, cfg.babble_n_samples // spt)
    babble_chunks = []
    prev_flux = np.zeros(bridges.max_bridges, dtype=np.float64)
    if hasattr(bridges, "flux"):
        prev_flux[:] = bridges.flux.astype(np.float64)
    for _ in range(n_babble_ticks):
        exported, _bh, _dh = dynamics.tick(
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
            tick_index=cfg.n_ticks_train,
        )
        current_flux = (
            bridges.flux.astype(np.float64)
            if hasattr(bridges, "flux")
            else np.zeros(bridges.max_bridges, dtype=np.float64)
        )
        route_node_firings(
            nodes, bridges, prev_flux, current_flux, bank, cfg.synth_cfg,
        )
        samples = read_output_samples(bank, spt)
        babble_chunks.append(samples)
        prev_flux = current_flux
    babble = np.concatenate(babble_chunks)[:cfg.babble_n_samples]

    mfcc_per_frame = compute_mfcc_per_frame(
        babble, cfg.sample_rate_hz,
        n_mfcc=cfg.mfcc_n_coeff, n_mels=cfg.mfcc_n_mels,
        frame_ms=cfg.mfcc_frame_ms, hop_ms=cfg.mfcc_hop_ms,
    )
    mfcc_hist = mfcc_histogram_from_per_frame(
        mfcc_per_frame,
        n_bins=cfg.mfcc_hist_n_bins,
        value_range=cfg.mfcc_hist_range,
    )

    return EncoderFreeTrainingResult(
        cfg=cfg,
        input_kind=input_kind,
        n_ticks_run=cfg.n_ticks_train,
        wallclock_s=wallclock_train_s,
        babble=babble,
        mfcc_per_frame=mfcc_per_frame,
        mfcc_histogram=mfcc_hist,
        n_bridges_alive=int(bridges.alive.sum()) if hasattr(bridges, "alive") else 0,
        n_nodes_alive=int(nodes.alive.sum()) if hasattr(nodes, "alive") else 0,
        n_quanta_alive_final=int(quanta.alive.sum()),
        n_quanta_alive_peak=n_quanta_alive_peak,
        waveform_rms=waveform_rms,
    )

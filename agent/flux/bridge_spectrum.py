"""R-13 bridge-weight spectrum — substrate-internal observable.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-13``. The cochlea-baseline
and encoder-free R-LR-1 runs both produced thousands of alive bridges, yet
the synthesis-driven babble was statistically indistinguishable between
trained and no-input substrates (R-LR-1: KL ≈ 1e-6). This module bypasses
the synthesis layer entirely and reads the substrate's own internal
topology: the joint (freq, weight) histogram across alive bridges.

Two distributions trained on differently-structured audio should differ;
two trained on the same audio should not. Acceptance: KL > 0.1 between
50k-tick English-audio and white-noise-trained substrates.

See ``docs/superpowers/plans/2026-05-19-flux-encoder-free-iter2.md`` for
the locked thresholds.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from world.flux.bridges import Bridges
from world.flux.structures import Nodes


# Locked binning for R-13. The (8, 16) shape gives 128 cells; the freq
# range matches the cochlea band the corpus is normalised to (50 Hz to
# 8 kHz); the weight range (0, 5) brackets bridge_w0=1.0 with a 5x ceiling
# adequate for the F1b plasticity rule's per-tick growth/decay rates.
DEFAULT_N_FREQ_BINS = 8
DEFAULT_N_WEIGHT_BINS = 16
DEFAULT_FREQ_RANGE_LOG_HZ: tuple[float, float] = (
    float(np.log(50.0)),
    float(np.log(8000.0)),
)
DEFAULT_WEIGHT_RANGE: tuple[float, float] = (0.0, 5.0)


def bridge_weight_spectrum(
    nodes: Nodes,
    bridges: Bridges,
    n_freq_bins: int = DEFAULT_N_FREQ_BINS,
    n_weight_bins: int = DEFAULT_N_WEIGHT_BINS,
    freq_range_log_hz: tuple[float, float] = DEFAULT_FREQ_RANGE_LOG_HZ,
    weight_range: tuple[float, float] = DEFAULT_WEIGHT_RANGE,
    endpoint: str = "mean",
) -> np.ndarray:
    """Return a normalised 2D ``(freq, weight)`` histogram of alive bridges.

    The frequency axis takes the bridge endpoint freq from ``nodes.freq``
    (log-Hz, per F2 cochlea convention; encoder-free injection puts all
    quanta at ``log(SR/2)`` so this axis collapses to one populated bin
    when the input is encoder-free). The weight axis is the bridge's
    scalar weight from ``bridges.weight``.

    Args:
        nodes: live Nodes container (SoA); ``nodes.freq`` is in log-Hz.
        bridges: live Bridges container (SoA).
        n_freq_bins: number of frequency bins (linear in log-Hz).
        n_weight_bins: number of weight bins (linear in raw weight).
        freq_range_log_hz: (low, high) edges in log-Hz units.
        weight_range: (low, high) edges in raw weight units.
        endpoint: one of {"src", "dst", "mean"} — which endpoint's freq
            to use per bridge. Default "mean" treats undirected.

    Returns:
        Array of shape ``(n_freq_bins, n_weight_bins)`` summing to 1.0
        when any bridge is alive, else a zero array of the same shape.
        Never NaN.
    """
    if endpoint not in ("src", "dst", "mean"):
        raise ValueError(
            f"endpoint must be one of 'src','dst','mean'; got {endpoint!r}"
        )

    alive_mask = bridges.alive
    if not bool(alive_mask.any()):
        return np.zeros((n_freq_bins, n_weight_bins), dtype=np.float64)

    alive_idx = np.where(alive_mask)[0]
    src = bridges.src[alive_idx]
    dst = bridges.dst[alive_idx]
    weights = bridges.weight[alive_idx]

    if endpoint == "src":
        freqs = nodes.freq[src]
    elif endpoint == "dst":
        freqs = nodes.freq[dst]
    else:
        freqs = 0.5 * (nodes.freq[src] + nodes.freq[dst])

    hist, _, _ = np.histogram2d(
        freqs.astype(np.float64),
        weights.astype(np.float64),
        bins=[n_freq_bins, n_weight_bins],
        range=[list(freq_range_log_hz), list(weight_range)],
    )
    total = float(hist.sum())
    if total <= 0.0:
        return np.zeros((n_freq_bins, n_weight_bins), dtype=np.float64)
    return (hist.astype(np.float64) / total).reshape(
        (n_freq_bins, n_weight_bins)
    )


def bridge_spectrum_kl(
    spec_a: np.ndarray, spec_b: np.ndarray, laplace_alpha: float = 1.0,
) -> float:
    """Asymmetric ``KL(spec_a || spec_b)`` with Laplace-add smoothing.

    Each input is a 2D probability histogram (or any non-negative array
    with equal sum) and may have empty cells. To keep KL finite we add
    ``laplace_alpha`` to every cell before renormalising, matching the
    smoothing used in R-11's MFCC-histogram KL (encoder_free_training).

    Args:
        spec_a, spec_b: probability arrays of identical shape.
        laplace_alpha: smoothing constant added to each cell pre-norm.

    Returns:
        ``KL(P_a || P_b)`` in nats. Always finite.
    """
    a = np.asarray(spec_a, dtype=np.float64)
    b = np.asarray(spec_b, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(
            f"spectra shape mismatch: {a.shape} != {b.shape}"
        )
    flat_a = a.ravel() + laplace_alpha
    flat_b = b.ravel() + laplace_alpha
    flat_a = flat_a / flat_a.sum()
    flat_b = flat_b / flat_b.sum()
    return float(np.sum(flat_a * (np.log(flat_a) - np.log(flat_b))))


def n_populated_bins(spectrum: np.ndarray, eps: float = 0.0) -> int:
    """Count cells with probability mass strictly greater than ``eps``."""
    return int(np.count_nonzero(np.asarray(spectrum) > eps))


# ---------- R-13 test substrate runner ------------------------------


def run_short_encoder_free_substrate(
    waveform: np.ndarray,
    n_ticks: int = 50_000,
    sample_rate_hz: int = 16_000,
    samples_per_tick: int = 16,
    grid_dims: tuple[int, int, int] = (30, 15, 8),
    seed: int = 4242,
) -> tuple[Nodes, Bridges]:
    """Drive an encoder-free substrate for ``n_ticks`` and return (nodes, bridges).

    Same F1b/F1c-locked sub-configs as R-11's ``EncoderFreeTrainingConfig``
    so the dynamics are identical; the grid is smaller (30x15x8 vs 80x40x10)
    to keep the 50k-tick run inside the postflight 30-min pytest cap on
    this Mac (~165 ticks/s vs ~36 ticks/s). The bridge spectrum is a
    substrate-internal observable so the geometry deviation does not
    invalidate the comparison: both runs in the test use the same grid.

    Args:
        waveform: 1-D audio buffer of length ``n_ticks * samples_per_tick``
            (extra samples ignored; shorter inputs zero-pad).
        n_ticks: substrate tick count.
        sample_rate_hz: audio sample rate (R-10-locked at 16 kHz).
        samples_per_tick: audio samples per substrate tick.
        grid_dims: grid shape.
        seed: RNG seed for substrate + injector.

    Returns:
        (Nodes, Bridges) — both containers at their final state.
    """
    from agent.flux.audio_raw import inject_raw_audio_chunk
    from world.flux import dynamics
    from world.flux.audit import EnergyAuditor
    from world.flux.binding import BindingConfig
    from world.flux.decay import DecayConfig
    from world.flux.grid import Grid
    from world.flux.plasticity import PlasticityConfig
    from world.flux.quantum import Quanta
    from world.flux.thermal import ThermalConfig

    rng = np.random.default_rng(seed)
    grid = Grid(dims=grid_dims, voxel_size=1.0, T_smoothing=0.1)
    quanta = Quanta(max_quanta=100_000)
    nodes = Nodes(max_nodes=5_000)
    bridges = Bridges(max_bridges=50_000)
    binding_cfg = BindingConfig(
        alpha=4.0, beta=4.0, T_crit=2.0, eta=0.1, r=1.5,
        coherence_eps=1.0, r_bridge=2.0, bridge_w0=1.0,
    )
    decay_cfg = DecayConfig(gamma=500.0, T_decay_crit=0.035)
    plasticity_cfg = PlasticityConfig(
        gamma=0.1, lam=0.1, flux_min=1.0, w_min=0.05, r_flux=0.75,
    )
    thermal_cfg = ThermalConfig(
        buoyancy_g=2.0, damping_mu=0.5, T_ref=0.0,
        T_hot_floor=5.0, T_cold_ceiling=0.0, pressure_coeff=1.0,
    )
    auditor = EnergyAuditor(
        quanta=quanta, nodes=nodes, bridges=bridges, tol=1e-9,
    )
    auditor.record_initial()

    n_audio_total = n_ticks * samples_per_tick
    wave = np.asarray(waveform, dtype=np.float64).ravel()
    if wave.size < n_audio_total:
        pad = np.zeros(n_audio_total, dtype=np.float64)
        pad[: wave.size] = wave
        wave = pad
    else:
        wave = wave[:n_audio_total]

    for k in range(n_ticks):
        chunk = wave[k * samples_per_tick : (k + 1) * samples_per_tick]
        inject_raw_audio_chunk(
            quanta, grid, chunk,
            base_sample_index=k * samples_per_tick,
            sample_rate_hz=sample_rate_hz,
            rng=rng,
        )
        dynamics.tick(
            quanta=quanta,
            grid=grid,
            dt=0.1,
            injector=None,
            nodes=nodes,
            binding_cfg=binding_cfg,
            decay_cfg=decay_cfg,
            bridges=bridges,
            plasticity_cfg=plasticity_cfg,
            thermal_cfg=thermal_cfg,
            rng=rng,
            tick_index=k,
        )
    return nodes, bridges


def load_english_stage1_segment(
    n_samples: int,
    manifest_path: Path | None = None,
    target_rms: float = 0.25,
) -> np.ndarray | None:
    """Read the first ``n_samples`` of R-7 corpus Stage 1, RMS-normalised.

    Returns ``None`` if the manifest or any required file is missing —
    callers can skip the test or fall back.
    """
    from agent.flux.audio_in import read_wav_mono_16k

    if manifest_path is None:
        manifest_path = Path.home() / ".eqmod/training/EN/manifest.json"
    if not manifest_path.is_file():
        return None
    import json
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    stage = manifest.get("stages", {}).get("stage1")
    if not stage:
        return None
    chunks = []
    total = 0
    for entry in stage["files"]:
        p = Path(entry["path"])
        if not p.is_file():
            return None
        samples = read_wav_mono_16k(p, target_sr_hz=16_000)
        chunks.append(samples)
        total += samples.size
        if total >= n_samples:
            break
    if not chunks:
        return None
    audio = np.concatenate(chunks).astype(np.float64)[:n_samples]
    rms = float(np.sqrt(np.mean(audio * audio)))
    if rms > 0.0:
        audio = audio * (target_rms / rms)
    return audio


def make_white_noise(n_samples: int, target_rms: float, seed: int) -> np.ndarray:
    """Gaussian white noise scaled to the given RMS."""
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n_samples).astype(np.float64)
    rms = float(np.sqrt(np.mean(x * x)))
    if rms > 0.0:
        x = x * (target_rms / rms)
    return x

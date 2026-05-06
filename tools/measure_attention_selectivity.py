"""Measure attentional selectivity at a candidate carrier frequency.

Given a firing matrix and a carrier frequency, identify which neurons resonate
with the carrier and quantify the network's selectivity index + phase coherence.

Usage:
    python tools/measure_attention_selectivity.py \\
        --firing-json firing.json \\
        --carrier-frequency F \\
        [--resonance-threshold 0.3] \\
        [--format text|json]

`firing.json` schema (compatible with synthesize_carrier_firing output):
{
    "firing_matrix": [[...], ...],
    "times": [...]
}

See docs/superpowers/specs/2026-05-06-phase-7-attention.md.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def _phase_grid_search(firing_history: np.ndarray, times: np.ndarray,
                       carrier_frequency: float, n_phases: int = 16) -> tuple[float, float]:
    """Find the phase offset that maximises correlation between firing and carrier.

    Returns (best_phase, best_correlation).
    """
    if firing_history.std() < 1e-9:
        return 0.0, 0.0
    best_corr = -np.inf
    best_phase = 0.0
    for k in range(n_phases):
        phase = (k / n_phases) * 2.0 * np.pi
        carrier = np.sin(2.0 * np.pi * carrier_frequency * times + phase)
        if carrier.std() < 1e-9:
            continue
        corr = float(np.corrcoef(firing_history, carrier)[0, 1])
        if not np.isfinite(corr):
            corr = 0.0
        if corr > best_corr:
            best_corr = corr
            best_phase = phase
    return best_phase, max(best_corr, 0.0)


def measure_selectivity(
    firing_matrix: np.ndarray,
    times: np.ndarray,
    carrier_frequency: float,
    resonance_threshold: float = 0.3,
    n_phase_steps: int = 16,
) -> dict:
    """Compute resonance scores, selectivity, and phase coherence."""
    fm = np.asarray(firing_matrix, dtype=np.float64)
    times = np.asarray(times, dtype=np.float64)
    if fm.ndim != 2:
        raise ValueError("firing_matrix must be 2D (T × N)")
    T, N = fm.shape
    if T != len(times):
        raise ValueError("times length must match firing_matrix rows")

    resonance_scores = np.zeros(N, dtype=np.float64)
    phase_offsets = np.zeros(N, dtype=np.float64)
    for n in range(N):
        phi, r = _phase_grid_search(fm[:, n], times, carrier_frequency, n_phase_steps)
        resonance_scores[n] = r
        phase_offsets[n] = phi

    abs_scores = np.abs(resonance_scores)
    mean_abs = float(np.mean(abs_scores)) if abs_scores.size else 0.0
    if mean_abs < 1e-9:
        selectivity_index = 0.0
    else:
        selectivity_index = float(np.std(abs_scores) / mean_abs)

    resonating_indices = [
        int(n) for n in range(N) if resonance_scores[n] > resonance_threshold
    ]

    # Phase coherence among resonating subset: 1 - circular variance
    if len(resonating_indices) >= 2:
        phases = phase_offsets[resonating_indices]
        mean_vec_x = float(np.mean(np.cos(phases)))
        mean_vec_y = float(np.mean(np.sin(phases)))
        r_bar = float(np.sqrt(mean_vec_x ** 2 + mean_vec_y ** 2))
        phase_coherence = r_bar  # ranges [0, 1]
    else:
        phase_coherence = 1.0 if len(resonating_indices) == 1 else 0.0

    return {
        "resonance_scores": resonance_scores.tolist(),
        "resonating_indices": resonating_indices,
        "selectivity_index": selectivity_index,
        "phase_offsets": phase_offsets.tolist(),
        "phase_coherence": phase_coherence,
        "carrier_frequency": carrier_frequency,
    }


def format_text(result: dict) -> str:
    lines = [
        f"# carrier frequency: {result['carrier_frequency']:.3f}",
        f"# selectivity index: {result['selectivity_index']:.3f}",
        f"# resonating neurons: {result['resonating_indices']}",
        f"# phase coherence (resonating subset): {result['phase_coherence']:.3f}",
        "# per-neuron resonance scores:",
    ]
    for i, r in enumerate(result["resonance_scores"]):
        marker = "✔" if i in result["resonating_indices"] else " "
        lines.append(f"  {marker} neuron {i:2d}: r = {r:+.3f}, phase = {result['phase_offsets'][i]:+.3f}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/measure_attention_selectivity.py")
    parser.add_argument("--firing-json", type=Path, required=True)
    parser.add_argument("--carrier-frequency", type=float, required=True)
    parser.add_argument("--resonance-threshold", type=float, default=0.3)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)
    data = json.loads(args.firing_json.read_text())
    fm = np.asarray(data["firing_matrix"], dtype=np.float64)
    times = np.asarray(data["times"], dtype=np.float64)
    result = measure_selectivity(fm, times, args.carrier_frequency,
                                   resonance_threshold=args.resonance_threshold)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

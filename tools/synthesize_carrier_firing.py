"""Generate a synthetic firing matrix where some neurons fire on a carrier rhythm.

Used to validate measure_attention_selectivity: given known resonating
indices and phase offsets, the measurement tool should recover them.

Usage:
    python tools/synthesize_carrier_firing.py --output firing.json \\
        --n-neurons N --n-snapshots T --dt DT \\
        --carrier-frequency F \\
        --resonating-indices i,j,k

See docs/superpowers/specs/2026-05-06-phase-7-attention.md.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def synthesize_carrier_firing(
    n_neurons: int,
    n_snapshots: int,
    dt: float,
    carrier_frequency: float,
    resonating_indices: list[int],
    phase_offsets: list[float] = None,
    firing_probability_resonating: float = 0.6,
    firing_probability_silent: float = 0.05,
    rng_seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Build a T×N firing matrix with specified resonators on the carrier rhythm.

    Returns (firing_matrix, times).
    """
    rng = np.random.default_rng(rng_seed)
    times = np.arange(n_snapshots) * dt

    if phase_offsets is None:
        phase_offsets = [0.0] * len(resonating_indices)
    if len(phase_offsets) != len(resonating_indices):
        raise ValueError("phase_offsets must match length of resonating_indices")

    fm = np.zeros((n_snapshots, n_neurons), dtype=np.int8)
    resonating_set = set(resonating_indices)

    for n in range(n_neurons):
        if n in resonating_set:
            phase = phase_offsets[resonating_indices.index(n)]
            # Probability of firing at time t is high when sin(2πft + phase) > 0
            for t_idx, t in enumerate(times):
                rhythm = np.sin(2.0 * np.pi * carrier_frequency * t + phase)
                # Map rhythm in [-1, 1] to firing probability in [0, fp_resonating]
                p = max(0.0, rhythm) * firing_probability_resonating
                if rng.random() < p:
                    fm[t_idx, n] = 1
        else:
            # Silent / baseline neuron
            for t_idx in range(n_snapshots):
                if rng.random() < firing_probability_silent:
                    fm[t_idx, n] = 1

    return fm, times


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/synthesize_carrier_firing.py")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--n-neurons", type=int, default=8)
    parser.add_argument("--n-snapshots", type=int, default=100)
    parser.add_argument("--dt", type=float, default=0.1)
    parser.add_argument("--carrier-frequency", type=float, default=2.0)
    parser.add_argument("--resonating-indices", type=str, required=True,
                        help="comma-separated list of indices that resonate")
    parser.add_argument("--phase-offsets", type=str, default=None,
                        help="comma-separated phase offsets in radians (defaults to 0 for each)")
    parser.add_argument("--firing-probability-resonating", type=float, default=0.6)
    parser.add_argument("--firing-probability-silent", type=float, default=0.05)
    parser.add_argument("--rng-seed", type=int, default=42)
    args = parser.parse_args(argv)

    indices = [int(s) for s in args.resonating_indices.split(",")]
    phases = (
        [float(s) for s in args.phase_offsets.split(",")]
        if args.phase_offsets is not None
        else None
    )

    fm, times = synthesize_carrier_firing(
        n_neurons=args.n_neurons,
        n_snapshots=args.n_snapshots,
        dt=args.dt,
        carrier_frequency=args.carrier_frequency,
        resonating_indices=indices,
        phase_offsets=phases,
        firing_probability_resonating=args.firing_probability_resonating,
        firing_probability_silent=args.firing_probability_silent,
        rng_seed=args.rng_seed,
    )
    args.output.write_text(json.dumps({
        "firing_matrix": fm.tolist(),
        "times": times.tolist(),
        "carrier_frequency": args.carrier_frequency,
        "resonating_indices": indices,
        "phase_offsets": phases or [0.0] * len(indices),
    }, indent=2))
    print(f"# wrote {args.output}")
    print(f"# shape: {fm.shape}, resonating: {indices}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

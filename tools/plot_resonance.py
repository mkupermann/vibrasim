"""Diagnostic plot: node frequencies over time during resonance cascade.

Shows how Kuramoto synchronization drives frequencies into binding windows.
Minimalist: frequency (y) vs time (x), colored by level. No 3D — the
right abstraction for the right question.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def run_and_record(cfg, sim_seconds=15.0, sample_interval=1.0):
    """Run simulation, record node frequencies at intervals."""
    # JIT warmup
    w = World(WorldConfig(n_initial_vibrations=10, rng_seed=1))
    for _ in range(3):
        tick(w, w.config.dt)
    del w

    world = World(cfg)
    dt = cfg.dt
    steps = int(sim_seconds / dt)
    sample_every = max(1, int(sample_interval / dt))

    snapshots = []
    for step in range(steps):
        tick(world, dt)
        if step % sample_every == sample_every - 1:
            K = world.k_count
            alive = world.k_alive[:K]
            t = (step + 1) * dt
            for i in range(K):
                if alive[i]:
                    snapshots.append({
                        't': t,
                        'freq': float(world.k_freq[i]),
                        'level': int(world.k_level[i]),
                        'node_id': i,
                    })
    return snapshots


def plot(snapshots, outpath):
    """Frequency vs time, colored by level."""
    if not snapshots:
        print("No data to plot")
        return

    colors = {1: '#888888', 2: '#4488cc', 3: '#cc8844', 4: '#cc4444',
              5: '#44cc44', 6: '#8844cc'}

    fig, ax = plt.subplots(figsize=(12, 6))

    for level in sorted(set(s['level'] for s in snapshots)):
        pts = [s for s in snapshots if s['level'] == level]
        ts = [p['t'] for p in pts]
        fs = [p['freq'] for p in pts]
        c = colors.get(level, '#000000')
        label = {1: 'electron', 2: 'pair', 3: 'triad', 4: 'atom',
                 5: 'molecule'}.get(level, f'L{level}')
        ax.scatter(ts, fs, c=c, s=3, alpha=0.5, label=label)

    ax.set_xlabel('Simulation time (s)')
    ax.set_ylabel('Node frequency (Hz)')
    ax.set_yscale('log')
    ax.legend(loc='upper right', markerscale=4)
    ax.set_title('Resonance Cascade: Frequency Synchronization')
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    print(f"Saved: {outpath}")
    plt.close(fig)


if __name__ == "__main__":
    cfg = WorldConfig(
        n_initial_vibrations=150, box_size=(30.0, 30.0, 30.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.02,
        mol_fusion_enabled=True, resonance_coupling=10.0,
        pair_decay_time=15.0, triad_decay_time=120.0, dt=0.1,
        n_nodes_max=2048, n_vibrations_max=1024, vibration_soft_cap=200,
        repulsion_k=0.0, lambda_gen=0.0003,
        neuron_dynamics_enabled=False, stdp_enabled=False, rng_seed=42,
    )
    print("Recording resonance cascade...")
    snapshots = run_and_record(cfg, sim_seconds=12.0, sample_interval=0.5)
    print(f"{len(snapshots)} data points")
    outpath = Path("docs/logbook/resonance_cascade.png")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plot(snapshots, outpath)

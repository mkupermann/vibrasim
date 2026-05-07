"""End-to-end integration tests for STDP (Plan B). P1 is necessary,
P2 and P3 are stretch (added in Task 11, marked slow)."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import apply_stdp, molecules_in_tube


def _stdp_e2e_world():
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=16, n_nodes_max=64,
        box_size=(100.0, 100.0, 100.0),
        stdp_enabled=True,
        tau_LTP=0.020, tau_LTD=0.020,
        delta_LTP=1.0, delta_LTD=0.5,
        r_bridge=5.0,
    )
    w = World(cfg)
    # Atom A at (50,50,50), atom B at (70,50,50)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = 4
    w.k_alive[0] = True
    w.k_pos[1] = [70.0, 50.0, 50.0]
    w.k_level[1] = 4
    w.k_alive[1] = True
    # Eight bridge molecules, evenly spaced along the segment, all on-line
    for i in range(8):
        x = 52.0 + 2.0 * i  # x = 52, 54, ..., 66
        w.k_pos[2 + i] = [x, 50.0, 50.0]
        w.k_level[2 + i] = 5
        w.k_alive[2 + i] = True
        w.k_strength[2 + i] = 1.0
    w.k_count = 10
    return w


def test_P1_causal_pair_training():
    """100 paired-pulse trials, A fires at t=k*0.5, B fires at t=k*0.5+0.010 for k=0..99.
    After training:
        - bridge molecules in A→B tube have strength ≥ 5
        - bridge orientation · (B-A)/|B-A| > 0.8 (i.e. mean orientation aligned)
    """
    w = _stdp_e2e_world()
    n_trials = 100

    for k in range(n_trials):
        t_A = k * 0.5
        t_B = k * 0.5 + 0.010
        w.firing_events.extend([(t_A, 0), (t_B, 1)])
        w.t = t_B + 0.001
        apply_stdp(w)
        # Trim firing log to the most recent pair to keep pair count tractable
        # (tau_LTP = 0.020 so older events don't contribute anyway)
        w.firing_events = w.firing_events[-2:]

    # Bridge strength check
    bridge_strengths = w.k_strength[2:10]
    assert (bridge_strengths >= 5.0).all(), (
        f"P1: not all bridges reached strength ≥ 5; strengths = {bridge_strengths.tolist()}"
    )

    # Orientation alignment check
    box = np.asarray(w.config.box_size, dtype=np.float64)
    AB = np.array([70.0, 50.0, 50.0]) - np.array([50.0, 50.0, 50.0])
    AB -= box * np.round(AB / box)
    AB_unit = AB / np.linalg.norm(AB)
    bridge_orientations = w.k_orientation[2:10]
    alignments = bridge_orientations @ AB_unit  # dot products
    assert (alignments > 0.8).all(), (
        f"P1: not all bridge orientations aligned with A→B; alignments = {alignments.tolist()}"
    )


@pytest.mark.slow
def test_P2_stdp_timing_curve():
    """Vary inter-spike Δt across [-50ms, +50ms], measure ΔStrength of
    bridge molecules over 20 trials per Δt. The curve must:
    - peak at Δt = 5-10 ms with mean ΔStrength ≥ 0.5
    - fall to near-zero at Δt = ±50 ms (|mean| < 0.05)
    - reach a negative minimum at Δt = -5 to -10 ms with mean ΔStrength ≤ -0.20

    Each Δt probes a fresh world pre-trained 10 LTP cycles A→B to establish
    orientation, so that negative Δt triggers genuine LTD rather than LTP
    in an unoriented bridge.
    """
    deltas_ms = np.array([-50, -25, -10, -5, 0, 5, 10, 25, 50])
    n_trials_per_dt = 20
    measurements = []

    for dt_ms in deltas_ms:
        w = _stdp_e2e_world()
        # Pre-train: 10 strong A→B pairs at Δt=+10ms to establish orientation
        for _ in range(10):
            w.firing_events.extend([(0.0, 0), (0.010, 1)])
            w.t = 0.020
            apply_stdp(w)
            w.firing_events = []
        # Record baseline strength after pre-training
        baseline = float(w.k_strength[2:10].mean())
        # Test phase: 20 trials at the candidate Δt
        for k in range(n_trials_per_dt):
            if dt_ms >= 0:
                w.firing_events.extend([(0.0, 0), (dt_ms / 1000.0, 1)])
            else:
                w.firing_events.extend([(0.0, 1), (-dt_ms / 1000.0, 0)])
            w.t = abs(dt_ms) / 1000.0 + 0.001
            apply_stdp(w)
            w.firing_events = []
        # Mean strength change relative to post-pre-training baseline
        mean_delta = float(w.k_strength[2:10].mean()) - baseline
        measurements.append((int(dt_ms), mean_delta))

    # Build a dict for easy assertion
    curve = dict(measurements)
    print(f"P2 timing curve: {curve}")

    # Peak at Δt = 5-10 ms
    peak_pos = max(curve[5], curve[10])
    assert peak_pos >= 0.5, f"P2: positive peak {peak_pos:.3f} below expected"

    # Near zero at ±50ms (below 0.05 absolute)
    assert abs(curve[50]) < 0.05 and abs(curve[-50]) < 0.05, (
        f"P2: tails not near zero — Δt=50 → {curve[50]:.3f}, Δt=-50 → {curve[-50]:.3f}"
    )

    # Negative trough at Δt = -5 to -10 ms
    trough_neg = min(curve[-5], curve[-10])
    assert trough_neg <= -0.20, f"P2: LTD trough {trough_neg:.3f} not negative enough"


@pytest.mark.slow
def test_P3_plasticity_drives_prediction():
    """Train: 50 paired-pulse trials A→B at 10 ms lag using the full
    substrate (tick()). Test: stimulate A only.
    B's firing rate during test phase must be ≥ 2× B's baseline firing
    rate before training.

    This requires the FULL substrate loop (neuron_dynamics + apply_stdp +
    synaptic_transmission), so we use tick() rather than apply_stdp directly.
    """
    from world.physics import tick

    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=512, n_nodes_max=4096,
        box_size=(100.0, 100.0, 100.0),
        rng_seed=42,
        # Substrate dynamics
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        # Plan A (mol_fusion disabled: don't let the substrate grow new bridges
        # during the trial; we seed them explicitly and track STDP-driven changes)
        lambda_dec_mol=0.001, r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=False,
        # Plan B (delta_LTP=4.0: aggressive enough to push strength over threshold
        # within 50 training trials)
        stdp_enabled=True,
        tau_LTP=0.020, delta_LTP=4.0, delta_LTD=0.5,
        r_bridge=8.0,
        synaptic_transmission_strength=1.0,
        synaptic_transmission_threshold=10.0,
    )
    w = World(cfg)
    # Atom A at (40,50,50), atom B at (60,50,50)
    w.k_pos[0] = [40.0, 50.0, 50.0]
    w.k_freq[0] = 30000.0
    w.k_level[0] = 4; w.k_alive[0] = True
    w.k_pos[1] = [60.0, 50.0, 50.0]
    w.k_freq[1] = 30000.0
    w.k_level[1] = 4; w.k_alive[1] = True
    # Pre-existing bridge molecules between A and B (seed so test focuses on plasticity)
    for i in range(8):
        x = 42.0 + 2.0 * i
        w.k_pos[2 + i] = [x, 50.0, 50.0]
        w.k_freq[2 + i] = 60000.0
        w.k_level[2 + i] = 5; w.k_alive[2 + i] = True
        w.k_strength[2 + i] = 9.0
    w.k_count = 10

    def burst_at(pos, n=6, freq=10000.0):
        free_idx = np.where(~w.s_alive)[0][:n]
        for i in free_idx:
            w.s_pos[i] = np.asarray(pos) + w.rng.uniform(-0.5, 0.5, 3)
            w.s_vel[i] = 0.0
            w.s_freq[i] = freq + w.rng.uniform(-100, 100)
            w.s_pol[i] = bool(w.rng.random() < 0.5)
            w.s_alive[i] = True
        if len(free_idx):
            w.n_alive = max(w.n_alive, int(free_idx.max()) + 1)

    # Baseline: 2 simulated seconds, stimulate A only, count B firings
    baseline_start_idx = len(w.firing_events)
    for k in range(int(2.0 / cfg.dt)):
        if (k + 1) % 30 == 0:
            burst_at([40.0, 50.0, 50.0])
        tick(w, cfg.dt)
    baseline_B_firings = sum(1 for t, ai in w.firing_events[baseline_start_idx:] if ai == 1)

    # Training: 50 trials, A then B with 10 ms lag (0.1s rest between trials)
    for trial in range(50):
        burst_at([40.0, 50.0, 50.0])
        for _ in range(int(0.010 / cfg.dt)):
            tick(w, cfg.dt)
        burst_at([60.0, 50.0, 50.0])
        for _ in range(int(0.1 / cfg.dt)):
            tick(w, cfg.dt)

    # Test: 2 simulated seconds, stimulate A only
    test_start_idx = len(w.firing_events)
    for k in range(int(2.0 / cfg.dt)):
        if (k + 1) % 30 == 0:
            burst_at([40.0, 50.0, 50.0])
        tick(w, cfg.dt)
    test_B_firings = sum(1 for t, ai in w.firing_events[test_start_idx:] if ai == 1)

    print(f"P3: baseline B firings = {baseline_B_firings}, "
          f"test B firings = {test_B_firings}")
    assert test_B_firings >= 2 * max(baseline_B_firings, 1), (
        f"P3: test B firings {test_B_firings} not ≥ 2× baseline {baseline_B_firings}"
    )

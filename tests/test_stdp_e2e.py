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
    """Plasticity-driven prediction: train A→B 50× with 10ms lag using the
    full substrate. After training, stimulating A should drive B's firing
    rate above baseline.

    Geometry: box_x=160, A at (10,25,25), B at (90,25,25). Both the direct
    distance (80) and the periodic-image distance (160-80=80) exceed the
    75-unit emission reach (emit_speed=15 × 5 sec = 75). The acoustic chain
    is broken in both periodic directions.

    Ambient vibration generation disabled (lambda_gen=lambda_dec=0) so
    background noise cannot fire B without synaptic transmission.

    One bridge at (82,25,25), level-5, strength=4.0 (below threshold=5.0),
    pre-oriented (1,0,0). With r_bridge=8, synaptic search centre at
    (90,25,25) — exactly at B. Below threshold → no transmission at baseline.

    After 50 paired-pulse trials: bridge strength climbs above threshold;
    synaptic_transmission deposits charge into B from A's emitted vibrations
    crossing the bridge. Baseline ~ 0; test should be ≥ 5.

    Threshold: with baseline engineered to 0 (acoustic chain broken, ambient
    gen off), the substantive claim is that trained transmission deposits
    enough charge to drive B's firing at all. We assert baseline_B_firings == 0
    explicitly to catch geometry/config regressions, then require
    test_B_firings >= 5 as the absolute floor.
    """
    from world.physics import tick

    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=512, n_nodes_max=2048,
        # box_x=160 so both direct (80) and periodic-image (80) distances from
        # A=(10) to B=(90) exceed the 75-unit emission reach at emit_speed=15
        # in 5 sim-sec. The acoustic chain is broken in BOTH periodic directions.
        box_size=(160.0, 50.0, 50.0),
        rng_seed=42,
        repulsion_cell_size=160.0,
        repulsion_k=0.0,        # disable repulsion (hand-placed atoms have no freq)
        # Disable ambient vibration generation so background noise can't fire B.
        lambda_gen=0.0, lambda_dec=0.0,
        # Substrate dynamics
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        # Plan A
        lambda_dec_mol=0.001, r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=False,
        # Plan B
        stdp_enabled=True,
        tau_LTP=0.020, delta_LTP=2.0, delta_LTD=0.5,
        r_bridge=8.0,
        synaptic_transmission_strength=1.0,
        synaptic_transmission_threshold=5.0,
    )
    w = World(cfg)
    # Atom A at (10, 25, 25)
    w.k_pos[0] = [10.0, 25.0, 25.0]
    w.k_level[0] = 4; w.k_alive[0] = True
    # Atom B at (90, 25, 25) — direct distance 80, periodic distance 80; both > 75.
    w.k_pos[1] = [90.0, 25.0, 25.0]
    w.k_level[1] = 4; w.k_alive[1] = True
    # Single bridge at (82, 25, 25): with orientation (1,0,0) and r_bridge=8,
    # synaptic search centre lands at (90, 25, 25) — exactly at B.
    w.k_pos[2] = [82.0, 25.0, 25.0]
    w.k_level[2] = 5; w.k_alive[2] = True
    w.k_strength[2] = 4.0  # BELOW synaptic_transmission_threshold=5.0
    # Pre-orient bridge toward A→B (+x) so STDP LTP reinforces the correct direction.
    # LTD from reversed pairs only reduces strength; orientation stays at (1,0,0).
    w.k_orientation[2] = np.array([1.0, 0.0, 0.0])
    w.k_count = 3

    def burst_at_atom(atom_idx: int) -> None:
        """Force atom_idx to fire by depositing charge above threshold."""
        w.k_charge[atom_idx] = cfg.theta_fire + 1.0

    # ---- Baseline: 5 sim-sec stimulating A only ----
    baseline_start_idx = len(w.firing_events)
    for k in range(int(5.0 / cfg.dt)):
        if (k + 1) % 30 == 0:
            burst_at_atom(0)  # fire A every 30 ticks
        tick(w, cfg.dt)
    baseline_B_firings = sum(
        1 for t, ai in w.firing_events[baseline_start_idx:] if ai == 1
    )
    print(f"P3 baseline: B fires = {baseline_B_firings}")

    # ---- Training: 50 paired-pulse trials A→B with 10ms lag ----
    for trial in range(50):
        burst_at_atom(0)   # A fires
        for _ in range(int(0.010 / cfg.dt)):
            tick(w, cfg.dt)
        burst_at_atom(1)   # B fires 10ms later
        for _ in range(int(0.5 / cfg.dt)):
            tick(w, cfg.dt)

    bridge_strength = float(w.k_strength[2])
    bridge_orient = w.k_orientation[2].tolist()
    print(f"P3 post-training: bridge strength = {bridge_strength:.2f}, "
          f"orientation = {bridge_orient}")

    # ---- Test: 5 sim-sec stimulating A only ----
    test_start_idx = len(w.firing_events)
    for k in range(int(5.0 / cfg.dt)):
        if (k + 1) % 30 == 0:
            burst_at_atom(0)
        tick(w, cfg.dt)
    test_B_firings = sum(
        1 for t, ai in w.firing_events[test_start_idx:] if ai == 1
    )

    print(f"P3 test: B fires = {test_B_firings} "
          f"(baseline = {baseline_B_firings}, need baseline==0 and test>=5)")
    # The geometry deliberately engineers baseline=0 (acoustic chain broken,
    # ambient generation off). Assert that explicitly so a future regression
    # that re-introduces ambient noise can't silently mask the test, then
    # require an absolute floor on test firings.
    assert baseline_B_firings == 0, (
        f"P3: baseline_B_firings={baseline_B_firings}, expected 0. "
        f"The geometry should isolate B from acoustic propagation; if baseline "
        f"is non-zero, ambient generation has been re-enabled or the box wraps "
        f"have re-aligned A and B."
    )
    assert test_B_firings >= 5, (
        f"P3: test B firings {test_B_firings} below absolute floor of 5. "
        f"Trained synaptic transmission should drive B at least 5 times "
        f"in 5 sim-sec under the engineered isolation."
    )

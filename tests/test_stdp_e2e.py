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

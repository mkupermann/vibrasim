"""Plan A.5 behavioural equivalence tests (AP1, AP2)."""
import numpy as np
import pytest
from dataclasses import replace
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def _run_short(slot_recycling_enabled: bool, numba_jit_enabled: bool,
               rng_seed: int = 42, n_ticks: int = 600):
    """Run a short sim with given flags; return summary counts."""
    cfg = WorldConfig(
        n_initial_vibrations=80, n_vibrations_max=200, n_nodes_max=4096,
        box_size=(60.0, 60.0, 60.0),
        r_1=3.0, r_2=20.0,
        freq_ratio=0.08, freq_tolerance=0.025,
        pair_decay_time=5.0, triad_decay_time=30.0,
        lambda_gen=0.001, lambda_dec=0.0005,
        rng_seed=rng_seed,
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        lambda_dec_mol=0.01, r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5), mol_fusion_enabled=True,
        slot_recycling_enabled=slot_recycling_enabled,
        numba_jit_enabled=numba_jit_enabled,
    )
    w = World(cfg)
    dt = cfg.dt
    for k in range(n_ticks):
        tick(w, dt)
    return {
        "k_count": w.k_count,
        "n_alive_nodes": int(w.k_alive[:w.k_count].sum()),
        "n_alive_vibrations": int(w.s_alive.sum()),
        "n_firings": len(w.firing_events),
    }


@pytest.mark.slow
def test_AP1_slot_recycling_preserves_observable_behaviour():
    """With same RNG seed, slot_recycling_enabled=True and =False must
    produce identical observable counts (alive nodes, alive vibrations,
    firings). Only k_count differs because recycling keeps it lower."""
    a = _run_short(slot_recycling_enabled=True, numba_jit_enabled=False)
    b = _run_short(slot_recycling_enabled=False, numba_jit_enabled=False)
    assert a["n_alive_nodes"] == b["n_alive_nodes"], (
        f"alive nodes differ: recycle={a['n_alive_nodes']}, "
        f"no-recycle={b['n_alive_nodes']}"
    )
    assert a["n_alive_vibrations"] == b["n_alive_vibrations"]
    assert a["n_firings"] == b["n_firings"]
    # k_count: recycle keeps it lower; not asserted equal
    print(f"AP1: recycle k_count={a['k_count']}, no-recycle k_count={b['k_count']}")
    print(f"AP1: a={a}, b={b}")


@pytest.mark.slow
@pytest.mark.skip(
    reason="awaiting Plan A.5 JIT migration (Tasks 9-13). The Python and "
    "JIT paths are the same code today, so this test would pass vacuously."
)
def test_AP2_jit_preserves_observable_behaviour():
    """With same RNG seed, numba_jit_enabled=True and =False must produce
    identical observable counts."""
    a = _run_short(slot_recycling_enabled=True, numba_jit_enabled=True)
    b = _run_short(slot_recycling_enabled=True, numba_jit_enabled=False)
    assert a["n_alive_nodes"] == b["n_alive_nodes"]
    assert a["n_alive_vibrations"] == b["n_alive_vibrations"]
    assert a["n_firings"] == b["n_firings"]
    assert a["k_count"] == b["k_count"]

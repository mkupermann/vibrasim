"""G24 amendment — energy-weighted flux pathway (R-17 acceptance tests).

Six tests pre-registered in `.eqmod/autopilot/QUEUE.yaml::R-17` and
`docs/amendments/G24-energy-weighted-flux.md` §3. The amendment text was
frozen 2026-05-20 and is locked while R-17 is in_progress.

Tests 1-4: the new `count_energy_flux_through` and
`apply_plasticity_energy_weighted` functions in `world.flux.plasticity`
behave per the amendment.

Tests 5-6: `agent.flux.encoder_free_training.training_step` dispatches
to the energy-weighted pair iff `EQMOD_USE_ENERGY_WEIGHTED_FLUX=1`.
"""
from __future__ import annotations

import numpy as np
import pytest

import agent.flux.encoder_free_training as eft
from world.flux.bridges import Bridges
from world.flux.plasticity import (
    PlasticityConfig,
    apply_plasticity_energy_weighted,
    count_energy_flux_through,
    count_flux_through,
)
from world.flux.quantum import Quanta
from world.flux.structures import Nodes


# ============================================================
# Test 1 — count_energy_flux_through sums quanta energies
# ============================================================


def test_count_energy_flux_through_sums_quanta_energy():
    """Amendment §3 row 1: 3 alive quanta of energies {1.0, 2.0, 4.0}
    all within r_flux of one alive bridge.

    count_energy_flux_through returns 7.0 for that slot;
    count_flux_through returns 3 for that slot; both arrays have shape
    (max_bridges,).
    """
    max_bridges = 4
    bridges = Bridges(max_bridges=max_bridges)
    nodes = Nodes(max_nodes=4)
    quanta = Quanta(max_quanta=10)
    cfg = PlasticityConfig(r_flux=0.5)

    # Two nodes defining a segment along x.
    nodes.add(pos=(0.0, 0.0, 0.0), energy=1.0, freq=1.0, born_tick=0)
    nodes.add(pos=(10.0, 0.0, 0.0), energy=1.0, freq=1.0, born_tick=0)
    bridges.add(src=0, dst=1, weight=1.0, born_tick=0)

    # Three quanta on the segment, energies 1.0, 2.0, 4.0 — sum 7.0.
    quanta.add(pos=(2.0, 0.0, 0.0), vel=(0, 0, 0),
                freq=1.0, polarity=1, energy=1.0)
    quanta.add(pos=(5.0, 0.0, 0.0), vel=(0, 0, 0),
                freq=1.0, polarity=1, energy=2.0)
    quanta.add(pos=(8.0, 0.0, 0.0), vel=(0, 0, 0),
                freq=1.0, polarity=1, energy=4.0)

    energy_flux = count_energy_flux_through(bridges, nodes, quanta, cfg)
    count_flux = count_flux_through(bridges, nodes, quanta, cfg)

    assert energy_flux.shape == (max_bridges,)
    assert count_flux.shape == (max_bridges,)
    assert energy_flux.dtype == np.float64
    assert float(energy_flux[0]) == pytest.approx(7.0)
    assert int(count_flux[0]) == 3


# ============================================================
# Test 2 — zero alive quanta returns zeros, no NaN
# ============================================================


def test_count_energy_flux_through_zero_quanta_returns_zeros():
    """Amendment §3 row 2: 0 alive quanta returns a float array of all
    zeros, no NaN.
    """
    bridges = Bridges(max_bridges=4)
    nodes = Nodes(max_nodes=2)
    quanta = Quanta(max_quanta=4)
    cfg = PlasticityConfig()

    nodes.add(pos=(0.0, 0.0, 0.0), energy=1.0, freq=1.0, born_tick=0)
    nodes.add(pos=(1.0, 0.0, 0.0), energy=1.0, freq=1.0, born_tick=0)
    bridges.add(src=0, dst=1, weight=1.0, born_tick=0)

    assert quanta.n_alive() == 0
    energy_flux = count_energy_flux_through(bridges, nodes, quanta, cfg)

    assert energy_flux.dtype == np.float64
    assert energy_flux.shape == (4,)
    assert not np.isnan(energy_flux).any()
    assert np.all(energy_flux == 0.0)


# ============================================================
# Test 3 — strengthening proportional to energy_flux
# ============================================================


def test_apply_plasticity_energy_weighted_strengthens_proportionally():
    """Amendment §3 row 3: two bridges, energy_flux=10.0 and 2.0 both
    above flux_min. First bridge's weight gain is exactly 5x the
    second's (matches the linear ``gamma * flux`` term).
    """
    bridges = Bridges(max_bridges=4)
    bridges.add(src=0, dst=1, weight=1.0, born_tick=0)
    bridges.add(src=1, dst=0, weight=1.0, born_tick=0)

    cfg = PlasticityConfig(gamma=0.1, lam=0.1, flux_min=1.0)
    energy_flux = np.zeros(4, dtype=np.float64)
    energy_flux[0] = 10.0
    energy_flux[1] = 2.0

    w0_before = float(bridges.weight[0])
    w1_before = float(bridges.weight[1])

    apply_plasticity_energy_weighted(
        bridges, energy_flux, cfg, tick_index=1,
    )

    gain_0 = float(bridges.weight[0]) - w0_before
    gain_1 = float(bridges.weight[1]) - w1_before

    # Both > flux_min so deficit = 0; gain = gamma * flux exactly.
    assert gain_0 == pytest.approx(cfg.gamma * 10.0)
    assert gain_1 == pytest.approx(cfg.gamma * 2.0)
    # Ratio = 5x.
    assert gain_0 == pytest.approx(5.0 * gain_1)


# ============================================================
# Test 4 — decay below flux_min, growth above
# ============================================================


def test_apply_plasticity_energy_weighted_decay_below_flux_min():
    """Amendment §3 row 4: bridge with energy_flux=0.0 and flux_min=1.0
    decreases by lam*1.0; energy_flux=0.5 decreases by lam*0.5;
    energy_flux=1.5 increases (linear in gamma*1.5).

    The decay cases isolate the decay term (gamma=0); the strengthen
    case isolates the strengthen term (deficit=0 so lam plays no role).
    """
    cfg_decay_only = PlasticityConfig(gamma=0.0, lam=0.3, flux_min=1.0)

    # Case A: energy_flux=0.0 → weight decreases by lam * 1.0.
    b_a = Bridges(max_bridges=1)
    b_a.add(src=0, dst=1, weight=1.0, born_tick=0)
    apply_plasticity_energy_weighted(
        b_a, np.array([0.0], dtype=np.float64),
        cfg_decay_only, tick_index=1,
    )
    assert float(b_a.weight[0]) == pytest.approx(1.0 - cfg_decay_only.lam * 1.0)

    # Case B: energy_flux=0.5 → weight decreases by lam * 0.5.
    b_b = Bridges(max_bridges=1)
    b_b.add(src=0, dst=1, weight=1.0, born_tick=0)
    apply_plasticity_energy_weighted(
        b_b, np.array([0.5], dtype=np.float64),
        cfg_decay_only, tick_index=1,
    )
    assert float(b_b.weight[0]) == pytest.approx(1.0 - cfg_decay_only.lam * 0.5)

    # Case C: energy_flux=1.5 → weight INcreases linearly in gamma*1.5.
    # deficit = max(0, 1 - 1.5) = 0, so decay term is 0; change = gamma * 1.5.
    cfg_strengthen = PlasticityConfig(gamma=0.2, lam=0.3, flux_min=1.0)
    b_c = Bridges(max_bridges=1)
    b_c.add(src=0, dst=1, weight=1.0, born_tick=0)
    apply_plasticity_energy_weighted(
        b_c, np.array([1.5], dtype=np.float64),
        cfg_strengthen, tick_index=1,
    )
    assert float(b_c.weight[0]) == pytest.approx(
        1.0 + cfg_strengthen.gamma * 1.5
    )
    assert float(b_c.weight[0]) > 1.0  # explicit "weight INcreases"


# ============================================================
# Test 5 & 6 — env-var dispatch
# ============================================================


def _make_substrate_for_training_step():
    """Minimal alive substrate suitable for one training_step call."""
    bridges = Bridges(max_bridges=2)
    nodes = Nodes(max_nodes=2)
    quanta = Quanta(max_quanta=2)
    nodes.add(pos=(0.0, 0.0, 0.0), energy=1.0, freq=1.0, born_tick=0)
    nodes.add(pos=(1.0, 0.0, 0.0), energy=1.0, freq=1.0, born_tick=0)
    bridges.add(src=0, dst=1, weight=1.0, born_tick=0)
    return bridges, nodes, quanta


def _install_call_spies(monkeypatch):
    """Install spies on the four plasticity entry points in eft module."""
    calls = {
        "count_flux": 0,
        "apply_p": 0,
        "count_energy": 0,
        "apply_p_energy": 0,
    }

    def spy_count_flux(bridges, nodes, quanta, cfg):
        calls["count_flux"] += 1
        return np.zeros(bridges.max_bridges, dtype=np.int64)

    def spy_apply_p(bridges, f, cfg, tick_index):
        calls["apply_p"] += 1

    def spy_count_energy(bridges, nodes, quanta, cfg):
        calls["count_energy"] += 1
        return np.zeros(bridges.max_bridges, dtype=np.float64)

    def spy_apply_p_energy(bridges, f, cfg, tick_index):
        calls["apply_p_energy"] += 1

    monkeypatch.setattr(eft, "count_flux_through", spy_count_flux)
    monkeypatch.setattr(eft, "apply_plasticity", spy_apply_p)
    monkeypatch.setattr(eft, "count_energy_flux_through", spy_count_energy)
    monkeypatch.setattr(eft, "apply_plasticity_energy_weighted",
                         spy_apply_p_energy)
    return calls


def test_env_var_routes_to_weighted_path_in_encoder_free_training(monkeypatch):
    """Amendment §3 row 5: with EQMOD_USE_ENERGY_WEIGHTED_FLUX=1,
    training_step calls count_energy_flux_through and
    apply_plasticity_energy_weighted, NOT the count-based versions.
    """
    monkeypatch.setenv("EQMOD_USE_ENERGY_WEIGHTED_FLUX", "1")
    calls = _install_call_spies(monkeypatch)
    bridges, nodes, quanta = _make_substrate_for_training_step()
    cfg = PlasticityConfig()

    eft.training_step(bridges, nodes, quanta, cfg, tick_index=0)

    assert calls["count_energy"] == 1
    assert calls["apply_p_energy"] == 1
    assert calls["count_flux"] == 0
    assert calls["apply_p"] == 0


def test_env_var_default_keeps_count_based_path(monkeypatch):
    """Amendment §3 row 6: without EQMOD_USE_ENERGY_WEIGHTED_FLUX or
    set to '0', training_step calls the count-based functions, not the
    weighted ones.
    """
    # Two sub-cases share one substrate config but distinct substrates
    # (training_step mutates bridge weights).

    # Sub-case A: env var unset.
    monkeypatch.delenv("EQMOD_USE_ENERGY_WEIGHTED_FLUX", raising=False)
    calls_unset = _install_call_spies(monkeypatch)
    bridges, nodes, quanta = _make_substrate_for_training_step()
    eft.training_step(bridges, nodes, quanta, PlasticityConfig(),
                       tick_index=0)
    assert calls_unset["count_flux"] == 1
    assert calls_unset["apply_p"] == 1
    assert calls_unset["count_energy"] == 0
    assert calls_unset["apply_p_energy"] == 0

    # Sub-case B: env var explicitly set to "0".
    monkeypatch.setenv("EQMOD_USE_ENERGY_WEIGHTED_FLUX", "0")
    calls_zero = _install_call_spies(monkeypatch)
    bridges2, nodes2, quanta2 = _make_substrate_for_training_step()
    eft.training_step(bridges2, nodes2, quanta2, PlasticityConfig(),
                       tick_index=0)
    assert calls_zero["count_flux"] == 1
    assert calls_zero["apply_p"] == 1
    assert calls_zero["count_energy"] == 0
    assert calls_zero["apply_p_energy"] == 0

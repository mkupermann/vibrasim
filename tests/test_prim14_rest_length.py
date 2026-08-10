"""PRIM14 engineering tests: per-bond rest length (world/state.py b_rest_len,
formation freeze in world/bridges.py + physics ILW pair path, tension branch).
Fast slice. The D0 experiment verdict lives in the amendment/LOGBOOK, not here."""
from __future__ import annotations
import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick

EMPTY = np.empty(0, dtype=np.int32)


def _cfg(per_bond: bool) -> WorldConfig:
    return WorldConfig(rng_seed=42, box_size=(60.0, 60.0, 60.0),
                       n_initial_vibrations=0, n_vibrations_max=64,
                       n_nodes_max=64, lambda_gen=0.0, lambda_dec=0.0,
                       atom_valence=2, atom_repulsion_k=0.0, repulsion_k=0.0,
                       node_thermal_speed=0.0, anchor_damping=0.0,
                       neuron_dynamics_enabled=False, stdp_enabled=False,
                       btsp_enabled=False, r_2=12.0, graceful_capacity=True,
                       per_bond_rest_enabled=per_bond)


def _chain(w: World, xs):
    slots = [w.allocate_node(np.array([x, 30.0, 30.0]), 1.0, True, 4, EMPTY, 0)
             for x in xs]
    for _ in range(8):
        for s, x in zip(slots, xs):
            w.k_pos[s] = (x, 30.0, 30.0)
            w.k_vel[s] = 0.0
        tick(w, w.config.dt)
    return slots


def test_formation_freezes_rest_length():
    w = World(_cfg(per_bond=True))
    _chain(w, (13.0, 21.0, 29.0))  # spacing 8/8, both within [r_1, r_2]
    alive = w.b_alive[: w.b_count]
    assert alive.sum() == 2
    rest = w.b_rest_len[: w.b_count][alive]
    assert np.allclose(rest, 8.0, atol=0.5), rest


def test_consolidation_bonds_short_edge_only():
    """At {13,17,29} consolidation forms exactly ONE bond — the SHORT edge
    (13-17, rest 4); the long edge (dist 12) is outside the formation
    radius. (Corrects the first D0 reading, which wrongly claimed r_1
    excludes the short edge — see LOGBOOK 2026-08-10 D1 erratum.)"""
    w = World(_cfg(per_bond=True))
    _chain(w, (13.0, 17.0, 29.0))
    alive = w.b_alive[: w.b_count]
    assert int(alive.sum()) == 1
    b = int(np.where(alive)[0][0])
    assert {int(w.b_atom_i[b]), int(w.b_atom_j[b])} == {0, 1}
    assert abs(float(w.b_rest_len[b]) - 4.0) < 0.5


def test_disabled_flag_leaves_rest_length_unused():
    """Flag off: dynamics must match the historic global-r_eq behaviour
    even though b_rest_len is populated at formation."""
    end_x = {}
    for flag in (False, True):
        w = World(_cfg(per_bond=flag))
        slots = _chain(w, (13.0, 17.0, 29.0))
        assert w.b_rest_len[: w.b_count].max() > 0  # always recorded
        w.k_pos[slots[1]] = (21.0, 30.0, 30.0)
        w.k_vel[slots[1]] = 0.0
        for _ in range(300):
            w.k_pos[slots[0]] = (13.0, 30.0, 30.0); w.k_vel[slots[0]] = 0.0
            w.k_pos[slots[2]] = (29.0, 30.0, 30.0); w.k_vel[slots[2]] = 0.0
            tick(w, w.config.dt)
        end_x[flag] = float(w.k_pos[slots[1]][0])
    # Off: single (17,29) bond with global r_eq=6 pushes AWAY from stored
    # (toward 23); On: rest 12 pulls back toward 17. They must differ, and
    # each in its predicted direction.
    assert end_x[False] > 21.0
    assert end_x[True] < 21.0

"""Tests for tools/construct_network.py."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World

from tools.construct_network import construct_network


def _empty_world(n_max=2048):
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(400.0, 400.0, 400.0),
        n_vibrations_max=128,
        n_nodes_max=n_max,
        rng_seed=42,
    )
    return World(cfg)


def test_construct_three_neurons_one_synapse():
    w = _empty_world()
    info = construct_network(
        w,
        neuron_centres=[
            [80.0, 100.0, 100.0],
            [120.0, 100.0, 100.0],
            [200.0, 100.0, 100.0],
        ],
        synapse_pairs=[(0, 1)],
    )
    assert info["n_neurons"] == 3
    assert info["n_synapses"] == 1
    matrix = np.array(info["topology_matrix"])
    assert matrix[0, 1] == 1
    assert matrix[1, 0] == 0
    assert matrix.sum() == 1


def test_construct_disconnected_pair():
    w = _empty_world()
    info = construct_network(
        w,
        neuron_centres=[[80, 100, 100], [200, 100, 100]],
        synapse_pairs=[],
    )
    assert info["n_neurons"] == 2
    assert info["n_synapses"] == 0
    matrix = np.array(info["topology_matrix"])
    assert matrix.sum() == 0


def test_self_synapse_rejected():
    w = _empty_world()
    with pytest.raises(ValueError):
        construct_network(
            w,
            neuron_centres=[[80, 100, 100], [120, 100, 100]],
            synapse_pairs=[(0, 0)],
        )


def test_chain_of_three_neurons():
    w = _empty_world()
    info = construct_network(
        w,
        neuron_centres=[
            [80.0, 100.0, 100.0],
            [120.0, 100.0, 100.0],
            [160.0, 100.0, 100.0],
        ],
        synapse_pairs=[(0, 1), (1, 2)],
    )
    assert info["n_neurons"] == 3
    assert info["n_synapses"] == 2
    matrix = np.array(info["topology_matrix"])
    assert matrix[0, 1] == 1
    assert matrix[1, 2] == 1


def test_invalid_synapse_index_rejected():
    w = _empty_world()
    with pytest.raises(ValueError):
        construct_network(
            w,
            neuron_centres=[[80, 100, 100], [120, 100, 100]],
            synapse_pairs=[(0, 2)],  # 2 is out of range
        )

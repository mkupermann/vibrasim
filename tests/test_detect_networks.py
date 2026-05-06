"""Tests for tools/detect_networks.py."""
import numpy as np
import pytest

from tools.detect_networks import detect_networks


class _StubWorld:
    """Minimal world stub — detect_networks only needs world to pass through to
    detect_neurons / detect_synapses, both of which we mock by passing pre-computed
    lists directly."""
    def __init__(self):
        pass


def test_no_neurons_no_network():
    w = _StubWorld()
    candidates = detect_networks(w, neurons=[], synapses=[])
    assert candidates == []


def test_two_neurons_no_synapse_no_network():
    w = _StubWorld()
    neurons = [
        {"member_indices": [0], "is_neuron_candidate": True, "centre": [0, 0, 0]},
        {"member_indices": [1], "is_neuron_candidate": True, "centre": [10, 0, 0]},
    ]
    candidates = detect_networks(w, neurons=neurons, synapses=[])
    assert candidates == []


def test_three_neurons_in_chain_is_network():
    w = _StubWorld()
    neurons = [
        {"member_indices": [0], "is_neuron_candidate": True, "centre": [0, 0, 0]},
        {"member_indices": [1], "is_neuron_candidate": True, "centre": [10, 0, 0]},
        {"member_indices": [2], "is_neuron_candidate": True, "centre": [20, 0, 0]},
    ]
    synapses = [
        {"pre_index": 0, "post_index": 1, "is_synapse_candidate": True},
        {"pre_index": 1, "post_index": 2, "is_synapse_candidate": True},
    ]
    candidates = detect_networks(w, neurons=neurons, synapses=synapses)
    assert len(candidates) == 1
    c = candidates[0]
    assert c["n_neurons"] == 3
    assert c["n_synapses"] == 2
    assert c["is_network_candidate"]


def test_two_separate_networks():
    w = _StubWorld()
    neurons = [
        {"member_indices": [i], "is_neuron_candidate": True, "centre": [i * 10, 0, 0]}
        for i in range(6)
    ]
    synapses = [
        # First triangle
        {"pre_index": 0, "post_index": 1, "is_synapse_candidate": True},
        {"pre_index": 1, "post_index": 2, "is_synapse_candidate": True},
        # Second triangle, disjoint
        {"pre_index": 3, "post_index": 4, "is_synapse_candidate": True},
        {"pre_index": 4, "post_index": 5, "is_synapse_candidate": True},
    ]
    candidates = detect_networks(w, neurons=neurons, synapses=synapses)
    assert len(candidates) == 2
    sizes = sorted(c["n_neurons"] for c in candidates)
    assert sizes == [3, 3]


def test_isolated_neurons_excluded():
    """A network of 3 + an isolated 4th neuron → one candidate of 3."""
    w = _StubWorld()
    neurons = [
        {"member_indices": [i], "is_neuron_candidate": True, "centre": [i * 10, 0, 0]}
        for i in range(4)
    ]
    synapses = [
        {"pre_index": 0, "post_index": 1, "is_synapse_candidate": True},
        {"pre_index": 1, "post_index": 2, "is_synapse_candidate": True},
    ]
    candidates = detect_networks(w, neurons=neurons, synapses=synapses)
    assert len(candidates) == 1
    assert candidates[0]["n_neurons"] == 3

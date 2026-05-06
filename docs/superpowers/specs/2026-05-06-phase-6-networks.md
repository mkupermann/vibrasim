# Phase 6 — Small Network Design Specification

**Status:** Draft for review (scaffolding only; emergent cognitive function is empirical and downstream of Phase 5 working)
**Date:** 2026-05-06
**Source:** [`docs/CONCEPT.md`](../../CONCEPT.md) v2 §5 Phase 6
**Precondition:** Phases 4 and 5 scaffolding shipped (yes); Phase 5 plasticity acceptance pending.

**Scope:** Define what a "small network" is operationally in this 3D substrate, build tools to construct + detect + measure network-level activity. Per CONCEPT.md v2 §10.6, the compute regime for Phase 6 is GPU territory (~200 000–4 000 000 vibrations); this scaffolding is CPU-tested with hand-built networks of 3–10 neurons. Emergent cognitive functions (pattern recognition, Hopfield-style memory, simple learning) are the **research questions** the tooling makes answerable.

---

## 1. Goal

Phase 6 makes "network-level cognitive function" testable. CONCEPT.md v2 §5 Phase 6 names three functions to look for:

- **Pattern recognition** — a network reliably maps input patterns A, B, C to consistent output patterns A', B', C'.
- **Associative memory (Hopfield-style)** — presenting a partial input recalls the full stored pattern; the network's energy landscape has a basin of attraction at each stored memory.
- **Simple learning** — repeated stimulation modifies the network's response (the synapses strengthen, per Phase 5).

This phase ships the apparatus to measure those properties. The substrate is unchanged.

## 2. Operational definition

A **network** in a snapshot is a set of N neuron candidates `[N_1, ..., N_n]` and a set of M synapse candidates `[(i, j) : i, j ∈ {1,...,n}, i ≠ j]`. Each synapse `(i, j)` represents a directed connection from neuron i (presynaptic) to neuron j (postsynaptic).

The network has:

- **Topology** — the directed graph of (i, j, weight) triples. Weights are inferred from the count of presynaptic-store molecules at neuron `i`'s outlet that face neuron `j`'s inlet (Phase 5 plasticity is what changes these counts).
- **Input neurons** — a designated subset of nodes that receive external stimulation (no presynaptic connections; their firing is forced by an external schedule).
- **Output neurons** — a designated subset whose firing pattern is the network's "answer".
- **Hidden neurons** — the rest, between input and output.

For 3-neuron toy networks, all three roles can collapse into the same neuron (e.g., a 2-input-1-output recogniser). For larger networks, the input/hidden/output distinction matters.

## 3. Activity measurement

Given a sequence of snapshots and a network definition, the measurement tool extracts:

- **Per-neuron firing history** — for each neuron, a binary array indicating "fired in this snapshot" derived from the Phase 4 measure_neuron_activity logic.
- **Network activity vector at time t** — the binary vector of (neuron_1_fired, neuron_2_fired, ..., neuron_n_fired) at time t.
- **Pairwise firing correlation matrix** — N×N matrix of correlations between neuron firing histories. Captures functional connectivity beyond raw topology.
- **Pattern recognition score** — for a list of (input_pattern, expected_output_pattern) tuples and a snapshot range:
  - Force input neurons to fire according to input_pattern at the start of each trial
  - Record output neuron activity vector
  - Compare to expected_output_pattern (Hamming distance, 0 = perfect match)
  - Aggregate score across trials

Hopfield-style memory recall is a special case: the same neurons act as input and output, and the score measures completion of partial cues.

## 4. Construction tool — `tools/construct_network.py`

```python
def construct_network(world, neuron_centres, synapse_pairs, neuron_radius=6.0,
                    n_atoms_per_neuron=8, n_molecules_per_neuron=6,
                    n_cleft_molecules=4, n_presynaptic_store=6,
                    n_postsynaptic_receivers=6):
    """Place N neurons connected by directed synapses.

    `neuron_centres`: list of (x, y, z) positions, one per neuron.
    `synapse_pairs`: list of (pre_idx, post_idx) tuples — directed edges.

    Returns dict with:
      - 'neurons': list of construct_neuron output dicts
      - 'synapses': list of {'pre_idx', 'post_idx', 'cleft_centre', ...}
      - 'topology_matrix': N×N int array of synapse counts (multi-edges allowed)
    """
```

For each synapse pair, the function calls `construct_synapse` between the two neuron centres with the appropriate axis. If two synapses share a neuron, the neurons are constructed once and the synapse's cleft + store + receivers attach to the existing neurons.

The CLI: `python tools/construct_network.py --output network.npz --topology topology.json` where the JSON encodes the network architecture.

## 5. Detection tool — `tools/detect_networks.py`

```python
def detect_networks(world, neurons=None, synapses=None) -> list[dict]:
    """Find network candidates in the world.

    Algorithm:
      1. detect_neurons → list of N neuron candidates
      2. detect_synapses on the neuron list → list of synapse candidates
      3. Build undirected graph from synapse pairs
      4. Find connected components in this graph
      5. Each connected component with ≥3 neurons is a network candidate

    Returns: list of candidates with fields:
      - 'neuron_indices': k_pos indices of constituent neurons
      - 'synapse_pairs': directed (i, j) tuples
      - 'n_neurons': len(neuron_indices)
      - 'n_synapses': len(synapse_pairs)
      - 'is_network_candidate': n_neurons >= 3
    """
```

## 6. Network activity measurement tool — `tools/measure_network_activity.py`

```python
def measure_network_activity(snapshot_paths, neuron_definitions):
    """Track per-neuron firing across a snapshot sequence.

    `neuron_definitions`: list of dicts with 'centre', 'axis', 'radius'.

    Returns: dict with
      - 'times': list of timestamps
      - 'firing_matrix': T×N array; firing_matrix[t, n] = 1 if neuron n fired at time t
      - 'firing_rates': N-length array of mean firing rate per neuron
      - 'correlation_matrix': N×N pairwise firing correlations
      - 'activity_vectors': T×N int array of network states
    """


def score_pattern_recognition(firing_matrix, input_pattern_indices, output_pattern_indices,
                              expected_outputs, time_windows):
    """Score how well the network maps inputs to expected outputs.

    For each (start_t, end_t) window, look at output_pattern_indices' activity vector
    and compare to expected_outputs[i]. Return mean Hamming-distance similarity.
    """
```

## 7. Tests

### `tests/test_construct_network.py`

| Test | Asserts |
|---|---|
| `test_construct_three_neurons_one_synapse` | 3 neurons placed; 1 synapse between two of them; topology_matrix has the expected entry |
| `test_construct_disconnected_pair` | 2 neurons, no synapses → empty topology_matrix |
| `test_construct_with_self_synapse_rejected` | Synapse pair (i, i) raises ValueError |
| `test_construct_chain_of_three` | 3 neurons in a chain (1→2→3) with 2 synapses |

### `tests/test_detect_networks.py`

| Test | Asserts |
|---|---|
| `test_no_neurons_no_network` | Empty world → no candidates |
| `test_two_neurons_no_synapse_no_network` | 2 isolated neurons → no candidate (need ≥3 in a component) |
| `test_three_neurons_in_chain_is_network` | After construction, detect returns one network with 3 neurons |
| `test_two_separate_networks` | Two chains of 3 in different regions → 2 network candidates |

### `tests/test_measure_network_activity.py`

| Test | Asserts |
|---|---|
| `test_firing_matrix_shape` | Output dict has firing_matrix of shape (T, N) |
| `test_correlation_matrix_diagonal_one` | Each neuron is perfectly correlated with itself |
| `test_pattern_recognition_perfect_match` | Synthetic firing matrices that perfectly match expected → score = 1.0 |
| `test_pattern_recognition_no_match` | Random firings → score near baseline |

## 8. Acceptance criteria

This spec is satisfied when:

1. `pytest tests/test_construct_network.py tests/test_detect_networks.py tests/test_measure_network_activity.py` is green.
2. `tools/construct_network.py` runs end-to-end with a 3-neuron chain topology.
3. `tools/detect_networks.py` correctly identifies the constructed chain as a network.
4. `tools/measure_network_activity.py` runs over any snapshot sequence and returns the documented dict shape.

The CONCEPT.md v2 §5 Phase 6 acceptance criterion (a 5–50-neuron network shows pattern recognition / associative memory / simple learning under simulation) is **empirical** and not part of this spec's deliverable. It is downstream of Phase 5 plasticity actually emerging — which itself is empirically untested.

## 9. Out of scope

- 50-neuron networks at GPU scale (the scaffolding handles 3–10 on CPU; large-scale runs are GPU work per CONCEPT.md §10.6).
- Network topology generators (e.g., random graph, scale-free) — for now, topologies are hand-specified.
- Training routines (gradient descent, etc.) — networks are observed, not trained.
- Hopfield-style energy-landscape analysis — the recall test exercises the same logic without computing energy.

## 10. Implementation order

1. `tools/construct_network.py` — uses construct_neuron + construct_synapse with attach-to-existing logic
2. `tools/detect_networks.py` — connected components on synapse graph
3. `tools/measure_network_activity.py` — firing-matrix construction + correlation + pattern scoring
4. Tests for all three
5. Smoke run: 3-neuron chain, run forward, measure correlation, score a synthetic pattern

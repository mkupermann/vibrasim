# Phase 4 — Neuron Models Design Specification

**Status:** Draft for review (scaffolding only; spontaneous and constructed neuron behaviour is empirical)
**Date:** 2026-05-06
**Source:** [`docs/CONCEPT.md`](../../CONCEPT.md) v2 §5 Phase 4
**Precondition:** Phase 3 scaffolding shipped (yes); Phase 2 partially closed — first molecules forming, ≥5-species acceptance pending.

**Scope:** Define what a "neuron" is operationally in this 3D substrate. Build a construction tool that hand-places a candidate neuron cluster. Build detection tools that find candidate clusters in any snapshot, and a measurement tool that tracks input and output activity across snapshot sequences. **Whether a constructed cluster actually exhibits integration + threshold + refractory under the natural laws is the empirical open question** — this spec only delivers the tooling needed to find out.

---

## 1. Goal

Phase 4 makes "neuron-like behaviour" testable. CONCEPT.md v2 §5 Phase 4 names four properties a candidate neuron has to show:

- **Input integration** — incoming activity sums over time
- **Threshold firing** — the cluster emits a strong signal when accumulated activity passes a threshold
- **Output** — a directional emission of mobile molecules
- **Refractory period** — after firing, the cluster temporarily cannot fire again

These are **emergent** properties of a node configuration under the existing natural laws. The substrate is unchanged. What we add is the apparatus to construct candidate neuron arrangements and to measure whether they exhibit any of those four properties under simulation.

## 2. Operational definition

A **neuron candidate** in a snapshot is a set of nodes satisfying:

- **Connectivity:** all member nodes within `r_neuron` of each other under periodic minimum-image distance. Default `r_neuron = 2.5 · r_2`, large enough to span typical molecule + atom drift but small enough to keep clusters compact.
- **Compactness:** the radius of the smallest sphere enclosing all members is below `r_compact`. Default `r_compact = 8.0` units in the calibrated `dense_60_n800` regime.
- **Atom + molecule mass:** at least `n_min_atoms = 6` level-4 nodes and `n_min_molecules = 4` level-5+ nodes inside the cluster. The total node count is at least `n_min_total = 12`.
- **Input region:** a sub-sphere of radius `r_io = 0.3 · r_compact` at the cluster's "inlet" face. By default, the inlet axis is the +X direction from the cluster centre. The inlet sub-sphere is centred at `centre + r_compact · 0.6 · inlet_axis`.
- **Output region:** symmetrically positioned at `centre + r_compact · 0.6 · outlet_axis`, where `outlet_axis = -inlet_axis`.

The inlet/outlet orientation is a hand-set property of the cluster. It is not currently inferred from morphology — that's a research question for later iterations, after we know whether constructed neurons even fire.

## 3. Activity measurement

Given a *sequence* of snapshots covering a time window `[t_0, t_1]` and a cluster definition (centre + radius + axis), the measurement tool extracts:

- **Input rate:** count of free vibrations (or low-level mobile nodes — electrons, pairs) that entered the input sub-sphere per unit simulated time. "Entered" means present at time `t` and not present at `t − dt`.
- **Output rate:** symmetric count for the output sub-sphere.
- **Firing event:** a contiguous time window where the output rate exceeds `firing_threshold = 5 × baseline_output_rate`. Each firing event has a start time, peak rate, and duration.
- **Integration time:** for each firing event, the lag between sustained input above input-threshold and the peak output. (Computed only when input precedes output.)
- **Refractory period:** the inter-firing interval when input remains above the firing threshold but output drops to baseline.

These metrics let calibration sessions answer:

- "Does this constructed cluster fire at all?" (any firing events?)
- "Does it integrate?" (correlation between input and output at non-zero lag?)
- "Does it have a refractory period?" (silence between consecutive firings while input is sustained?)

A cluster that never fires is a negative result — informative but not a Phase 4 success.

## 4. Construction tool — `tools/construct_neuron.py`

```python
def construct_neuron(world, centre, radius, axis, n_atoms=8, n_molecules=6,
                    base_freq_atom=30000.0, base_freq_molecule=60000.0):
    """Place a candidate neuron cluster centred at `centre` with radius `radius`.

    The cluster contains:
      - `n_atoms` atoms (level 4) at positions inside the sphere
      - `n_molecules` molecules (level 5) at positions inside the sphere
    The `axis` (length-3 vector, normalised) sets the input/output orientation.
    """
```

Atom and molecule frequencies are slightly varied (each successive node uses `base_freq * (1 + 0.001 * i)`) so the cluster has visible mass distinction without confusing the species classifier.

The CLI: `python tools/construct_neuron.py --output cluster.npz --centre 50,50,50 --radius 6 --axis 1,0,0 --n-atoms 8 --n-molecules 6`.

## 5. Detection tool — `tools/detect_neurons.py`

```python
def detect_neurons(world, *, r_neuron=None, r_compact=None,
                  n_min_atoms=6, n_min_molecules=4):
    """Find candidate neuron clusters.

    Returns: list of candidate dicts with fields:
      - 'member_indices': k_pos indices of constituent nodes
      - 'centre': cluster centroid
      - 'radius': enclosing-sphere radius
      - 'n_atoms', 'n_molecules', 'n_total': counts
      - 'is_compact': radius < r_compact
      - 'meets_mass': enough atoms + molecules
      - 'is_neuron_candidate': both above true
    """
```

Algorithm:

1. Build adjacency on alive level-4+ nodes within `r_neuron`.
2. Find connected components (BFS).
3. For each component: compute centroid + max-distance-from-centroid (= radius).
4. Apply compactness and mass thresholds.

Reuses the connected-components helper from `tools/detect_membranes.py`. The two detection tools live independently because the criteria are different (membranes are hollow shells; neurons are dense balls).

## 6. Activity measurement tool — `tools/measure_neuron_activity.py`

```python
def measure_activity(snapshot_paths, cluster_centre, cluster_axis, r_compact,
                    output_threshold_multiplier=5.0):
    """Track input and output activity across a snapshot sequence.

    Returns: dict with
      - 'times': list of snapshot timestamps
      - 'input_count_per_step': count of free mobile nodes inside input sphere per snapshot
      - 'output_count_per_step': symmetric for output sphere
      - 'firing_events': list of {'start_t', 'peak_t', 'peak_rate', 'duration'}
      - 'integration_lag_ms': mean integration time across firings (None if < 2 firings)
      - 'refractory_ms': mean inter-firing interval (None if < 2 firings)
    """
```

Counts treat each free vibration *and* each level-1/2/3 mobile node (electrons, pairs, triads have positions but only electrons are stationary; pairs/triads can drift under repulsion in our v2 substrate) as candidates for "activity". Atoms and molecules are excluded because they're typically embedded in the cluster, not transient input/output.

The "free vibration" count requires reading `s_alive` and `s_pos` from the snapshot.

## 7. Tests

### `tests/test_construct_neuron.py`

| Test | Asserts |
|---|---|
| `test_construct_basic` | `n_atoms=8, n_molecules=6` produces 14 alive nodes inside the sphere |
| `test_construct_axis_orientation` | The cluster's centroid is at `centre`; axis is normalised internally |
| `test_construct_capacity_overflow` | Capacity exhaustion raises `RuntimeError` |
| `test_construct_then_detect_round_trip` | `construct_neuron(...)` then `detect_neurons(...)` returns the cluster as a candidate |

### `tests/test_detect_neurons.py`

| Test | Asserts |
|---|---|
| `test_empty_world_no_candidates` | A world with no nodes returns `[]` |
| `test_sparse_atoms_not_a_neuron` | 5 atoms scattered far apart → not a candidate (fails connectivity) |
| `test_compact_dense_cluster_is_candidate` | Atoms + molecules in a small sphere → candidate with `is_neuron_candidate=True` |
| `test_atoms_only_no_molecules_fails_mass` | 10 atoms but 0 molecules → fails the molecule mass threshold |

### `tests/test_measure_neuron_activity.py`

| Test | Asserts |
|---|---|
| `test_no_input_no_output_zeros` | Snapshot sequence with no mobile nodes → all rates 0 |
| `test_input_only_no_firing` | Mobile nodes enter input sphere but no output → input_count > 0, firing_events empty |
| `test_synthetic_firing_event_detected` | Hand-crafted output spike → registered as firing event with correct start/peak |

## 8. Acceptance criteria

This spec is satisfied when:

1. `pytest tests/test_construct_neuron.py tests/test_detect_neurons.py tests/test_measure_neuron_activity.py` is green.
2. `tools/construct_neuron.py --output /tmp/neuron.npz --centre 50,50,50 --radius 6 --axis 1,0,0` runs without error.
3. `tools/detect_neurons.py /tmp/neuron.npz` reports the constructed cluster as a candidate.
4. `tools/measure_neuron_activity.py` runs over any snapshot sequence without error and returns the documented dict shape.

The CONCEPT.md v2 §5 Phase 4 acceptance criterion (at least one cluster shows integration + threshold + refractory under simulation) is **empirical** and not part of this spec's deliverable. It will be answered by calibration sessions once Phase 2 is fully closed.

## 9. Out of scope

- Synaptic transmission between two neurons (Phase 5).
- Plastic strengthening of connections (Phase 5).
- Self-organising neuron formation (open research; constructed neurons are how we test if firing is achievable at all).
- Inferring inlet/outlet axis from cluster morphology.
- GPU acceleration (single-machine CPU is enough for hand-built clusters).

## 10. Implementation order

1. `tools/construct_neuron.py` + `tests/test_construct_neuron.py` (mechanical)
2. `tools/detect_neurons.py` + `tests/test_detect_neurons.py` (reuses connected-components logic)
3. `tools/measure_neuron_activity.py` + `tests/test_measure_neuron_activity.py` (the most novel piece)
4. Smoke run: construct one neuron in a calibrated world, run forward 30 s, measure activity, document in LOGBOOK.
5. Decide on Phase 5 scaffolding shape based on what we learn.

This is scaffolding. The substrate-modifying experiments — does the cluster fire? at what input rate? — are calibration work that follows.

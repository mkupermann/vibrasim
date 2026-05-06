# Phase 5 — Synapses with Molecular Transmission Design Specification

**Status:** Draft for review (scaffolding only; emergent plasticity remains the central research hurdle)
**Date:** 2026-05-06
**Source:** [`docs/CONCEPT.md`](../../CONCEPT.md) v2 §5 Phase 5 + §6 + §6.5 (open thermodynamic question)
**Precondition:** Phase 4 scaffolding shipped (yes); Phase 1 calibrated (yes); Phases 2–4 acceptance pending.

**Scope:** Operationally define a synapse in this 3D substrate, build construction + detection tools for it, build a longitudinal plasticity-measurement tool, and ship tests. **Whether constructed synapses actually exhibit Hebbian plasticity under our natural laws is the central Phase 5 research question** — CONCEPT.md v2 §6.5 is explicit that this may fail. This spec only delivers the apparatus to find out.

---

## 1. Goal

Phase 5 makes "Hebbian plasticity" testable. CONCEPT.md v2 §6.3 commits to the mechanism: **local capture from the §4.7 ambient field**. When two neurons are co-active, repeated binding events in the synapse region capture more vibrations from the ambient supply than the inactive surrounding regions. Over time, the synapse region grows structurally — more presynaptic store molecules, more postsynaptic receivers — while inactive regions decay back to baseline.

This phase ships the tools to measure that growth. The four properties to look for:

- **Spatial structure:** synapse occupies a definite cleft region between two neurons
- **Activity-dependent release:** sender activity correlates with mobile-molecule presence in the cleft
- **Activity-dependent strengthening:** repeated co-activity grows the count of nodes in the synapse region
- **Inactivity-dependent decay:** unused synapses lose nodes faster than they gain

The substrate is unchanged. We are observing what the existing rules produce in the configurations that constructed synapses establish.

## 2. Operational definition

A **synapse candidate** in a snapshot is a pair of neuron candidates `(N_pre, N_post)` and a **cleft region** between them satisfying:

- **Pairwise distance:** `D = ||centre_pre − centre_post||` lies in `[D_min, D_max]`. Defaults: `D_min = 2 · r_compact`, `D_max = 5 · r_compact` (where `r_compact` is the Phase 4 compactness radius). At default `r_compact = 8.0`, that's `D ∈ [16, 40]`.
- **Axis alignment:** `N_pre`'s outlet axis points within ±30° of the direction from `N_pre`'s centre to `N_post`'s centre. `N_post`'s inlet axis points within ±30° of the reverse direction.
- **Cleft region:** the cylindrical region between `N_pre`'s outlet sub-sphere and `N_post`'s inlet sub-sphere, with radius `r_cleft = 0.4 · r_compact` (default 3.2 units) and length equal to `D` minus the two sub-sphere radii.

A synapse is **active** in a time interval if both `N_pre` and `N_post` register at least one firing event each during that interval.

## 3. Plasticity measurement

Given a *sequence* of snapshots and a synapse definition, the measurement tool extracts:

- **Cleft mobile-node count over time** — count of free vibrations + mobile low-level nodes inside the cleft cylinder per snapshot.
- **Presynaptic store count over time** — count of level-5+ molecules within `r_io` of `N_pre`'s outlet centre.
- **Postsynaptic receiver count over time** — symmetric for `N_post`'s inlet.
- **Mean store + receiver growth rate** — slope of (store + receiver) count over time, in nodes per simulated second.
- **Active vs inactive growth comparison** — split the snapshot sequence into windows where `N_pre` and `N_post` were co-firing vs windows of silence; report the growth rate in each. *A positive Hebbian signal is `growth_active > growth_inactive`.*

These metrics let calibration sessions answer whether the substrate-level emergent plasticity (§4.7 ambient capture) actually concentrates structure at the synapse during co-activity.

## 4. Construction tool — `tools/construct_synapse.py`

```python
def construct_synapse(world, pre_centre, post_centre, neuron_radius=6.0,
                     n_atoms_per_neuron=8, n_molecules_per_neuron=6,
                     n_cleft_molecules=4, n_presynaptic_store=6,
                     n_postsynaptic_receivers=6):
    """Place two neurons connected by an initial synapse.

    Internally calls construct_neuron twice with axes pointing at each other,
    populates the cleft with `n_cleft_molecules` mobile molecules,
    populates the presynaptic store and postsynaptic receivers.

    Returns dict with:
      - 'pre_neuron': info from construct_neuron(pre)
      - 'post_neuron': info from construct_neuron(post)
      - 'cleft_centre': midpoint between the two centres
      - 'cleft_radius': radius of the cleft cylinder
      - 'cleft_node_indices': k_pos indices of mobile molecules in cleft
      - 'presynaptic_store_indices': indices of molecules in pre's outlet region
      - 'postsynaptic_receiver_indices': indices of receivers in post's inlet region
    """
```

The CLI: `python tools/construct_synapse.py --output synapse.npz --pre-centre 50,50,50 --post-centre 90,50,50 [...other knobs]`.

## 5. Detection tool — `tools/detect_synapses.py`

```python
def detect_synapses(world, neurons=None, *,
                  d_min=None, d_max=None, axis_tolerance_deg=30.0):
    """Find synapse candidates in the world.

    `neurons` is an optional list returned by detect_neurons; if None, runs
    detect_neurons with defaults.

    Returns: list of candidate dicts with fields:
      - 'pre_index': index in `neurons` of the presynaptic candidate
      - 'post_index': index in `neurons` of the postsynaptic candidate
      - 'distance': pairwise neuron centre distance
      - 'axis_alignment_deg': angular alignment of pre's outlet with the cleft direction
      - 'cleft_centre', 'cleft_radius', 'cleft_length': geometry
      - 'cleft_node_count': total mobile nodes currently in the cleft
      - 'is_synapse_candidate': passes all geometric tests
    """
```

## 6. Plasticity measurement tool — `tools/measure_synapse_plasticity.py`

```python
def measure_plasticity(snapshot_paths, synapse_def, neuron_pre_def,
                      neuron_post_def, activity_window_s=1.0):
    """Track plasticity-relevant counts across a snapshot sequence.

    Returns: dict with
      - 'times': list of timestamps
      - 'cleft_count_per_step': mobile-node count in cleft per snapshot
      - 'presynaptic_store_per_step': store count per snapshot
      - 'postsynaptic_receivers_per_step': receiver count per snapshot
      - 'pre_active_intervals': time intervals when pre fired
      - 'post_active_intervals': time intervals when post fired
      - 'co_active_intervals': time intervals when both fired within activity_window_s of each other
      - 'growth_rate_active': mean (store+receiver) growth slope during co-active intervals
      - 'growth_rate_inactive': symmetric for inactive intervals
      - 'hebbian_signal': growth_rate_active - growth_rate_inactive (positive = Hebbian)
    """
```

## 7. Tests

### `tests/test_construct_synapse.py`

| Test | Asserts |
|---|---|
| `test_construct_basic` | Two neurons constructed at the right positions; correct atom + molecule + cleft + store + receiver counts |
| `test_axes_point_at_each_other` | `pre.outlet_axis` and `post.inlet_axis` point along the centre-centre line within tolerance |
| `test_cleft_population` | n_cleft_molecules nodes in cleft region |
| `test_construct_then_detect_round_trip` | After construction, detect_synapses returns the pair as is_synapse_candidate=True |

### `tests/test_detect_synapses.py`

| Test | Asserts |
|---|---|
| `test_two_far_neurons_not_synapse` | Two neurons at D > D_max → no candidate |
| `test_two_close_misaligned_neurons_not_synapse` | Distance OK but axes misaligned → fails axis_alignment |
| `test_constructed_synapse_detected` | Constructed synapse passes detect_synapses |
| `test_lone_neuron_no_synapse` | Single neuron, no second cluster → no candidate |

### `tests/test_measure_synapse_plasticity.py`

| Test | Asserts |
|---|---|
| `test_no_activity_no_co_active_intervals` | Snapshot sequence with no firing → empty activity intervals, signal=None |
| `test_unilateral_firing_no_co_active` | Only pre fires → no co-active interval |
| `test_synthetic_growth_during_co_activity` | Hand-crafted store+receiver counts that grow during co-active intervals → positive Hebbian signal |
| `test_decay_during_inactivity` | Inactive intervals show negative growth → captured as growth_rate_inactive < 0 |

## 8. Acceptance criteria

This spec is satisfied when:

1. `pytest tests/test_construct_synapse.py tests/test_detect_synapses.py tests/test_measure_synapse_plasticity.py` is green.
2. `tools/construct_synapse.py` runs end-to-end and produces a snapshot whose synapse passes detection.
3. `tools/detect_synapses.py` correctly distinguishes synapse pairs from random neuron pairs.
4. `tools/measure_synapse_plasticity.py` runs over any snapshot sequence and returns the documented dict shape.

The CONCEPT.md v2 §5 Phase 5 acceptance criterion (repeatedly co-active synapses develop measurably stronger connections under simulation) is **empirical** and not part of this spec's deliverable. It is the central question of the calibration work that follows.

## 9. Open thermodynamic question (per CONCEPT.md §6.5)

CONCEPT.md v2 §6.5 explicitly flags that the parameter regime in which Hebbian plasticity holds — strengthening on minute-scale co-activity, weakening on minute-scale inactivity, ambient density bounded indefinitely — may not exist for our natural laws. If session-N calibration with this scaffolding never produces `hebbian_signal > 0` on co-active synapses, the honest finding is that the substrate is insufficient and additional rules are needed.

That outcome is informative, not a failure of this spec.

## 10. Out of scope

- Networks of more than 2 neurons (Phase 6).
- Neurotransmitter-receptor specificity beyond frequency compatibility (Phase 5+ amendment, if the basic mechanism works).
- Membrane-bound synapses that require closed shells from Phase 3.
- GPU acceleration (the scaffolding works on CPU; long-duration plasticity sweeps will need GPU per CONCEPT.md §10.6).

## 11. Implementation order

1. `tools/construct_synapse.py` (uses `construct_neuron` twice + cleft + store + receivers)
2. `tools/detect_synapses.py` (geometric pair-test on detect_neurons output)
3. `tools/measure_synapse_plasticity.py` (longitudinal counts + activity windows + slope comparison)
4. Tests for all three
5. Smoke run: construct synapse, run forward 30 s, measure plasticity, document
6. Decide on Phase 6 scaffolding shape based on what we learn

# Phase 7 — Attention and Selection Design Specification

**Status:** Draft for review (scaffolding only; emergent attention is an open research question)
**Date:** 2026-05-06
**Source:** [`docs/CONCEPT.md`](../../CONCEPT.md) v2 §5 Phase 7; theoretical roots in Fries (2005, 2015) Communication-through-Coherence
**Precondition:** Phases 4–6 scaffolding shipped; Phase 5 plasticity acceptance pending; Phase 6 cognitive function pending.

**Scope:** Define what "attention via carrier-frequency selection" means operationally in this 3D substrate. Build measurement tools that, given a firing matrix and a candidate carrier frequency, identify which neurons resonate with the carrier and quantify the network's attentional selectivity. Build a synthetic-firing generator for testing. Whether the natural laws produce such selectivity *spontaneously*, given a hypothesised global carrier mechanism, is the research question. **No substrate change.**

---

## 1. Goal

Phase 7 makes "attentional selection" testable. CONCEPT.md v2 §5 Phase 7 names three properties:

- **Global carrier frequency** — a hypothesised ambient oscillation against which clusters can synchronise
- **Selective amplification** — neurons whose intrinsic firing rhythm matches the carrier are amplified
- **Lateral inhibition** — non-resonating clusters are damped

The scaffolding doesn't *implement* the carrier. It assumes the substrate (or an external modulation mechanism) is producing some global rhythm at frequency `f_c`, and provides tools to ask: *given the firing data, which neurons resonate, and how selective is the network?*

If the firing histories of a calibrated network show measurable resonance with any candidate carrier, Phase 7 has emergent attention. If they don't, the substrate is insufficient and the candidate mechanism (e.g., global ambient oscillation, lateral coupling) needs amendment.

## 2. Operational definition

A network exhibits **attentional selectivity at carrier frequency `f_c`** if:

- **Per-neuron resonance score** `r_i = corr(firing_history_i, carrier_signal(f_c))` is significantly higher for some neurons than others. The carrier signal is `sin(2π · f_c · t)` evaluated at each snapshot timestamp.
- **Selectivity index** `S = std(r_1, …, r_n) / mean(|r_1|, …, |r_n|)` — high value means the network has clearly preferred resonators; low value means uniform response.
- **Resonating subset** = neurons with `r_i > θ_r` (threshold, default 0.3). The subset is the network's "attended" set at carrier `f_c`.
- **Phase coherence** — among the resonating subset, the variance of their phase offsets relative to the carrier is small.

A network with high `S` *and* a coherent phase-aligned subset is exhibiting attention-like behaviour. The four properties together are the empirical signature.

## 3. Measurement tool — `tools/measure_attention_selectivity.py`

```python
def measure_selectivity(firing_matrix, times, carrier_frequency,
                       resonance_threshold=0.3):
    """Compute per-neuron resonance scores and the network's selectivity.

    `firing_matrix`: T×N int array (firing per snapshot per neuron)
    `times`: T-length array of simulated timestamps
    `carrier_frequency`: float, in Hz of simulated time

    Returns dict:
      - 'resonance_scores': N-length array of per-neuron resonance values
        (Pearson correlation between firing history and carrier signal)
      - 'resonating_indices': subset of neurons with r_i > threshold
      - 'selectivity_index': std/mean of |resonance_scores|
      - 'phase_offsets': N-length array of best-fit phase offsets
        (radians) for each neuron's firing relative to the carrier
      - 'phase_coherence': 1 − circular variance of phase offsets among
        resonating subset (1.0 = perfectly aligned, 0.0 = uniform)
    """
```

The phase offset for neuron `i` is computed by maximising the correlation between `firing_history_i` and `sin(2π · f_c · t + φ)` over `φ ∈ [0, 2π]`. Coarse grid search at 16 phase values is sufficient for first-pass measurement.

## 4. Synthetic-firing generator — `tools/synthesize_carrier_firing.py`

```python
def synthesize_carrier_firing(n_neurons, n_snapshots, dt, carrier_frequency,
                            resonating_indices, phase_offsets,
                            firing_probability_resonating=0.6,
                            firing_probability_silent=0.05):
    """Generate a synthetic T×N firing matrix where listed neurons fire on
    the carrier rhythm with given phase offsets, others fire at baseline rate.

    Used to validate measure_selectivity: given known resonating indices and
    phase offsets, the measurement should recover them.
    """
```

CLI: `python tools/synthesize_carrier_firing.py --output firing.json --n-neurons 8 --n-snapshots 100 --dt 0.1 --carrier-frequency 2.0 --resonating-indices 1,3,5`.

## 5. Tests

### `tests/test_measure_attention_selectivity.py`

| Test | Asserts |
|---|---|
| `test_uniform_silent_network_low_selectivity` | All neurons silent → selectivity_index ≈ 0 |
| `test_one_resonator_in_silent_network_high_selectivity` | 1 of 5 fires on carrier rhythm, others silent → resonating_indices includes only that one |
| `test_synthesised_resonators_recovered` | Synthesise 3 of 8 with known phase offsets → measure recovers the 3 indices and approximate phases |
| `test_phase_coherence_aligned_resonators` | Synthesised neurons all in-phase (offset 0) → phase_coherence > 0.9 |
| `test_phase_coherence_misaligned_resonators` | Synthesised neurons with random phase offsets → phase_coherence < 0.3 |

### `tests/test_synthesize_carrier_firing.py`

| Test | Asserts |
|---|---|
| `test_shape_and_dtype` | Output is T×N int array |
| `test_resonating_neurons_have_higher_firing_rate` | Resonating neurons fire more often than silent ones |
| `test_silent_neurons_baseline_rate` | Silent neurons fire at approximately the baseline probability |

## 6. Acceptance criteria

This spec is satisfied when:

1. `pytest tests/test_measure_attention_selectivity.py tests/test_synthesize_carrier_firing.py` is green.
2. `tools/measure_attention_selectivity.py` runs over any firing matrix and returns the documented dict shape.
3. `tools/synthesize_carrier_firing.py` produces firing matrices that the measurement tool correctly classifies.

The CONCEPT.md v2 §5 Phase 7 acceptance criterion (a global modulation can selectively determine which parts of a network are active) is **empirical** and requires:
1. A working Phase 6 network producing measurable firing histories
2. A candidate carrier-frequency mechanism (either substrate amendment or external observation of natural rhythms)
3. Measurement showing significant selectivity at that frequency

The tooling makes step 3 possible. Steps 1 and 2 are downstream of session-N+ calibration that satisfies Phase 5 plasticity.

## 7. Out of scope

- Implementing a global carrier in the substrate (would be a CONCEPT.md amendment).
- Lateral inhibition between non-resonating neurons (a substrate-level coupling rule).
- Dynamic attention switching (carrier frequency changing during a run; for now we test against fixed `f_c`).
- Fourier-spectrum analysis beyond a single candidate carrier (extensible later).

## 8. Implementation order

1. `tools/synthesize_carrier_firing.py` (simpler; produces test data)
2. `tools/measure_attention_selectivity.py` (uses scipy-free numpy + correlation + phase grid search)
3. Tests for both (the synthesise → measure round trip is the keystone)
4. Smoke run: synthesise a 5-neuron network with neuron 0 resonating at 2 Hz with phase 0, measure → recovers neuron 0 in resonating_indices

This is the simplest scaffolding deliverable yet because we don't need physical-substrate construction tools. Attention is a property of *firing histories*, not of physical configuration.

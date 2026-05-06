# Code Review — Phase 4–7 Scaffolding (b87254d → 4f5df5a)

**Reviewer:** independent `superpowers:code-reviewer` agent, 2026-05-06
**Repo:** `/Users/mkupermann/Documents/GitHub/EQMOD`
**Tests at review time:** 146 passing in 0.15s

---

## 1. Summary

**Confidence: mixed.** The seven commits land a coherent scaffolding shape (spec → construct → detect → measure → tests, repeated four times) with consistent file organisation, sensible CLI ergonomics, and no missing pieces relative to the spec deliverable list. Tests are green, the eight phases form a clean dependency chain, and the LOGBOOK entries flag known limitations honestly. The shape is correct.

What lowers confidence: several headline tools have implementation issues that would silently produce wrong calibration results.

---

## 2. Critical issues

### C1. `tools/detect_synapses.py` — axis alignment is ignored

The Phase 5 spec §2 requires that pre's outlet axis points within ±30° of the cleft direction. The implementation hard-codes alignment to 0° and unconditionally sets `is_synapse_candidate=True` for any neuron pair within `[D_min, D_max]`. The `axis_tolerance_deg=30.0` parameter is dead. **Status: still open** — fix would require either inferring axis from cluster morphology or accepting the spec drift and amending §2.

### C2. `tools/detect_synapses.py` — every pair reported twice
Iteration was `for j in enumerate(...)` rather than `for j > i`. **Status: FIXED** in this integration commit.

### C3. `tools/measure_neuron_activity.py` — false firing events when output is zero throughout
`firing_threshold = max(1.0, baseline_output * output_threshold_multiplier)` produces threshold 1.0 when baseline is 0, so any single transient registers as a firing event. **Status: FIXED** — added MIN_FIRING_FLOOR=3.

### C4. `tools/measure_neuron_activity.py` — integration lag is mechanically wrong
Spec says "lag between sustained input above input-threshold and the peak output". Implementation uses any input > 0 (no threshold) and picks the most recent preceding sample. **Status: still open** — needs a sustained-input-window detector.

### C5. `tools/detect_networks.py` — broken on constructed networks but never tested
The chain-of-three test uses pre-computed neurons + synapses, bypassing the merged-cluster issue. **Status: still open** — flagged in Phase 5 spec as "needs density-based clustering"; no end-to-end test on real snapshots yet.

### C6. `tools/measure_synapse_plasticity.py` — `slopes_active` collected start times, not slopes
List comprehension `[s for s, e in co_active for slope in [...] if slope is not None]` yielded `s` (start time) instead of `slope`. The Hebbian signal was silently meaningless. **Status: FIXED** + regression test added (`test_growth_rate_active_is_actual_slope_not_window_start`).

---

## 3. Important issues

### I1. `_co_active_windows` returned convex hull when starts were within max_lag
Including the silent gap between two non-overlapping firings as "active". **Status: FIXED** — now reports the union, not the convex hull.

### I2. `_slope_in_window` doesn't suppress numpy RankWarning on constant windows
**Status: still open** (cosmetic).

### I3. `measure_attention_selectivity` clips Pearson correlation to ≥ 0
Changes the formal definition of resonance score. **Status: still open** — minor spec drift.

### I4. `score_pattern_recognition` Hamming convention inverted
Spec says "0 = perfect match"; implementation returns similarity (1 = perfect). **Status: still open** — needs spec wording update.

### I5. `detect_networks` neuron_indices semantics are arbitrary
Picks first member index per cluster. **Status: still open** — cosmetic.

### I6. Phase grid resolution: 16 may misclassify near-threshold neurons
**Status: still open** — recommended bumping default to 32.

### I7. Round-trip detection test for synapses was relaxed to "≥1 neuron"
**Status: still open** — papers over the merged-cluster issue rather than fixing it.

### I8. → C6 (promoted)

---

## 4. Spec-vs-implementation gaps per phase

| Phase | Critical Issues | Status After Integration |
|---|---|---|
| 4 (neurons) | C3, C4 | C3 fixed; C4 open |
| 5 (synapses) | C1, C2, C6, I1 | C2/C6/I1 fixed; C1 open |
| 6 (networks) | C5, I4 | both open |
| 7 (attention) | I3, I6 | both open |

---

## 5. Recommendations (priority order)

1. ✅ **C6** — fix slope-collection comprehension. **Done.**
2. **C1** — implement axis alignment in `detect_synapses` or amend Phase 5 spec.
3. **C5** — implement DBSCAN-style density clustering for `detect_neurons`.
4. ✅ **C3** — firing-event zero-baseline floor. **Done.**
5. ✅ **C2** — deduplicate `detect_synapses` results. **Done.**
6. ✅ **I1** — `_co_active_windows` union vs convex hull. **Done.**
7. **C4** — sustained-input-window detection for integration lag.
8. **I7** — restore the spec'd round-trip test once C5 lands.
9. **I3, I4, I6** — minor spec/code reconciliation.

The scaffolding is structurally complete and tests are green. After this integration pass, four of the six critical issues are fixed; the remaining two (C1 axis alignment and C5 DBSCAN) require non-trivial implementation work.

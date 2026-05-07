# Plan A — Pre-registration Decision Claim

**Date:** 2026-05-06  
**Branch:** feat/baby-brain-plan-A  
**Status:** Pre-registered before Task 9 (acceptance run)

---

## Hypothesis under test

Plan A bears on **CONCEPT.md §8 H5 — Plasticity from repeated activity,
thermodynamically bounded**.

H5 verbatim (CONCEPT.md §8, line 371):

> Clusters that are repeatedly co-active develop a measurably stronger synaptic
> connection than random cluster pairs. This strengthening manifests in the
> physical configuration of the synapse region. The ambient vibration field
> maintains bounded steady-state density throughout — *this stability is itself
> part of what the hypothesis claims.*

---

## Routing decision: F2 routes to H5, not H2

Plan A tests the **substrate-statistics weak form** of H5: molecule-density at
the input location as a proxy for "connection strength" in H5's full claim.

**F2 (activity-coupled growth)** — not F2-style spatial sorting — is the
falsification candidate for H5's weak form.

H2 is about spatial sorting by frequency order of magnitude, driven by §4.6
scale repulsion. F2 tests activity-coupled structural growth, which is H5
territory.

---

## Decision logic

If F2 passes on the held-out seed grid: H5 is supported (substrate-statistics
weak form).

If F2 fails: H5's weak form is **falsified for this substrate
parameterisation**, and the project's next move is either (a) propose a CONCEPT
amendment that changes the binding rules, or (b) accept that H5's weak form is
wrong as stated and revise §8.

---

## Implementation pointers

| Artefact | Path |
|---|---|
| Acceptance thresholds + seed grid | `tests/acceptance.toml` |
| F2 test (activity-coupled growth) | `tests/test_substrate_growth_e2e.py::test_F2_activity_coupled_growth_at_input_location` |
| Full acceptance suite (F1–F5) | `tests/test_substrate_growth_e2e.py` |

---

## Seed provenance

- **Calibration seeds:** {42, 43, 44} — used during development to set config
  defaults. Results on these seeds are not reported as acceptance evidence.
- **Held-out seeds (10):** {7, 100, 314, 999, 2024, 17, 77, 256, 512, 1337} —
  never used during config tuning; the actual acceptance contract per
  `tests/acceptance.toml` `[seeds]`.

Provenance note from `tests/acceptance.toml`: `acceptance.toml` was committed
after config-tuning commits `f0f8911` and `7bc2412`. Calibration seeds were
used implicitly during that search; held-out seeds were never used during
tuning. See `[provenance]` block in `acceptance.toml` for the full record.

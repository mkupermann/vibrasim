# JEP-465 — Does cloud dimension D raise the energy model's affect ceiling?

## Motivation
JEP-463/464 located the energy model's affect ceiling over VSA clouds (~order 2) and attributed it to
the cloud representation (superposition noise), not the learner. The actionable follow-up: is the cloud
DIMENSION D a knob? Higher D reduces superposition crosstalk (each slot feature is cleaner in the
bundle — VSA capacity scales with D, JEP-294), which might lift the order-3 signal the reservoir is
currently losing (0.63). If order-3 accuracy rises with D, "use bigger clouds for richer affect" is a
concrete lever; if flat, the ceiling is the reservoir's order-3 representational limit, independent of D.

## Method (`tools/run_jep465_dimension_vs_affect.py`)
Order-3 balanced parity affect over VSA clouds (as JEP-463), `ValenceReservoirLearner` (600 random
features), seeds 0 & 7. Sweep cloud dimension D ∈ {4096, 8192, 16384}; report held-out accuracy vs D.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J465a (baseline):** D=4096 held-out ∈ [0.55, 0.72], both seeds (reproduces JEP-463's order-3 ≈ 0.63).
- **J465b (does D help?):** D=16384 held-out ≥ D=4096 + 0.10, both seeds → bigger clouds raise the
  affect ceiling (the knob works). [If this fails, D is NOT the knob — the ceiling is the reservoir's
  order-3 limit.]
- **J465c (report the trend):** state whether accuracy rises monotonically with D and whether D=16384
  crosses 0.80 (a usable order-3 affect).

Honest expectation: genuinely uncertain — higher D cleans the signal (could help) but the reservoir's
fixed 600 features cap order-3 regardless (could stay flat). PASS = D is a usable lever for richer
affect. NULL = the ceiling is dimension-independent (the reservoir's order-3 limit) — also informative.
Bars locked; no retuning. Established methods (VSA/HRR + reservoir/RLS), named. No transformer.

## RESULT (2026-06-05): NULL — D is NOT the lever (the ceiling is reservoir capacity, D-independent)

| seed | D=4096 | D=8192 | D=16384 |
|------|--------|--------|---------|
| 0 | 0.640 | 0.613 | 0.623 |
| 7 | 0.645 | 0.592 | 0.643 |

J465a ✓ (baseline ~0.63), **J465b ✗ (D=16384 ≈ D=4096, flat) → NULL.** Accuracy is flat across a 4×
increase in dimension.

**Honest finding — the affect ceiling is dimension-independent.** Increasing cloud dimension from 4096
to 16384 does NOT raise the order-3 affect ceiling (stays ~0.63). So the bottleneck is NOT superposition
crosstalk (which more D would reduce) — it is the RESERVOIR'S random-feature capacity for the order-3
interaction (600 random features cannot span the degree-3 structure, the JEP-429 C(P,k) cost). Two knobs
now ruled out for the deployed energy model's affect ceiling: the LEARNER (JEP-464, node perturbation
worse) and the DIMENSION (JEP-465, flat). The remaining lever is the reservoir's number of FEATURES (its
main hyperparameter) — tested in JEP-466. Established methods, named; a measurement, not new science.

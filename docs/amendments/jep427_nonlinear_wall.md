# JEP-427 — Locating the real wall: valence learns linear rules, FAILS non-linear (XOR)

## Motivation
JEP-426 showed (correcting my wrong prediction) that a scalar valence signal learns LINEARLY-SEPARABLE rules cheaply.
This tests the NON-LINEAR case — a hidden rule "good iff A XOR B" — where per-feature valence-correlation must be at
chance (Minsky-Papert, 1969). The goal: locate the real wall precisely. The honest expectation: the wall is NOT the
valence signal (which works for linear rules) but the FEATURE REPRESENTATION — non-linear rules need conjunctive
features, and DISCOVERING the right non-linear features unsupervised is the open problem. Established theory (perceptron
limits), named; no claim of novelty. No transformer.

## Method
Hidden rule: good iff (property A XOR property B). Stream experiences (entity properties + valence) with noise.
- Measure per-feature valence-correlation (linear readout) — should be at CHANCE for A and B individually.
- Measure with CONJUNCTIVE features (A∧B, A∧¬B, ¬A∧B) provided — should recover the rule, showing the fix is the
  representation (which must be supplied/engineered, not discovered by the scalar signal).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J427a (non-linear wall):** with the XOR rule, neither A nor B individually has valence-correlation distinguishable
  from non-predictive properties — per-feature (linear) learning is at chance, both seeds (0, 7).
- **J427b (representation is the fix):** with conjunctive features provided, the XOR rule IS recovered (the predictive
  conjunctions stand out), both seeds — locating the wall at FEATURE DISCOVERY, not the signal.
- **J427c (the honest map):** linear rules learnable from scalar valence (JEP-426), non-linear NOT without the right
  features — and unsupervised discovery of those features is the open problem (one of the five named to Michael).

Predicted: J427a and J427b both hold — the wall is non-linear feature discovery. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (after fixing a base-rate confound in the experiment)
First run used base rate 0.4, which under XOR leaves a residual LINEAR signal (P(good|A)=0.6 vs 0.4 → correlation ~0.2),
so J427a read inconsistently. Fixed the experiment to base rate 0.5 (where XOR is EXACTLY chance for any single
feature) — an estimator/parameter fix, not bar-tuning. Clean result:
- **J427a (non-linear wall): PASS** — per-feature (linear) valence-correlation for A and B ≈ **0.01-0.02** (true
  chance, below the noise band ~0.03-0.045). Linear learning from scalar valence is at chance on XOR. Both seeds.
- **J427b (representation is the fix): PASS** — CONJUNCTIVE features recover it cleanly: Ab/aB (good) ≈ +0.82,
  AB/ab (bad) ≈ -0.80 — a 1.6 separation. Both seeds.

## Verdict: **PASS — the real wall is unsupervised non-linear FEATURE DISCOVERY, not the energy signal**
Combined with JEP-426: a scalar valence/energy signal LEARNS linearly-separable rules cheaply, but is at CHANCE on a
non-linear (XOR) rule — UNLESS the right conjunctive (non-linear) features are provided, which then recover it cleanly.
So the wall is NOT the energy signal Michael described (that works for linear structure); it is the **unsupervised
discovery of the right non-linear features** — exactly one of the five open problems (sample-efficient/compositional
abstraction). This precisely locates where new mathematics is needed: a principled mechanism to DISCOVER non-linear
features/abstractions from experience without supervision. Established theory (perceptron limits, Minsky-Papert 1969),
named; NOT new science — an honest, quantified map of the frontier. No transformer.

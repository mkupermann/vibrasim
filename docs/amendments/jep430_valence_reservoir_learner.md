# JEP-430 — Couple the valence signal to a reservoir: energy-driven non-linear learning

## Motivation
JEP-429 showed random nonlinear features (the project's reservoir/ELM) give a tractable route past the non-linear wall.
Build the first INTEGRATED piece of Michael's energy model that actually learns non-linear structure: a learner that
takes experiences (entity property vectors + a valence/energy signal) and learns to PREDICT the valence of NEW entities
via reservoir features + an online linear readout — energy-driven, no enumeration, no labels beyond the scalar energy.
Established (reservoir/ELM + recursive least squares; ties to EQMOD-2), named; no claim of novelty. No transformer.

## Method
`ValenceReservoirLearner`: random nonlinear features φ(x)=tanh(Rx+b); an online least-squares readout maps φ(x) → the
valence sign. Train on a stream of (property-vector, valence) from a non-linear rule (XOR); test valence prediction on
held-out entities. Compare to a raw-linear baseline (chance on XOR).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J430a (energy-driven non-linear learning):** on the XOR rule, the valence-reservoir learner predicts held-out
  valence ≥ 0.85, while the raw-linear baseline is ≈ chance (≤0.60), both seeds (0, 7).
- **J430b (generalization):** the learner predicts the valence of ENTITIES IT NEVER SAW (held-out), not just memorized
  ones — ≥0.85 held-out accuracy, both seeds.
- **J430c (honest residual):** on a 3-way rule it needs more reservoir units for the same accuracy (the JEP-429
  residual) — report it; this is the integrated demonstration, with its honest limit.

Predicted PASS — a working energy-driven non-linear learner (first integrated piece of the energy model). Established
methods, named; the residual (high-order scaling) is the open problem. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J430a (energy-driven non-linear learning): PASS** — the valence-reservoir learner predicts XOR-rule valence at
  **0.90** vs raw-linear **0.49** (chance). Both seeds.
- **J430b (generalization to UNSEEN entities): PASS** — held-out accuracy 0.896-0.902 on entities never experienced
  (not memorization). Both seeds.
- **J430c (honest residual): confirmed** — a 3-way rule needs more reservoir units: M=300 → 0.77-0.79, M=1200 →
  0.86-0.87 (the JEP-429 high-order scaling).

## Verdict: **PASS — first integrated piece of the energy model that learns non-linear structure**
`world/valence_reservoir.py` (`ValenceReservoirLearner`): random nonlinear reservoir features + an ONLINE recursive-
least-squares readout learn to predict the valence/energy of NEW experiences from a non-linear rule — driven only by the
scalar energy signal, no enumeration, no labels. It cracks XOR (0.90) where a linear readout is at chance, and
generalizes to unseen entities. This couples Michael's affective-energy signal to the project's reservoir, giving a
working energy-driven non-linear learner. Honest: all established (reservoir/ELM — Rahimi-Recht; RLS), named — NOT new
science; the residual (units grow with interaction order) is the open problem (principled high-order discovery). A
constructive close to the frontier arc: the energy model now learns non-linear structure, tractably. No transformer.

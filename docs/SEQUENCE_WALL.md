# The Sequence-Prediction Wall (EQMOD-2, consolidated 2026-05-31)

## What works (BET-110–113, all PASS)
A modular, energy-based, geometric, self-supervised, NON-transformer learning
system that genuinely learns:
- content-addressable associative memory (completion 0.995),
- capacity that scales linearly with size (~0.095·N),
- error-correcting recall (basin ~25% flipped bits),
- single-sequence next-state prediction (A→E exact) — a predictive world-model
  primitive.

This is real learning, built only from local Hebbian/energy rules.

## What does NOT work (BET-114–118, NULL)
Holding MULTIPLE overlapping, context-dependent sequences at once — recalling each
without cross-talk. Tried and failed: more capacity (N up to 400), context tags,
sparse distributed codes. Recovery stalls at ~0.6–0.74 (need ≥0.9); capacity
helps only marginally.

## The finding
The binding wall is the **sequence-prediction MECHANISM**, not capacity. A
pairwise Hebbian transition matrix superimposes overlapping chains and cannot
disambiguate them; this is intrinsic to second-order (pairwise) associative
dynamics. Capacity (N) is necessary but far from sufficient.

## Why this answers the written-language question
Written language is the EXTREME case of overlapping, context-dependent sequences
(millions of context-specific next-token paths). So:
- The capacity to *store* a vocabulary is feasible (N ~ 10⁵–10⁶ with sparse
  modular connectivity), but
- **You cannot reach written language by scaling N.** The context-dependent
  prediction mechanism is the wall, and the transformer-free, pairwise-associative
  mechanisms tried here do not break it.

Crossing this wall needs a fundamentally stronger predictor — compositional,
higher-order, or with inferred latent context (e.g. deep predictive coding) — and
doing that without attention/backprop is the genuine open research problem. That
is the honest boundary of this paradigm, established with data, not assertion.

# Cognition Programme Summary (EQMOD-2, BET-110 → 130)

Consolidated end-state of the autonomous run that, after the memory programme hit
its structural ceiling (see MEMORY_PROGRAMME_SUMMARY.md), redesigned around an
engineered modular scaffold with emergent dynamics and pursued the real goal:
a substrate that can move toward written language by GENERALIZING BY ITSELF and
LEARNING ONLINE — with NO LLM, NO transformer, no pretraining. Written 2026-05-31.

## What was SOLVED

1. **Content-addressable energy memory (BET-110-113).** Modular Hopfield-style
   EnergyNet: capacity ~0.1·N, error-correcting recall (basin of attraction),
   single-sequence prediction via an asymmetric transition operator.
2. **Multi-sequence storage without interference (BET-121).** Least-squares
   (projection) transition learning replaces Hebbian outer-products — stores many
   overlapping sequences with near-zero cross-talk; order-K context replays
   arbitrary text. KEY framing finding (BET-117): capacity N is NOT the language
   blocker — the prediction MECHANISM is. Memorization cannot generalize.
3. **Online learning, mathematically (BET-124).** The substrate's random modular
   projection + nonlinear activation IS a random feature map φ(x)=tanh(Rx). A linear
   readout on φ generalizes to unseen inputs (held-out R²=0.999 vs linear-baseline
   0.312) and is learned ONLINE in closed form via recursive least squares — every
   example refines the same ridge solution, no replay, no backprop. (world/reservoir.py)
4. **Systematic symbolic-combination generalization (BET-126 → 130).** Composing
   symbols with ANALOG VSA (bind + non-sign bundle) and reading out online, the
   substrate generalizes a RELATION (v[i]>v[j]) to NOVEL symbol pairs it never saw:
   **90.6%** at M=20 (BET-130), with no-binding and shuffled-label controls always
   collapsing to chance. This is the property language needs that memorization lacks.

## The law that governs it (the central finding)

Systematic generalization is a **CURRICULUM LAW**: held-out accuracy rises
monotonically with the NUMBER OF COMPOSITIONS EXPERIENCED (BET-129 M=14: 0.68→0.88;
BET-130 M=20: crosses 0.906, still climbing). It is NOT governed by dimension D or
normalization (BET-127/128 NULL — refuted). "The substrate learns from every
interaction" is therefore literal and measured: each new composition raises
generalization to unseen ones.

## Honest boundaries (pre-registered NULLs that taught the most)

- BET-125 NULL: systematic generalization does NOT fall out of sign-bundled VSA +
  reservoir (~0.64). The sign() clamp was the culprit (fixed by analog bundle).
- BET-127/128 NULL: bigger D and code-normalization do NOT help — experience does.
- BET-130 T130c: the curriculum curve has NOT saturated by 300 compositions — more
  experience keeps helping (a good boundary, not a failure).
- Demonstrated on a linearly-recoverable relation; reservoir ≈ linear here.
  Real written-language next-symbol prediction over a vocabulary is the open
  frontier (BET-131+).

## Reusable patterns surfaced

- docs/patterns/substrate_reservoir_online.md — emergent generalization + online RLS.
- docs/patterns/systematic_generalization.md — analog VSA + online readout +
  curriculum law, with the controls that must collapse.

## Honest answer to the strategic question

A substrate that communicates in language, generalizes ITSELF, and learns online is
NOT blocked by capacity or by needing a transformer. The pieces are now in hand and
measured: substrate-native composition (analog VSA), a substrate-native online
self-generalizing readout (reservoir/RLS), and a measured curriculum law tying
generalization to experience. The remaining work is to point this engine at actual
written symbols and scale the experience — engineering and curriculum, not a missing
mechanism. NO LLM, NO transformer was used or needed.

## Next direction

BET-131+: replace the relational toy target with real written-language next-symbol
prediction over a small vocabulary — VSA-composed context codes → online reservoir
readout → next symbol — and measure held-out generalization to novel contexts and
online improvement per interaction. This is the bridge from "generalizes a relation"
to "communicates in writing."

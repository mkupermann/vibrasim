# JEP-442 — The non-local upper bound: does LEARNED (backprop) feature discovery escape C(P,k)?

## Status of this experiment (scope honesty)
This is a **reference-baseline measurement, NOT an adopted substrate mechanism.** The substrate's
energy model uses reservoir + online RLS (no backprop), per CLAUDE.md. JEP-442 measures what a
*learned* 2-layer net (full backprop, non-local credit assignment) does on the exact case where every
cheap/local route failed (JEP-438→441), to (a) confirm the frontier claim "only targeted/learned
features escape the combinatorial cost" and (b) sharpen the open problem to precisely **local vs
non-local**. Backprop is the comparison upper bound here, not part of the solution. No transformer.

## Method (`tools/run_jep442_backprop_reference.py`)
Order-3 parity `y = x0·x1·x2`, bipolar, P=18 (where flat/deep random features maxed ~0.73), N=2500
train / 1000 test, seeds 0 & 7. A 2-layer net (hidden tanh, M units, linear output) trained by
plain gradient descent (numpy, MSE to ±1). Compare:
- **learned (backprop):** M=64 hidden units, ~2000 epochs.
- **random (matched M=64):** same architecture, first layer FROZEN random + ridge readout (the
  JEP-439 flat baseline at this M).
- **interpretability:** permutation feature-importance on the learned net — drop in accuracy when each
  input feature is shuffled; the 3 true features {0,1,2} should dominate.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J442a (learned features escape the combinatorial cost):** backprop net held-out ≥ 0.95 with only
  M=64 ≪ C(18,3)=816 units, both seeds.
- **J442b (the gap is LEARNING, not capacity):** matched-M random features ≤ 0.70 held-out, both seeds
  (same architecture, only the first layer learned-vs-random differs).
- **J442c (it found the interaction):** the top-3 permutation-importance features are exactly {0,1,2},
  both seeds.

Predicted PASS: backprop cracks order-3 parity with few units and concentrates on the true triple,
where matched random features fail — so the escape is *learning the features*, which is the non-local
route. This makes the open problem precise: match this with a LOCAL rule. NULL if J442a fails (even
backprop struggles at this M/epochs — would need more) — honest. Bars locked; no retuning. The
substrate path remains backprop-free; this is a measurement only.

## RESULT (2026-06-05): **PASS** (prediction HIT)

| seed | backprop (M=64) | matched random (M=64) | top-3 features |
|------|-----------------|------------------------|----------------|
| 0 | 1.000 | 0.533 | [0, 1, 2] ✓ |
| 7 | 1.000 | 0.544 | [0, 1, 2] ✓ |

J442a ✓ · J442b ✓ · J442c ✓ → **PASS, both seeds.**

## Verdict: the gap is non-local LEARNING, and it is targeted
A learned 2-layer net cracks order-3 parity perfectly with only **M=64 ≪ C(18,3)=816** units and its
permutation-importance concentrates on exactly the true triple {0,1,2} — it *found the interaction*.
A matched-capacity random-feature net (same M=64, first layer frozen) is at chance (0.53). So the
escape from the combinatorial wall is **learning the features** (gradient-targeted), not capacity and
not enumeration. This closes the frontier map with its upper bound: cheap/local routes fail
(JEP-438→441), targeted enumeration is O(C(P,k)) (JEP-438), and *learned* features escape cheaply but
require **non-local** credit assignment (backprop, measured here).

**The open problem, now fully pinned:** match this learned, targeted, sub-combinatorial discovery
with a LOCAL rule (e-prop / equilibrium-propagation). Backprop is the reference upper bound only — the
substrate path stays backprop-free (reservoir + online RLS). Established methods; measurement, not a
new mechanism.

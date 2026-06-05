# JEP-443 — Toward locality: does feedback alignment (no weight transport) escape the order-k wall?

## Scope honesty
Still a reference-baseline probe, not an adopted substrate mechanism. JEP-442 showed full backprop
cracks order-3 parity (M=64, finds the triple) where cheap/local routes fail — but backprop needs
**weight transport** (the backward pass uses the exact forward weights `w2`), which is the least
biologically-plausible part. Feedback alignment (Lillicrap et al. 2016) replaces `w2` in the backward
pass with a FIXED RANDOM feedback vector `B`, removing weight transport — a step toward locality.
JEP-443 asks: does that still escape the combinatorial wall? It maps how far toward a local rule the
escape survives. The substrate path stays backprop-free regardless. No transformer.

## Method (`tools/run_jep443_feedback_alignment.py`)
Identical to JEP-442 (order-3 parity, P=18, M=64, N=2500/1000, seeds 0 & 7) except the hidden-layer
gradient uses a fixed random feedback `B` instead of `w2`: `dh = outer(do, B) · (1−h²)`. More epochs
allowed (FA aligns gradually). Compare to full backprop (J442) and matched random features.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J443a (FA escapes the wall):** feedback-alignment held-out ≥ 0.90 with M=64, both seeds.
- **J443b (FA finds the interaction):** top-3 permutation-importance features = {0,1,2}, both seeds.
- **J443c (the gap is still learning):** FA ≥ matched-random + 0.20 (same M, random first layer), both seeds.

Honest expectation: genuinely uncertain. FA frequently solves such tasks but can be slower / less
reliable than backprop, and parity (no low-order signal) is a hard alignment case. PASS = J443a–c →
the escape survives removal of weight transport (a more-local rule still discovers the order-3 term).
NULL if J443a fails → weight transport (or full backprop) is needed at this scale; the locality
frontier is tighter than FA. Either way it sharpens where the open "local targeted discovery" problem
bites. Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): NULL — feedback alignment DIVERGED (numerical instability at the pre-set LR)

| seed | FA (M=64) | matched random | note |
|------|-----------|----------------|------|
| 0 | 0.000 | 0.557 | NaN (RuntimeWarning: invalid value in multiply) |
| 7 | 0.000 | 0.546 | NaN |

J443a ✗, J443c ✗ (J443b's "found triple" is spurious — permutation importance on NaN weights) →
**NULL.** This is an **instrument failure, not a scientific answer**: FA's pseudo-gradient (fixed
random feedback B instead of w2) is noisier/larger than backprop's, so LR=0.5 / 6000 epochs blew the
weights up to NaN. Backprop tolerated LR=0.5 (JEP-442); FA does not — a known FA sensitivity. Like
JEP-434's noise mis-scale, the experiment never actually tested the hypothesis.

**Corrected re-run pre-registered as JEP-444:** stable optimizer (LR=0.02 + per-step gradient-norm
clipping), same bars, to get a clean FA answer. The LR is an optimizer hyperparameter (a broken
instrument here), not an acceptance bar — fixing it is not post-hoc tuning.

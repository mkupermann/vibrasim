# HYB-02 — Hybrid decomposes a MIXED rule where neither pure method suffices

## Motivation
HYB-01 escaped the SQ wall but on PURE parity (where GF(2) alone already works). HYB-02 is the genuinely
informative test: a MIXED rule with a low-order part (local-learnable) AND an SQ-hard parity part, where
NEITHER pure method works and the hybrid must DECOMPOSE — local handles the easy part, an algebraic
module discovers the parity from local's own RESIDUAL (boosting-style, general — it is not told which
feature gates). This is the real test of the constructive architecture from JEP-461/HYB-01.

## The mixed rule
`y = +1 if x0 = +1, else parity(x1..x8)` (P=18). Half the inputs are decided by a single feature
(local-trivial); the other half by order-8 parity (SQ-hard). So pure-local ≈ 0.75 (gating half + chance
on parity half); pure-GF(2)-linear fails (the target is not linear over GF(2)).

## Method (`tools/run_hyb02_mixed_rule.py`)
Seeds 0 & 7. (a) raw `ValenceReservoirLearner` on x; (b) pure GF(2) linear solve on the whole target;
(c) HYBRID: train the energy learner on raw x → take its LOW-CONFIDENCE training samples (lower half by
|feel|, NOT told which feature gates) → run GF(2) on that residual subset to discover the parity set s →
augment inputs with φ = ∏_{i∈s} x_i → retrain the energy learner on [x, φ]; evaluate.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **HYB02a (raw local is partial):** raw energy held-out ∈ [0.65, 0.85], both seeds (gets the gating
  half, misses the parity half).
- **HYB02b (pure GF(2) fails on the mixture):** GF(2)-linear-whole ≤ 0.80, both seeds.
- **HYB02c (hybrid decomposes both):** hybrid held-out ≥ 0.93, both seeds — neither pure method does
  this.

Predicted PASS → the energy + algebraic hybrid genuinely DECOMPOSES a mixed rule, recovering the SQ-hard
part from the local learner's own residual where neither pure method can. NULL if HYB02c fails (the
residual does not isolate the parity → the general hybrid needs supervision the toy hides). Bars locked;
no retuning. Established methods (reservoir/RLS + GF(2) + residual/boosting), named — the contribution
is the working decomposition, not new science. No transformer.

## RESULT (2026-06-05): NULL/partial — the decomposition works, but residual isolation is fragile

| seed | raw energy | GF(2)-whole | HYBRID | residual set discovered |
|------|------------|-------------|--------|--------------------------|
| 0 | 0.745 | 0.496 | **0.981** | {1,2,3,4,5,6,7,8} (exact ✓) |
| 7 | 0.759 | 0.497 | 0.756 | {0,2,3,…,17} (garbage ✗) |

HYB02a ✓ (raw partial ~0.75), HYB02b ✓ (pure GF(2) at chance — the mixture is not GF(2)-linear),
**HYB02c ✗ (hybrid 0.981 / 0.756) → NULL/partial.**

**The architecture is proven, the isolation heuristic is not.** Seed 0 decomposed the mixed rule
PERFECTLY — the energy learner's residual cleanly isolated the parity subset, GF(2) recovered the exact
set {1..8}, and the augmented energy learner hit 0.981 (vs 0.745 raw, 0.496 GF(2)). So the hybrid CAN do
what neither pure method can. But seed 7's residual (lower-half by |feel|) was NOT a clean parity subset
(it mixed gated and parity samples), so GF(2) found garbage and the hybrid stayed at raw level. The weak
link is the GENERAL residual-isolation step, not the decomposition itself.

**Fix → HYB-03 (cleaner isolation).** Use the MISCLASSIFIED training samples as the residual instead of
low-confidence: on the gated rule, every sample the local learner gets WRONG is an x0=−1 parity case
(it is correct on the gating half), so the misclassified set is a pure, unbiased parity subset → GF(2)
clean. This is a better residual criterion (an algorithm choice, not a bar tweak — the accuracy bars
stay locked). Recorded NULL honestly; the principle (seed 0) stands.

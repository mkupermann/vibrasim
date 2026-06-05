# JEP-444 — Feedback alignment with a stable optimizer (JEP-443 divergence fixed)

## Motivation
JEP-443 was NULL because feedback alignment diverged to NaN at LR=0.5 (its fixed-random-feedback
pseudo-gradient is noisier than backprop's). JEP-444 re-runs with a stable optimizer to get the clean
answer: does feedback alignment (no weight transport — a step toward locality) still escape the
order-3 parity wall and find the interaction, as full backprop did (JEP-442)? Reference probe only;
the substrate path stays backprop-free. No transformer.

## Method (`tools/run_jep444_feedback_alignment_stable.py`)
Same as JEP-443 (order-3 parity, P=18, M=64, N=2500/1000, seeds 0 & 7, FA backward pass with fixed
random feedback B) but with a STABLE optimizer: LR=0.02, per-step gradient-L2-norm clipping to 1.0
per parameter block, EPOCHS=12000. Compare to matched random features.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J444a (FA escapes the wall):** FA held-out ≥ 0.90, M=64, both seeds.
- **J444b (FA finds the interaction):** top-3 permutation-importance = {0,1,2}, both seeds.
- **J444c (gap is learning):** FA ≥ matched-random + 0.20, both seeds.

Honest expectation: uncertain — with a stable LR, FA plausibly solves it (FA aligns over training),
but parity has no low-order signal so alignment may stall. PASS = the escape survives removing weight
transport (a more-local rule discovers high-order structure). NULL if FA still < 0.90 (full
backprop's weight transport is needed at this scale). Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT)

| seed | FA (M=64) | matched random | top-3 features |
|------|-----------|----------------|----------------|
| 0 | 1.000 | 0.557 | [0, 1, 2] ✓ |
| 7 | 1.000 | 0.546 | [0, 1, 2] ✓ |

J444a ✓ · J444b ✓ · J444c ✓ → **PASS, both seeds.**

## Verdict: targeted high-order discovery survives removing weight transport
Feedback alignment — backprop's backward pass with the exact forward weights `w2` replaced by a FIXED
RANDOM feedback `B` (Lillicrap et al. 2016) — still cracks order-3 parity perfectly with M=64 and
concentrates on exactly the true triple {0,1,2}, where matched random features are at chance. So the
escape from the combinatorial wall does **not** require exact weight transport (the least
biologically-plausible part of backprop); a more-local credit signal suffices to *learn the targeted
interaction*. This narrows the open problem: the remaining gap to a fully-LOCAL rule
(e-prop / equilibrium-propagation — remove the global error broadcast too) is smaller than "needs
full backprop." Reference probe only; the substrate path stays backprop-free (reservoir + RLS).
Established method (feedback alignment), named — measurement, not a new mechanism.

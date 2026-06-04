# JEP-79b — WHERE does JEPA beat generative? Capacity-bottleneck regime

## Motivation
JEP-79 NULL: with ample capacity, a generative model encodes state AND unpredictable distractors at no cost, so
JEPA gained nothing. Theory says JEPA's advantage appears when modeling the unpredictable content COMPETES with
modeling state for capacity. Test that regime directly.

## Setup (favorable-to-theory, pre-registered)
- Make the unpredictable content DOMINATE: distractor = 96 dims (vs 32 predictable), sigma_d=2.0 (fully
  unpredictable from action). Latent BOTTLENECKED to dim 4. Decoder reconstructs all 128 obs dims (generative) so
  the distractor dominates its loss; JEPA predicts the 4-d latent (+VICReg) so the distractor is pure noise to it.
- Metric: state-probe R^2 (controllable s from the 4-d latent), JEPA vs generative.

## Pre-registration (locked BEFORE run)
- PASS (advantage found): JEPA state-R^2 - GENERATIVE state-R^2 >= 0.20, with JEPA >= 0.70. Locates the regime
  where latent prediction beats generative (the bottleneck where modeling noise costs state fidelity).
- NULL: gap < 0.20 -> even in the favorable bottleneck regime the advantage is small at this scale; report honestly
  (a stronger deflation of the standard story). Established (JEPA rationale), named; no novelty.

## Result — PASS (locates the advantage)
Bottleneck regime: latent dim 4, distractor 96-d (vs 32-d predictable), fully unpredictable (sigma_d=2.0).
- **JEPA state-R^2 = 0.982   GENERATIVE state-R^2 = 0.490   gap = +0.493.**

**VERDICT: PASS.** In the capacity-bottleneck regime JEPA strongly beats the generative model on state fidelity.
Combined with JEP-79 (NULL at ample capacity), the honest characterization is precise: **the JEPA-over-generative
advantage requires a CAPACITY BOTTLENECK where modeling the unpredictable content competes with modeling
controllable state** — not unpredictability alone. With scarce latent the generative model spends it on
irreducible noise (reconstruction loss is dominated by the 96-d distractor); JEPA's latent-prediction objective
suppresses the unpredictable features and keeps the 4-d latent for state. This LOCATES LeCun's argument rather than
asserting it. Established (JEPA rationale, VICReg), named; no novelty. The transferable result is the BOUNDARY:
predict-in-latent helps exactly when capacity is the binding constraint against unpredictable content.

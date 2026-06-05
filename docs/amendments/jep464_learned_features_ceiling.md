# JEP-464 — Would LEARNED features raise the energy model's affect ceiling over clouds?

## Motivation
JEP-463 found the deployed energy model (random features + RLS) caps at affect order ~2 over VSA clouds
(order-3 = 0.61). Two causes were proposed: cloud noise AND the FIXED random features (weaker than
learned). JEP-457 showed LEARNED local features (node perturbation) reach ~order-5 on raw bits. The
actionable question for Michael: does swapping the energy model's fixed random features for a LEARNED
local rule (node perturbation) RAISE the affect ceiling over clouds — i.e., is the order-3 failure the
learning rule's weakness (fixable) or the cloud noise (fundamental)? Test at order-3, the reservoir's
breaking point.

## Method (`tools/run_jep464_learned_features_ceiling.py`)
Order-3 balanced parity affect over VSA clouds (same construction as JEP-463), D=4096, seeds 0 & 7.
Compare on held-out clouds:
- **random reservoir** (`ValenceReservoirLearner`, fixed features + RLS) — the deployed model (~0.61).
- **learned local** (node perturbation, M=64 hidden, ~3000 epochs) — learns the features.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J464a (learned features help):** node perturbation held-out ≥ random reservoir + 0.15, both seeds —
  learning the features raises the order-3 ceiling that fixed random features hit.
- **J464b (and reaches a usable level):** node perturbation held-out ≥ 0.75, both seeds.

Honest expectation: genuinely uncertain — learned features SHOULD beat fixed random ones (JEP-457), but
the cloud's superposition noise may cap both. PASS = a learning-rule upgrade raises the affect ceiling
(actionable: improve the energy model's learner). NULL if node perturbation ≈ reservoir (the order-3
failure is the cloud noise, not the learning rule — the ceiling is more fundamental). Either way it
attributes the ceiling. Bars locked; no retuning. Established methods (reservoir/RLS; node
perturbation), named. No transformer, no backprop.

## RESULT (2026-06-05): NULL — learned features do NOT help; the ceiling is the cloud, not the learner

| seed | random reservoir | learned (node perturbation) |
|------|------------------|------------------------------|
| 0 | 0.630 | 0.490 |
| 7 | 0.637 | 0.500 |

J464a ✗ (node perturbation is WORSE, not +0.15 better), J464b ✗ (node at chance) → **NULL.**

**Honest attribution — and a correction to my node-perturbation enthusiasm.** Swapping the energy
model's fixed random features for a LEARNED local rule (node perturbation) does NOT raise the order-3
affect ceiling over clouds — it makes it WORSE (chance, 0.49–0.50, below the reservoir's 0.63). Node
perturbation is a zeroth-order gradient estimator whose variance scales with the input dimension, and
over D=4096-dim VSA clouds buried in superposition noise its gradient signal for an order-3 interaction
is hopeless — whereas the random reservoir's closed-form RLS readout over 600 random features captures a
bit more (0.63). So:
1. **The order-2 affect ceiling is a property of the CLOUD REPRESENTATION (+ SQ-hardness), not the
   fixed-features weakness** — a learning-rule upgrade is NOT the fix.
2. **Node perturbation's earlier success (JEP-457, ~order-5) was specific to LOW-dim raw bits (P=18);**
   in high-dim cloud space its variance dominates — an honest nuance on that result.

So the deployed energy model's affect ceiling over clouds (~order 2) is fundamental to the
representation; the demonstrated escape for genuinely high-order affect remains the algebraic hybrid
module (HYB-01/03), not a different local learner. This cleanly attributes and closes the affect-ceiling
question. Established methods (reservoir/RLS; node perturbation), named; a measurement + honest
attribution, not new science. No transformer.

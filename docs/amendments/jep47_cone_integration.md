# JEP-47 — does highest cross-branch PRECISION (entailment cones) give the best integration? (validate JEP-46)

## Motivation
JEP-46: for grounding, CROSS-BRANCH PRECISION matters, not aggregate accuracy (order's cross-branch FPs made
integration worse). Prediction: entailment cones, which have the HIGHEST cross-branch precision (TNR 0.98,
JEP-39b) - even though low recall (TPR 0.42) - should give the BEST integration: they never ground a WRONG
entity, and as long as >=1 true member per goal is grounded, the agent reaches a correct one. Tests the JEP-46
mechanism with the third method.

## Pre-registration (locked BEFORE run)
- Same WordNet carnivore integration env (JEP-37/46), is-a via entailment cones (Ganea 2018).
- Bars: reached-correct-category (over GROUNDED goals) >= 0.85 (high precision -> correct when grounded),
  beating order's 0.50 (JEP-46). Report #grounded trials (may be fewer due to low recall). PASS = cross-branch
  precision is confirmed as what grounding needs; cones best for grounding despite worst aggregate scale recall.
  NULL otherwise. Established (Ganea 2018, SR/TD), named as such.

## Result — NULL (prediction REFUTED; deepens JEP-46)
| is-a method | random-pair TNR | integration (reached-correct) |
|-------------|-----------------|-------------------------------|
| poincare (JEP-37) | (cross-branch correct) | 0.79 |
| order (JEP-46) | 0.96 | 0.50 |
| cones (JEP-47) | 0.98 | 0.245 |

**VERDICT: NULL - my prediction was WRONG, and the reason deepens the lesson.** I predicted cones (highest
cross-branch precision, TNR 0.98 on random pairs) would give the BEST grounding integration. They gave the
WORST (0.245). The reason: aggregate TNR on RANDOM pairs does NOT predict precision on the TASK-SPECIFIC
distribution. Grounding checks is_a(leaf-ENTITY, intermediate-CATEGORY); intermediate categories are general, so
their cones are WIDE (aperture psi grows as norm shrinks) and SWALLOW cross-branch leaves -> false positives ->
wrong groundings. The cone's good TNR on random pairs (many leaf-leaf, narrow cones) doesn't transfer to the
leaf-vs-general-category pairs the task uses. So JEP-46's lesson deepens: not just "error pattern matters" but
"the error pattern ON THE ACTUAL TASK DISTRIBUTION matters - aggregate metrics, even precision, on a random/
benchmark distribution don't predict it." Final grounding ranking: poincare 0.79 > order 0.50 > cones 0.245 -
poincare's CALIBRATED cross-branch correctness (JEP-32) holds specifically on leaf-vs-category pairs, which is
what grounding needs. CONFIRMS poincare as the grounding default. Two wrong predictions in a row (JEP-46, JEP-47)
both taught the same sharpening lesson: measure on YOUR task's distribution. Established (Ganea 2018), named.

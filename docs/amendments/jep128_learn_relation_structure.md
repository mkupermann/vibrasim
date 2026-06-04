# JEP-128 — learning a relation's STRUCTURE from observation (infer transitivity), a frontier attempt

## Why
The engine is TOLD which relations are transitive (comparison hard-coded as transitive). The frontier (JEP-69/70):
learn the relation's STRUCTURE from data. Test: infer whether a relation is transitive by checking if transitive-
closure is CONSISTENT with observations (a total order IS transitive; a cyclic 'beats' is NOT).

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 PARTIAL/PASS (>=0.85): the learner classifies transitive vs non-transitive by closure-consistency in most
  cases; degrades with SPARSE observations (a violation it never observes can't be detected). MOST-LIKELY MISS:
  sparse sampling hiding inconsistency.

## Acceptance
- Report classification accuracy (transitive vs non-transitive) over random relations, and the effect of
  observation density. Established (consistency-based structure inference), named; no novelty.

## Result — PASS in the favorable regime (HIT), with a principled data limit
| density | transitive-correct | non-transitive-correct | overall |
|---------|--------------------|------------------------|---------|
| 1.0 | 1.00 | 0.97 | 0.98 |
| 0.6 | 1.00 | 0.90 | 0.95 |
| 0.3 | 1.00 | 0.23 | 0.61 |

The learner infers a relation's transitivity from observation via CLOSURE-CONSISTENCY: reliable at dense
observation (0.98/0.95), degrading sharply when sparse (non-transitive -> 0.23 at density 0.3). HONEST LIMIT: a
violating triple you never OBSERVE can't be detected, so a sparsely-observed non-transitive relation is mis-inferred
as transitive — a fundamental DATA limit (same flavor as JEP-118c's exposure limit), not a method flaw. (Transitive
is always inferred correctly because a total order genuinely has no violations to see.) This is a real STEP on the
JEP-69/70 "learn the STRUCTURE, not just the facts" frontier: the engine learns a relation's ALGEBRAIC PROPERTY
from data in the favorable regime. Prediction HIT (predicted PASS dense + degradation sparse, exactly observed);
tally 27/42. Established (consistency-based structure inference), named; no novelty.

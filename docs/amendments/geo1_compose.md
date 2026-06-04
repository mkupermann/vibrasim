# GEO-1 — Does the geometric space COMPOSE relations? (foundation of understanding)

## Pre-registration
2D conceptual grid (6x6=36 entities), relations right/up = translations. TransE-style embedding trained on
70% of edges. Test: held-out edge inference, and COMPOSITION right+up (= diagonal) on pairs whose composite
was never a training edge. Bars: compose hits@1 >= 0.5; random-embedding control < 0.1; single-relation
control < 0.3 (proving composition, not memorization).

## Result
| metric | hits@1 |
|--------|--------|
| held-out single-edge inference | 0.22 |
| COMPOSITION right+up (unseen composites) | **0.52** |
| control: random embedding | 0.00 (chance ~0.028) |
| control: single relation (right only) | 0.00 |

**VERDICT: PASS** — the geometry composes relations to infer unseen composite facts; controls collapse.

## Finding — geometric composition works (and generalizes better than single edges)
A learned geometric space represents relations as translations that COMPOSE: right+up predicts the diagonal
for cells never trained on that composite (0.52), while a single relation or random embedding cannot (0.00).
Composition (0.52) beats held-out single-edge inference (0.22) — the relation-translations transfer
GLOBALLY even where local positioning is imperfect. This is the first working rung of EQMOD-3: geometric
COMPOSITION as a foundation of understanding (established method TransE; the contribution is the framing +
held-out composition test). Next: multi-hop composition + inverses (GEO-2), then real relational/language
structure.

# GEO-86 — Does a TRAINED kind-router beat keyword routing (fix the cross-type limitation)?

## Motivation
GEO-85: keyword kind-routing has a ~0.90 ceiling ("thing" mis-routes). GEO-66: linear probes on embeddings
work. GEO-86 tests whether a TRAINED kind-classifier (logistic on query embeddings) routes a query to its
target type better than keywords — potentially fixing the cross-type confusion on the personal KB.

## Pre-registration (locked BEFORE run)
- Training queries labelled by target kind (contact/task/note), ~8 per kind.
- Train a logistic classifier on query embeddings -> kind. Test on HELD-OUT queries including the ambiguous
  GEO-85 cases ("when's the tax thing", "the pipe fixing person").
- Compare to the keyword router (GEO-85).
- Metric: kind-routing accuracy on held-out. Bar: trained >= 0.85 AND >= keyword. PASS = the cross-type
  limitation is fixable with a small trained router. NULL if training doesn't beat keywords.

## Result — PASS (cross-type limitation resolved)
| router | held-out kind-acc |
|--------|-------------------|
| keyword (GEO-85) | 0.88 |
| trained logistic on query embeddings | **1.00** |
Trained router correctly routes the ambiguous "when's the tax thing" -> task (keyword mis-routed to note).

**VERDICT: PASS.** A small trained logistic kind-router (8 labelled queries/kind, logistic regression on query
embeddings) routes 1.00 on held-out queries including the ambiguous ones that defeat keyword routing (0.88).
So the cross-type confusion (GEO-83/84/85) IS fixable — not by keyword heuristics (ceiling 0.88) but by a TINY
TRAINED classifier. This is consistent with GEO-66: routing is just another linear-probe task on embeddings.
**Constructive resolution:** for a mixed-type personal KB, train a small kind-router from a handful of example
queries per type (cheap, instant); it beats keywords and fixes the cross-type misses. The earlier "bounded UX
limitation" (GEO-85) becomes "fixable with a small trained router." Complete cross-type story: confusion
exists (GEO-83/84) -> explicit scoping fixes when type known (GEO-83) -> keyword auto-routing insufficient
(GEO-85) -> trained router fixes it (GEO-86).

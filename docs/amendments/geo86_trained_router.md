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

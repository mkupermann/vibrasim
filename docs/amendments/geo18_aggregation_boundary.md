# GEO-18 — The aggregation/synthesis BOUNDARY (where generator-free geometry breaks, and the honest fix)

## Motivation
GEO-15–17: geometric retrieval/chaining is strong and robust. But this is RETRIEVAL — it returns a stored
entity. Real understanding also AGGREGATES: "How many people work in Boston?", "List everyone at Acme."
These have no single stored answer; pure nearest-neighbour retrieval CANNOT produce a count/set. GEO-18
maps this boundary honestly AND tests the honest fix: retrieval to FILTER + a tiny symbolic compute step
(count/collect) on top. This delimits what geometry alone does vs what needs a symbolic layer.

## Pre-registration (locked BEFORE run)
- Store: 20 "<Person> works at <Company>." + 20 "<Company> is in <City>." Several people share a city.
- Aggregation question: "How many people work in <City>?" true answer = the count.
- (A) PURE geometric: embed the question, retrieve nearest fact, read off an answer -> expected to FAIL
  (no single fact holds a count). Score = exact-count accuracy.
- (B) RETRIEVAL+SYMBOLIC: for each person, chain person->company->city (geometry), then COUNT (symbolic)
  how many resolve to the queried city. Score = exact-count accuracy.
- Bars: (A) expected NULL (<0.3); (B) PASS if >=0.8. This is a boundary rung — the NULL on (A) is the
  finding, not a failure.

PASS-as-designed if (A) fails AND (B) succeeds (delineates the boundary + the fix). Report both.

## Result
true counts: Boston 6, Austin 6, Denver 4, Seattle 4
| method | exact-count acc |
|--------|-----------------|
| (A) pure geometric retrieval | **0.00** |
| (B) retrieval + symbolic count | **1.00** |

**VERDICT: PASS-as-designed** — the boundary is confirmed: pure nearest-neighbour geometry CANNOT produce a
count/aggregate (no single fact holds it), but geometric retrieval to RESOLVE each person->city + a tiny
symbolic COUNT solves it exactly. The honest architecture: **geometry for filter/retrieve/chain, a symbolic
layer for aggregate/synthesize.** This is exactly the division of labour real RAG+tools systems use.

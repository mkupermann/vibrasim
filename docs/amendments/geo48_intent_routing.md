# GEO-48 — Query intent routing: can geometry dispatch a query to the right operation?

## Motivation
The system has many operators (factoid, count/aggregate, temporal, comparison, join, contradiction). To be
usable it must ROUTE a query to the right one. Meta-level question: does the query EMBEDDING reveal the
needed operation? If so, a few-shot nearest-prototype classifier auto-dispatches. GEO-48 tests it.

## Pre-registration (locked BEFORE run)
- 6 intent classes: FACTOID ("which team is X on"), COUNT ("how many people..."), TEMPORAL ("...in 2023"),
  COMPARE ("who is bigger, X or Y"), JOIN ("who is on the same team as X"), EXISTS ("is there anyone who...").
- ~10 example queries per class. Few-shot: hold out 30%, classify held-out by nearest CLASS-CENTROID in
  embedding space (and by k-NN). 
- Metric: held-out intent-classification accuracy. Bar: >= 0.75 (geometry routes intents; chance = 1/6 =
  0.17). Report confusion if below. NULL if query embeddings don't separate intents.

## Result — PARTIAL/NULL (geometry routes intent poorly)
held-out intent accuracy = 0.56 (chance 0.17). Confusions: FACTOID->JOIN, COMPARE->JOIN, EXISTS->COUNT.

**VERDICT: PARTIAL/NULL.** Query embeddings cluster by CONTENT/topic (all "team" queries look alike), not by
the abstract OPERATION needed, so geometric centroid routing only reaches 0.56. Honest: intent/operation type
is a STRUCTURAL/syntactic property ("how many" -> count, "in <year>" -> temporal, "same X as" -> join), which
geometry (a content-semantics tool) does not capture. Consistent with the programme's division: geometry =
semantics, symbolic = structure. The right router is symbolic/keyword-based — tested in GEO-48b.

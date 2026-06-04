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

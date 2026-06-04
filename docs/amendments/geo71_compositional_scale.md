# GEO-71 — Does compositional/word-order understanding scale with model size?

## Motivation
GEO-70b: the transformer beats static on word order, but only 0.75 on MiniLM (22M). Is compositional encoding
STRONGER in a bigger model? GEO-71 re-runs the clean 2-way word-order test on MiniLM (22M) vs mpnet (110M).
Tells whether 0.75 is a small-model limit and which model to choose for compositional/role-sensitive tasks.

## Pre-registration (locked BEFORE run)
- Same GEO-70b clean 2-way identical-bag word-order items.
- Models: all-MiniLM-L6-v2 (22M), all-mpnet-base-v2 (110M).
- Metric: 2-way word-order accuracy. Bars (descriptive): report both; flag if mpnet >= MiniLM + 0.1
  (compositional encoding scales with size). The curve is the finding.

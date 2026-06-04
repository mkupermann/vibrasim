# GEO-28 — Compositional zero-shot: two learned attributes, composed on UNSEEN entities

## Motivation
GEO-27b: a single learned relation transfers zero-shot to unseen entities. The deeper understanding test is
COMPOSITIONAL zero-shot: learn TWO independent attribute relations (size, predator-status) on seen
entities, then answer a COMPOSED query ("large AND predator?") on entities never seen in training. Systematic
composition + zero-shot transfer together is a strong hallmark of understanding (vs memorization). Honest
interpretation either way: success = compositional understanding via geometry; failure = a boundary (second
attribute not cleanly encoded, or composition breaks).

## Pre-registration (locked BEFORE run)
- 20 animals, each labelled size-rank (real-world) and predator (1/0, real-world).
- Learn size-score and predator-score (two linear projections) from SEEN animals only (12 seen / 8 unseen).
- On UNSEEN animals, compositional decision: classify "large AND predator" (size-score > median AND
  predator-score > 0) vs ground truth. Balanced accuracy on the 8 unseen.
- Compare LLM-init vs random-init. 5 splits.
- Bars: LLM compositional balanced-acc on unseen >= 0.70 AND >= random + 0.20. PASS = compositional zero-shot
  understanding; NULL = honest boundary. Report per-attribute unseen accuracy too (localize any failure).

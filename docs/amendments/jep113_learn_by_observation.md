# JEP-113 — learning a taxonomy by OBSERVATION (unsupervised), feeding the engine's reasoning

## Why (toward human-like LEARNING: from observation, not told)
The engine learns from TOLD facts. A human discovers categories by OBSERVING which things are alike. Integrate:
observe objects with feature vectors, DISCOVER the category hierarchy by agglomerative clustering, build the IS-A
graph from the dendrogram (no IS-A told), then reason over the self-discovered taxonomy. Attacks the unsupervised-
structure frontier (JEP-69/70 NULL) with the mature engine.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 PARTIAL/PASS: when features are HIERARCHICALLY structured (coarse categories featurally distinct, the JEP-54
  condition), clustering recovers the taxonomy and the engine answers multi-hop is_a over the SELF-DISCOVERED graph
  at >= 0.8 agreement with ground truth. MOST-LIKELY MISS: dendrogram-to-IS-A mapping (cluster granularity), or
  leaf-to-category assignment. With NON-hierarchical features it would degrade (the honest JEP-69/70 limit).

## Acceptance
- PASS: >= 0.8 is_a agreement with ground truth over the self-discovered taxonomy. Established (agglomerative
  clustering -> hierarchy; JEP-54), named; no novelty. The point: learning-by-observation FEEDS the engine.

## Result — PASS (HIT), with the honest bound that matters
Subclass purity 1.00, superclass purity 1.00; the engine reasons multi-hop over the self-discovered taxonomy (1.00).
Learning-by-observation -> reasoning works end-to-end WHEN features are coarse-distinctive (the JEP-54 condition).
Prediction HIT; tally 16/25; 24 tests gated green. HONEST BOUNDS (the substance): (1) it discovers STRUCTURE, not
MEANING — the categories are nameless clusters ('super1', 'sub3'); no semantic labels are learned (grounding the
clusters to words/concepts is the open symbol-grounding step). (2) It works only because the features are
hierarchically structured; non-hierarchical/arbitrary structure degrades (the JEP-69/70 NULL). So: unsupervised
STRUCTURE discovery feeding reasoning is reachable in the favorable regime; unsupervised MEANING + arbitrary
structure remain the frontier. Established (agglomerative clustering -> hierarchy, JEP-54), named; no novelty.

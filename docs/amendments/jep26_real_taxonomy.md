# JEP-26 — hyperbolic cognitive map on a REAL irregular taxonomy: IS-A / hypernym inference

## Motivation
JEP-24 used a perfect synthetic balanced tree. Real conceptual hierarchies are IRREGULAR (varying branching and
depth). And the USEFUL task is IS-A / hypernym inference ("a cat is a kind of mammal"). Hyperbolic embeddings
famously capture this because the RADIAL coordinate encodes generality (general concepts near origin, specific
near boundary; Nickel-Kiela 2017). Test on a hand-built realistic taxonomy of living things (~70 concepts).

## Pre-registration (locked BEFORE run)
- Realistic IRREGULAR taxonomy (living_thing -> animal/plant -> ... -> species), ~70 nodes, IS-A edges.
- Embeddings: pure EUCLIDEAN (4D) and HYPERBOLIC (2D Poincare, transitive-closure positives + Riemannian SGD).
- Metrics: (a) Spearman(emb-dist, graph-dist); (b) ANCESTOR-DIRECTION accuracy: for ancestor-descendant pairs,
  predict which is the ANCESTOR (more general) by smaller embedding norm (radial generality); chance 0.5.
- Bars: hyperbolic ancestor-direction acc >= 0.85 AND >= Euclidean + 0.2 AND hyperbolic Spearman > Euclidean.
  PASS = hyperbolic cognitive map captures REAL taxonomic IS-A structure (incl. the generality axis) where
  Euclidean cannot. NULL otherwise. Poincare embeddings (Nickel-Kiela 2017) established - named as such.

# JEP-25 — mixed-curvature cognitive map for structures with BOTH metric and hierarchical parts

## Motivation
JEP-23/24: Euclidean fits metric structure, hyperbolic fits hierarchy. Real conceptual knowledge has BOTH
(similarity/metric relations AND IS-A/taxonomic hierarchy). The established synthesis is a MIXED-CURVATURE
(product-manifold) embedding: Euclidean x Hyperbolic (Gu et al. 2019). Test: on a graph that is part-grid
(metric) and part-tree (hierarchy), does a mixed-curvature map beat BOTH pure geometries (each fits only half)?

## Pre-registration (locked BEFORE run)
- Graph: a KxK grid (metric), with a small tree (hierarchy) hanging off each grid node. Distances = BFS.
- Three embeddings at MATCHED total dimension (4): pure EUCLIDEAN (4D), pure HYPERBOLIC (4D Poincare), MIXED
  (2D Euclidean x 2D Poincare). Optimize each to preserve graph distances (stress, learnable scale).
- Metric: Spearman(emb-dist, graph-dist).
- Bars: MIXED Spearman >= max(Euclidean, Hyperbolic) + 0.05 AND mixed >= 0.85. PASS = mixed-curvature handles
  the combined structure better than either pure geometry - the synthesis the geometry thread pointed to. NULL
  otherwise. Product manifolds (Gu et al. 2019), Poincare (Nickel-Kiela 2017) established - named as such.

## Result — NULL (metric-dominated structure; mixed capacity-starved)
| embedding | Spearman |
|-----------|----------|
| pure Euclidean (4D) | 0.933 |
| MIXED (2D x 2D) | 0.833 |
| pure Hyperbolic (4D) | 0.502 |

**VERDICT: NULL (informative).** Pure Euclidean WON - hypothesis refuted on this structure, for a clear reason:
the graph is METRIC-DOMINATED (96/112 nodes are SHALLOW depth-2 trees that barely distort Euclidean; the grid
dominates distances), and the mixed model's 2D Euclidean component was CAPACITY-STARVED vs pure 4D Euclidean for
that dominant grid. Mixed-curvature only helps when BOTH geometries are genuinely needed and balanced. Fair test
= a true GRID x TREE Cartesian product (distance = grid_dist + tree_dist) where pure Euclidean fails the tree
factor AND pure hyperbolic fails the grid factor -> JEP-25b. Bars locked, not tuned.

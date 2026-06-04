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

## JEP-25b — true grid x tree product — NULL (and an honest reason my demo couldn't isolate it)
| embedding | Spearman |
|-----------|----------|
| pure Euclidean (4D) | 0.947 |
| MIXED (2D x 2D) | 0.725 |
| pure Hyperbolic (4D) | 0.481 |

**VERDICT: NULL - I could NOT cleanly demonstrate the mixed-curvature advantage.** Pure Euclidean won again.
Honest diagnosis of MY demo's flaw (not a refutation of the established result): (1) the Cartesian GRAPH product
has ADDITIVE (L1) distance grid_dist+tree_dist, but the Riemannian MANIFOLD product uses L2 sqrt(d_E^2+d_H^2) -
a metric mismatch that handicaps the mixed model while free 4D Euclidean approximates the additive structure
better; (2) Spearman (rank) is forgiving of a SMALL tree's absolute distortion, so Euclidean's tree distortion
barely hurts the rank metric. The mixed-curvature benefit (Gu et al. 2019) is established on REAL graph data with
proper objectives, but my synthetic toys did not isolate it. NOT overclaiming a synthesis I couldn't show.

## Geometry thread (JEP-23/24/25) - honest conclusion
CLEAN results: Euclidean cognitive maps fit METRIC structures (JEP-23b: ring 0.99, grid 0.92), DISTORT
hierarchies (tree 0.41); HYPERBOLIC recovers hierarchies (JEP-24b: 0.83). These are solid and reproduced. The
MIXED-curvature synthesis (JEP-25) is an established idea (Gu et al. 2019) that my clean toy demos did NOT
reproduce - honest limitation. Net honest signpost toward conceptual understanding: different relation types want
different geometries (metric->Euclidean, taxonomic->hyperbolic); combining them is a real, established, but
non-trivial engineering problem I did not solve here. Named as established; not overclaimed.

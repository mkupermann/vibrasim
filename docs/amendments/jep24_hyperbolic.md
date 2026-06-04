# JEP-24 — hyperbolic (Poincare) cognitive map recovers HIERARCHIES where Euclidean fails

## Motivation
JEP-23b: Euclidean cognitive maps distort trees (Spearman 0.41, worse with more dims). The established fix is
HYPERBOLIC geometry - trees embed in the Poincare ball with low distortion (Nickel & Kiela 2017), because
hyperbolic space's exponential volume growth matches a tree's exponential branching. If a Poincare embedding
recovers tree distance where Euclidean failed, it (a) confirms the JEP-23b geometry-mismatch diagnosis and (b)
extends the EQMOD-4 relational machinery to HIERARCHIES (IS-A / taxonomies) - the structure conceptual knowledge
most needs.

## Pre-registration (locked BEFORE run)
- Same balanced binary tree (63 nodes). Learn a 2D POINCARE-ball embedding via a ranking loss (graph-adjacent
  pairs closer than random negatives) with projected gradient (keep ||x||<1). Hyperbolic distance:
  d(u,v)=arccosh(1 + 2||u-v||^2 / ((1-||u||^2)(1-||v||^2))).
- Metric: Spearman(hyperbolic-dist, graph-dist) over all pairs, vs the Euclidean baseline (0.41 from JEP-23b).
- Bars: hyperbolic Spearman >= 0.85 AND >= Euclidean + 0.3. PASS = hyperbolic geometry recovers the hierarchy,
  confirming the boundary diagnosis and extending the approach to trees. NULL otherwise. Poincare embeddings
  (Nickel-Kiela 2017) established - named as such.

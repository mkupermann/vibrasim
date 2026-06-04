# JEP-23 — boundary of Euclidean cognitive maps: which relational STRUCTURES embed well?

## Motivation
EQMOD-4 relational reasoning (JEP-17/20b) worked on grids/orders - LOW-DIMENSIONAL METRIC structures. Honest
question: where does "reasoning as navigation in a Euclidean concept space" BREAK? Established result: TREES /
hierarchies do NOT embed in low-dim Euclidean space without large distortion - they need HYPERBOLIC geometry
(Nickel & Kiela 2017). This rung maps the cognitive-map approach's boundary by measuring embedding distortion
across structure types with the SAME SR + low-dim-Euclidean pipeline.

## Pre-registration (locked BEFORE run)
- Structures (~64 nodes each): RING (1D cyclic), GRID (2D), BALANCED TREE (hierarchy), RANDOM graph. Learn SR by
  local TD; embed via top-k eigenvectors (Euclidean); compute embedded pairwise distance vs true GRAPH distance.
- Metric: Spearman(embedded-dist, graph-dist) and relative distortion (mean |emb-dist/graph-dist normalized|).
- Hypothesis/bars: RING & GRID embed well (Spearman >= 0.9); TREE embeds POORLY (Spearman < 0.8) AND tree
  distortion >> grid - establishing that Euclidean cognitive maps match METRIC structures but DISTORT
  hierarchical ones (the honest boundary; hyperbolic geometry is the established fix). Report the full table;
  this is a CHARACTERIZATION (the "PASS" is correctly identifying the boundary, not maximizing a score).

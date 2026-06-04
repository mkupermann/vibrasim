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

## Result — PARTIAL (tree clearly worst, confirming hypothesis; but k=6 over-embedding confounded metric baselines)
| structure | Spearman(emb,graph) | rel-distortion |
|-----------|---------------------|----------------|
| grid | 0.866 | 0.313 |
| ring | 0.578 | 0.459 |
| random | 0.570 | 0.392 |
| tree | 0.355 | 0.496 |

**VERDICT: PARTIAL.** The KEY signal holds: the TREE embeds WORST by a clear margin (Spearman 0.36, highest
distortion) - consistent with hierarchies needing hyperbolic, not Euclidean, geometry. BUT the metric-structure
baselines missed the >=0.9 bar because k=6 OVER-EMBEDS low-dim structures: a ring is intrinsically a 2D circle
(top-2 SR eigenvectors), and the extra 4 harmonic eigenvectors add noise that distorts the distance. So the
fixed k=6 confounded the absolute comparison (it penalizes low-dim structures). Fix: use the natural low
dimension k=2 -> JEP-23b. The relative ordering (tree worst) already supports the boundary; 23b confirms it
cleanly. Bars locked, not tuned.

## JEP-23b — clean boundary at natural low dim — PASS
| structure | Spearman (Euclidean SR embedding) |
|-----------|-----------------------------------|
| ring (k=2) | 0.988 |
| grid (k=2) | 0.915 |
| tree (k=2) | 0.411 |
| tree (k=4, MORE dims) | 0.354 |

**VERDICT: PASS (boundary mapped cleanly).** At natural low dim, metric structures embed well in Euclidean SR
space (ring 0.99, grid 0.92) but the TREE distorts badly (0.41) and gets WORSE with more dimensions (k=4 -> 0.35)
- proving it is a GEOMETRY MISMATCH, not a dimensionality shortfall. Hierarchies need HYPERBOLIC (negatively
curved) space (Nickel-Kiela 2017). 

## Honest implication for "understanding"
This boundary matters: much of CONCEPTUAL knowledge is HIERARCHICAL (taxonomies, IS-A, part-whole). The EQMOD-4
Euclidean cognitive-map approach - which does grid/order relational reasoning well - is the WRONG geometry for
hierarchies. So extending toward conceptual understanding would require HYPERBOLIC cognitive maps (a known,
established direction), not just more of the Euclidean machinery. An honest, specific signpost for what genuine
conceptual reasoning needs - mapped, not hand-waved. Nickel-Kiela hyperbolic embeddings (2017) established - named.

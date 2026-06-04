# JEP-27 — mixed-curvature redeemed on a TASK basis: relatedness (Euclidean) + IS-A (hyperbolic)

## Motivation
JEP-26 found the geometries are COMPLEMENTARY: Euclidean captures relatedness/distance, hyperbolic captures IS-A
generality. JEP-25 failed because it measured combined DISTANCE (L2 product mismatch). The honest synthesis is
TASK-BASED: a mixed representation with a Euclidean component (for relatedness queries) + a hyperbolic component
(for IS-A queries), routing each query type to the geometry that handles it. Test whether this mixed map is the
best ALL-ROUNDER on BOTH tasks where each pure geometry fails one.

## Pre-registration (locked BEFORE run)
- Real taxonomy (JEP-26, 77 concepts). Train: pure Euclidean (4D), pure hyperbolic (2D), MIXED (Euclid2D for
  distance + Hyper2D for hierarchy, trained jointly with each component's own objective).
- Two task scores: (a) RELATEDNESS = Spearman(component-distance, graph-distance); (b) IS-A = ancestor-direction
  accuracy (smaller hyperbolic-component norm = more general). For pure models, both read from the single space.
- Bars: MIXED relatedness >= 0.85 AND MIXED IS-A >= 0.85 AND mixed's MIN-over-tasks > each pure geometry's
  MIN-over-tasks. PASS = mixed-curvature is the best all-rounder (handles both relation types) - the honest
  synthesis, task-based. NULL otherwise. Product/mixed-curvature representations (Gu 2019) established - named.

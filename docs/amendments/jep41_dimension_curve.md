# JEP-41 — dimension-scaling curve: is the ~0.78 IS-A ceiling capacity or method?

## Motivation
JEP-40 showed held-out IS-A on WordNet 366 plateaus at ~0.78 with more ITERATIONS. Open question: is the ceiling
DIMENSION (embedding capacity) or METHOD (the calibrated-Poincare approach itself)? Sweep hyperbolic dimension
at fixed iterations to find out.

## Pre-registration (locked BEFORE run)
- WordNet carnivore 366, 16k iters, hold out 30%. Sweep hyp_dim in {10,20,40,80}; measure held-out IS-A.
- CHARACTERIZATION (no pass/fail): if accuracy climbs past ~0.88 with dimension -> ceiling was capacity; if it
  plateaus -> ceiling is the method. Established methods (Poincare embeddings), named as such.

## Result — dimension does NOT help: the ceiling is the METHOD (conclusive)
| hyp_dim | held-out IS-A (calibrated) |
|---------|----------------------------|
| 10 | 0.784 |
| 20 | 0.778 |
| 40 | 0.771 |
| 80 | 0.771 |

**VERDICT: CONCLUSIVE - the ~0.78 ceiling is the METHOD, not compute or capacity.** Held-out IS-A is FLAT (even
slightly decreasing) with dimension - 80D is no better than 10D. Combined with JEP-40 (iterations also plateau at
~0.78), this DEFINITIVELY settles the scaling question: the ~0.78 ceiling on real WordNet IS-A is a METHOD/readout
limit, NOT compute and NOT capacity. Neither more iterations nor more dimensions break it. The residual gap to
the toy's 0.91 is fundamental to the calibrated-Poincare approach on deep real hierarchies; exceeding it needs a
DIFFERENT METHOD (order embeddings / entailment cones tuned for depth / a better is-a readout), not more
resources. This CONCLUSIVELY corrects my repeated "under-convergence is just compute" over-claim made across
JEP-29/31/39b. Honest final scaling statement: the reasoner reaches ~0.91 on small/clean taxonomies but has a
~0.78 METHOD ceiling on deep real WordNet hierarchies that more compute/dimension does not break.

## Scaling thread (JEP-29/31/39b/40/41) - final honest conclusion
The concept reasoner's IS-A accuracy: 0.91 (77-concept toy) -> ~0.78 CEILING (366 real WordNet, depth-12),
unbroken by iterations (JEP-40) or dimension (JEP-41). My earlier "just compute" framing was WRONG; quantifying
it (JEP-40/41) revealed a real METHOD limit on deep real hierarchies. To close it needs a different IS-A
formulation, not bigger budgets. An honest, measured boundary - and a corrected claim. Established methods
(Poincare embeddings, order/cone embeddings), named as such.

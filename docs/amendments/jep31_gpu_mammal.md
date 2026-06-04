# JEP-31 — GPU-accelerated concept reasoner on the FULL mammal WordNet subtree (1170 concepts)

## Motivation
Tie together the GPU work (JEP-18) and the reasoning result at MAXIMUM real scale: the full mammal.n.01 hyponym
closure (1170 concepts, Nickel-Kiela's headline dataset). Large embedding optimization is exactly where the GPU
helps. Tests whether the mixed-curvature reasoning holds at 16x the toy scale on real data, GPU-trained.

## Pre-registration (locked BEFORE run)
- Full mammal subtree (1170 concepts). GPU (torch-directml, AMD RX 7700S). Euclidean 16D (minibatched stress) +
  hyperbolic 40D (minibatched ranking + Riemannian SGD). Hold out 30% of ancestor pairs.
- Bar: held-out IS-A direction accuracy >= 0.85 (generalizes at full real scale). PASS = reasoning scales to 16x
  on real data, GPU-accelerated. NULL otherwise. WordNet + Poincare (Nickel-Kiela 2017) established - named.

## Result — NULL (GPU works; embedding under-trained at full 1170-mammal scale)
| metric | value |
|--------|-------|
| concepts | 1170 |
| GPU training time (AMD RX 7700S) | 50s Euclid + 120s hyperbolic |
| trained IS-A direction acc | 0.575 |
| HELD-OUT IS-A direction acc | 0.531 (random 0.5) |

**VERDICT: NULL - honest scaling boundary.** TWO honest takeaways: (1) the GPU genuinely WORKS at scale - it
trained 1170-concept embeddings on the AMD RX 7700S via DirectML in 170s (GPU utility demonstrated at real
scale). (2) BUT the reasoner embedding did NOT converge: held-out IS-A 0.531 (~chance) and even TRAINED accuracy
0.575 - the model did not fit the deep hierarchy. The low TRAINED accuracy is the red flag: this is UNDER-
TRAINING (6000 minibatched iters insufficient for 1170 nodes / depth-12 / 9014 positives), not just a
generalization gap. Consistent with JEP-29b's lesson (real scale needs proportionally more compute) but more
acute at 16x scale. The norm-direction readout also degrades on deep hierarchies (tiny per-level norm gaps).
Honest: NOT claiming the reasoner scales to 1170 mammals at this budget; it would need far more training (the GPU
makes that feasible) and/or a better hypernymy score. NOT chasing it further (diminishing returns; the scaling-
needs-compute point is already made at 366). Bars locked, not tuned.

## Honest scaling summary (concept reasoner)
- 77-concept toy: held-out IS-A 0.91 (>=5D) - reliable.
- 366-concept carnivore (real): held-out IS-A 0.86 (20D, 12k full-batch iters) - holds with adequate compute.
- 1170-concept mammal (real): held-out IS-A 0.53 (40D, 6k minibatched iters, GPU) - UNDER-TRAINED, fails.
Pattern: the result holds at real scale ONLY with compute scaled to the hierarchy's size/depth; the toy/medium
budgets do not transfer to the full subtree. The GPU enables larger budgets but I did not push to convergence here.

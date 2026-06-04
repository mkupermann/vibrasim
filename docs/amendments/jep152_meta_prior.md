# JEP-152 — meta-learning the structural prior (the deepest piece of the structure-learning frontier)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 meta-learning a domain's complexity prior from a few fully-observed structures, then applying it to one-shot
  inference of a NEW structure, BEATS a fixed/wrong prior WHEN the domain is CONSISTENT (meta-prior matches), but is
  uninformative for a HETEROGENEOUS domain. MOST-LIKELY MISS: meta-learning being trivial / not generalizing.

## Acceptance (characterization)
- Report one-shot accuracy with a META-LEARNED prior vs a fixed-WRONG prior, on consistent vs heterogeneous domains.
  The consistent-helps / heterogeneous-uninformative result is the finding. Established (hierarchical Bayes / meta-
  learning the prior), named; no novelty.

## Result — PASS (HIT); exhaustively closes the structure-learning frontier
| domain | meta-prior-correct | fixed-Occam-correct |
|--------|--------------------|----------------------|
| consistent (deep) | 0.18 | 0.05 |
| consistent (simple) | 0.86 | 0.86 |
| heterogeneous | 0.28 | 0.28 |

Meta-learning the structural prior from a domain's regularities HELPS RELATIVELY: on a consistently-DEEP domain the
meta-learned 'deep' prior beats fixed-Occam 3.6x (0.18 vs 0.05, since Occam wrongly assumes simple); on a simple
domain both match (meta learns simple = Occam); on a HETEROGENEOUS domain the meta-prior is uninformative (no
consistent regularity to learn). HONEST NUANCE: 0.18 is still LOW — meta-learning the right prior HELPS but does NOT
SOLVE deep one-shot inference, because one example of a deep structure is genuinely UNDER-DETERMINED even with the
right prior (the data is insufficient, not just the bias). So the named open piece IS addressable (learn the prior
from domain regularities) but HUMAN-LEVEL one-shot structure learning needs MORE than the right prior — compositional
reuse, active querying, and richer inductive biases TOGETHER. Prediction HIT; tally 47/66. This EXHAUSTIVELY closes
the structure-learning frontier characterization (JEP-128..152): clean=easy (search-cost), noisy=hard (closures
compound; redundancy at cost), sparse-passive=ambiguous, sparse=ACTIVE-querying solves (n log n), one-shot=PRIORS
help with a bias cost, META-PRIOR=learnable from consistent domains but doesn't solve deep-one-shot. Established
(hierarchical Bayes / meta-learning the prior; learning-to-learn), named; no novelty.

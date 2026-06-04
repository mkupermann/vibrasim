# JEP-44 — hybrid is-a (order + relatedness guard): recognized CIRCULAR before running, not presented

## The idea
Order embeddings (JEP-42/43) fix siblings + scale but have a cross-branch residual (rose dominates animal across
branches). Idea: guard with RELATEDNESS - reject is_a(a,b) when a and b are unrelated (graph-far), keeping it
when a is a true descendant (close to its ancestor). This would fix all three residuals.

## Why I did NOT present a result (honest recognition)
My first implementation used the GRAPH DISTANCE as the relatedness guard. I recognized BEFORE accepting any
output that this is CIRCULAR: graph distance DETERMINES ancestry (ancestors are close, cross-branch far), so
using it to predict is-a is using the answer to predict the answer. Any "high accuracy" from it would be an
artifact, not a real result. Also, my held-out setup held out ancestor-pair LABELS while keeping ALL graph
EDGES, so the graph (and thus GD) already encodes the held-out relationships - a second form of leakage.

## Honest status
A FAIR test of the hybrid needs: (a) a LEARNED relatedness signal (not ground-truth GD), and (b) held-out EDGES
(link-prediction split), so neither the order embedding nor the guard sees the held-out relationships. That is a
substantial, careful separate setup. Rather than present a leaky/circular number, I record the hybrid as a
PROMISING but NOT-CLEANLY-TESTED idea. The honest conclusion of the is-a method exploration stands at JEP-43:
- order embeddings: best for LARGE REAL hierarchies (0.91, siblings fixed, small cross-branch residual);
- entailment cones: best for SMALL/CLEAN (1.00, both residuals fixed, do not scale);
- calibrated Poincare: robust middle, kept as shipped default.
No universally-best method; the tradeoffs are mapped. Caught the circularity by checking my own design before
trusting its output - the kind of honesty the project is about. Established methods (Vendrov 2016, Ganea 2018,
Nickel-Kiela 2017), named as such.

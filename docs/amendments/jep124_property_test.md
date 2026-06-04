# JEP-124 — randomized property-based validation of the core reasoning

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100% match vs an independent reference (transitive closure over the random DAG) across thousands of random
  taxonomies + queries — OR a real edge-case bug is found (also valuable). MOST-LIKELY MISS: random concept names
  hitting a parse/normalization edge (e.g., a name that normalizes to another).

## Acceptance
- PASS: >= 0.999 agreement with the reference over the random suite (core reasoning sound). Any systematic mismatch
  is a found bug to record. Established (property-based testing), named; no novelty.

## Result — PASS (HIT)
400 random DAG taxonomies, 23,916 is_a pair-checks: **0 mismatches** vs an independent transitive-closure reference
(agreement 1.00000). The engine's multi-hop is_a is SOUND under randomized property-based testing — the core
reasoning is correct, not just tuned to hand-picked batteries. Prediction HIT; tally 23/38. A compact version is
locked into the regression suite. Established (property-based testing), named; no novelty.

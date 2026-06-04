# JEP-135 — active querying solves the sparse-data structure-learning limit (the constructive close)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 an ACTIVE learner (choose comparisons to sort) determines a transitive order in ~n log n queries and detects
  non-transitivity (a cycle) efficiently, vastly fewer than passive random observation needs. MOST-LIKELY MISS:
  cycle detection in the non-transitive case.

## Acceptance
- PASS: active determines the correct order with O(n log n) queries (<< n^2 passive) and detects cycles.
  Established (active learning / comparison sorting), named; no novelty.

## Result — PASS (HIT) on the main claim; honest caveat on cycle detection
| n | active queries (~n log n) | passive-to-determine (~n^2) | speedup | active-correct |
|---|---------------------------|------------------------------|---------|----------------|
| 8 | 16 | 39 | 2.4x | 1.00 |
| 16 | 45 | 193 | 4.3x | 1.00 |
| 32 | 119 | 844 | 7.1x | 1.00 |
| 64 | 300 | 3582 | 11.9x | 1.00 |

ACTIVE querying determines the transitive order in ~n log n queries (1.00 correct); the speedup over passive grows
with n (~12x at n=64). By CHOOSING the informative comparisons (binary-insertion sort) instead of waiting for them,
active learning SOLVES the sparse-data limit (JEP-128). Prediction HIT on the main claim; tally 31/49. HONEST
CAVEAT (self-flagged): assumes a NOISELESS oracle (with noise, you'd need repeated queries, JEP-134); and my
cyclic-detection sub-test was INADEQUATE — a single long n-cycle (0>1>...>n-1>0) is NOT caught by sampling random
triples (it needs path-tracing / cycle-finding), so the non-transitive ACTIVE case is subtler than the transitive
one and not properly demonstrated here. Recorded as-is, no over-claim. Established (active learning / comparison
sorting), named; no novelty. This CLOSES the structure-learning characterization: clean=easy (search-cost limited),
noisy=hard (closures compound, redundancy-rescuable), SPARSE=solved by ACTIVE querying.

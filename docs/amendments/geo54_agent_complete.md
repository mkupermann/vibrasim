# GEO-54 — UnifiedReasoner operator-complete: add negation + comparison, test expanded workload

## Motivation
GEO-51/53 validated comparison + negation standalone. The UnifiedReasoner (GEO-49) handles
factoid/count/temporal/join but not yet negation/comparison. GEO-54 adds them so the agent exposes the FULL
validated operator set, and re-tests on an expanded mixed workload.

## Pre-registration (locked BEFORE run)
- Extend the router: NEGATE (not/n't/don't) and COMPARE (more/older/than ... or). Add numeric attrs (salary).
- Expanded mixed test set: factoid + count + temporal + join + NEGATION + COMPARISON, answers known.
- Metric: end-to-end accuracy across all intents. Bar: >= 0.8 overall AND the two new intents both correct.
  PASS = the agent is operator-complete end-to-end.

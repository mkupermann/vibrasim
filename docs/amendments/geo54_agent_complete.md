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

## Result — PASS (after a caught router bug)
First run scored 0.50: the router-extension edit had silently failed (only the operator branches were added,
not the routing rules), so negation/comparison queries fell through to FACTOID. The pre-registered test
CAUGHT it; fixing route() gave end-to-end 1.00 (FACTOID/COUNT/TEMPORAL/JOIN/NEGATE/COMPARE all correct). The
UnifiedReasoner is OPERATOR-COMPLETE end-to-end, including the two geometry-fails cases (negation, comparison)
handled by the symbolic layer. Regression tests added (11 -> 13 pytest). A clean example of pre-registration
catching a silent bug.

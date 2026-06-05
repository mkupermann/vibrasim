# JEP-185 — read() extracts COMPARISON/ordering relations (completing the relation-type coverage)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 adding a 'X is ADJ than Y' handler to read() (before the copula) lets transitive comparison work from prose.
  RISK: pattern overlap with the copula handler — match comparison first.

## Result — PASS (HIT)
read() now detects 'X is/are (more) <comparative> than Y' and routes it to the order/comparison mechanism (matched
BEFORE the copula handler so 'X is bigger than Y' is not mis-read as is-a). Results:
- read('An elephant is bigger than a dog. A dog is bigger than a cat. A cat is bigger than a mouse.') -> learned
  {comparison: 3}.
- 'is an elephant bigger than a dog?' -> Yes; 'is an elephant bigger than a mouse?' -> Yes (TRANSITIVE 3-hop from
  prose); 'is a mouse bigger than an elephant?' -> 'Not that I can tell' (correct direction).
- is-a extraction unaffected (no interference). 60/60 regression tests green (+1).
This COMPLETES read()'s relation-type coverage: is-a (taxonomy) + part-of (mereology) + causal + spatial-containment
+ COMPARISON/ordering — the five distinct relation types the engine reasons over, all now extractable from prose.
Prediction HIT; tally 74/101. Established (lexico-syntactic extraction, transitive order); named; no novelty.

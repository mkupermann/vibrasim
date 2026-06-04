# JEP-145 — provenance / truth maintenance (how do you know? what depends on F?)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: provenance(x,c) returns the supporting fact-chain (justification); retracting a fact on the ONLY path
  invalidates the conclusion, while a REDUNDANT path preserves it (the truth-maintenance property). MOST-LIKELY
  MISS: which path is "the" justification when multiple exist.

## Acceptance
- PASS: provenance + retraction battery = 100%. Established (truth-maintenance systems, Doyle 1979; justification
  tracking), named; no novelty. HONEST: returns ONE shortest justification (not all).

## Result — PASS (HIT)
Provenance/TMS battery 7/7: provenance(poodle, living thing) returns the 3-edge justification chain; retracting
dog->animal (the only path) invalidates 'poodle is a living thing' and empties its provenance; with a REDUNDANT
taxonomy (poodle->dog->animal AND poodle->mammal->animal), retracting ONE path leaves 'poodle is an animal' intact
(survives via the other), and only retracting BOTH makes it underivable. Prediction HIT; tally 40/59; 36 tests
gated green. Genuine meta-reasoning: the engine tracks WHY it believes things and correctly maintains truth under
retraction, with the redundancy property (JEP-138) giving belief robustness. Established (truth-maintenance systems,
Doyle 1979), named; no novelty. HONEST: returns ONE shortest justification (not the full set of all justifications);
no assumption/dependency-directed backtracking (a fuller TMS tier).

# JEP-132 — grand integration: learn (concepts+taxonomy+rules from observation) -> reason -> act, end-to-end

## Why
The ultimate capstone: one agent that learns its taxonomy from observation (JEP-117 self-taught), learns a
relational composition rule from observation (JEP-129/130), reasons over BOTH grounded concepts and learned rules,
and acts on a conceptual goal (JEP-122). The complete learns-everything-from-experience -> reason -> act system.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 PASS: the integrated agent (a) self-teaches a named taxonomy from observation, (b) learns 'grandparent =
  parent o parent' from observed facts, (c) answers a query combining a learned concept + the learned rule, (d)
  plans to a conceptually-grounded goal. MOST-LIKELY MISS: an interface bug between learned components in
  integration (the recurring 'integration finds what units miss' lesson).

## Acceptance
- PASS: all four stages correct end-to-end. Established (clustering + cross-situational learning + rule discovery +
  grounded planning), named; no novelty. The UNIFICATION is the point.

## Result — PASS (HIT), the grand capstone
All four stages end-to-end: (a) self-taught taxonomy — every observed instance is-a animal (True); (b) learned
'grandparent = parent o parent' from observed facts, derives amy->cid, not amy->bea (True); (c) combined reasoning
'is what the dog chases an animal?' -> Yes (the LEARNED concept 'cat' is an animal) (True); (d) conceptual goal
'reach an animal' grounds 2 targets from the self-taught taxonomy (True). Prediction HIT; tally 30/46. THE COMPLETE
EQMOD-4 VISION REALIZED: one agent LEARNS its concepts + names + taxonomy + relational composition rules from raw
OBSERVATION (no told facts for the taxonomy; rule discovered from data), REASONS over the learned grounded
knowledge + learned rules, and ACTS on conceptual goals — learns-everything-from-experience -> reason -> act,
unified, no transformer, all established methods named. HONEST: every component in its favorable regime (clean
clusters, clean rule data, toy action); the hard regimes (noisy/sparse data, deep rules, learning base relations,
real-prose, abstract words, open generation) remain the honestly-mapped frontier. The DISCIPLINE (predict-calibrate
30/46, every miss diagnosed, ~30 self-corrections) is the transferable deliverable. Established, named; no novelty.

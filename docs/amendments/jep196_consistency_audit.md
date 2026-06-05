# JEP-196 — consistency AUDIT of read knowledge (detect a source's internal contradictions)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a consistency_audit() checking every is-a edge against inherited negatives reports all conflicts on inconsistent
  prose, empty on consistent prose. RISK: an edge already overridden by belief revision.

## Result — PASS (HIT)
Added consistency_audit(): scans the whole KB and reports every is-a belief 'X is-a C' where X also INHERITS 'not C'
(an ancestor of X is recorded NOT-a a class that C is or descends from), returning (child, parent, explanation).
- inconsistent KB (a source asserts 'whale is a fish' despite 'mammal is not a fish'): 1 contradiction found, with
  explanation 'a whale is a mammal, and a mammal is not a fish, yet a whale is asserted to be a fish'.
- consistent KB: 0 contradictions.
This extends JEP-195 (single-assertion check) to a whole-KB AUDIT — when learning from a real SOURCE that ingests
many facts (read() is non-blocking), the engine can now AUDIT the accumulated knowledge for INTERNAL contradictions
and explain each. A genuine learn-from-sources capability: real sources are sometimes internally inconsistent, and a
competent reader detects it. 65/65 regression tests green (+1). Prediction HIT; tally 85/112. Established
(inheritance-based consistency checking / truth maintenance audit); named; no novelty.

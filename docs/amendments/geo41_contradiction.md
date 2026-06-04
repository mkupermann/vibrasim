# GEO-41 — Contradiction detection: does the store flag a new fact that conflicts with an existing one?

## Motivation
A trustworthy knowledge store should DETECT contradictions (a new fact asserting a different value for a
functional relation about an entity already in the store). This is a real knowledge-management property and
untested. Hybrid check: geometric retrieval finds the most similar existing fact (same subject+relation);
symbolic comparison of the structured object flags a conflict if the objects differ. GEO-41 measures how
well this separates true contradictions from consistent additions.

## Pre-registration (locked BEFORE run)
- Store 12 "<P> is on the <Team> team." facts (functional: one team per person).
- Candidate new facts: 8 CONTRADICTORY (existing person, DIFFERENT team) + 8 CONSISTENT (new person, or
  existing person SAME team). 
- Detection rule: embed candidate; retrieve nearest stored fact; if its subject == candidate subject AND
  stored object != candidate object -> FLAG contradiction. (geometric retrieve + symbolic compare)
- Metric: balanced accuracy separating contradictory (should flag) vs consistent (should not). Bar: >= 0.8.
- Also report a PURE-geometric variant (flag if similarity very high but not identical) to show the symbolic
  object-compare is needed. NULL if it can't separate.

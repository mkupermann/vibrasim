# GEO-96 — Grounded generation with CONFLICTING context (robustness to inconsistent retrieval)

## Motivation
The store may hold inconsistent facts (GEO-62). If retrieval returns BOTH conflicting facts in the context,
how does the generator behave — flag the conflict, pick one arbitrarily, or hallucinate a third answer?
GEO-96 tests generation robustness to conflicting context, the generation-time analogue of the GIGO/conflict
findings.

## Pre-registration (locked BEFORE run)
- ~6 cases: context contains TWO conflicting facts about an entity (e.g. "Alice is on Analytics" AND "Alice
  is on Platform"). Ask the question.
- (a) Plain prompt: what does it answer? (b) Conflict-aware prompt ("if the context is inconsistent, say so").
- Metric: (a) fraction where it picks ONE of the two stored values (not a hallucinated third); (b) fraction
  where the conflict-aware prompt FLAGS the inconsistency. Bars: picks-a-stored-value >= 0.8 (no hallucinated
  third); conflict-aware flags >= 0.5. Honest characterization of generation under inconsistent retrieval.

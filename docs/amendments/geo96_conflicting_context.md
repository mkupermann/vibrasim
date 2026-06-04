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

## Result — PARTIAL (grounding contains damage; generator can't flag conflicts)
| behavior | value |
|----------|-------|
| picks a STORED value under conflict (no hallucinated 3rd) | **1.00** |
| conflict-aware prompt FLAGS the inconsistency | 0.17 |

**VERDICT: PARTIAL (honest, architecturally clarifying).** Under conflicting context the generator NEVER
invents a third value (1.00) — grounding contains the damage; conflicting retrieval causes ARBITRARY selection,
not hallucination. BUT the 0.5B model cannot reliably DETECT/flag the conflict even when prompted (0.17) — it
just picks one. **Lesson:** detect conflicts SYMBOLICALLY (values_for, GEO-62, 1.00) BEFORE generation, and
surface them explicitly; do NOT rely on the generator to notice inconsistency. Reinforces the architecture —
symbols for STRUCTURE/DETECTION (conflict, ambiguity, answerability), the generator only for fluent OUTPUT
over already-verified context. Deployment: run values_for() to catch store inconsistencies; only pass clean,
single-valued context to the generator. Generation is robust to conflict (no hallucination) but not self-aware
of it; the symbolic layer is the guard. Good news: grounding prevents the worst failure (invented facts) even
on imperfect retrieval.

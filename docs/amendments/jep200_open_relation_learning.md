# JEP-200 — OPEN-RELATION learning: induce a new relation type from prose examples (milestone)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 from a few consistent examples the engine induces the surface template, extracts new instances, and the new
  relation becomes queryable — extending beyond the 5 fixed types. Honest limit: needs a consistent surface pattern.
  RISK: template over/under-generalization.

## Result — PASS (HIT)
Added learn_relation(examples) + extract_relation(sentence): induce a relational template from example sentences that
share ONE connective (strip articles; first noun = subject, last = object, middle = connective), store the example
facts (in BOTH self.facts and the VSA self._fact_vecs so role-binding queries work), register the template, and
extract new instances from matching sentences. Results:
- learn_relation(['Paris is the capital of France', 'London is the capital of England', 'Tokyo is the capital of
  Japan']) -> ('is capital of', 3); a SECOND relation 'is author of' learned independently.
- extract_relation('Berlin is the capital of Germany') -> ('berlin', 'is capital of', 'germany').
- relation_true('berlin', 'is capital of', 'germany') True; wrong object False; REVERSED ('germany ... berlin') False
  (role-binding keeps it order-sensitive).
- INCONSISTENT examples (different connectives) -> None (correctly refuses to induce a spurious template).
So the engine now LEARNS NEW RELATION TYPES from prose, beyond the 5 hard-coded ones (is-a/part-of/causal/spatial/
comparison) — open-relation extraction by surface-template induction, NO transformer. HONEST LIMIT (the no-transformer
wall): it needs a CONSISTENT surface pattern; paraphrase variation ('Paris, capital of France' vs 'France's capital
is Paris') is out of scope (that is exactly what learned extractors handle and patterns cannot). 69/69 regression
tests green (+1). The JEP-200 milestone: a genuinely-NEW capability, not a refinement. Prediction HIT; tally 89/116.
Established (lexico-syntactic template induction, OpenIE-style surface patterns, VSA role-binding); named; no novelty.

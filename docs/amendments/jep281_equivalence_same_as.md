# JEP-281 — equivalence/synonym 'X is the same as Y' -> mutual is-a

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a similarity QA pass showed 'A puma is the same as a cougar' NOT captured, so 'is a puma a cat?' -> No (despite
  'A cougar is a cat'). 'Same as' is equivalence; treating it as MUTUAL is-a (puma<->cougar) makes each inherit the
  other's ancestors (puma is-a cat) -- the transitive closure must handle the resulting 2-cycle without looping.

## Result — PASS (HIT)
Added 'X is the same as Y' -> tell(X is-a Y) AND tell(Y is-a X) (mutual is-a = equivalence).
- 'A puma is the same as a cougar. A cougar is a cat. A cat is a mammal.' -> 'is a puma a cat?' Yes (puma->cougar->
  cat); 'is a puma a mammal?' Yes (transitive through the puma<->cougar 2-CYCLE, no infinite loop -- the closure's
  visited-set handles it); 'is a cougar a puma?' Yes (symmetric).
- NOT over-general: 'is a cat a puma?' False (cat is broader, not equal).
118/118 regression tests green (test added; the cycle does not break the suite). Prediction HIT; tally 160/196.
Established (equivalence as symmetric subsumption; cycle-safe transitive closure), named; no novelty. Residue:
'X is similar to Y' / 'X differs from Y' are WEAKER than equality (similar != same) -> left as open relations (induce
at >=2 occurrences), not equated.

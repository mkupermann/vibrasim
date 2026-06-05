# JEP-279 — possessive mereology "X's Y" -> Y is part-of X

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a possessive QA pass showed "The engine of a car is powerful" / "A dog's heart..." did not yield the part-of
  link. The 'X of Y' subject form is ambiguous (compound concepts: 'form of government'), but the POSSESSIVE "X's Y"
  is unambiguous mereology -> handle "X's Y ..." -> Y part-of X, guarded by valid-concept.

## Result — PASS (HIT)
Added a possessive preprocessor: "X's Y ..." -> tell_part(Y, X) (Y is part-of the owner X), then rewrite the sentence
to start at Y so the predicate still parses. Guarded by valid_concept + not-a-pronoun (so 'it's raining' contractions
don't misfire).
- "A dog's heart is large." -> heart part-of dog; "The car's engine is powerful." -> engine part-of car.
- 'is a heart part of a dog?' -> Yes; 'does a dog have a heart?' -> Yes (the possession question reads the
  possessive-derived part-of). Regular is-a unaffected.
116/116 regression tests green (test added). Prediction HIT; tally 158/194. Established (possessive mereology),
named; no novelty. RESIDUE (deliberately not fixed -- ambiguous): the 'X of Y' nominal in subject position
('the engine of a car is powerful') stays unhandled because 'X of Y' is ambiguous between a part-of relation and a
compound concept ('form of government', 'state of matter') -- distinguishing them needs world knowledge / NER.

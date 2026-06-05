# JEP-208 — integrate numeric attributes into communication (describe)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 describe() mentioning numeric attributes ('It has 4 legs') completes the numeric integration; no regression.
  RISK: pluralization of the attribute in output.

## Result — PASS (HIT)
describe() now appends an entity's numeric attributes (from JEP-207's num_attrs), correctly pluralized (n!=1 -> +'s'):
- describe('dog') after 'A dog is a mammal. A dog has 4 legs. A dog has 2 eyes. A heart is part of a dog.' ->
  'A dog is a mammal. That makes it also an animal. It has a heart. It has 2 eyes and 4 legs.'
This completes the QUANTITATIVE-reasoning integration: extract 'X has N Y' (JEP-207) -> 'how many' Q&A -> numeric
comparison -> describe (JEP-208). The engine now learns, reasons about, answers questions on, AND communicates
quantities. 76/76 regression tests green (+1). Prediction HIT; tally 97/124. Established (template NL generation +
numeric attributes); named; no novelty.

# JEP-263 — mereological verbs 'X contains/consists of Y' -> Y part-of X

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 biology/geography QA showed 'The body consists of cells' / 'A cell contains a nucleus' / 'Bronze contains
  copper' extracted nothing (or induced 'contains' as OPEN). Adding 'X contains/consists of/comprises/includes Y' ->
  Y part-of X (whole->part) + excluding these from read_open fixes it; transitive part-of follows.

## Result — PASS (HIT)
Added a mereological-containment-verb pattern to read(): 'X contains/consists of/comprises/includes Y' -> tell_part(Y,
X) (Y is part-of the whole X), and added these verbs to read_open's is_fixed so they are not redundantly induced as
open relations.
- 'The body consists of cells. A cell contains a nucleus. Bronze contains copper.' -> cell part-of body, nucleus
  part-of cell, copper part-of bronze.
- TRANSITIVE: 'is a nucleus part of the body?' -> Yes (nucleus->cell->body). No redundant open 'contains'.
104/104 regression tests green (test added, suite already covers). Prediction HIT; tally 142/178. Established
(mereological lexical verbs, JEP-150/167), named; no novelty. Residual still open from the biology pass: 'does X have
Y?' question (JEP-264); 'has N <parts>' as both count AND part-of.

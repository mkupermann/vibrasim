# JEP-264 — 'does X have Y?' possession question (part-of with is-a inheritance, or numeric)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 biology QA showed 'does a human have a heart?' / 'does a mammal have a heart?' -> 'I cannot parse'. Adding a
  'does X have Y?' handler -> part_of(Y, X) (which already inherits to subtypes: human is-a mammal, heart part-of
  mammal) + a numeric-attribute fallback fixes it, without shadowing the existing 'does X have more Y than Z'.

## Result — PASS (HIT)
Added a possession-question handler AFTER the numeric 'more...than' comparison (so that form matches first): 'does X
have Y?' -> Yes if part_of(Y, X) (part-of query, which distributes the whole's parts to its is-a SUBTYPES, JEP-169),
else the numeric attribute if present, else No.
- 'does a human have a heart?' -> 'Yes. A heart is part of a human.' (human->mammal, heart part-of mammal — inherited).
- 'does a mammal have a heart?' -> Yes (direct). 'does a dog have legs?' -> 'Yes. A dog has 4 legs.' (numeric).
- 'does a human have a tail?' -> No. 'does a spider have more legs than a dog?' -> Yes (the comparison form still
  matches first — no shadowing).
105/105 -> 106/106 regression tests green (+1). Prediction HIT; tally 143/179. Established (possession-as-mereology +
the part-of x is-a interaction), named; no novelty. This + JEP-263 close the biology/anatomy QA pass.

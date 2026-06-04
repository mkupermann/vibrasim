# JEP-96 — engine tier 5: human-like LEARNING by correction in dialogue

## Why (Michael: "human-like LEARNING")
A human revises beliefs when corrected. Add: negative facts ("X is not a Y") that RETRACT a wrong belief and record
a constraint, plus a later "X is a Z" that installs the corrected parent — so the engine's answers CHANGE after
correction, like learning from a teacher.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100% on a believe->correct->answer-flips battery. MOST-LIKELY MISS: the negation parse in tell() (the _ISA
  regex grabbing 'not' as the object — the surface-form class AGAIN). Per the logged lesson, handle 'is not a'
  explicitly BEFORE _ISA (dedicated _NEG_ISA regex with required-space articles), retract the edge, and let an
  explicit negative override closure in is_a(). Predict 100%.

## Acceptance
- PASS: after correction the engine's is_a and explain answers flip correctly = 100%.
- Established (belief revision over a graph, negative constraints), named; no novelty. Honest: explicit single
  corrections; full belief-revision (propagating retractions, contradiction detection across chains) is a later tier.

## Calibration (after) — HIT
🔮 predicted 100% with negation-parse as the risk; handled 'is not a' with a dedicated _NEG_ISA regex BEFORE _ISA
(surface-form lesson applied proactively). ACTUAL 8/8 = 100%. HIT. Tally 5/8.

## Result — PASS (100%)
Correction battery 8/8 = 100%. The engine learns by correction: told "A whale is a fish" it infers whale->animal
via fish; corrected with "A whale is not a fish" + "A whale is a mammal" it RETRACTS the wrong edge, records the
negative constraint, installs the new parent, and BOTH its is_a answers and its English explanation flip:
"is a whale an animal?" -> "Yes. A whale is a mammal, a mammal is an animal." Human-like learning from a teacher,
no transformer. HONEST: explicit single corrections; full belief revision (propagating retractions, contradiction
detection across chains) is a later tier. Established (belief revision over a graph, negative constraints), named.

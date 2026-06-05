# JEP-195 — detect IMPLIED inconsistency in prose (inherited negatives), not just explicit

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 extending would_contradict to check inherited negatives (X or an ancestor recorded not-a Y) detects the implied
  inconsistency. RISK: over-flagging, or the negative-inheritance direction.

## Result — PASS (HIT)
would_contradict previously detected only DIRECT negatives ('X explicitly told NOT C'). Extended it: 'X is C'
contradicts if some ancestor A of X is recorded NOT-a B where C is (or is-a) B — i.e., X INHERITS 'not B' from A, so
asserting X is-a C (a kind of B) conflicts. Results:
- read('A whale is a mammal. A mammal is not a fish.') then 'A whale is a fish' -> 'Contradiction: a whale is a
  mammal, and a mammal is not a fish.' (the implied inconsistency, WITH the explaining chain).
- consistent assertions NOT flagged: 'A whale is an animal' -> None; 'A whale is a mammal' (already true) -> None.
- MULTI-HOP inherited negative: 'A poodle is a dog. A dog is a mammal. A mammal is not a plant.' -> 'A poodle is a
  plant' flagged (poodle->dog->mammal, mammal not plant).
So the engine now detects contradictions IMPLIED by the combination of read facts (inherited class-exclusion), not
just explicitly-stated ones — important for LEARN-FROM-SOURCES, where real sources carry IMPLICIT inconsistencies a
reader must catch. It explains WHY (the inheriting chain). No over-flagging on consistent assertions. 64/64
regression tests green (+1). Prediction HIT; tally 84/111. Established (inheritance-based consistency checking,
truth maintenance); named; no novelty.

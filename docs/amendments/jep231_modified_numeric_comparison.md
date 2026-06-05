# JEP-231 — adjective-modified numeric COMPARISON ('more large moons than'), symmetric with JEP-229

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 extending the numeric-comparison regex to 'more <modifier>* <head> than', keyed by head noun, makes modified
  comparisons work symmetric with JEP-229, no regression on 'more legs than'; a non-count predicate
  ('more interesting than') correctly falls through. Counter-examples run IN-RUNG (applying the JEP-230 lesson):
  plain / modified / non-count.

## Result — PASS (HIT)
JEP-229 fixed numeric CAPTURE of modified counts but left the COMPARISON path on a single-word regex — an asymmetry.
Closed it: the comparison query now allows modifiers and keys by the HEAD noun (same as capture). Counter-examples,
run in the same rung per error-class 11:
- modified:  'does Jupiter have more large moons than the Earth?' -> head 'moon' -> 4>1 -> 'Yes.'
- plain:     'does a spider have more legs than a dog?'           -> 8>4 -> 'Yes.' (no regression)
- reverse:   'does a dog have more legs than a spider?'           -> 'No.'
- non-count: 'does a dog have more interesting than a spider?'    -> 'I don't have those numbers.' (graceful; 'interesting'
             is not a stored attribute -> no false numeric claim, no crash).

94/94 -> 95/95 regression tests green (+1). Prediction HIT; tally 118/146. Capture and comparison are now symmetric for
modified count nouns. Established (head-noun keying across the read/query boundary); named; no novelty.

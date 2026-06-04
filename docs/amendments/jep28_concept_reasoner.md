# JEP-28 — mixed-curvature concept reasoner + held-out IS-A generalization (capstone of the reasoning arc)

## Motivation
Integrate JEP-26/27 into a usable artifact (a concept reasoner answering relatedness + IS-A) AND rigorously test
GENERALIZATION: hold out a fraction of IS-A (ancestor) supervision, train the hyperbolic map on the rest, predict
the HELD-OUT relations. Standard link-prediction test - does the embedding capture the hierarchy or memorize it?

## Pre-registration (locked BEFORE run)
- Real 77-concept taxonomy. Hold out 30% of (ancestor,descendant) supervision pairs at random; train hyperbolic
  on the remaining 70% (+ Euclidean for relatedness on full distances).
- Held-out test: for each held-out ancestor pair, predict the ANCESTOR (more general) by smaller hyperbolic norm.
- Bars: held-out IS-A direction accuracy >= 0.80 (generalizes to unseen hypernym relations) AND >> random (~0.5).
  PASS = the reasoner GENERALIZES the hierarchy. Ship tools/concept_reasoner.py. Poincare (Nickel-Kiela 2017),
  named as established.

## Result — PASS on held-out generalization; but per-query reliability LIMITED (honest caveat)
| metric | value |
|--------|-------|
| trained-pairs IS-A direction acc | 0.778 |
| HELD-OUT IS-A direction acc | 0.856 (random 0.5) |
| demo: nearest('cat') | ['tiger','lion','feline','canine','dog'] (correct) |
| demo: is_a('cat','mammal') | FALSE (WRONG - a cat IS a mammal) |
| demo: more_general('cat','mammal') | 'cat' (WRONG - mammal is more general) |

**VERDICT: PASS on the locked aggregate bar, with an HONEST reliability caveat.** Held-out IS-A direction
accuracy (0.856 >> 0.5) meets the >=0.80 bar - the hyperbolic embedding GENERALIZES the hierarchy to unseen
hypernym pairs (captures structure, not memorizes; held-out ~= trained). The relatedness side works well
(nearest('cat') returns felines/canines). BUT the demo VISIBLY FAILS on a common query: is_a('cat','mammal')
returns False and more_general('cat','mammal') returns 'cat' - both WRONG. At ~0.78-0.86 accuracy, ~15-22% of
individual IS-A queries are wrong, and cat/mammal is one of them. So: the generalization-ABOVE-CHANCE claim
holds, but the tool is NOT per-query reliable (a 2D Poincare embedding + norm-ordering readout is too crude for
confident individual answers; higher dim + a better hypernymy score, e.g. the Nickel-Kiela is-a score, would be
needed). I do NOT claim a deployable concept reasoner - I claim a demonstration that hierarchy generalizes,
honestly bounded. tools/concept_reasoner.py shipped as a reference, not a reliable product. Nickel-Kiela (2017)
established - named as such. Bars locked, not tuned.

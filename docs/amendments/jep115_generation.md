# JEP-115 — generative communication: describe a concept from structure (no transformer)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: describe(X) generates sentences covering X's categories, inherited categories, properties (own +
  induced, minus exceptions), and relations; an unknown concept says so. MOST-LIKELY MISS: de-duplication/ordering
  or property inheritance in the generated text.

## Acceptance
- PASS: description battery = 100% (contains the right facts, grammatical, no dupes). Established (template NL
  generation over a knowledge graph), named; no novelty. Honest: scripted templates, not open-ended generation.

## Result — generation works; the integration found TWO real bugs (now fixed)
describe(poodle): "A poodle is a dog and a pet. That makes it also an animal, a living thing. It chases the cat."
describe(robin): "A robin is a bird. That makes it also an animal, a living thing. It can fly."  describe(quark):
"I don't know anything about a quark yet." Battery 6/6. CALIBRATION: prediction MISSED (predicted dedup/ordering).
The describe() integration exposed TWO real bugs: (1) _norm_phrase did not strip a leading article, so describe("a
poodle") looked up "a poodle" -> fixed (strip leading article in the canonical normalizer, so every caller is
safe). (2) DEEPER: induction OVER-GENERALIZED - 'robins and sparrows fly' + they are animals made induce() add
'fly' to ANIMAL (and living thing), so a POODLE wrongly 'could fly'. JEP-105's test missed it (only checked
bird-level). FIX: induce a property only for the MOST-SPECIFIC common ancestor of the positive instances (their
lowest common ancestor), not every ancestor -> 'birds fly', not 'animals fly'; poodle no longer flies; penguin
override still works. Both fixed, 24 tests green. Tally MISS (17/27). LESSON (recurring): integration/generation
exposes errors unit tests assume away; and induction must generalize to the RIGHT (most-specific) category.
Established (template NL generation; subsumption-correct induction), named; no novelty.

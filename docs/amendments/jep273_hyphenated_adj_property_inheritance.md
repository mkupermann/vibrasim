# JEP-273 — hyphenated participial adjectives + defeasible PROPERTY inheritance

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 'Every mammal is warm-blooded' (JEP-272 strips the quantifier) left 'warm-blooded' uncaptured (the JEP-258
  adjective-suffix shape doesn't match hyphenated -ed); and even captured, a category property of an ancestor would
  not inherit to subtypes. Adding hyphenated participial adjectives to the property shape (in BOTH read-capture and
  describe-split) + ancestor-property inheritance in has_property fixes both, with explicit exceptions overriding.

## Result — PASS (HIT)
Two fixes: (1) the property-shape regex (used in read() capture AND describe() split -- the fix-in-every-parser
lesson) now also matches HYPHENATED participial adjectives `[a-z]+-[a-z]+(?:ed|ing)` ('warm-blooded','cold-blooded').
(2) has_property() now inherits a category property from an ANCESTOR to its subtypes (defeasibly), unless x explicitly
LACKS it -- the property x is-a interaction (parallel to JEP-169 parts distributing to subtypes).
- 'Every mammal is warm-blooded. A dog is a mammal. A poodle is a dog.' -> 'is a dog warm-blooded?' Yes (inherited),
  'is a poodle warm-blooded?' Yes (multi-hop poodle->dog->mammal). describe a mammal: 'It is warm-blooded.'
- EXCEPTION OVERRIDE: 'A bird can fly. A penguin cannot fly.' -> 'can a penguin fly?' No (explicit not_property beats
  the inherited 'bird can fly') -- defeasible inheritance with exceptions.
111/111 -> 112/112 regression tests green (+1). Prediction HIT; tally 152/188. Established (participial adjectives;
defeasible inheritance with exceptions, JEP-105/169), named; no novelty. Closes the quantified/property QA pass.

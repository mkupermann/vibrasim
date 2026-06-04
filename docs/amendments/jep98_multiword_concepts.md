# JEP-98 — multi-word concepts (a bug the DEMO caught that the tests missed)

## Why
The dialogue demo (real usage) exposed a bug the controlled tests missed: tests used the single token
"living_thing" (underscore); the demo used natural "living thing" (two words), which the engine couldn't parse
(object captured only one word) -> "No. ... makes a poodle a living." Real usage surfaces what controlled tests
assume away.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 routing every concept key through one _norm_phrase (lowercase, strip period, singularize LAST word) and
  capturing multi-word objects in _ISA/_NEG_ISA/ask/explain makes "An animal is a living thing" -> animal->'living
  thing', fixes the demo, and keeps all 9 tests + tiers 92/93/94 green (underscore form still one token). MOST-
  LIKELY MISS: greedy multi-word capture swallowing a trailing token, or SVO/relation mis-fire -> scoped multi-word
  to IS-A/ask objects only, relations stay single-word. Predict 100% + no regressions.

## Result — PASS (HIT)
Regression suite 9/9; tiers JEP-92 19/19, JEP-93 12/12, JEP-94 16/16 — all still 100%. Demo fixed:
"is a poodle a living thing?" -> "Yes. A poodle is a dog, a dog is an animal, an animal is a living thing." HIT;
tally 7/10. LESSON: the DEMO caught a bug the tests missed because the tests used a convenient encoding
("living_thing") the real input ("living thing") doesn't share — always exercise the engine on natural input, not
just the test-friendly form. Established (noun-phrase normalization), named; no novelty. Honest: subject still
single-token; full NP parsing (adjuncts, relative clauses) remains the frontier.

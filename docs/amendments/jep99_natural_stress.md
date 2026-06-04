# JEP-99 — natural-input stress test: harden the engine, map its boundary (lesson from JEP-98)

## Why
JEP-98's lesson: exercise on NATURAL input, not the test-friendly form. Stress the engine with varied phrasings,
predict per item which break, fix the tractable ones, document the rest as the honest boundary.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 PASS: plurals, multi-word categories, no-article questions. FAIL: adjectival subjects ("A big dog is an
  animal" -> subject regex grabs "big"), plural SVO ("Poodles chase cats" -> _SVO requires "the"), pronouns.

## Result — per-item prediction HIT, then fixed
Initial run: "A big dog is an animal" and "Poodles chase cats" both failed to parse (exactly as predicted).
Fixes: (1) _ISA/_NEG_ISA subject -> multi-word noun phrase; (2) _SVO leading "the" optional (plural statements);
(3) PROPAGATED multi-word to the QUERY parsers via a shared _parse_isa_q() (the JEP-94 "fix every parser" lesson —
I'd fixed the fact parser but not the question parser, so "is a big dog an animal" still failed until propagated).
After fixes: "A big dog is an animal" parses; is_a("big dog","animal")=True; "Poodles chase cats" parses and
"does the poodle chase the cat"=True (correctly linked). Full suite 10/10, tiers 92-97 all 100% (gated). One
runner "miss" was my own WRONG expected value (None) — the engine correctly returns True. Calibration: per-item
prediction HIT; tally 7/11. HONEST BOUNDARY (still out of scope): pronouns, relative clauses, multi-word relation
objects, compound subjects ("dogs and cats"). Established (NP normalization, regex parsing), named; no novelty.

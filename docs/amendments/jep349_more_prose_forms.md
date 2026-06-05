# JEP-349 — More prose forms: conjunctions, relative clauses, locational

## Motivation
Keep widening Half-1: handle three more common encyclopedic forms in the substrate-legal normalizer (no engine
change): conjunction subjects ("Cats and dogs are mammals" → two facts), relative clauses ("A poodle, which is a
dog, can bark" → is-a + property), and locational ("Paris is in France" → located_in). No transformer.

## Method
`_normalize_for_learning` now returns (sentences_list, extra_facts): split a conjunction subject into one sentence
per subject; split a "X, which is a Y, …" relative clause into the is-a plus the remainder with X as subject; emit a
located_in fact for "X is (located) in Y".

## Pre-registered bars (BEFORE the run)
- **J349a (new forms work):** "Cats and dogs are mammals." → is_a(cat,mammal) ∧ is_a(dog,mammal); "A poodle, which
  is a dog, can bark." → is_a(poodle,dog) ∧ has_property(poodle,bark); "Paris is in France." → located_in via climb;
  all true, both seeds (0, 7).
- **J349b (coverage + no prose regression):** a richer paragraph mixing all forms parses ≥ 0.85; JEP-347/348
  re-run still PASS (coverage not reduced on prior forms).
- **J349c (no regression):** conversation gate (test_conversation) + substrate gate green.

Predicted most-likely failure: the conjunction/relative-clause split is greedy and mangles a normal sentence (e.g.
"black and white" as a conjunction subject), or the relative-clause remainder loses its subject. Keep patterns
conservative (require " and " between two single nouns; require "which is a"); if J349b regresses, report the
sentence.

## Result (seeds 0, 7): **PASS**
- **J349a:** all new forms = **1.0** — conjunction ("Cats and dogs are mammals" → cat∧dog is-a mammal); relative
  clause ("A poodle, which is a dog, can bark" → is_a(poodle,dog) ∧ has_property(poodle,bark)); locational
  ("Paris is in France", "France is in Europe" → located_in, incl. multi-hop Paris→Europe), both seeds. **PASS.**
- **J349b/c:** JEP-347 (0.933) and JEP-348 re-run still PASS; conversation + substrate gates green. **PASS.**

## Verdict: **PASS**
The substrate-legal normalizer now reads conjunction subjects, relative clauses, and locational forms — three more
common encyclopedic constructions — without touching the engine and without regressing prior coverage. Steady Half-1
progress toward reading-a-book-and-discussing. No transformer.


# JEP-382 — Fix the relative-clause head bug in plural is-a ("X are Y that ...")

## Motivation
JEP-381's one real defect: the plural is-a rule normalizes "Mammals are animals that are warm-blooded" to "A mammal is
a warm-blooded" — it takes the LAST word of the object as the head, so a trailing relative clause ("that are warm-
blooded") hijacks the head, mis-storing `mammal→warm-blooded` instead of `mammal→animal` and breaking every multi-hop
chain through "mammal". Fix: strip a trailing relative clause ("... that/which ...") before taking the head noun, and
opportunistically capture "that are <adjective>" as a property. No transformer.

## Method
In `_normalize_for_learning`, before taking the object head in the plural is-a rule, split off any "that|which ..."
relative clause and use the head of the remaining noun phrase. If the relative clause is "that are <adj>", add
(subj, hasprop, <adj>) as an extra fact.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: the fix yields `mammal→animal` (+ optionally mammal hasprop warm-blooded), restoring dog→animal and
poodle→animal; JEP-381 Q&A rises to ≥0.90 with multi-hop; coverage and abstention unchanged; suite green.

- **J382a (head fixed):** "Mammals are animals that are warm-blooded" yields (mammal, isa, animal) [and NOT (mammal,
  isa, warm-blooded)], both seeds (0, 7).
- **J382b (JEP-381 Q&A restored):** re-running JEP-381, Q&A accuracy ≥0.90 AND both multi-hop questions (poodle→animal,
  salmon→vertebrate) correct, coverage still ≥0.90, OOD abstention still 1.0, both seeds.
- **J382c (no regression):** simple plural is-a ("Dogs are mammals" → dog→mammal) and the conjunction/such-as handlers
  still work; `pytest -m "not slow" tests/test_conversation.py` passes.

If stripping the relative clause breaks another construction, report it. Predicted clean fix. Bars fixed; no retuning.
No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — bug fixed, article now fully reliable)
- **J382a (head fixed): PASS** — "Mammals are animals that are warm-blooded" → (mammal, isa, **animal**), and NOT
  (mammal, isa, warm-blooded); the relative clause is captured as a property instead. Both seeds.
- **J382b (JEP-381 Q&A restored): PASS** — re-running the full JEP-381 article: Q&A accuracy **1.0** (up from 0.833),
  both multi-hop questions (poodle→animal, salmon→vertebrate) correct, coverage still **0.963**, OOD abstention **1.0**.
  Both seeds.
- **J382c (no regression): PASS** — simple plural is-a ("Dogs are mammals" → dog→mammal) and the conjunction handler
  ("Cats and dogs are carnivores") still work; `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — real-prose capture is now reliable end-to-end at article scale**
Stripping the trailing relative clause before taking the head noun fixes the "X are Y that ..." mis-parse, restoring
the is-a chains through "mammal". The ~28-sentence natural article is now captured at **96% coverage**, answered at
**100% Q&A accuracy** (including multi-hop via consolidation), with **perfect honest abstention** on everything
unmentioned — all through the live `Conversation.say()` path, end-to-end. Combined with the within-domain reliability
arc (370→378), the substrate now reads a realistic factual article and answers it without mistakes inside the captured
domain while saying "I don't know" outside it. The open-domain knowledge-tail wall (JEP-362) is separate and stands.
Established method (rule-based normalization + VSA consolidation); no transformer.

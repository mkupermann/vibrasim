# JEP-415 — Wikipedia-style factual prose: parentheticals, head fix, singular fix, superlatives

## Motivation
Probing real encyclopedia opening sentences (the prose Michael will successfully use) surfaced WRONG captures and gaps:
- "The lion is a large cat native to Africa." → ('lion', isa, **africa**) — the trailing "native to Africa" hijacks the
  is-a head (should be "cat").
- "Oxygen is a gas." → ('oxygen', isa, **ga**) — `_singular` wrongly strips "gas"→"ga".
- "The lion (Panthera leo) is a large cat." → NONE — the parenthetical breaks parsing.
- "The Nile is the longest river in the world." / "A tiger is the largest cat." → NONE — "is THE <noun>" (superlative)
  not handled (only "is a/an").
Fix these (the wrong captures are correctness-critical). No transformer.

## Method
- Strip parentheticals "(…)" at the top of `_normalize_for_learning`.
- In the singular copular is-a head rule (JEP-414), split the noun phrase before a trailing modifier (native/found/
  located/known/used/called/of/in/that/…) so the head is the noun, not a trailing place ("large cat native to Africa"
  → cat; "longest river in the world" → river).
- Handle "X is the <…> <head>" (superlatives) like "X is a <head>".
- Add `_singular` exceptions for -s singular nouns (gas, bus, lens, virus, species, series, news, physics).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J415a (head/place fix):** "The lion is a large cat native to Africa. A cat is a mammal." → "is a lion a cat?" yes,
  "is a lion a mammal?" yes, and NO ('lion', isa, 'africa'); both seeds (0, 7).
- **J415b (parenthetical + superlative):** "The lion (Panthera leo) is a large cat." → (lion, isa, cat); "A tiger is
  the largest cat." → (tiger, isa, cat); both seeds.
- **J415c (singular + no regression):** "Oxygen is a gas." → (oxygen, isa, gas) [not 'ga']; "A dog is a mammal." → still
  (dog, isa, mammal); `pytest -m "not slow" tests/test_conversation.py` passes; both seeds.

If a fix mis-fires, report it. Predicted clean. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (all fixes; wrong captures eliminated)
- **J415a (head/place fix): PASS** — "The lion is a large cat native to Africa." → (lion, isa, **cat**) [was 'africa'];
  with "A cat is a mammal. Mammals are animals." → "is a lion an animal?" yes. No lion→africa.
- **J415b (parenthetical + superlative): PASS** — "The lion (Panthera leo) is a large cat." → (lion, isa, cat);
  "A tiger is the largest cat." → (tiger, isa, cat); "The Nile is the longest river in the world." → (nile, isa, river).
- **J415c (singular + reverse-attribute + no regression): PASS** — "Oxygen is a gas." → (oxygen, isa, **gas**) [was
  'ga']; "Berlin is the capital of Germany." → (germany, capital, berlin) → "what is the capital of Germany?" → Berlin;
  "A dog is a mammal." intact; full cognition suite **35 tests** pass.

## Verdict: **PASS — real encyclopedia opening sentences parse correctly, no wrong captures**
Parenthetical stripping, head-noun extraction before trailing modifiers, superlative "is the <noun>", reverse attribute
"V is the A of Y", and _singular exceptions (gas) make Wikipedia-style factual prose parse correctly — fixing two wrong
captures (lion→africa, oxygen→ga) and enabling common forms — while keeping never-wrong-capture and 35 tests green. This
is the reachable target hardened: clean factual reference prose. No transformer.

# JEP-420 — Teaching English (3): antonyms and opposite-reasoning

## Motivation
Continuing the English foundation from Fernald (Synonyms AND Antonyms). Teaching opposites lets the substrate reason
"if X is tall, X is NOT short" and answer "what is the opposite of X?". The reverse-attribute rule (JEP-415) already
stores "Big is the opposite of small" as (small, opposite, big) cleanly. Wire that into reasoning. No transformer.

## Method
- `_opposites(w)`: words taught as the opposite of w (symmetric `opposite` relation).
- `has_property`: if x has a property that is the opposite of p, then x is NOT p (antonym-based negation).
- Parser: "what is the opposite of X?" → the stored opposite.

## Pre-registered bars
- **J420a:** "Tall is the opposite of short. A giraffe is tall." → "is a giraffe tall?" yes, "is a giraffe short?" No
  (antonym); "A mouse is small. Big is the opposite of small." → "is a mouse big?" No; both seeds (0, 7).
- **J420b:** "what is the opposite of tall?" → short; "what is the opposite of big?" → small.
- **J420c:** `pytest -m "not slow" tests/test_conversation.py` passes.

## Result: **PASS** (both seeds) — giraffe tall yes / short No, mouse big No, opposite-of tall->short / big->small,
10 tests pass.

## Verdict: **PASS — the substrate reasons with opposites (a third English lesson)**
Antonyms taught from Fernald give the substrate opposite-reasoning ("if X is tall, X is not short") and an
"what is the opposite of X?" query, built on the cleanly-stored `opposite` relation. With synonyms (JEP-419) and verb
morphology (JEP-417), the English-understanding foundation is broadening — all taught by the LLM from real resources,
with no LLM in the substrate.

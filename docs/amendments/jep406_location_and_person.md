# JEP-406 — "where is X?" + first/second-person is-a ("I am a teacher", "You are a substrate")

## Motivation
More natural GUI forms: locational facts store correctly ("Paris is in France" → located_in) but "where is X?" isn't
parsed; and first/second-person is-a ("I am a teacher", "You are a substrate") stores nothing (pronoun subjects are
rejected). Add the "where is X?" query and self/second-person is-a so a user can describe themselves and the substrate.
No transformer.

## Method
- `_normalize_for_learning`: "I am a/an Y" → (user, isa, Y); "You are a/an Y" → (you, isa, Y).
- `BrainQuery.ask`: "where is X?" → located_in(X) (display value); "what am I?" → most-specific parent of "user";
  "what are you?" → most-specific parent of "you".

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J406a (where):** "Paris is in France." → "where is Paris?" → France, both seeds (0, 7).
- **J406b (person is-a):** "You are a substrate." → "what are you?" → substrate; "I am a teacher." → "what am I?" →
  teacher, both seeds.
- **J406c (no regression):** is-a multi-hop intact; `pytest -m "not slow" tests/test_conversation.py` passes; both seeds.

If a rule mis-fires, report it. Predicted clean. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J406a (where): PASS** — "Paris is in France." → "where is Paris?" → **France**. Both seeds.
- **J406b (person is-a): PASS** — "You are a substrate." → "what are you?" → **substrate**; "I am a teacher." → "what
  am I?" → **teacher**. Both seeds.
- **J406c (no regression): PASS** — is-a multi-hop intact; `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — locational queries and self/second-person facts now work**
"where is X?" answers from the stored `located_in` relation, and the user can describe themselves and the substrate
("I am a teacher" → "what am I?"; "You are a substrate" → "what are you?"). Natural conversational self-reference is now
supported, extending the GUI's teaching range. No transformer.

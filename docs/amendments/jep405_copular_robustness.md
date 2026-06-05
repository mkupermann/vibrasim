# JEP-405 — GUI teaching robustness: past tense, copular adjectives, first-person

## Motivation
Probing what a GUI user naturally types surfaced common failures: "Einstein was a physicist" (past-tense is-a),
"The sun is hot" / "Dogs are loyal" (copular ADJECTIVE → property, not is-a), and first-person "My name is Michael" /
"what is my name?" (the JEP-404 attribute store uses entity "user" for "my", but there was no query for it). Fix these
three high-frequency forms so Michael can teach naturally. No transformer.

## Method
- **Past tense:** rewrite "X was a/an Y" → "X is a/an Y" and "X were Y" → "X are Y" (after the passive rule, which
  already consumes "was/were <participle> by").
- **Copular adjective → property:** "X is/are <single-word>" with NO article before the word and the word not a known
  class → (X, hasprop, word). The article distinguishes is-a ("a dog is A mammal") from property ("the sun is hot").
- **First-person query:** "what is my <A>?" → look up (user, A, ?), matching the existing "my A is V" storage.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: the three forms work, is-a/property stay correct, no regression.

- **J405a (past tense is-a):** "Einstein was a physicist." → "is Einstein a physicist?" → yes, both seeds (0, 7).
- **J405b (copular adjective property):** "The sun is hot." → "is the sun hot?" → yes; "Dogs are loyal." → "are dogs
  loyal?" → yes; AND "A dog is a mammal." → "is a dog a mammal?" → yes (article still routes to is-a, not property),
  both seeds.
- **J405c (first-person + no regression):** "My name is Michael." → "what is my name?" → Michael; is-a multi-hop still
  works ("A poodle is a dog. A dog is a mammal." → "is a poodle a mammal?" yes); `pytest -m "not slow"
  tests/test_conversation.py` passes; both seeds.

If the copular-adjective rule mis-fires on an is-a/locational sentence, report it. Predicted clean. Bars fixed; no
retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — all three forms work)
- **J405a (past-tense is-a): PASS** — "Einstein was a physicist." → "is Einstein a physicist?" → yes AND "what was
  Einstein?" → physicist. Both seeds.
- **J405b (copular adjective property): PASS** — "The sun is hot." → "is the sun hot?" → yes; "Dogs are loyal." → "are
  dogs loyal?" → yes; "A dog is a mammal." → "is a dog a mammal?" → yes (article still routes to is-a). Both seeds.
- **J405c (first-person + no regression): PASS** — "My name is Michael." → "what is my name?" → Michael; is-a multi-hop
  intact; `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — natural GUI teaching forms now handled**
Past tense ("X was a Y" → is-a; "what was X?"), copular adjectives ("The sun is hot", "Dogs are loyal" → answerable via
is_a-or-property), and first-person attributes ("My name is Michael" → "what is my name?") all work; the article
distinguishes is-a from a copular predicate so is-a is unaffected. Adjectives stored as degenerate is-a (queryable by
"is X Y?" and "are X Y?") — a pragmatic conversational-brain choice, the honest trade. No transformer.

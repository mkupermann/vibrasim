# JEP-341 — Richer conversational understanding (more natural phrasings + pronouns + "tell me about")

## Motivation
The conversation's STATEMENT side already spans the full Understanding Engine (123 construction tests). The QUESTION
side (BrainQuery parser) is narrowly templated. Widen it toward "human-to-human": handle "does X have Y?",
"how many legs does a dog have?", "is X a kind of Y?", "tell me about X" (a spoken summary), and the pronoun "it"
(referring to the last thing discussed). No transformer.

## Method
Add `BrainQuery` templates + a `describe(x)` summary ("A poodle is a dog; it can bark; it has 4 legs."). Track the
last subject in `Conversation` and substitute a standalone "it". All over the durable store.

## Pre-registered bars (BEFORE the run)
- **J341a (natural question battery):** a battery of varied natural phrasings — "does a poodle have legs?",
  "how many legs does a dog have?", "is a poodle a kind of animal?", "tell me about a poodle", "what does a cat
  eat?", plus a pronoun follow-up ("…can it bark?") — answered correctly ≥ 0.90, both seeds (0, 7).
- **J341b (no regression):** JEP-322 + JEP-340 still PASS; substrate test gate green.
- **J341c (describe is well-formed):** `describe(x)` returns a sentence that names the class AND at least the known
  properties/quantities, and re-reads into the engine without error.

Predicted most-likely failure: pronoun "it" mis-binds when a question (not a statement) was the last turn — bind
only to the last SUBJECT mentioned (statement or question topic). If J341a misses on the pronoun turn, report the
binding rule.

## Result (seeds 0, 7): **PARTIAL**
- **J341a:** natural-question battery = **5/6 (0.833)** + pronoun 1.0. Working: "is X a kind of Y?",
  "does X have legs?", "how many legs does X have?", "can X bark?", "does X have a heart?", pronoun "it". The one
  miss: **"what does a cat eat?"** → []. **Diagnosed:** the Understanding Engine only INDUCES an open verb ("eats")
  when both occurrences are in ONE `read()` call; the conversation reads one sentence per turn, so it never crosses
  the 2-occurrence threshold — an engine architectural boundary, not a substrate/parser bug. Fixed the regex
  ("a kind of" vs article-stripping) and `ingest_engine` now DOES bridge open relations (`eng.facts`) when the
  engine has learned them. **Bar not met (0.833 < 0.90).**
- **J341b:** no regression — JEP-322, JEP-340 still PASS; 13 substrate tests green. **PASS.**
- **J341c:** `describe("poodle")` = "A poodle is a dog; it can bark; it has 4 legs." — names class + properties +
  quantity, re-readable. **PASS.**

## Verdict: **PARTIAL**
Conversation understanding is meaningfully richer (kind-of / does-have / how-many / tell-me-about / pronoun "it",
all PASS) and `ingest_engine` now carries open relations. The lone miss is the engine's open-verb induction needing
co-occurrence within one read — a real, honestly-named boundary of the engine (open relations must be taught
together, not drip-fed across turns), not the substrate. Bar held at 0.90, not moved. No transformer.


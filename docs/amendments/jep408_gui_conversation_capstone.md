# JEP-408 — GUI conversation capstone: all natural forms compose in one session

## Motivation
JEP-404→407 each added a natural teaching form. This validates they COMPOSE in one realistic mixed GUI session
(taxonomy + attributes + actions + locations + self-reference + past tense + adjectives + corrections), with every
question answered correctly and ZERO wrong answers — interaction bugs between the many parser rules are what isolated
tests miss. No transformer.

## Method
One `Conversation`: teach ~16 statements spanning all forms, then ask ~14 questions with known answers (including the
corrected one), plus out-of-domain probes. Classify each as correct / abstain / falsehood.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: all forms compose; high correctness; zero falsehoods.

- **J408a (mixed Q&A):** ≥0.90 of in-domain questions correct across is-a (multi-hop), property, attribute, action,
  location, self-reference, past tense, both seeds (0, 7).
- **J408b (zero falsehoods):** zero confident-wrong answers across the session incl. OOD probes, both seeds.
- **J408c (no regression):** `pytest -m "not slow" tests/test_conversation.py` passes.

If a form breaks another (interaction bug), report it. Predicted clean. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** — **15/15 Q&A, zero falsehoods, suite green**, both seeds.
A single session teaching ~16 statements across taxonomy, property, attribute, action, location, self/second-person,
past tense, and a mid-stream correction answered EVERY question correctly (poodle→animal multi-hop, dog loyal, 4 legs,
dog has tail, creator→Michael Kupermann, my-name→Michael, what-am-I→teacher, what-are-you→substrate, Michael-likes→
coffee, where-Paris→France, Einstein→physicist, sun→hot, correction whale-not-fish→mammal), with zero falsehoods incl.
OOD probes, and the conversation suite green.

## Verdict: **PASS — the conversational substrate handles a realistic mixed session end-to-end**
All natural teaching forms added across the programme compose without interference in one GUI session — every question
correct, zero falsehoods, honest abstention on the unmentioned, no interaction bugs. The integration proof for the GUI
Michael is using: he can teach naturally across all forms and get correct answers without mistakes. No transformer.

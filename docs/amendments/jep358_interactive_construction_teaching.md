# JEP-358 — Interactive construction teaching: the brain asks when it can't parse, and learns the form

## Motivation
JEP-357 added self-extending reading via `teach_construction`. Make it INTERACTIVE: when the conversation gets a
statement it genuinely can't parse, it asks the teacher "what does that mean?"; the teacher answers with the fact;
the brain records it and, after 2 examples of the same form, learns the construction and reads it thereafter. This
is Michael's human-in-the-loop made live. No transformer.

## Method
`Conversation`: `_is_unparseable(s)` (a fresh engine + normalizer + learned templates all yield nothing) → enter a
pending state and ask. Next turn, a fact-shaped answer ("humans domesticated dog") routes to `teach_construction`;
after the 2nd aligned example it announces it learned the pattern. A re-stated KNOWN fact does NOT trigger the ask
(it parsed, just nothing new).

## Pre-registered bars (BEFORE the run)
- **J358a (asks + learns live):** an unparseable statement → the brain asks for the meaning; the teacher's fact is
  recorded; after 2 such examples of one construction, a HELD-OUT sentence of that form is then read and answered,
  ≥ 0.90, both seeds (0, 7).
- **J358b (no false ask):** a normal parseable statement ("A poodle is a dog.") does NOT trigger the ask; a
  RE-STATED known fact does NOT trigger it either.
- **J358c (no regression):** conversation gate + JEP-357 still PASS.

Predicted most-likely failure: `_is_unparseable` false-positives on a parseable-but-duplicate sentence (triggering a
needless ask) — gate the ask on a fresh-engine parse check, not on grew==0. If J358b shows a false ask, report it.

## Result (seeds 0, 7): **PASS**
- **J358a:** unparseable "The dog was domesticated by humans." → brain asks for the meaning; teacher answers
  "humans domesticated dog"; after the 2nd example it announces "I've learned that pattern!"; a held-out
  "A cat was domesticated by farmers." then parses (farmers,domesticated,cat in the store), both seeds. **PASS.**
- **J358b:** a normal "A poodle is a dog." does NOT trigger the ask; a RE-STATED known fact does NOT either
  (gated on a fresh-engine parse check, not grew==0), both seeds. **PASS.**
- **J358c:** conversation gate + JEP-357 still PASS. **PASS.**

## Verdict: **PASS — human-in-the-loop self-extension, live**
When the brain genuinely can't parse a sentence it ASKS the teacher for the meaning (3-word fact), records it, and
after 2 examples of that form induces the construction and reads it by itself thereafter — all in the live
Conversation (and thus the web GUI). This is Michael's teaching-in-the-loop made real: the human teaches the
substrate to UNDERSTAND NEW SENTENCE FORMS, conversationally, and it extends its own reading — no LLM. The honest
boundaries (template-level, synonyms need taught equivalence) stand from JEP-355/356. No transformer.


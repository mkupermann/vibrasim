# JEP-409 — "Tell me about X" synthesizes actions/attributes too, not just taxonomy

## Motivation
`describe` ("tell me about X") synthesized only taxonomy/property/count/parts, so "tell me about Michael" after teaching
"Michael is a teacher / likes coffee / wrote a book" returned only "a Michael is a teacher" — missing the actions and
attributes. Enrich `describe` to include open-relation facts where X is the subject, so discussion reflects EVERYTHING
known about an entity (helps the user inspect what the brain learned). No transformer.

## Method
In `describe`, after taxonomy/property/count/parts, append open-relation facts (s == x, relation not structural):
attribute-like relations ("name", "role", "creator", …) phrased "its R is V", others "it R V".

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J409a (actions/attributes included):** after "Michael is a teacher. Michael likes coffee. Michael wrote a book." →
  "tell me about Michael" mentions teacher AND coffee AND book, both seeds (0, 7).
- **J409b (taxonomy intact, no junk):** "tell me about a poodle" (dog/bark/legs/tail taught) still mentions dog, bark,
  legs, and tail, with no spurious open-relation noise, both seeds.
- **J409c (no regression):** `pytest -m "not slow" tests/test_conversation.py` passes.

If enrichment adds noise to a taxonomy describe, report it. Predicted clean. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J409a (actions/attributes): PASS** — "tell me about Michael" → "A Michael is a teacher; it likes coffee; it wrote
  book." Both seeds.
- **J409b (taxonomy intact): PASS** — "tell me about a poodle" → "A poodle is a dog; it can bark; it has 4 legs; it has
  a tail." (no spurious noise). Both seeds.
- **J409c (no regression): PASS** — `tests/test_conversation.py` **10 passed**.

## Verdict: **PASS — discussion reflects everything known about an entity**
`describe` now synthesizes taxonomy + properties + count + parts + open relations (actions/attributes), so "tell me
about X" gives the full picture — directly helping the user inspect what the brain learned. Taxonomy describe unchanged.
(Cosmetic: name-casing/articles imperfect; content correct.) No transformer.

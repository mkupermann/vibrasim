# JEP-404 — Teach attribute/possessive facts in natural language (Michael's GUI need)

## Motivation
Michael, using the GUI, found he can't teach detailed/personal facts: "The name of your creator is Michael Kupermann",
"Your creator is Michael Kupermann", "Your name is EQMOD" all fail (or, worse, "the capital of France is Paris" →
junk `('capital of france','isa','paris')`). The substrate only handled is-a/property forms. Add ATTRIBUTE/possessive
statements ("X's A is V", "the A of X is V", "your A is V", "V is your A") with multi-word proper-noun values, and make
them queryable ("who is your creator?", "what is your name?", "what is the capital of France?"). Uses the open-relation
machinery (attribute = role). No transformer.

## Method
- `_normalize_for_learning`: extract attribute facts to (entity, attr, value): possessive "X's A is V" / "the A of X
  is V" / "your A is V" / reverse "V is your A". `your` → entity "you"; multi-word proper-noun values joined with "_".
- `BrainQuery`: query rules "what is the A of X?", "what is X's A?", "who/what is your A?", "what is your A?" →
  forward lookup of (entity, attr, ?); answers display "_" as space, title-cased for names.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: attribute facts are taught and queryable; the junk is-a mis-capture is gone.

- **J404a (teach + query self/attribute):** "Your creator is Michael Kupermann." then "who is your creator?" →
  "Michael Kupermann"; "Your name is EQMOD." then "what is your name?" → "EQMOD", both seeds (0, 7).
- **J404b (of/possessive + query):** "The capital of France is Paris." → "what is the capital of France?" → "Paris"
  (and NOT the junk `('capital of france','isa','paris')`); "The name of your creator is Michael Kupermann." → "what is
  the name of your creator?" → "Michael Kupermann", both seeds.
- **J404c (no regression):** is-a still works ("A poodle is a dog." → "is a poodle a dog?" yes); `pytest -m "not slow"
  tests/test_conversation.py` passes; both seeds.

If an attribute rule mis-fires on an is-a sentence, report it. Predicted clean. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — Michael can teach detailed facts now)
- **J404a (teach + query self/attribute): PASS** — "Your creator is Michael Kupermann." → "who is your creator?" →
  **Michael Kupermann**; "Your name is EQMOD." → "what is your name?" → **EQMOD**. Both seeds.
- **J404b (of/possessive + no junk): PASS** — "The capital of France is Paris." → "what is the capital of France?" →
  **Paris**, with NO junk `('capital of france','isa','paris')`; "The name of your creator is Michael Kupermann." →
  "what is the name of your creator?" → **Michael Kupermann**. Both seeds.
- **J404c (no regression): PASS** — "A poodle is a dog." → "is a poodle a dog?" → yes; `tests/test_conversation.py`
  **10 passed**. Both seeds.

## Verdict: **PASS — natural-language attribute/personal facts now teachable (Michael's GUI need met)**
Possessive/attribute statements ("X's A is V", "the A of X is V", "your A is V", "V is your A") are parsed to
(entity, attr, value) open relations — with multi-word proper-noun values joined — and answered by natural questions
("who is your creator?", "what is your name?", "what is the capital of France?"). The prior junk mis-capture
("capital of france"→isa→paris) is gone, and is-a is unaffected. Michael can now teach the substrate detailed and
personal facts in the GUI, not just is-a/property forms. (Minor: an all-caps value like "EQMOD" displays title-cased as
"Eqmod" since values are lowercased on store — cosmetic.) Uses the open-relation machinery (attribute = role); no
transformer.

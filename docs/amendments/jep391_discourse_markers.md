# JEP-391 — Strip leading discourse markers so corrections in prose parse ("Actually, a whale is not a fish")

## Motivation
Michael explicitly wanted the substrate to handle CORRECTIONS. The probe found it silently ignores them in natural
prose: "Actually, a whale is not a fish." produces NO not_isa fact (the leading "Actually," breaks the negation parse),
so after a correction "is a whale a fish?" still wrongly answers "yes". Discourse markers (Actually/However/In fact/
Indeed/...) are exactly how corrections and emphasis appear in real text. Fix: strip a leading discourse marker before
normalizing, so the underlying statement (including negations/corrections) parses. No transformer.

## Method
At the top of `_normalize_for_learning`, strip a leading discourse marker (actually/however/indeed/in fact/of course/
moreover/furthermore/therefore/thus/note that) with an optional following comma. Then the existing negation handler
yields not_isa, and defeasible is_a (not_isa wins) returns the corrected answer.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: corrections in flowing prose now parse and override the earlier statement.

- **J391a (marker stripped):** "Actually, a whale is not a fish." → (whale, not_isa, fish); "However, a dog is a
  mammal." → (dog, isa, mammal), both seeds (0, 7).
- **J391b (correction overrides end-to-end):** read "A whale is a fish." then "Actually, a whale is not a fish. A
  whale is a mammal." → `say("is a whale a fish?")` → no AND `say("is a whale a mammal?")` → yes, both seeds.
- **J391c (no regression):** a plain sentence with no marker still parses ("A dog is a mammal" → dog→mammal); `pytest
  -m "not slow" tests/test_conversation.py` passes.

If stripping a marker mangles a sentence whose first word legitimately is one of these, report it. Predicted clean.
Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — corrections in prose now work)
- **J391a (marker stripped): PASS** — "Actually, a whale is not a fish." → (whale, not_isa, fish); "However, a dog is
  a mammal." → (dog, isa, mammal). Both seeds.
- **J391b (correction overrides end-to-end): PASS** — read "A whale is a fish." (→ "is a whale a fish?" yes), then
  "Actually, a whale is not a fish. A whale is a mammal." → "is a whale a fish?" → **no**, "is a whale a mammal?" →
  **yes**. The correction overrides via defeasible is_a (not_isa wins). Both seeds.
- **J391c (no regression): PASS** — "A dog is a mammal" → dog→mammal; `tests/test_conversation.py` **10 passed**.
  Both seeds.

## Verdict: **PASS — the substrate now updates from corrections in real text**
Stripping a leading discourse marker (Actually/However/In fact/Indeed/...) lets corrections and emphasis in flowing
prose parse: a correction like "Actually, a whale is not a fish" now stores the negation and overrides the earlier
"whale is a fish" through defeasible is_a (most-specific/negation wins), so after the correction the brain answers
"no". This realizes the correction-handling Michael asked for — the substrate revises its knowledge when the text
corrects it, rather than silently keeping the wrong fact. Established rule-based normalization over the existing
negation/defeasible machinery; no transformer.

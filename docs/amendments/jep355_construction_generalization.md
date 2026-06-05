# JEP-355 — Construction induction, attack C: does it learn structure or just slots?

## Motivation
JEP-354 induced TEMPLATES that need exact fixed words. The real breakthrough test: does it generalise to sentences
with minor variation (different article "a"↔"the") it never saw? Naive exact-match should FAIL (it memorised the
literal fixed words); abstracting FUNCTION WORDS (articles) should let it generalise — a genuine step from
slot-memorisation toward structure. Established (function-word abstraction in template/grammar induction). No
transformer.

## Method
Train a template from 2 examples (with "The …"); test on held-out sentences with a DIFFERENT article ("A …").
`apply_template(..., flex_articles=False)` = naive exact match; `flex_articles=True` treats a/an/the at fixed
positions as a wildcard (any article matches).

## Pre-registered PREDICTION + bars
Prediction: naive exact-match FAILS on article-varied held-out (it learned the literal "the"); function-word
abstraction generalises it. This is the honest "structure vs slots" boundary — abstraction over function words is
real generalisation; abstraction over content/word-order is NOT yet attempted.
- **J355a (naive is brittle):** naive `flex_articles=False` recall on article-varied held-out < 0.5, both seeds
  (0, 7) — the honest gap that proves it had memorised literal words.
- **J355b (abstraction generalises):** `flex_articles=True` recall on the SAME article-varied held-out ≥ 0.90, both
  seeds, with still zero false-fire on a different construction.

Predicted most-likely surprise: if naive ALREADY ≥0.5, the templates happened to share articles — report and use a
harder variation. If even flex < 0.90, the residual variation (word order / synonyms) is the named next boundary.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J355a:** naive exact-match on article-varied held-out = **0.0**, both seeds — proving the template had memorised
  the literal "The"; it cannot handle "A …". **PASS** (the honest brittleness gap).
- **J355b:** with function-word abstraction (a/an/the → wildcard at fixed positions), recall on the SAME varied
  held-out = **1.0**, zero false-fire on a different construction, both seeds. **PASS.**

## Verdict: **PASS — a real step from slots toward structure**
Naive few-shot induction memorises literal words (brittle: 0.0 when an article changes). Abstracting FUNCTION WORDS
lets the LEARNED construction generalise to unseen surface variants (1.0) — the template now captures the pattern,
not the exact words. This is genuine structural generalisation over function words, the next breakthrough-programme
rung after JEP-354. Honest boundary, named: it generalises over articles, NOT yet over word order, synonyms, or
content abstraction — those are the next attacks, and whether the substrate reaches them (without an LLM) is the
open question the programme exists to answer. Established method (function-word abstraction in template induction),
named as such. No transformer.


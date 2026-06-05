# JEP-350 — Honest aggregate Half-1 reach: a realistic multi-paragraph article

## Motivation
After the normalizer work (JEP-348/349), measure the AGGREGATE reach honestly on a longer realistic factual article
(~25 mixed-form sentences): parse coverage, content Q&A, and the gaps it reports. One honest number for "how much of
a real clear article does it understand today." No transformer.

## Method
Read a ~25-sentence realistic article (mixed forms: is-a, plural, conjunction, relative clause, locational,
property, numeric, causal) via `read_to_brain`/`read_text`; measure coverage (sentences yielding ≥1 fact), a content
Q&A battery vs the engine, and list the gaps.

## Pre-registered bars (BEFORE the run)
- **J350a (coverage):** ≥ 0.80 of the article's factual sentences yield ≥1 fact, both seeds (0, 7).
- **J350b (Q&A):** content question battery (is-a multi-hop, property, located-in, numeric) ≥ 0.85 vs the engine,
  both seeds.
- **J350c (gaps honest):** the "what is not clear to you?" report lists genuine undefined concepts (not roots).

Predicted outcome: ~0.85-0.95 coverage given the normalizers, with residual misses on forms still unhandled
(comparatives, "used for", appositives) — reported honestly. If coverage < 0.80, that's the honest aggregate reach.

## Result (seeds 0, 7): **PASS**
- **J350a:** parse coverage = **0.962 (25/26)**, both seeds. Only miss: *"A wolf, which is a wild animal, can
  howl."* — a relative clause whose object is TWO words ("wild animal"); the rule requires a single-word class.
  **PASS.**
- **J350b:** content Q&A = **1.0** vs the engine — is-a multi-hop (poodle→animal, salmon→animal), property
  (poodle inherits bark), numeric (dog 4 legs), locational multi-hop (paris→europe), causal (smoking→cancer), and a
  true-negative (salmon is not a mammal). **PASS.**
- **J350c:** gaps reported = {berlin, cancer, carnivore, europe, france, germany, heart, paris} — genuine undefined
  concepts (it knows "Paris is in France" but not what a Paris/France IS; "carnivore" is a class things ARE but is
  itself undefined). Honest. **PASS.**

## Verdict: **PASS**
Honest aggregate Half-1 reach today: on a realistic ~25-sentence mixed-form article the brain reads **96%** and
answers content questions perfectly, and tells you honestly what it still can't place. The single residual miss
(two-word relative-clause object) is named. This is concrete, measured evidence that "read a clear factual article
and discuss it" works now. No transformer.


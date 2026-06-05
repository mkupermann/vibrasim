# JEP-401 — The honest coverage ceiling on dense, hard encyclopedic prose

## Motivation
Prior real-prose tests (JEP-381/387/395) used articles I wrote, which may unconsciously favor parseable forms. This
honestly maps the TRUE coverage ceiling on deliberately DENSE prose with constructions the rule-based normalizer is NOT
built for: long compound-complex sentences, parentheticals, comparatives, numbers/dates, prepositional chains, and
embedded clauses. The goal is an honest number for "how much genuinely hard text becomes knowledge" — a low result is a
valid, expected finding (mapping the ceiling), not a failure. No transformer.

## Method
A dense ~16-sentence encyclopedic paragraph written to NOT favor the parser (each sentence packs multiple clauses /
modifiers). Read via `read_text`; measure coverage (sentences yielding ≥1 fact). Separately, confirm that whatever IS
captured is still correct (no junk, answers right) and the rest is honestly abstained — i.e. low coverage must NOT
come with wrong facts.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: coverage drops materially on dense prose (the rule-based normalizer captures the simple is-a/property/
causal cores but misses heavily-modified sentences) — I expect ~0.40–0.65, far below the ~0.90 on clean articles. The
finding is the honest ceiling. Critically, captured facts must stay CORRECT (no junk) — partial capture, never wrong
capture.

- **J401a (honest ceiling measured):** report coverage on the dense paragraph (no pass/fail threshold on the NUMBER —
  it is the measurement); both seeds (0, 7) within 0.1 of each other (stable measurement).
- **J401b (no wrong capture):** junk rate (multi-word entity names) ≤0.05, AND a spot-check of 4 questions whose
  answers WERE captured are all correct, both seeds — low coverage must not mean wrong facts.
- **J401c (honest abstention on the missed):** a question about a fact in a SENTENCE THAT DID NOT PARSE returns "don't
  know"/no (not a fabricated answer), both seeds.

This is a measurement + correctness test, not a target to hit. If coverage is surprisingly high, report that honestly
too. Bars (correctness/abstention) fixed; the coverage number is reported as-is. No transformer.

## Result (seeds 0, 7): **PARTIAL / important honest finding** — low ceiling AND wrong-capture on dense prose
- **J401a (honest ceiling): MEASURED — coverage 0.312** (5/16), identical both seeds. Dense prose drops from ~0.90
  (clean articles) to **~31%**: the rule-based normalizer captures the simple cores ("A dog is a mammal", "Smoking
  causes cancer", "A salmon is a fish") but misses heavily-modified sentences (the cheetah/elephant/whale/photosynthesis
  sentences with embedded clauses, parentheticals, comparatives all unparsed). This is the honest real-text ceiling.
- **J401c (honest abstention): PASS** — "is a cheetah the fastest animal?" → not-yes (the dense cheetah sentence didn't
  parse, and the brain doesn't fabricate). Both seeds.
- **J401b (no wrong capture): FAILED — junk rate 0.1.** Two genuine WRONG captures from partial parses of dense
  sentences:
  1. **`('heart', 'isa', 'fist')`** — from "The heart, a muscular organ roughly the size of a fist, pumps blood": the
     appositive rule takes the LAST word of the appositive phrase as the head, but here the phrase ends in a comparative
     modifier ("…the size of a fist"), so it wrongly concludes a heart is a fist.
  2. **`('because they', 'hasprop', 'warm-blooded')`** — from "Because they are warm-blooded and breathe air, whales…":
     a subordinate-clause fragment was captured as a subject ("because they").

## Verdict: **PARTIAL — the honest ceiling is ~31%, and dense prose breaks "never wrong capture"**
The honest measurement: genuinely hard, dense encyclopedic prose yields only ~31% coverage (vs ~90% on clean
articles) — the documented wall, quantified. More importantly, J401b caught that on dense prose the pipeline can produce
WRONG facts (heart→fist; a subordinate-clause subject), not just misses — the "no junk" guarantee that held on clean
articles does NOT hold on dense prose. Since "never wrong capture" underpins the "no mistakes" guarantee, this is the
priority fix: add correctness GUARDS that REJECT suspicious parses (appositive heads inside comparative/prepositional
modifiers; subordinate-clause/pronoun subjects) — better to MISS than to be WRONG. Pre-registered as JEP-402. Coverage
reported as-is (no bar moved); the correctness failure is the actionable finding. No transformer.

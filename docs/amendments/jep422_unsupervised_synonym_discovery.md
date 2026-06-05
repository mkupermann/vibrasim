# JEP-422 — Frontier probe: can the substrate DISCOVER synonyms unsupervised (not taught)?

## Motivation
Michael asked if we built new science. Honest answer: no — established methods, assembled. The honest way to seek
novelty is to attack a concretely OPEN problem, pre-registered, accepting a likely NULL. One frontier I named:
unsupervised meaning-acquisition without an LLM. A sharp, testable slice: JEP-356 showed synonym equivalence must be
TAUGHT (doesn't emerge from induction). Can it instead be DISCOVERED from USAGE — i.e., if two words appear in the same
relational contexts, infer they are equivalent — without being told? This is distributional similarity (an ESTABLISHED
idea, word2vec/Harris' distributional hypothesis) applied over the substrate's symbolic fact store. NOT a claim of new
science — an honest test of where unsupervised equivalence discovery stands in this substrate. No transformer.

## Method
Build a taught world of entities with rich relational profiles. Designate TRUE synonym pairs (used in OVERLAPPING
contexts) at controlled overlap fractions, and random non-synonym pairs. Compute each entity's relational profile
(the set of (role, value) it participates in, as subject and as object) and the Jaccard similarity between profiles.
Ask: does profile similarity SEPARATE true-synonym pairs from random pairs — and at what usage-overlap does separation
break?

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction (honest, stated before running): at HIGH usage-overlap (≥0.9) profile similarity trivially separates true
synonyms (near-tautological — they share almost all facts). At REALISTIC partial overlap (~0.5–0.6) separation BREAKS
(true-synonym similarity overlaps the random-pair distribution) — i.e. **unsupervised synonym discovery does NOT work
reliably over a small symbolic store** (it needs the massive co-occurrence statistics LLMs/word2vec use). I predict the
realistic case is NULL.

- **J422a (high-overlap separability):** at overlap 0.9, every true-synonym pair has profile-Jaccard strictly greater
  than the max random-pair Jaccard, both seeds (0, 7).
- **J422b (realistic-overlap — the frontier):** at overlap 0.55, true-synonym pairs are NOT cleanly separable from
  random pairs (their Jaccard distribution overlaps) — confirming unsupervised discovery is unreliable at realistic
  overlap. (If they ARE cleanly separable, that is a genuinely interesting positive — report it loudly.)
- **J422c (the break-point curve):** report the minimum overlap at which true synonyms become reliably discoverable
  (clean separation) — the honest characterization.

Either outcome is the finding. I predict: works only at near-identical usage (trivial), fails at realistic overlap —
the documented limit, now quantified. Bars fixed; no retuning. Established method (distributional/Jaccard similarity),
named as such; no claim of novelty. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — the frontier limit, quantified)
- **J422a (high-overlap 0.9 separable): PASS** — true-synonym profile-Jaccard min 0.846 >> random-pair max 0.412.
  Near-identical usage is trivially separable.
- **J422b (realistic 0.55 NOT separable): PASS (predicted)** — true-synonym Jaccard (~0.41-0.47) OVERLAPS the random-
  pair distribution (max ~0.44-0.5). At realistic partial overlap, true synonyms are NOT separable from random pairs.
- **J422c (break-point): clean separation only at overlap ≥ 0.8** (fails at 0.4-0.7). 

## Verdict: **PASS — unsupervised synonym discovery fails at realistic overlap (established limit, quantified)**
Relational-profile (distributional) similarity over a small symbolic store DISCOVERS synonyms only when usage is
near-identical (overlap ≥0.8 — almost tautological); at realistic partial overlap (~0.55, where real synonyms live) the
signal is indistinguishable from chance. So unsupervised equivalence discovery needs the massive co-occurrence
statistics that LLMs/word2vec exploit — not available in a small taught store. This is an honest, quantified frontier
limit (consistent with JEP-356's "synonyms must be taught"), using the established distributional hypothesis — NOT new
science. It is one concrete shadow of the deep open problem: sample-efficient unsupervised abstraction. No transformer.

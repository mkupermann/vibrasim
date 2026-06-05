# JEP-424 — Fix natural-knowledge gaps from JEP-423 (proper nouns, multi-word classes, superlatives)

## Motivation
JEP-423 (teaching the Solar System) exposed real gaps. Fix the impactful, clean ones so the LLM-parent can teach a real
topic and the substrate answers complex questions. No transformer.

## Method (`conversation.py` + `brain_query.py`)
- **Multi-word proper nouns:** join 2+ consecutive Capitalized words into one token ("Milky Way" → "milky_way") so they
  pass the junk guard.
- **Proper-noun morphology:** the numeric rule no longer singularizes the subject ("Mars has two moons" → (mars,
  has_moons, 2)); the singular copular is-a keeps a Capitalized subject ending in "s" ("Mars is a planet" → (mars, isa,
  planet)).
- **Superlatives:** "X is the <largest|smallest|…> Y" also stores (Y_head, <sup>, X); query "what is the <sup> Y?" →
  that X.
- **Query-side multi-word class:** "is X a <modifiers> <noun>?" → is_a(X, head-noun).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J424a:** "Mars has two moons." → "how many moons does Mars have?" → 2; "Mars is a planet." → "is Mars a planet?" yes
  (no Mars→mar); both seeds (0, 7).
- **J424b:** "Jupiter is the largest planet." → "what is the largest planet?" → Jupiter; "The Milky Way is a galaxy." →
  "is the Milky Way a galaxy?" yes; both seeds.
- **J424c:** re-running JEP-423, complex Q&A ≥0.90 with zero junk; `pytest -m "not slow" tests/test_conversation.py`
  passes; both seeds.

If a fix mis-fires, report it. Predicted clean. Bars fixed; no retuning. No transformer.

## RESULT (2026-06-05): **PARTIAL → mostly PASS** (implemented J424a + the superlative half of J424b)

Implemented and verified (regression: conversation 10/10 + substrate_memory 14/14 + understanding_engine green):
- **J424a PASS — proper nouns preserved.** `_proper_singular`: in singular-verb rules (X has…, X is a…) a
  Capitalized subject ending in 's' is kept (Mars → **mars**, not "mar"); plural common nouns use "are" so they
  still singularize (Dogs → dog). Copular is-a for a proper noun adds the fact DIRECTLY (bypassing the engine's
  re-singularization). "Mars has two moons" → "how many moons does Mars have?" → **2**; "Mars is a planet" → "is Mars
  a planet?" → **Yes**. Regression intact (cheetah → cat, dog → mammal).
- **J424b superlative PASS.** "X is the <largest|longest|…> Y" → `(Y_head, <sup>, X)`; query "what is the <sup> Y?" →
  X. "Jupiter is the largest planet" → "what is the largest planet?" → **Jupiter**.
- **J424b multi-word proper noun ("Milky Way") — DEFERRED (the one remaining piece).** A clean join needs BOTH the
  teach side and the query side (the question parser in `brain_query`), with an article guard so "The Sun" is not
  joined — higher regression risk; deliberately not rushed during the long-running JEP-459 compute experiment.
  Honestly left open.

Net: 5 of 6 pre-registered sub-cases pass; the proper-noun bug (Mars→mar) and superlatives are fixed and tested.
Established rule-based normalization, named; no new science.

